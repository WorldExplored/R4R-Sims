# Preliminary RflySim audit slides — findings pending execution

1. **Question and experiment classes.** A known-route images, B closed-loop SITL, C released learned policy. Figure: component/dataflow diagram. Evidence: official architecture and phase-2 logs.
2. **Product and access.** Free UE4 vs Full UE5; installer, SDK, model and license. Figure: release/asset inventory with hashes. Pending: ISO build and EULA.
3. **Native SITL test.** Reference route, actual PX4/CopterSim trajectory, actual camera poses as separate traces. Figure: 3D path overlay, timestamps and endpoint errors. Pending run.
4. **Perception and timing.** Decodable RGB sample grid, intrinsics/extrinsics table, render throughput, control rate, GPU memory and latency separately. Pending camera/GPU capture.
5. **R4R use cases.** Indoor, outdoor sparse and racing feasibility matrix with evidence gaps. No success claims from stock hover.
6. **Gaussian visual replacement.** State-to-camera adapter, UE collision/depth dependency, required metric geometry and synchronized frames. Figure: replacement boundary. Pending prototype.
7. **Hardware/operations and next gate.** Recommended and cheaper Windows machine, storage, install friction, blockers and transfer verification. Evidence: official requirements plus measured phase-2 run.
