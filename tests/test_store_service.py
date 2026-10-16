from pathlib import Path
import json
import pytest

from vated_studio.errors import StudioError
from vated_studio.service import StudioService
from vated_studio.store import StudioStore


def test_store_runs_events_feedback_and_assets(tmp_path):
    store = StudioStore(tmp_path)
    store.start_run("r1", "test", {"x": 1})
    store.finish_run("r1", "succeeded", result={"ok": True})
    store.record_asset(asset_id="a1", project_id="p1", kind="sprite", relative_path="assets/a.png", sha256="abc", metadata={"source": "test"})
    store.add_feedback(feedback_id="f1", project_id="p1", artifact_id="a1", category="art", rating=4, notes="Readable", reviewer_type="human", context={})
    assert store.runs()[0]["result"]["ok"] is True
    assert store.assets()[0]["id"] == "a1"
    assert store.counts()["feedback"] == 1
    assert store.counts()["events"] >= 4


def test_service_command_execution_is_tracked(service):
    result = service.execute("status", {})
    assert result["status"] == "succeeded"
    assert result["result"]["name"] == "11vatedTech AI Game Studio"
    runs = service.execute("runs.list", {})["result"]["runs"]
    run = next(row for row in runs if row["command"] == "status")
    assert run["status"] == "succeeded"


def test_service_unknown_command_has_structured_error(service):
    with pytest.raises(StudioError) as exc:
        service.execute("does.not.exist", {})
    assert exc.value.code == "unknown_command"


def test_service_skills_search_and_read(service):
    result = service.execute("skills.search", {"query": "character identity", "limit": 10})["result"]
    assert result["count"] >= 1
    selected = next(row for row in result["results"] if row["id"] == "character-animation-identity")
    content = service.execute("skills.read", {"id": selected["id"]})["result"]["content"]
    assert "Acceptance" in content or "acceptance" in content.lower()
    with pytest.raises(StudioError):
        service.execute("skills.read", {"id": "../secrets"})


def test_project_creation_and_static_validation(service, workspace):
    made = service.execute("project.create", {"title": "Test Game", "slug": "test-game"})["result"]
    assert made["status"] == "created"
    path = Path(made["project_path"])
    assert (path / "project.godot").is_file()
    check = service.execute("project.validate", {"path": "projects/test-game", "run_engine": False})["result"]
    assert check["static_valid"] is True
    guarded = service.execute("project.create", {"title": 'Bad "title"\nInjected', "slug": "../outside"})["result"]
    guarded_path = Path(guarded["project_path"]).resolve()
    assert guarded_path.parent == (workspace / "projects").resolve()
    project_text = (guarded_path / "project.godot").read_text(encoding="utf-8")
    assert "__PROJECT_TITLE__" not in project_text


def test_service_rejects_asset_path_traversal(service):
    with pytest.raises(StudioError) as exc:
        service.execute("asset.inspect", {"path": "../../etc/passwd"})
    assert exc.value.code == "path_outside_workspace"


def test_schema_validation_reports_invalid_document(service, workspace):
    doc = workspace / "brief.json"
    doc.write_text(json.dumps({"title": "Missing fields"}), encoding="utf-8")
    result = service.execute("schema.validate", {"schema": "game-brief.schema.json", "document": "brief.json"})["result"]
    assert result["valid"] is False
    with pytest.raises(StudioError):
        service.execute("schema.validate", {"schema": "../bad.schema.json", "document": "brief.json"})
