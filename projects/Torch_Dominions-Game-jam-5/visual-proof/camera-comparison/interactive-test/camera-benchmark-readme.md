# Matched Interactive Camera Benchmark

This is a diagnostic Godot scene, isolated from the game project. Open this directory's `project.godot` in Godot 4.7+ and run `benchmark.tscn`.

Controls: **WASD/arrows** move, **Shift** dodge, **Space** torch sweep, **H** cast Haze, **R** reset, **Tab** dim/focus alternate camera for close inspection. Both camera views stay visible and display the same live state.

The command-line smoke modes are `side`, `elevated`, and `paired`; see `benchmark-report.json` for tested commands/results and captured evidence. Attack anticipation/contact/follow-through/recovery, dodge compression/burst/settle, alternating locomotion, rogue wind-up/strike/recovery, and Haze effects are event-timed authored diagnostic drawings driven by shared encounter state. Both views keep actor anatomy upright while changing the environment-depth projection. The fused hero cutout remains a static identity reference (replaced during authored action/movement poses); this is not a production character rig, final art, or a camera approval. Verified with Godot 4.7.2 GL Compatibility at 1440x900 (16:10) and 1600x900 (16:9), fixed 30 FPS; see `aspect-captures/aspect-ratio-review.html` and `.json`. 4:3, OS-scale/device, manual playtest, production framing, and camera-approval gates remain open.
