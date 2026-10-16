# Security policy

The studio is designed for local agent-operated use. Its APIs can write files, run selected local tools, generate assets, and launch engine processes; treat these operations as developer tooling with meaningful filesystem and process privileges.

- Bind HTTP to loopback unless you intentionally configure a protected deployment.
- Authenticated command endpoints require a bearer token. Do not commit token files or `.env` files.
- The workspace-root check is a safety boundary, not a substitute for OS-level sandboxing. Do not point the studio at directories containing secrets or unrelated critical files.
- Provider URLs are restricted to loopback by default. Set `AGS_ALLOW_REMOTE_PROVIDERS=true` only when you understand the trust and network implications.
- Imported source paths are explicitly opt-in operations. Validate and review them before running transformations.
- The process launcher never invokes a shell with user-provided command strings. Executables and arguments are passed as an argument vector with a timeout.
- Do not expose the HTTP service directly to the public internet. For remote access, put it behind a properly authenticated, TLS-enabled gateway and a least-privilege runtime.
- Treat prompts, model workflows, generated scripts, and imported project files as untrusted data. Never execute code extracted from an image model's output.

Report security issues privately to the repository maintainers before publishing exploit details. No warranty or security certification is implied by the presence of these controls.
