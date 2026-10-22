from pathlib import Path
import json
import re
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_every_json_schema_parses_and_meets_meta_schema():
    import jsonschema
    schemas = sorted((ROOT / "schemas").glob("*.schema.json"))
    assert len(schemas) >= 20
    for path in schemas:
        schema = json.loads(path.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(schema)
        assert schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema"


def test_bundled_schemas_are_identical_to_repository_schemas():
    root = ROOT / "src" / "vated_studio" / "data" / "schemas"
    for source in (ROOT / "schemas").glob("*.schema.json"):
        bundled = root / source.name
        assert bundled.is_file(), source.name
        assert json.loads(bundled.read_text(encoding="utf-8")) == json.loads(source.read_text(encoding="utf-8"))


def test_skill_library_is_populated_and_search_metadata_is_parseable(service):
    rows = service.execute("skills.list", {})["result"]["skills"]
    assert len(rows) >= 75
    assert len({row["id"] for row in rows}) == len(rows)
    for row in rows:
        assert row["title"]
        assert row["summary"]
        assert row["tags"]
        path = ROOT / "skills" / row["id"] / "SKILL.md"
        content = path.read_text(encoding="utf-8")
        assert content.startswith("---\n") and ("## Acceptance criteria" in content or "## Acceptance" in content)


def test_required_public_repository_docs_exist():
    required = [
        "AGENTS.md", "FREEBUFF.md", "CLAUDE.md", "GEMINI.md", "SECURITY.md", "CONTRIBUTING.md",
        "docs/studio/11vatedtech-game-production-canon.md", "docs/workflows/game-jam-24h.md",
        "docs/workflows/game-jam-72h.md", "docs/workflows/game-jam-14d.md",
        "docs/research/source-register.json", "docs/architecture.md", "docs/known-limitations.md",
        "docs/creative/animation-production.md", "docs/creative/asset-production-standard.md",
        "docs/capability-register.json", ".github/workflows/ci.yml", "VERIFICATION.md",
    ]
    missing = [item for item in required if not (ROOT / item).is_file()]
    assert not missing, missing


def test_public_repository_has_no_env_or_local_state_files():
    bad_names = {".env", ".env.local", "studio.sqlite3", "api-token"}
    # Git-ignored local tooling/state dirs are runtime side effects
    # (ags CLI creates .state/; dev installs live in .venv/). Both paths
    # verify as ignored via `git check-ignore`. CI covers the clean tree.
    excluded_top_dirs = {
        ".venv", "venv", ".git", "build", "dist", "dist-check",
        "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
        "htmlcov", ".state", ".studio-state", ".cache", ".cache-ags",
        "workspace",
    }
    found = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if rel.parts[0] in excluded_top_dirs:
            continue
        if path.name in bad_names or path.name.endswith((".sqlite", ".sqlite3", ".db", ".token")):
            # A workspace-local secret/config file is not part of the public
            # repository if Git actually ignores it. Keep scanning for tracked
            # or otherwise publishable secret files; clean CI still catches any
            # unignored .env without depending on a developer's local setup.
            ignored = subprocess.run(
                ["git", "check-ignore", "--quiet", "--", rel.as_posix()],
                cwd=ROOT,
                capture_output=True,
                check=False,
            ).returncode == 0
            if not ignored:
                found.append(str(rel))
    assert not found, found


def test_source_register_has_valid_urls_and_unique_ids():
    data = json.loads((ROOT / "docs/research/source-register.json").read_text(encoding="utf-8"))
    sources = data["sources"]
    ids = [row["id"] for row in sources]
    assert len(ids) == len(set(ids))
    assert len(sources) >= 12
    assert all(row["url"].startswith("https://") for row in sources)


def test_cli_entrypoint_runs_without_repository_cwd(tmp_path):
    env = dict(__import__("os").environ)
    env["PYTHONPATH"] = str(ROOT / "src")
    status = subprocess.run([sys.executable, "-m", "vated_studio.cli", "--help"], cwd=tmp_path, env=env, capture_output=True, text=True, timeout=10)
    assert status.returncode == 0
    assert "AI Game Studio" in status.stdout


def test_no_generated_weights_are_committed_to_repo():
    weight_suffixes = {".safetensors", ".ckpt", ".gguf", ".pth", ".pt"}
    # Local tooling dirs are git-ignored and never published; scanning them
    # produces false positives (e.g. editable-install .pth pointers in .venv).
    # CI validates this correctly from a clean checkout without those dirs.
    excluded_top_dirs = {
        ".venv", "venv", ".git", "build", "dist", "dist-check",
        "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
        "htmlcov",
    }
    found = []
    for p in ROOT.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in weight_suffixes:
            continue
        rel = p.relative_to(ROOT)
        if rel.parts[0] in excluded_top_dirs:
            continue
        if p.suffix.lower() == ".egg-info":
            continue
        found.append(str(rel))
    assert not found, found


def test_static_capability_register_matches_runtime_and_schema():
    import jsonschema
    from vated_studio.capabilities import CapabilityRegistry

    register_path = ROOT / "docs" / "capability-register.json"
    data = json.loads(register_path.read_text(encoding="utf-8"))
    schema = json.loads((ROOT / "schemas" / "capability-register.schema.json").read_text(encoding="utf-8"))
    jsonschema.validate(data, schema)
    runtime = CapabilityRegistry().list()
    assert data["capabilities"] == runtime
    assert len(data["capabilities"]) >= 15
    for capability in runtime:
        for field in ("dependencies", "verification", "limitations"):
            values = capability[field]
            assert isinstance(values, list)
            assert all(isinstance(value, str) and len(value) > 1 for value in values), (capability["id"], field, values)


def test_github_actions_uses_pinned_actions_and_least_permissions():
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "permissions:\n  contents: read" in workflow
    assert re.search(r"uses: actions/checkout@[0-9a-f]{40}", workflow)
    assert re.search(r"uses: actions/setup-python@[0-9a-f]{40}", workflow)
    assert "AGS_WORKSPACE: ${{ runner.temp }}/ags-workspace" in workflow


def test_bundled_skill_library_is_identical_to_authoritative_skill_sources():
    root_skills = ROOT / "skills"
    bundled_skills = ROOT / "src" / "vated_studio" / "data" / "skills"
    root_files = {p.relative_to(root_skills).as_posix(): p.read_bytes() for p in root_skills.glob("*/SKILL.md")}
    bundled_files = {p.relative_to(bundled_skills).as_posix(): p.read_bytes() for p in bundled_skills.glob("*/SKILL.md")}
    assert len(root_files) >= 75
    assert root_files == bundled_files
