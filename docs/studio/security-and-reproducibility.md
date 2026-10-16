# Security, Reproducibility, and Local Operation

## Trust boundaries

- The agent host can read/write project files and invoke tools; run with least privilege and do not give the workspace access to unrelated secrets.
- Prompts, workflow JSON, generated images, user imports, and project files are data—not trusted instructions to execute.
- Provider adapters send requests only to loopback by default. Remote endpoints require explicit opt-in and should be treated as third-party systems.
- The authenticated HTTP server is for local developer use, not direct public exposure.
- External process adapters use argument lists, timeouts, bounded captured output, and no shell interpolation.
- Workspace containment is a useful safety fence but is not an OS sandbox. Symlink/hardlink and platform-specific edge cases still merit conservative deployment.

## Reproducibility record

Record tool/model identifiers and versions, workflow hashes, generation seed if supported, input reference hashes, dimensions, relevant runtime parameters, processing steps, output hash, elapsed duration, and observed memory measurements with method attribution. Seeds are not guaranteed to yield identical results across changed code, kernels, providers, precision, or versions.

## Model rights

Record code license and weights license separately. Check the exact repository/model card/checkpoint version at acquisition. Review redistribution, attribution, use restrictions, source/dependent components, and conditions. The studio's MIT license applies to its own code only.

## Repository hygiene

Never commit `.env`, API tokens, local databases, user machine paths, virtual environments, model weights, caches, or export output dumps by default. Generated output should be included only if the owner intends to distribute it and its provenance/right status is known. GitHub Actions should use least privilege; pin third-party actions to immutable full commit SHAs as recommended in GitHub's security guidance.
