from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json

from .errors import StudioError


DEFAULT_PROFILES: dict[str, dict[str, Any]] = {
    "24h": {"hours": 24, "reserve_fraction": 0.25, "milestones": [
        {"stage": "discovery_and_pitch", "fraction": 0.06}, {"stage": "design_and_scope", "fraction": 0.09},
        {"stage": "playable_prototype", "fraction": 0.20}, {"stage": "visual_identity_and_vertical_slice", "fraction": 0.17},
        {"stage": "content_and_integration", "fraction": 0.18}, {"stage": "polish_and_playtest", "fraction": 0.12},
        {"stage": "release_and_buffer", "fraction": 0.18}],
        "scope_rules": ["One core loop", "One primary environment", "A small approved asset set", "A complete start-to-restart path", "No optional feature after content freeze"]},
    "72h": {"hours": 72, "reserve_fraction": 0.22, "milestones": [
        {"stage": "discovery_and_research", "fraction": 0.05}, {"stage": "design_and_scope", "fraction": 0.08},
        {"stage": "vertical_slice", "fraction": 0.18}, {"stage": "visual_identity", "fraction": 0.10},
        {"stage": "content_production", "fraction": 0.22}, {"stage": "integration_and_audio", "fraction": 0.13},
        {"stage": "playtest_and_polish", "fraction": 0.12}, {"stage": "release_and_buffer", "fraction": 0.12}],
        "scope_rules": ["Vertical slice before content expansion", "Reuse proven tools", "One feature freeze", "Ship only integrated content"]},
    "14d": {"hours": 336, "reserve_fraction": 0.20, "milestones": [
        {"stage": "discovery_and_research", "fraction": 0.06}, {"stage": "design_and_scope", "fraction": 0.07},
        {"stage": "prototype", "fraction": 0.10}, {"stage": "vertical_slice", "fraction": 0.12},
        {"stage": "content_production", "fraction": 0.25}, {"stage": "systems_and_levels", "fraction": 0.14},
        {"stage": "polish_and_playtest", "fraction": 0.12}, {"stage": "release_and_buffer", "fraction": 0.14}],
        "scope_rules": ["Maintain a playable build", "Review art direction before batch generation", "Use content freeze and release-candidate gates", "Profile before optimization"]},
}


@dataclass(frozen=True, slots=True)
class Task:
    id: str
    title: str
    estimate_minutes: int
    priority: int = 3
    depends_on: tuple[str, ...] = ()
    mandatory: bool = True


def load_profiles() -> dict[str, Any]:
    # Callers receive their own snapshot; mutable module defaults remain private.
    import copy
    return copy.deepcopy(DEFAULT_PROFILES)


