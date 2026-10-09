# Asset inventory — phase 1, 2026-10-04

| Asset | Provenance / use | Size / hash / access | Retention decision |
|---|---|---|---|
| RflySim Toolchain Free ISO | <https://rflysim.com/doc/en/5.HW/dl.html> links <https://rflysim.com/download/>; installer + precompiled model + UE4 scenes | Official download form names `RflySimToolchain-v5.01-20260831.iso`; email-delivered link, bytes and hash **unknown** until requested. Expanded installation officially 80–100 GB. | Keep original ISO locally or in durable storage with verified SHA-256; record source URL and license. Do not rely on expiring host. |
| Installed RflySim3D stock scene and model DLL | Included in selected Free install; native A/B reproduction | Exact filenames, sizes, hashes and license pending installed inspection | Preserve manifest and installer ISO; copy scene/model only if license permits; otherwise verified retrievable installer URL/hash plus durable ISO. |
| PX4 SITL firmware/build and parameters | Included/compiled by selected installer, controller in B | Exact git commit/build and params pending | Export version, build, parameters and log; preserve source/firmware hash or durable source URL. |
| Camera Config.json | Stock VisionCaptureApi example in selected install | Intrinsics/extrinsics/type/size pending | Copy config into run; if no camera config, A blocked. |
| CopterSim public source | <https://github.com/RflySim/CopterSim> | HEAD `0d14487f8dc3086ad29387ed40e068e301905343`; archive hash/license unresolved | Record exact checkout commit and diff on host; source is not UE visual toolchain. |
| RflyExpCode public examples | <https://github.com/RflySim/RflyExpCode> | HEAD `7dbec4d8796d6e23ee86c523e4ba5712203b1519`; archive hash/license unresolved | Same. No need to clone full history for first run. |
| Pretrained learned policy | none identified for this task | missing | C blocked; no substitute. |
| Common indoor/outdoor/racing or Gaussian scene | none provided | missing | Future comparison, separate from native scene. Require explicit provenance, license, scale and calibration. |

Before download/install, check `Get-PSDrive C`, ISO content length and hash, installed directory size, free space, and destination free space. During and after run, generate a per-file SHA-256 manifest and verify every transferred file; open representative images, CSV and JSON. Keep Windows originals and source ISO until verified local/durable copies exist. If an asset is too large to copy, record a **tested** stable URL, exact hash and access method; an untested URL is not retention.
