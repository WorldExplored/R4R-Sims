# Working instructions

- Read `README.md` and the relevant simulator notes before making changes.
- Keep simulator-specific code in `simulators/<simulator>/`. Put shared code in `scripts/` only when it is actually shared.
- Inspect existing plans and evidence. Do not invent requirements, measurements, completed experiments, or missing personal context. Ask for a missing prior evaluation plan when it is necessary to run the requested tests.
- Record exact commands, upstream revisions, environment, GPU model, configuration, metrics, failure reasons, and artifact provenance for completed runs in `results/<simulator>/<run-id>/`.
- Keep downloaded engines, third-party repositories, builds, datasets, checkpoints, and large outputs out of Git. Store retrieval instructions and links instead. Respect upstream redistribution terms.
- Never commit private keys, tokens, passwords, `.env` files, or machine-specific credentials.
- Use Git commits and pushes to synchronize code and small results between local and remote checkouts. Do not overwrite uncommitted work, force-push, or erase unrelated changes.
- For large outputs, use resumable transfer or durable storage and record file sizes and SHA-256 checksums. Verify preservation before terminating a rented instance. A path on an ephemeral instance is not a durable artifact location.
- Preserve work already present on either machine. Only skip copying engine installations or other reproducible dependencies when their retrieval and versions are documented.
- Do not rent GPUs, train policies, or expand evaluation scope just because the structure supports it. Follow the user's actual task.
- Report what changed, what was tested, what remains blocked, and where results can be viewed. Claim completion only when supported by evidence.
