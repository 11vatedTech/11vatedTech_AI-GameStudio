import pytest
from vated_studio.errors import StudioError
from vated_studio.planner import load_profiles, plan_jam
from vated_studio.workflow import ProjectWorkflow, Stage


def test_all_jam_profiles_have_reserve_and_milestones():
    profiles = load_profiles()
    assert set(profiles) == {"24h", "72h", "14d"}
    assert all(0 < p["reserve_fraction"] < 0.5 for p in profiles.values())
    # Returned profile mutation must not mutate process-wide defaults.
    profiles["24h"]["hours"] = 999
    assert load_profiles()["24h"]["hours"] == 24


def test_planner_schedules_dependencies_before_dependents():
    tasks = [
        {"id": "b", "title": "Integrate", "estimate_minutes": 30, "depends_on": ["a"]},
        {"id": "a", "title": "Create prototype", "estimate_minutes": 60},
    ]
    result = plan_jam("24h", tasks)
    ordered = [task["id"] for task in result["planned_tasks"]]
    assert ordered.index("a") < ordered.index("b")


def test_planner_never_schedules_task_when_dependency_is_deferred():
    # Only 1h planned capacity remains after setting elapsed time; first task is too long.
    tasks = [
        {"id": "base", "title": "Build base", "estimate_minutes": 300},
        {"id": "dependent", "title": "Integrate dependent", "estimate_minutes": 10, "depends_on": ["base"]},
        {"id": "independent", "title": "Independent polish", "estimate_minutes": 10},
    ]
    result = plan_jam("24h", tasks, elapsed_minutes=17 * 60)
    planned = {task["id"] for task in result["planned_tasks"]}
    cut = {task["id"]: task["reason"] for task in result["deferred_tasks"]}
    assert "base" not in planned and "dependent" not in planned
    assert "Dependency deferred" in cut["dependent"]
    assert "independent" in planned
    assert result["overrun_risk"] is True


def test_planner_uses_measured_estimates_and_release_reserve():
    tasks = [{"id": "a", "title": "A", "estimate_minutes": 3}]
    result = plan_jam("24h", tasks, measured_tasks={"a": 17})
    assert result["total_estimate_minutes"] == 17
    assert result["release_reserve_minutes"] == 360


def test_planner_rejects_unknown_dependency_and_cycles():
    with pytest.raises(StudioError, match="Task dependency"):
        plan_jam("24h", [{"id": "a", "title": "A", "estimate_minutes": 1, "depends_on": ["b"]}])
    with pytest.raises(StudioError) as exc:
        plan_jam("24h", [
            {"id": "a", "title": "A", "estimate_minutes": 1, "depends_on": ["b"]},
            {"id": "b", "title": "B", "estimate_minutes": 1, "depends_on": ["a"]},
        ])
    assert exc.value.code == "dependency_cycle"


@pytest.mark.parametrize("tasks", [
    [{"id": "a", "title": "A", "estimate_minutes": 0}],
    [{"id": "a", "title": "A", "estimate_minutes": 1}, {"id": "a", "title": "Duplicate", "estimate_minutes": 1}],
    [{"id": "a", "title": "A", "estimate_minutes": 1, "mandatory": "false"}],
])
def test_planner_rejects_malformed_tasks(tasks):
    with pytest.raises(StudioError):
        plan_jam("24h", tasks)


def test_workflow_allowed_transition_and_evidence():
    wf = ProjectWorkflow.create("Project", "project-id")
    wf.advance(Stage.RESEARCH, evidence=["docs/research.md"], note="Validated references")
    assert wf.current_stage is Stage.RESEARCH
    assert wf.to_dict()["history"][0]["evidence"] == ["docs/research.md"]


def test_workflow_rejects_invalid_transition():
    wf = ProjectWorkflow.create("Project")
    with pytest.raises(StudioError) as exc:
        wf.advance(Stage.RELEASE)
    assert exc.value.code == "invalid_transition"
