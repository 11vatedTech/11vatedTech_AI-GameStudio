"""Durable job queue built on the existing SQLite ``runs`` table.

Lifecycle::

    queued --claim--> running --succeed--> succeeded
       ^                 |  \\--fail(non-retryable / attempts exhausted)--> failed
       |                 |  \\--fail(cancel requested)------------------> cancelled
       |                 |  \\--fail(retryable, attempts left)-----------+
       |                 \\--lease expires (crash) --reconcile------------+
       \\--cancel (queued) --> cancelled

Guarantees:
- Every claim issues a fresh fencing token; only the current holder can
  heartbeat, report progress, succeed or fail. A stale worker cannot overwrite
  the outcome of a job that was reconciled and re-claimed.
- ``claim`` reconciles expired leases inside the same ``BEGIN IMMEDIATE``
  transaction, so a crashed worker is recovered without a separate daemon.
- Resources listed in ``serial_resources`` (default: ``gpu``) run at most one
  job at a time.
- Idempotency keys are permanent: resubmitting the same key and request returns
  the existing job; reusing a key with a different request is a conflict.
- Cancellation is cooperative: queued jobs are cancelled immediately; running
  jobs get ``cancel_requested`` and end as ``cancelled`` when the worker reports
  a failure. A worker that reports success is recorded as succeeded.

This module has no network or GPU dependency. It is exercised with deterministic
tests in ``tests/test_job_queue.py``; it is not yet wired to ComfyUI generation.
"""
from __future__ import annotations

import json
import sqlite3
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Callable, Iterator, Mapping

from .errors import StudioError
from .store import StudioStore

QUEUED, RUNNING, SUCCEEDED, FAILED, CANCELLED = "queued", "running", "succeeded", "failed", "cancelled"
TERMINAL_STATUSES = frozenset({SUCCEEDED, FAILED, CANCELLED})
RETRYABLE_CODES = frozenset({"provider_unavailable", "provider_protocol_error", "generation_timeout", "lease_expired"})
DEFAULT_SERIAL_RESOURCES = frozenset({"gpu"})
MAX_ATTEMPTS_LIMIT = 10


def _dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)


def _loads(text: str | None) -> Any:
    return json.loads(text) if text else None


