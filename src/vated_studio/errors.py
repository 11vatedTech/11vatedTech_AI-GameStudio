from __future__ import annotations


class StudioError(Exception):
    """Expected operator-facing error with a stable machine-readable code."""

    def __init__(self, message: str, *, code: str = "studio_error", details: dict | None = None, http_status: int = 400):
        super().__init__(message)
        self.code = code
        self.details = details or {}
        self.http_status = http_status

    def as_dict(self) -> dict:
        return {"code": self.code, "message": str(self), "details": self.details}