def plan_jam(profile: str, tasks: list[dict[str, Any]], *, elapsed_minutes: int = 0,
             measured_tasks: dict[str, int] | None = None) -> dict[str, Any]:
    """Plan tasks within a time budget while respecting dependencies and release reserve.

    This is a deterministic greedy planner, not a project-duration oracle or full
    resource-constrained critical-path scheduler. It never plans a task whose
    dependencies were deferred.
    """
    if profile not in DEFAULT_PROFILES:
        raise StudioError("Unknown jam profile", code="unknown_profile", details={"profile": profile, "available": sorted(DEFAULT_PROFILES)})
    if not isinstance(tasks, list):
        raise StudioError("tasks must be an array", code="invalid_tasks")
    if isinstance(elapsed_minutes, bool) or not isinstance(elapsed_minutes, int) or elapsed_minutes < 0:
        raise StudioError("elapsed_minutes must be a non-negative integer", code="invalid_elapsed_minutes")
    measured_tasks = measured_tasks or {}
    if not isinstance(measured_tasks, dict):
        raise StudioError("measured_tasks must be an object", code="invalid_measured_tasks")

    normalized: list[Task] = []
    seen: set[str] = set()
    for item in tasks:
        if not isinstance(item, dict):
            raise StudioError("Each task must be an object", code="invalid_task")
        task_id = str(item.get("id", "")).strip()
        title = str(item.get("title", "")).strip()
        try:
            estimate = int(item.get("estimate_minutes", 0))
            priority = int(item.get("priority", 3))
        except (TypeError, ValueError) as exc:
            raise StudioError("Task estimate and priority must be integers", code="invalid_task_numbers", details={"id": task_id}) from exc
        if not task_id or not title or task_id in seen or estimate <= 0 or not 1 <= priority <= 5:
            raise StudioError("Task id/title must be unique and estimate positive; priority must be 1..5", code="invalid_task", details={"id": task_id})
        deps = item.get("depends_on", [])
        if not isinstance(deps, list) or any(not isinstance(dep, str) or not dep.strip() for dep in deps):
            raise StudioError("depends_on must be an array of task IDs", code="invalid_dependencies", details={"id": task_id})
        if len(set(deps)) != len(deps):
            raise StudioError("Dependency IDs must not be duplicated", code="invalid_dependencies", details={"id": task_id})
        raw_mandatory = item.get("mandatory", True)
        if not isinstance(raw_mandatory, bool):
            raise StudioError("mandatory must be a boolean", code="invalid_mandatory", details={"id": task_id})
        seen.add(task_id)
        normalized.append(Task(task_id, title, estimate, priority, tuple(deps), raw_mandatory))

    by_id = {task.id: task for task in normalized}
    estimates: dict[str, int] = {}
    for task in normalized:
        unknown = set(task.depends_on) - by_id.keys()
        if unknown:
            raise StudioError("Task dependency references unknown IDs", code="unknown_dependency", details={"id": task.id, "unknown": sorted(unknown)})
        if task.id in task.depends_on:
            raise StudioError("Task cannot depend on itself", code="dependency_cycle", details={"id": task.id})
        measured = measured_tasks.get(task.id, task.estimate_minutes)
        try:
            if isinstance(measured, bool):
                raise ValueError
            measured = int(measured)
        except (TypeError, ValueError) as exc:
            raise StudioError("Measured task duration must be a positive integer", code="invalid_measured_duration", details={"id": task.id}) from exc
        if measured <= 0:
            raise StudioError("Measured task duration must be a positive integer", code="invalid_measured_duration", details={"id": task.id})
        estimates[task.id] = measured
    _assert_acyclic(by_id)

    data = DEFAULT_PROFILES[profile]
    budget = data["hours"] * 60
    remaining = max(0, budget - elapsed_minutes)
    reserve = round(budget * data["reserve_fraction"])
    work_capacity = max(0, remaining - reserve)
    total_mandatory = sum(estimates[task.id] for task in normalized if task.mandatory)
    total_all = sum(estimates.values())

    pending = dict(by_id)
    planned: list[dict[str, Any]] = []
    cut: list[dict[str, Any]] = []
    planned_ids: set[str] = set()
    deferred_ids: set[str] = set()
    remaining_work = work_capacity

    while pending:
        # Any task with a deferred dependency is impossible in this plan.
        impossible = [task for task in pending.values() if set(task.depends_on) & deferred_ids]
        for task in sorted(impossible, key=lambda item: item.id):
            failed_deps = sorted(set(task.depends_on) & deferred_ids)
            cut.append({"id": task.id, "title": task.title, "estimate_minutes": estimates[task.id],
                        "reason": "Dependency deferred: " + ", ".join(failed_deps)})
            deferred_ids.add(task.id)
            pending.pop(task.id)
        if not pending:
            break

        ready = [task for task in pending.values() if set(task.depends_on) <= planned_ids]
        if not ready:
            # Cycles should be caught above; this is a defensive invariant.
            raise StudioError("No schedulable task remains after dependency validation", code="planner_invariant_failed")
        ready.sort(key=lambda task: (not task.mandatory, task.priority, estimates[task.id], task.id))
        progressed = False
        for task in ready:
            estimate = estimates[task.id]
            if estimate <= remaining_work:
                planned.append({"id": task.id, "title": task.title, "estimate_minutes": estimate,
                                "priority": task.priority, "mandatory": task.mandatory, "depends_on": list(task.depends_on)})
                planned_ids.add(task.id)
                remaining_work -= estimate
            else:
                reason = "Insufficient planned work capacity; preserve release reserve."
                cut.append({"id": task.id, "title": task.title, "estimate_minutes": estimate, "reason": reason})
                deferred_ids.add(task.id)
            pending.pop(task.id)
            progressed = True
        if not progressed:
            raise StudioError("Planner failed to make progress", code="planner_invariant_failed")

    mandatory_cut = any(task["id"] in {t.id for t in normalized if t.mandatory} for task in cut)
    return {"profile": profile, "time_budget_minutes": budget, "elapsed_minutes": elapsed_minutes,
            "remaining_minutes": remaining, "release_reserve_minutes": reserve,
            "planned_work_capacity_minutes": work_capacity, "mandatory_estimate_minutes": total_mandatory,
            "total_estimate_minutes": total_all, "within_mandatory_budget": total_mandatory <= work_capacity and not mandatory_cut,
            "overrun_risk": total_mandatory > work_capacity or mandatory_cut,
            "planned_tasks": planned, "deferred_tasks": cut, "remaining_planned_capacity_minutes": remaining_work,
            "scope_rules": list(data["scope_rules"]),
            "warning": "Task durations are estimates, not guarantees. This deterministic greedy planner respects task dependencies but is not a full critical-path or resource-constrained scheduler."}


def _assert_acyclic(by_id: dict[str, Task]) -> None:
    visiting: set[str] = set()
    visited: set[str] = set()
    def visit(task_id: str) -> None:
        if task_id in visiting:
            raise StudioError("Dependency graph contains a cycle", code="dependency_cycle", details={"task_id": task_id})
        if task_id in visited:
            return
        visiting.add(task_id)
        for dep in by_id[task_id].depends_on:
            visit(dep)
        visiting.remove(task_id)
        visited.add(task_id)
    for key in by_id:
        visit(key)