class JobQueue:
    def __init__(self, store: StudioStore, *, clock: Callable[[], float] = time.time,
                 lease_seconds: float = 60.0, serial_resources: frozenset[str] = DEFAULT_SERIAL_RESOURCES):
        if lease_seconds <= 0:
            raise StudioError("lease_seconds must be positive", code="invalid_configuration")
        self.store = store
        self.clock = clock
        self.lease_seconds = float(lease_seconds)
        self.serial_resources = frozenset(serial_resources)

    # ----- transactions -------------------------------------------------
    @contextmanager
    def _tx(self) -> Iterator[sqlite3.Connection]:
        db = self.store.connect()
        db.isolation_level = None  # explicit transaction control
        try:
            db.execute("BEGIN IMMEDIATE")
            try:
                yield db
            except BaseException:
                db.execute("ROLLBACK")
                raise
            db.execute("COMMIT")
        finally:
            db.close()

    def _event(self, kind: str, job: Mapping[str, Any]) -> None:
        self.store.event(kind, {"run_id": job["id"], "command": job["command"], "status": job["status"],
                                "attempt": job["attempt"], "resource": job["resource"]})

    # ----- read model ---------------------------------------------------
    @staticmethod
    def _to_dict(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "id": row["id"], "command": row["command"], "status": row["status"], "resource": row["resource"],
            "attempt": row["attempt"], "max_attempts": row["max_attempts"],
            "idempotency_key": row["idempotency_key"], "not_before": row["not_before"],
            "enqueued_at": row["started_at"], "finished_at": row["finished_at"],
            "cancel_requested": bool(row["cancel_requested"]),
            "lease_expires_at": row["lease_expires_at"],
            "request": _loads(row["request_json"]), "result": _loads(row["result_json"]),
            "error": _loads(row["error_json"]), "progress": _loads(row["progress_json"]),
        }

    def _row(self, db: sqlite3.Connection, run_id: str) -> sqlite3.Row:
        row = db.execute("SELECT * FROM runs WHERE id=? AND queue_managed=1", (run_id,)).fetchone()
        if row is None:
            raise StudioError("Job not found", code="job_not_found", http_status=404, details={"run_id": run_id})
        return row

    def get(self, run_id: str) -> dict[str, Any]:
        with self._tx() as db:
            return self._to_dict(self._row(db, run_id))

    def list_jobs(self, *, status: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        limit = max(1, min(500, int(limit)))
        with self._tx() as db:
            if status is None:
                rows = db.execute("SELECT * FROM runs WHERE queue_managed=1 ORDER BY started_at, rowid LIMIT ?", (limit,)).fetchall()
            else:
                rows = db.execute("SELECT * FROM runs WHERE queue_managed=1 AND status=? ORDER BY started_at, rowid LIMIT ?", (status, limit)).fetchall()
        return [self._to_dict(r) for r in rows]

    # ----- submission ---------------------------------------------------
    def enqueue(self, command: str, args: Mapping[str, Any] | None = None, *, idempotency_key: str,
                max_attempts: int = 1, resource: str = "cpu") -> dict[str, Any]:
        if not command or not isinstance(command, str):
            raise StudioError("Job command is required", code="invalid_job", http_status=400)
        if not isinstance(idempotency_key, str) or not idempotency_key.strip() or len(idempotency_key) > 200:
            raise StudioError("idempotency_key must be a non-empty string of at most 200 characters",
                              code="invalid_idempotency_key", http_status=400)
        if not isinstance(max_attempts, int) or not 1 <= max_attempts <= MAX_ATTEMPTS_LIMIT:
            raise StudioError(f"max_attempts must be between 1 and {MAX_ATTEMPTS_LIMIT}", code="invalid_job", http_status=400)
        if not resource or not isinstance(resource, str):
            raise StudioError("resource must be a non-empty string", code="invalid_job", http_status=400)
        request_json = _dumps(dict(args or {}))
        now = self.clock()
        with self._tx() as db:
            existing = db.execute("SELECT * FROM runs WHERE idempotency_key=?", (idempotency_key,)).fetchone()
            if existing is not None:
                if existing["command"] != command or existing["request_json"] != request_json:
                    raise StudioError("idempotency_key was already used for a different job", code="idempotency_conflict",
                                      http_status=409, details={"idempotency_key": idempotency_key, "run_id": existing["id"]})
                return self._to_dict(existing)
            run_id = uuid.uuid4().hex
            db.execute(
                "INSERT INTO runs(id,command,status,started_at,request_json,attempt,max_attempts,idempotency_key,resource,queue_managed) "
                "VALUES(?,?,?,?,?,?,?,?,?,1)",
                (run_id, command, QUEUED, now, request_json, 0, max_attempts, idempotency_key, resource),
            )
            job = self._to_dict(self._row(db, run_id))
        self._event("job_enqueued", job)
        return job

    # ----- worker side --------------------------------------------------
    def _reconcile_locked(self, db: sqlite3.Connection, now: float) -> list[dict[str, Any]]:
        expired = db.execute(
            "SELECT * FROM runs WHERE queue_managed=1 AND status=? AND lease_expires_at < ?", (RUNNING, now)).fetchall()
        changed = []
        for row in expired:
            error = {"code": "lease_expired", "message": "worker lease expired before the job reported an outcome",
                     "attempt": row["attempt"], "details": {}, "retryable": True}
            if row["cancel_requested"]:
                db.execute("UPDATE runs SET status=?, finished_at=?, error_json=?, lease_token=NULL, lease_expires_at=NULL WHERE id=?",
                           (CANCELLED, now, _dumps(error), row["id"]))
            elif row["attempt"] < row["max_attempts"]:
                db.execute("UPDATE runs SET status=?, not_before=?, error_json=?, lease_token=NULL, lease_expires_at=NULL WHERE id=?",
                           (QUEUED, now, _dumps(error), row["id"]))
            else:
                error["retryable"] = False
                db.execute("UPDATE runs SET status=?, finished_at=?, error_json=?, lease_token=NULL, lease_expires_at=NULL WHERE id=?",
                           (FAILED, now, _dumps(error), row["id"]))
            changed.append(self._to_dict(self._row(db, row["id"])))
        return changed

    def reconcile(self) -> list[dict[str, Any]]:
        """Recover jobs whose worker stopped heartbeating. Returns the changed jobs."""
        now = self.clock()
        with self._tx() as db:
            changed = self._reconcile_locked(db, now)
        for job in changed:
            self._event("job_reconciled", job)
        return changed

    def claim(self, worker_id: str) -> dict[str, Any] | None:
        """Atomically claim the oldest eligible queued job, or return None."""
        if not worker_id:
            raise StudioError("worker_id is required", code="invalid_job", http_status=400)
        now = self.clock()
        token = uuid.uuid4().hex
        with self._tx() as db:
            self._reconcile_locked(db, now)
            busy = {r["resource"] for r in db.execute(
                "SELECT DISTINCT resource FROM runs WHERE queue_managed=1 AND status=?", (RUNNING,)).fetchall()
                if r["resource"] in self.serial_resources}
            candidates = db.execute(
                "SELECT id, resource FROM runs WHERE queue_managed=1 AND status=? AND (not_before IS NULL OR not_before<=?) "
                "ORDER BY started_at, rowid", (QUEUED, now)).fetchall()
            chosen = next((c["id"] for c in candidates if not (c["resource"] in self.serial_resources and c["resource"] in busy)), None)
            if chosen is None:
                return None
            db.execute("UPDATE runs SET status=?, attempt=attempt+1, lease_token=?, lease_expires_at=? WHERE id=?",
                       (RUNNING, token, now + self.lease_seconds, chosen))
            job = self._to_dict(self._row(db, chosen))
        job["lease_token"] = token
        job["worker_id"] = worker_id
        self._event("job_claimed", job)
        return job

    def _require_holder(self, db: sqlite3.Connection, run_id: str, token: str) -> sqlite3.Row:
        row = self._row(db, run_id)
        if row["status"] != RUNNING or row["lease_token"] != token:
            raise StudioError("Lease is no longer held by this worker", code="lease_lost", http_status=409,
                              details={"run_id": run_id, "status": row["status"]})
        return row

    def heartbeat(self, run_id: str, token: str) -> dict[str, Any]:
        now = self.clock()
        with self._tx() as db:
            row = self._require_holder(db, run_id, token)
            db.execute("UPDATE runs SET lease_expires_at=? WHERE id=?", (now + self.lease_seconds, run_id))
            return {"run_id": run_id, "lease_expires_at": now + self.lease_seconds,
                    "cancel_requested": bool(row["cancel_requested"])}

    def progress(self, run_id: str, token: str, *, fraction: float, message: str = "") -> dict[str, Any]:
        if not 0.0 <= float(fraction) <= 1.0:
            raise StudioError("progress fraction must be between 0 and 1", code="invalid_progress", http_status=400)
        now = self.clock()
        with self._tx() as db:
            self._require_holder(db, run_id, token)
            value = {"fraction": round(float(fraction), 4), "message": str(message)[:500], "updated_at": now}
            db.execute("UPDATE runs SET progress_json=?, lease_expires_at=? WHERE id=?",
                       (_dumps(value), now + self.lease_seconds, run_id))
            return value

    def succeed(self, run_id: str, token: str, result: Any) -> dict[str, Any]:
        now = self.clock()
        with self._tx() as db:
            self._require_holder(db, run_id, token)
            db.execute("UPDATE runs SET status=?, finished_at=?, result_json=?, error_json=NULL, "
                       "lease_token=NULL, lease_expires_at=NULL WHERE id=?",
                       (SUCCEEDED, now, _dumps(result), run_id))
            job = self._to_dict(self._row(db, run_id))
        self._event("job_succeeded", job)
        return job

    def fail(self, run_id: str, token: str, *, code: str, message: str, retryable: bool = False,
             backoff_seconds: float = 0.0, details: Mapping[str, Any] | None = None) -> dict[str, Any]:
        now = self.clock()
        with self._tx() as db:
            row = self._require_holder(db, run_id, token)
            error = {"code": code, "message": message, "attempt": row["attempt"], "details": dict(details or {}),
                     "retryable": bool(retryable)}
            if row["cancel_requested"]:
                db.execute("UPDATE runs SET status=?, finished_at=?, error_json=?, lease_token=NULL, lease_expires_at=NULL WHERE id=?",
                           (CANCELLED, now, _dumps(error), run_id))
            elif retryable and row["attempt"] < row["max_attempts"]:
                db.execute("UPDATE runs SET status=?, not_before=?, error_json=?, lease_token=NULL, lease_expires_at=NULL WHERE id=?",
                           (QUEUED, now + max(0.0, float(backoff_seconds)), _dumps(error), run_id))
            else:
                error["retryable"] = False
                db.execute("UPDATE runs SET status=?, finished_at=?, error_json=?, lease_token=NULL, lease_expires_at=NULL WHERE id=?",
                           (FAILED, now, _dumps(error), run_id))
            job = self._to_dict(self._row(db, run_id))
        self._event("job_failed", job)
        return job

    # ----- operator side ------------------------------------------------
    def cancel(self, run_id: str) -> dict[str, Any]:
        now = self.clock()
        with self._tx() as db:
            row = self._row(db, run_id)
            if row["status"] == QUEUED:
                db.execute("UPDATE runs SET status=?, finished_at=?, error_json=? WHERE id=?",
                           (CANCELLED, now, _dumps({"code": "cancelled", "message": "cancelled before start",
                                                    "attempt": row["attempt"], "details": {}, "retryable": False}), run_id))
            elif row["status"] == RUNNING:
                db.execute("UPDATE runs SET cancel_requested=1 WHERE id=?", (run_id,))
            job = self._to_dict(self._row(db, run_id))
        self._event("job_cancel_requested", job)
        return job


@dataclass
class JobContext:
    queue: JobQueue
    job: dict[str, Any]

    def heartbeat(self) -> dict[str, Any]:
        return self.queue.heartbeat(self.job["id"], self.job["lease_token"])

    def progress(self, fraction: float, message: str = "") -> dict[str, Any]:
        return self.queue.progress(self.job["id"], self.job["lease_token"], fraction=fraction, message=message)

    def cancel_requested(self) -> bool:
        return self.heartbeat()["cancel_requested"]


def run_once(queue: JobQueue, handlers: Mapping[str, Callable[[dict[str, Any], JobContext], Any]], *,
             worker_id: str = "worker") -> dict[str, Any] | None:
    """Claim one job, run its handler, and record the outcome. Returns the final job or None if idle."""
    job = queue.claim(worker_id)
    if job is None:
        return None
    token = job["lease_token"]
    handler = handlers.get(job["command"])
    if handler is None:
        return queue.fail(job["id"], token, code="no_handler", message=f"no handler for {job['command']}")
    try:
        result = handler(dict(job["request"] or {}), JobContext(queue, job))
    except StudioError as exc:
        retryable = exc.code in RETRYABLE_CODES
        backoff = min(60.0, 5.0 * (2 ** max(0, job["attempt"] - 1)))
        return queue.fail(job["id"], token, code=exc.code, message=str(exc), details=exc.details,
                          retryable=retryable, backoff_seconds=backoff)
    except Exception as exc:  # unexpected handler defect: never retried automatically
        return queue.fail(job["id"], token, code="internal_error", message=f"{type(exc).__name__}: {exc}")
    return queue.succeed(job["id"], token, result)
