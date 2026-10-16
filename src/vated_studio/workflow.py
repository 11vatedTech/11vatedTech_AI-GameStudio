from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
import uuid

from .errors import StudioError


class Stage(StrEnum):
    DISCOVER = "discover"
    RESEARCH = "research"
    DEFINE = "define"
    DESIGN = "design"
    SCOPE = "scope"
    PROTOTYPE = "prototype"
    VISUAL_IDENTITY = "visual_identity"
    VERTICAL_SLICE = "vertical_slice"
    PRODUCE = "produce"
    INTEGRATE = "integrate"
    PLAYTEST = "playtest"
    REFINE = "refine"
    VERIFY = "verify"
    PACKAGE = "package"
    RELEASE = "release"
    LEARN = "learn"


_TRANSITIONS: dict[Stage, set[Stage]] = {
    Stage.DISCOVER: {Stage.RESEARCH},
    Stage.RESEARCH: {Stage.DEFINE, Stage.DISCOVER},
    Stage.DEFINE: {Stage.DESIGN, Stage.RESEARCH},
    Stage.DESIGN: {Stage.SCOPE, Stage.DEFINE},
    Stage.SCOPE: {Stage.PROTOTYPE, Stage.DESIGN},
    Stage.PROTOTYPE: {Stage.VISUAL_IDENTITY, Stage.DESIGN, Stage.SCOPE},
    Stage.VISUAL_IDENTITY: {Stage.VERTICAL_SLICE, Stage.PROTOTYPE, Stage.DESIGN},
    Stage.VERTICAL_SLICE: {Stage.PRODUCE, Stage.DESIGN, Stage.SCOPE},
    Stage.PRODUCE: {Stage.INTEGRATE, Stage.VISUAL_IDENTITY, Stage.DESIGN},
    Stage.INTEGRATE: {Stage.PLAYTEST, Stage.PRODUCE, Stage.DESIGN},
    Stage.PLAYTEST: {Stage.REFINE, Stage.VERIFY, Stage.DESIGN, Stage.SCOPE},
    Stage.REFINE: {Stage.INTEGRATE, Stage.PLAYTEST, Stage.VERIFY},
    Stage.VERIFY: {Stage.PACKAGE, Stage.REFINE, Stage.INTEGRATE},
    Stage.PACKAGE: {Stage.RELEASE, Stage.VERIFY},
    Stage.RELEASE: {Stage.LEARN},
    Stage.LEARN: {Stage.DISCOVER},
}


@dataclass(slots=True)
class StageEvent:
    stage: str
    occurred_at: str
    evidence: list[str] = field(default_factory=list)
    note: str = ""


@dataclass(slots=True)
class ProjectWorkflow:
    project_id: str
    title: str
    current_stage: Stage = Stage.DISCOVER
    history: list[StageEvent] = field(default_factory=list)

    @classmethod
    def create(cls, title: str, project_id: str | None = None) -> "ProjectWorkflow":
        title = title.strip()
        if not title:
            raise StudioError("Project title is required", code="missing_title")
        return cls(project_id or uuid.uuid4().hex, title)

    def advance(self, destination: Stage | str, *, evidence: list[str] | None = None, note: str = "") -> None:
        try:
            target = destination if isinstance(destination, Stage) else Stage(destination)
        except ValueError as exc:
            raise StudioError("Unknown workflow stage", code="invalid_stage", details={"stage": str(destination)}) from exc
        if target not in _TRANSITIONS[self.current_stage]:
            raise StudioError("Invalid workflow transition", code="invalid_transition",
                              details={"current": self.current_stage.value, "target": target.value,
                                       "allowed": sorted(s.value for s in _TRANSITIONS[self.current_stage])}, http_status=409)
        self.history.append(StageEvent(self.current_stage.value, datetime.now(timezone.utc).isoformat(), evidence or [], note))
        self.current_stage = target

    def to_dict(self) -> dict[str, Any]:
        return {"project_id": self.project_id, "title": self.title, "current_stage": self.current_stage.value,
                "history": [{"stage": item.stage, "occurred_at": item.occurred_at, "evidence": item.evidence, "note": item.note} for item in self.history]}


def workflow_contract() -> dict[str, Any]:
    return {"stages": [stage.value for stage in Stage],
            "transitions": {stage.value: sorted(target.value for target in targets) for stage, targets in _TRANSITIONS.items()},
            "principle": "Stages are revisitable under explicit evidence; a completed stage is not a claim that the game is release-ready."}
