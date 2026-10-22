# Known Limitations and Capability Boundaries

- **Artistic quality:** current metrics do not certify commercial quality. The agent owns producing and iterating candidate art; inspect important assets in-game and label agent assessment, any explicitly required human review, and rights review as distinct evidence states. Routine art creation is not an operator task.
- **Identity consistency:** same seed is not identity lock. Historical Klein img2img was promising but had a hand/prop ownership fault; review each action frame.
- **Animation:** frame assembly/anchor metrics do not judge semantic motion, weight, arcs, timing, foot sliding or expressive readability. Cutout and Blender routes need project-specific verification.
- **RIFE:** interpolation is not semantic action generation. A historical sprite test produced opaque frames and was rejected.
- **Background removal:** edge-connected color-distance cleanup is not semantic matting and can erase valid edges if tolerance is high.
- **VRAM:** source evidence reports near-limit 11.1/12.2 GB during some generation workflows. Historical machine-specific values only; serialize jobs and remeasure when versions change.
- **External services:** ComfyUI, SD WebUI, Godot, Blender and RIFE are optional. This rebuild does not invoke GPU generation or prove those tools are installed on a new machine.
- **Godot export:** the adapter checks commands and expected files; actual target-runtime/gameplay tests are separate.
- **MCP:** protocol tests do not verify every target agent host's configuration.
- **Jam estimates:** plans use estimated durations and reserve; observed data should calibrate estimates.
- **Licensing:** registers are evidence tools, not legal advice; check exact weights/assets/fonts/data and redistribution rights.
- **Public distribution:** model weights, local state, `.env`, virtual environments and repetitive game exports are excluded by default.
- **Historical evidence:** archive results are not test results for this clean-room package. Current evidence is documented separately.
- **Job queue scope:** `vated_studio.jobs` is a library. The CLI, HTTP API, MCP tools and ComfyUI generation still execute synchronously through `StudioService`; they are not yet enqueued.
- **Synchronous run recovery:** a synchronous command that crashes mid-execution stays in status `running`. Only queue-managed jobs are reconciled.
- **Lease timing:** a worker that stalls longer than its lease without heartbeating can have its job reclaimed while it is still running. Heartbeat well inside `lease_seconds`.
- **Cancellation is cooperative:** the queue does not interrupt an in-flight ComfyUI prompt. A job that completes after a cancel request is recorded as succeeded.
- **Connection handling:** `StudioStore` schema initialization uses `with connect()` without closing the connection, which emits `ResourceWarning` under `-W error`. Pre-existing; not changed in this pass.

