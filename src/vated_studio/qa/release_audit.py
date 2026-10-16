from __future__ import annotations

from pathlib import Path
from typing import Any
import json
import os
import tempfile
import zipfile

from ..jsonio import sha256_file
from ..paths import ensure_inside


_SECRET_BASENAMES = {".env", ".env.local", ".env.production", "api-token", "credentials.json", "secrets.json", "id_rsa", "id_ed25519"}
_SECRET_SUFFIXES = {".pem", ".key", ".p12", ".pfx", ".token"}
_MODEL_SUFFIXES = {".safetensors", ".ckpt", ".pt", ".pth", ".gguf", ".onnx", ".bin"}
_EXCLUDED_DIRS = {
    ".git", ".venv", "venv", "env", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    ".godot", ".blender", "node_modules", ".state", ".cache", "cache", "caches", "dist", "dist-check", "build", 
}


def _relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _excluded_reason(rel: str) -> str | None:
    path = Path(rel)
    parts = {part.lower() for part in path.parts}
    name = path.name.lower()
    suffix = path.suffix.lower()
    if parts & _EXCLUDED_DIRS:
        return "generated_cache_or_local_state"
    if any(part.endswith(".egg-info") for part in parts):
        return "build_metadata"
    if name in _SECRET_BASENAMES or (name.startswith(".env.") and name != ".env.example"):
        return "environment_or_secret_file"
    if suffix in _SECRET_SUFFIXES:
        return "secret_or_private_key_file"
    if suffix in _MODEL_SUFFIXES:
        return "model_weight_or_binary_checkpoint"
    if name.endswith(".sqlite") or name.endswith(".sqlite3") or name.endswith(".db"):
        return "local_database"
    if name.endswith(".pyc") or name.endswith(".pyo"):
        return "compiled_python_cache"
    if name in {"thumbs.db", ".ds_store"}:
        return "operating_system_metadata"
    return None


def audit_release(root: Path, release_dir: str | Path, *, required_files: list[str] | None = None) -> dict[str, Any]:
    target = ensure_inside(root, release_dir)
    findings: list[dict[str, Any]] = []
    if not target.is_dir():
        return {"status": "blocked", "release_dir": str(target), "findings": [{"severity": "blocker", "code": "release_directory_missing"}], "file_count": 0}
    files: list[dict[str, Any]] = []
    excluded: list[dict[str, str]] = []
    for path in target.rglob("*"):
        rel = _relative(path, target)
        if path.is_symlink():
            findings.append({"severity": "blocker", "code": "symlink_in_release", "path": rel})
            continue
        reason = _excluded_reason(rel)
        if reason:
            severity = "blocker" if reason in {"environment_or_secret_file", "secret_or_private_key_file", "model_weight_or_binary_checkpoint"} else "warning"
            findings.append({"severity": severity, "code": reason, "path": rel})
            excluded.append({"path": rel, "reason": reason})
            continue
        if path.is_file():
            size = path.stat().st_size
            if not size:
                findings.append({"severity": "warning", "code": "empty_file", "path": rel})
            files.append({"path": rel, "bytes": size, "sha256": sha256_file(path)})
    paths = {item["path"] for item in files}
    missing = sorted(set(required_files or []) - paths)
    for item in missing:
        findings.append({"severity": "blocker", "code": "required_file_missing", "path": item})
    web_files = [name for name in paths if name.endswith((".html", ".wasm", ".pck", ".js"))]
    if web_files and not any(name.endswith(".html") for name in web_files):
        findings.append({"severity": "blocker", "code": "web_export_missing_html"})
    has_test_evidence = any("pytest" in name.lower() or "test" in name.lower() and name.lower().endswith((".txt", ".log", ".json")) for name in paths)
    if not has_test_evidence:
        findings.append({"severity": "warning", "code": "test_evidence_not_found"})
    status = "blocked" if any(row["severity"] == "blocker" for row in findings) else "review_required"
    return {"status": status, "release_dir": str(target), "file_count": len(files), "total_bytes": sum(item["bytes"] for item in files),
            "required_files": required_files or [], "missing_required_files": missing, "excluded_or_risky_files": excluded,
            "web_export_related_files": sorted(web_files), "test_evidence_present": has_test_evidence, "files": files, "findings": findings,
            "human_gates": {"commercial_rights": "open", "art_direction": "open", "cold_playtest": "open"},
            "note": "This audit inventories and hashes files. It flags secret/model-weight risks and does not certify artistic quality, legal clearance, or gameplay correctness."}


def package_release(root: Path, source_dir: str | Path, archive_path: str | Path, *, overwrite: bool = False) -> dict[str, Any]:
    """Create a deterministic-path source archive with public-repository safety exclusions.

    The archive does not include secrets, local state/databases, virtual environments,
    engine caches, or model weights by default. Exclusions are returned as evidence.
    """
    root = root.resolve()
    source = ensure_inside(root, source_dir)
    if not source.is_dir():
        raise ValueError("source_dir must be a directory inside the workspace")
    output = ensure_inside(root, archive_path)
    if source == output or source in output.parents:
        raise ValueError("Archive output cannot be inside the source tree")
    if output.exists() and not overwrite:
        raise ValueError("Archive output already exists; pass overwrite=True to replace it")
    if output.is_dir():
        raise ValueError("Archive output must be a file path")
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{output.name}.", suffix=".tmp", dir=output.parent)
    os.close(fd)
    temp_path = Path(temp_name)
    entries: list[dict[str, Any]] = []
    excluded: list[dict[str, str]] = []
    try:
        with zipfile.ZipFile(temp_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as archive:
            for path in sorted(source.rglob("*"), key=lambda item: item.relative_to(source).as_posix().lower()):
                rel = _relative(path, source)
                if path.is_symlink():
                    raise ValueError(f"Refusing to package symlink: {path}")
                if not path.is_file():
                    continue
                reason = _excluded_reason(rel)
                if reason:
                    excluded.append({"path": rel, "reason": reason})
                    continue
                archive.write(path, arcname=rel)
                entries.append({"path": rel, "bytes": path.stat().st_size, "sha256": sha256_file(path)})
        with zipfile.ZipFile(temp_path) as archive:
            corrupt = archive.testzip()
            names = archive.namelist()
        if corrupt:
            raise ValueError(f"ZIP integrity verification failed at {corrupt}")
        os.replace(temp_path, output)
    finally:
        try:
            temp_path.unlink(missing_ok=True)
        except OSError:
            pass
    archive_hash = sha256_file(output)
    hash_path = output.with_suffix(output.suffix + ".sha256")
    hash_path.write_text(f"{archive_hash}  {output.name}\n", encoding="utf-8")
    manifest = {"schema_version": "1.0", "archive": output.name, "archive_sha256": archive_hash,
                "file_count": len(names), "uncompressed_bytes": sum(item["bytes"] for item in entries),
                "zip_integrity": "passed", "entries": entries, "excluded_files": excluded,
                "policy": "Secrets, local state, caches, private-key files, and model-weight formats are excluded by default."}
    manifest_path = output.with_suffix(output.suffix + ".manifest.json")
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return {"archive": str(output), "sha256": archive_hash, "sha256_file": str(hash_path),
            "manifest_file": str(manifest_path), "file_count": len(names), "excluded_file_count": len(excluded), "zip_integrity": "passed"}
