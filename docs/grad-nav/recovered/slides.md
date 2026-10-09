# Preliminary presentation outline — all findings pending execution

1. Question and experiment levels: A camera render, B feedback dynamics, C pretrained closed loop. Figure: input/output path with distinct branches. Evidence: source trace and run IDs.
2. Code and artifact map. Figure: scene config/checkpoint versus geometric point cloud versus policy checkpoint inventory. Evidence: hashes, asset sizes and licenses after download.
3. Native indoor/gate reproduction. Figure: five route camera frames and depth plus camera frusta. Evidence: A PNGs, pose JSONL and visual inspection; pending.
4. Dynamics and optional policy. Figure: desired versus actual height, command and state timeline; C trajectory only if verified weights. Evidence: B/C records and outcomes; pending.
5. Runtime resources. Figure: wall step components, render throughput, actor latency, GPU memory, with paper baseline separated. Evidence: synchronized timing, 1 s memory samples; pending.
6. R4R fit: indoor, sparse outdoor, racing and Unreal visual replacement. Figure: common calibrated route with held-out viewpoints and geometry checks. Evidence: future common-scene dataset and matched-camera comparison; pending.
7. Decision and next experiment. Figure: feasibility gates and blockers; no real-world transfer claim.
