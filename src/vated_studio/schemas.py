from __future__ import annotations

from pathlib import Path
from typing import Any
import json

from .errors import StudioError


def schema_root() -> Path:
    # Development repo has ./schemas; installed wheels keep a copy under package data only if bundled.
    candidates = [Path.cwd() / "schemas", Path(__file__).resolve().parents[2] / "schemas", Path(__file__).resolve().parent / "data" / "schemas"]
    return next((candidate for candidate in candidates if candidate.is_dir()), candidates[0])


def list_schemas(root: Path | None = None) -> list[str]:
    base = root or schema_root()
    return sorted(path.name for path in base.glob("*.schema.json"))


def validate_document(document: Any, schema_name: str, root: Path | None = None) -> dict[str, Any]:
    if "/" in schema_name or "\\" in schema_name or not schema_name.endswith(".schema.json"):
        raise StudioError("Use a schema basename ending in .schema.json", code="invalid_schema_name")
    base = root or schema_root()
    path = (base / schema_name).resolve()
    if path.parent != base.resolve() or not path.is_file():
        raise StudioError("Schema not found", code="schema_not_found", details={"schema": schema_name}, http_status=404)
    schema = json.loads(path.read_text(encoding="utf-8"))
    try:
        import jsonschema
    except ImportError:
        missing = _minimal_validate(document, schema)
        return {"valid": not missing, "validator": "required-fields-fallback", "errors": missing,
                "warning": "Install the validation extra for full JSON Schema validation."}
    validator = jsonschema.Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(document), key=lambda e: (list(e.absolute_path), e.message))
    return {"valid": not errors, "validator": "jsonschema-draft-2020-12", "errors": [
        {"path": "/" + "/".join(str(part) for part in err.absolute_path), "message": err.message,
         "validator": err.validator} for err in errors]}


def _minimal_validate(document: Any, schema: dict[str, Any]) -> list[dict[str, str]]:
    if not isinstance(document, dict):
        return [{"path": "/", "message": "Expected a JSON object"}]
    return [{"path": "/" + key, "message": "Required property is missing"}
            for key in schema.get("required", []) if key not in document]
