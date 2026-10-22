# Resource-Aware Creative Job Orchestration

## Why this exists

Local creative generation can fail or starve other workloads when model cold-starts, high VRAM allocation, RAM pressure and multiple agents overlap. Resource constraints should defer heavy execution—not cause a silent downgrade in quality.

## Minimum preflight signals

- GPU: name, total/free/used memory, utilization and active GPU processes when `nvidia-smi` is available.
- RAM: total and available memory (use `psutil` if installed; otherwise Windows API or explicit `unknown`, never guessed).
- Disk: free space at workspace/output/model roots.
- Services: loopback health and socket checks for configured ComfyUI/SD/Blender MCP/Godot/MCP services.
- Models/nodes: inspect the live service's installed inventory; never infer that model weights or custom nodes exist merely because the server is healthy.
- Work queue: active heavy jobs, stale jobs, cancellation/resume support, estimated peak resource requirement and expected output size.

## Conservative defaults

These are safe starting thresholds, not hardware truths; calibrate them from observed runs:

- **Pause heavyweight GPU generation** when system available RAM is below 2 GiB or free VRAM is below 2.5 GiB.
- **Require a sequential job and a low-memory workflow** when free VRAM is below 4 GiB or available system RAM below 4 GiB.
- **Permit a planned full-memory job** only when measured free VRAM exceeds the workflow's previously observed peak by at least 1.5 GiB and system RAM is not under pressure.
- Never launch competing GPU jobs by default, even with nominal headroom, until concurrent behavior has been measured for those exact models/workflows.
- Never automatically terminate or lower priority of unrelated user applications. Pause this studio's own queue or ask before a system-level action.

## Queue state machine

`pending → preflight → ready → running → output-validation → completed` with side states `blocked_resource`, `blocked_dependency`, `failed_retryable`, `failed_terminal`, `cancel_requested`, `cancelled`, and `needs_review`.

A durable job record includes: `job_id`, project/asset/action ID, type, priority, method, serialized request/settings, source references+hashes, estimated VRAM/RAM/disk, observed peak, start/end times, attempt number, retry class, ComfyUI prompt/job IDs where applicable, outputs+hashes, result code, stdout/stderr paths and resume condition.

## Retry rules

- Retry network/service timeouts with bounded backoff only when job identity prevents duplicate submission or the system can detect the original job.
- Do not retry OOM in a tight loop. Release this job's tensors/process, wait for a measured recovery condition, then select a smaller validated graph or a distinct method.
- Do not change multiple creative variables during an output-quality experiment.
- Preserve bad outputs and failure notes when useful for diagnosis; never promote them as accepted assets.
- A cancelled task keeps inputs and state so it can resume from the last safe boundary.

## Safe work while blocked

Agents should continue CPU-safe and low-resource work: authoring pose specs, animation timing charts, rig/bone mapping, Blender/Python scripts, model/node/license research, prompt sets, scene architecture, Godot state machine and event code, validation tests, import configuration, UI/layout work, and documentation. No work is counted complete unless its output passes its own acceptance criteria.

## Evidence and calibration

Record model/workflow cold-start and warm latency, peak VRAM/RAM, output dimensions, successful/rejected output counts, retries and error classes. Do not universalize one machine's measurements. Tune thresholds using multiple tasks on the target host. Preflight reports must indicate unknown data rather than invent a metric.
