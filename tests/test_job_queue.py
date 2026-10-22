"""Deterministic tests for the durable job queue (stdlib only, no GPU/network).

These exercise real SQLite transactions and real threads. They do not prove
ComfyUI generation; the handlers used here are plain Python functions.
"""
from __future__ import annotations

import sqlite3
import tempfile
import threading
import unittest
from pathlib import Path

from vated_studio.errors import StudioError
from vated_studio.jobs import FAILED, QUEUED, RUNNING, SUCCEEDED, CANCELLED, JobQueue, run_once
from vated_studio.store import StudioStore


class FakeClock:
    def __init__(self, start: float = 1_000.0):
        self.now = start

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


class JobQueueTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.workspace = Path(self._tmp.name)
        self.clock = FakeClock()
        self.store = StudioStore(self.workspace)
        self.queue = JobQueue(self.store, clock=self.clock, lease_seconds=10)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def enqueue(self, key: str, command: str = "generate", **kwargs) -> dict:
        return self.queue.enqueue(command, {"prompt": key}, idempotency_key=key, **kwargs)

    # ----- submission ---------------------------------------------------
    def test_enqueue_creates_queued_job_with_defaults(self) -> None:
        job = self.enqueue("k1", max_attempts=3, resource="gpu")
        self.assertEqual(job["status"], QUEUED)
        self.assertEqual(job["attempt"], 0)
        self.assertEqual(job["max_attempts"], 3)
        self.assertEqual(job["resource"], "gpu")
        self.assertEqual(job["request"], {"prompt": "k1"})
        self.assertIsNone(job["result"])

    def test_idempotent_enqueue_returns_existing_job_and_rejects_different_request(self) -> None:
        first = self.enqueue("same-key")
        again = self.enqueue("same-key")
        self.assertEqual(first["id"], again["id"])
        self.assertEqual(len(self.queue.list_jobs()), 1)
        with self.assertRaises(StudioError) as ctx:
            self.queue.enqueue("generate", {"prompt": "different"}, idempotency_key="same-key")
        self.assertEqual(ctx.exception.code, "idempotency_conflict")
        with self.assertRaises(StudioError) as ctx:
            self.queue.enqueue("other-command", {"prompt": "same-key"}, idempotency_key="same-key")
        self.assertEqual(ctx.exception.code, "idempotency_conflict")

    def test_invalid_submissions_are_rejected_before_writing(self) -> None:
        with self.assertRaises(StudioError) as ctx:
            self.queue.enqueue("generate", {}, idempotency_key="   ")
        self.assertEqual(ctx.exception.code, "invalid_idempotency_key")
        with self.assertRaises(StudioError):
            self.enqueue("k-zero", max_attempts=0)
        with self.assertRaises(StudioError):
            self.enqueue("k-many", max_attempts=99)
        self.assertEqual(self.queue.list_jobs(), [])

    # ----- claiming and serialization ----------------------------------
    def test_claim_is_fifo_issues_a_token_and_returns_none_when_idle(self) -> None:
        self.enqueue("a")
        self.clock.advance(1)
        self.enqueue("b")
        first = self.queue.claim("w1")
        self.assertEqual(first["request"], {"prompt": "a"})
        self.assertEqual(first["status"], RUNNING)
        self.assertEqual(first["attempt"], 1)
        self.assertTrue(first["lease_token"])
        second = self.queue.claim("w1")
        self.assertEqual(second["request"], {"prompt": "b"})
        self.assertIsNone(self.queue.claim("w1"))

    def test_gpu_jobs_run_one_at_a_time_while_cpu_jobs_are_not_blocked(self) -> None:
        self.enqueue("gpu-1", resource="gpu")
        self.enqueue("gpu-2", resource="gpu")
        self.enqueue("cpu-1", resource="cpu")
        g1 = self.queue.claim("w")
        self.assertEqual(g1["request"], {"prompt": "gpu-1"})
        # Second GPU job must wait; the CPU job proceeds.
        cpu = self.queue.claim("w")
        self.assertEqual(cpu["request"], {"prompt": "cpu-1"})
        self.assertIsNone(self.queue.claim("w"))
        self.queue.succeed(g1["id"], g1["lease_token"], {"ok": True})
        g2 = self.queue.claim("w")
        self.assertEqual(g2["request"], {"prompt": "gpu-2"})

    # ----- outcomes and fencing ----------------------------------------
    def test_succeed_records_result_and_stale_token_is_rejected(self) -> None:
        self.enqueue("ok")
        job = self.queue.claim("w")
        done = self.queue.succeed(job["id"], job["lease_token"], {"images": ["x.png"]})
        self.assertEqual(done["status"], SUCCEEDED)
        self.assertEqual(done["result"], {"images": ["x.png"]})
        with self.assertRaises(StudioError) as ctx:
            self.queue.succeed(job["id"], job["lease_token"], {"again": True})
        self.assertEqual(ctx.exception.code, "lease_lost")

    def test_retryable_failure_requeues_with_backoff_then_exhausts_attempts(self) -> None:
        self.enqueue("flaky", max_attempts=2)
        job = self.queue.claim("w")
        requeued = self.queue.fail(job["id"], job["lease_token"], code="provider_unavailable",
                                   message="down", retryable=True, backoff_seconds=30)
        self.assertEqual(requeued["status"], QUEUED)
        self.assertEqual(requeued["error"]["code"], "provider_unavailable")
        self.assertIsNone(self.queue.claim("w"), "backoff must delay the retry")
        self.clock.advance(30)
        retry = self.queue.claim("w")
        self.assertEqual(retry["attempt"], 2)
        final = self.queue.fail(retry["id"], retry["lease_token"], code="provider_unavailable",
                                message="still down", retryable=True)
        self.assertEqual(final["status"], FAILED, "retry budget must be bounded by max_attempts")
        self.assertIsNotNone(final["finished_at"])

    def test_non_retryable_failure_is_terminal_immediately(self) -> None:
        self.enqueue("bad", max_attempts=5)
        job = self.queue.claim("w")
        failed = self.queue.fail(job["id"], job["lease_token"], code="invalid_workflow", message="bad node", retryable=False)
        self.assertEqual(failed["status"], FAILED)
        self.assertIsNone(self.queue.claim("w"))

    # ----- crash recovery ----------------------------------------------
    def test_crashed_worker_lease_expiry_is_reclaimed_and_stale_worker_is_fenced(self) -> None:
        self.enqueue("crash", max_attempts=2)
        crashed = self.queue.claim("worker-a")
        self.clock.advance(11)  # lease was 10 seconds; worker-a stopped heartbeating
        takeover = self.queue.claim("worker-b")  # claim reconciles the expired lease first
        self.assertEqual(takeover["id"], crashed["id"])
        self.assertEqual(takeover["attempt"], 2)
        self.assertNotEqual(takeover["lease_token"], crashed["lease_token"])
        # The original worker wakes up late and must not overwrite the outcome.
        with self.assertRaises(StudioError) as ctx:
            self.queue.succeed(crashed["id"], crashed["lease_token"], {"stale": True})
        self.assertEqual(ctx.exception.code, "lease_lost")
        done = self.queue.succeed(takeover["id"], takeover["lease_token"], {"fresh": True})
        self.assertEqual(done["result"], {"fresh": True})

    def test_lease_expiry_with_no_attempts_left_fails_with_lease_expired(self) -> None:
        self.enqueue("last-chance", max_attempts=1)
        self.queue.claim("worker-a")
        self.clock.advance(11)
        changed = self.queue.reconcile()
        self.assertEqual(len(changed), 1)
        self.assertEqual(changed[0]["status"], FAILED)
        self.assertEqual(changed[0]["error"]["code"], "lease_expired")
        self.assertFalse(changed[0]["error"]["retryable"])

    def test_heartbeat_extends_the_lease_and_prevents_reconciliation(self) -> None:
        self.enqueue("long")
        job = self.queue.claim("w")
        for _ in range(5):
            self.clock.advance(8)  # each step is under the 10-second lease
            self.queue.heartbeat(job["id"], job["lease_token"])
        self.assertEqual(self.queue.reconcile(), [], "a heartbeating worker must not be reconciled")
        self.assertEqual(self.queue.get(job["id"])["status"], RUNNING)

    def test_recovery_survives_process_restart_because_state_is_in_sqlite(self) -> None:
        self.enqueue("durable", max_attempts=3)
        self.queue.claim("worker-a")
        # Simulate a new process: fresh store and queue object over the same workspace.
        reopened = JobQueue(StudioStore(self.workspace), clock=self.clock, lease_seconds=10)
        self.assertEqual(reopened.get(reopened.list_jobs()[0]["id"])["status"], RUNNING)
        self.clock.advance(11)
        recovered = reopened.claim("worker-c")
        self.assertEqual(recovered["request"], {"prompt": "durable"})
        self.assertEqual(recovered["attempt"], 2)

    # ----- cancellation -------------------------------------------------
    def test_cancelling_a_queued_job_prevents_any_run(self) -> None:
        job = self.enqueue("never")
        cancelled = self.queue.cancel(job["id"])
        self.assertEqual(cancelled["status"], CANCELLED)
        self.assertIsNone(self.queue.claim("w"))

    def test_cancelling_a_running_job_is_cooperative(self) -> None:
        self.enqueue("long-gpu", resource="gpu", max_attempts=3)
        job = self.queue.claim("w")
        requested = self.queue.cancel(job["id"])
        self.assertEqual(requested["status"], RUNNING)
        self.assertTrue(requested["cancel_requested"])
        self.assertTrue(self.queue.heartbeat(job["id"], job["lease_token"])["cancel_requested"])
        ended = self.queue.fail(job["id"], job["lease_token"], code="cancelled", message="stopped by operator", retryable=True)
        self.assertEqual(ended["status"], CANCELLED, "cancellation must win over retry")

    # ----- handlers and progress ---------------------------------------
    def test_run_once_records_success_retryable_failure_and_unknown_command(self) -> None:
        self.enqueue("good", command="echo")
        self.enqueue("slow", command="flaky", max_attempts=2)
        self.enqueue("odd", command="missing")

        def echo(args, ctx):
            ctx.progress(0.5, "halfway")
            return {"echo": args["prompt"]}

        def flaky(args, ctx):
            raise StudioError("provider down", code="provider_unavailable")

        handlers = {"echo": echo, "flaky": flaky}
        out = run_once(self.queue, handlers, worker_id="w")
        self.assertEqual(out["status"], SUCCEEDED)
        self.assertEqual(out["result"], {"echo": "good"})
        out = run_once(self.queue, handlers, worker_id="w")
        self.assertEqual(out["status"], QUEUED)
        self.assertEqual(out["error"]["code"], "provider_unavailable")
        out = run_once(self.queue, handlers, worker_id="w")
        self.assertEqual(out["status"], FAILED)
        self.assertEqual(out["error"]["code"], "no_handler")
        self.assertIsNone(run_once(self.queue, handlers, worker_id="w"))

    def test_unexpected_handler_exception_is_never_retried(self) -> None:
        self.enqueue("boom", command="crash", max_attempts=5)

        def crash(args, ctx):
            raise ValueError("defect")

        out = run_once(self.queue, {"crash": crash}, worker_id="w")
        self.assertEqual(out["status"], FAILED)
        self.assertEqual(out["error"]["code"], "internal_error")
        self.assertIn("ValueError", out["error"]["message"])

    def test_progress_is_observable_and_bounded(self) -> None:
        self.enqueue("p")
        job = self.queue.claim("w")
        self.queue.progress(job["id"], job["lease_token"], fraction=0.25, message="sampling")
        self.assertEqual(self.queue.get(job["id"])["progress"]["fraction"], 0.25)
        with self.assertRaises(StudioError) as ctx:
            self.queue.progress(job["id"], job["lease_token"], fraction=1.5)
        self.assertEqual(ctx.exception.code, "invalid_progress")

    # ----- concurrency ---------------------------------------------------
    def test_concurrent_claims_produce_exactly_one_winner(self) -> None:
        self.enqueue("only-one")
        contenders = [JobQueue(StudioStore(self.workspace), clock=self.clock, lease_seconds=10) for _ in range(8)]
        barrier = threading.Barrier(len(contenders))
        winners: list[dict] = []
        errors: list[BaseException] = []
        lock = threading.Lock()

        def contend(queue: JobQueue, index: int) -> None:
            try:
                barrier.wait(timeout=10)
                job = queue.claim(f"thread-{index}")
                if job is not None:
                    with lock:
                        winners.append(job)
            except BaseException as exc:  # surfaced in the main thread below
                errors.append(exc)

        threads = [threading.Thread(target=contend, args=(q, i)) for i, q in enumerate(contenders)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=30)
        self.assertEqual(errors, [])
        self.assertEqual(len(winners), 1, "exactly one worker may claim a queued job")
        self.assertEqual(winners[0]["attempt"], 1)

    # ----- schema evolution ---------------------------------------------
    def test_legacy_runs_table_is_migrated_without_losing_rows(self) -> None:
        fresh = Path(tempfile.mkdtemp())  # setUp already migrated self.workspace
        state = fresh / ".state"
        state.mkdir(parents=True, exist_ok=True)
        legacy = sqlite3.connect(state / "studio.sqlite3")
        legacy.executescript("""
            CREATE TABLE runs (id TEXT PRIMARY KEY, command TEXT NOT NULL, status TEXT NOT NULL,
                started_at REAL NOT NULL, finished_at REAL, request_json TEXT NOT NULL,
                result_json TEXT, error_json TEXT);
            INSERT INTO runs(id,command,status,started_at,request_json) VALUES('legacy1','status','completed',1.0,'{}');
        """)
        legacy.commit()
        legacy.close()
        migrated = StudioStore(fresh)  # must add queue columns, keep the row
        columns = {row[1] for row in migrated.connect().execute("PRAGMA table_info(runs)")}
        self.assertTrue({"attempt", "lease_token", "idempotency_key", "queue_managed"} <= columns)
        self.assertEqual(migrated.runs(5)[0]["id"], "legacy1")
        self.assertEqual(StudioStore(fresh).runs(5)[0]["status"], "completed", "second open must be idempotent")
        job = JobQueue(migrated, clock=self.clock).enqueue("generate", {"p": 1}, idempotency_key="after-migration")
        self.assertEqual(job["status"], QUEUED)


if __name__ == "__main__":
    unittest.main()
