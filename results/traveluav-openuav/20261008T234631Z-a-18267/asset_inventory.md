# Asset inventory — 2026-10-04

The local audit contains the 47 MB source checkout and 9.8 MB of official JSON metadata. No scene executable, full navigation archive, or checkpoint was downloaded to the local Mac. Local free space at inspection: 690 GiB; phase 2 storage must be checked again on its host. Sizes below are repository object sizes, decimal GB. **Expanded sizes are unknown until `7z l -slt` and extraction on the Linux host**; do not infer them from zip bytes. The selected scene archive is indivisible at download time even though only one scene executable is run. The selected navigation archive contains a whole map; only one episode is extracted/used for smoke evaluation.

| Role and exact file | Bytes | SHA-256 (HF LFS oid) | Access / local status |
| --- | ---: | --- | --- |
| `TravelUAV_env@44de5739a95a2f6a88767446421cddada9606642/closeloop_envs.z01` | 4,026,531,840 | `acc4e6e2f68d2c2606084cb068f7879670b1e2c6c2900a0b621fbdb4020054c2` | Public, ungated; pending |
| `closeloop_envs.z02` | 4,026,531,840 | `ba5fc7c11996aa7932070b7b0e3c19d331c99d9757534a6d1b41f446b2ca762c` | Public; pending |
| `closeloop_envs.z03` | 4,026,531,840 | `1825f0a3124d80130de1bd3cd8761abea2ab28c48e497e8f1ad098a745feebea` | Public; pending |
| `closeloop_envs.z04` | 4,026,531,840 | `abb292ae7b9f614244216bb37ecc44c2be6b24055acae6829a9a3092da8a8b6d` | Public; pending |
| `closeloop_envs.zip` | 2,539,575,135 | `9c8d745acbcc3519146f8c15d52980a77d6c9c2f6bc2d8a04073c801cfca0827` | Public; pending |
| `TravelUAV@faa8f2514156455ea7423464cc1295e6f92575cb/ModernCityMap.z01` | 4,037,017,600 | `0fe135b061079a7e01e8125e08c93fcffbdff25a991d7d7bd0ffc80d78612e2c` | Public; pending |
| `ModernCityMap.z02` | 4,037,017,600 | `6ce7d801d196cb679d415ac92ae45c2e2de64372e4ddb14717ff1d713710cd33` | Public; pending |
| `ModernCityMap.zip` | 1,773,021,965 | `4ce2e547449f60c681541afba3087e8ea859bd44c4b443a8e971fa5b705473f7` | Public; pending |
| `TravelUAV_data_json@5a1ed4c99d3e7bb2b35fa34135910cb7687fc831/data/uav_dataset/seen_valset.json` | 9.15 MB | local `af5b7b660ed3b1dea95b53aa72a98f74ae7a37cd381aa0e818ee2a343cf54552` | Downloaded and parsed |
| `data/meta/map_spawnarea_info.json`; `object_description.json` | 901 kB; 8.7 kB | local `120438c62c6fa286c8cf44213dd03f5b7cd863e33889ae21c913ab5f68b530e6`; `a7297b5d06fea6e7369de8378a82f1af3f2786460a73dde1b8a9a87b35b61a8a` | Downloaded and parsed |
| One selected seen episode index, `ModernCityMap/00ac4ad3-1b8b-410d-9abc-43b65186571f/merged_data.json` | unknown until extracted | `selected_seen_one.json` local hash `7ee96d45f31185e66dbbdbe23ae530b687baf58192e176675b0905cfd4bcba81` | Episode payload pending archive download; 33 split rows, one unique episode |
| `llama-uav-7b@6cd1a273ba26338a1be4eb93b43489ee0099fbce/adapter_model.bin` | 319,970,957 | `b6a7f8c7a4c43092b863b210a6f9f23b3076ce80c32c2f5f45eb6b108ea4c1ca` | Public, ungated; pending |
| `mm_projector.bin` | 763,949,522 | `dd9c61b1ddc7be0fafe9bb1a23d17b1235479fbcab4cccf4176adae6124a9f59` | Public; pending |
| `non_lora_trainables.bin` | 654,613,560 | `a77df7f4cc9b79cb59d4276892a84988bfc2a7066e73c37b121abd00e4b0b92d` | Public; pending |
| `traveluav-traj-model@583a3f6b9111fd80e76d6905eaa0f1793f3fd03f/model_5.pth` | 1,982,506,481 | `f8607cb31434adc7973688c23e14c9e1f440ea2c2980c297c2b1df2e4c29b425` | Public, ungated; pending |
| `lmsys/vicuna-7b-v1.5@3321f76e3f527bd14065daf69dad9344000a201d` | 13.48 GB total | shard hashes `4133d2fcc5f31286881ea50806d95b721d016b533036a99dedce3f8fe88520e6`, `d261d3c35e92d3070d1e61ed821ebfca812a847d2a880757d82728acf005c5ac` | Public listing; base Llama 2 terms; pending access check |
| EVA ViT G `eva_vit_g.pth`, QFormer `instruct_blip_vicuna7b_trimmed.pth`, Grounding DINO `groundingdino_swint_ogc.pth` | not verified | compute SHA-256 after retrieval | Author-linked external objects; pending size, license and download check |
| `llamavid/processor/clip-patch14-224` config and preprocessor | within code checkout | Git commit identifies bytes | Present in checkout; this is not a vision checkpoint |

The selected compressed scene plus navigation archives total **28.50 GB**. Adding the listed LoRA/trajectory/Vicuna files yields **about 45.70 GB before EVA, QFormer, Grounding DINO, Python packages, expanded archives, outputs, and collection copies**. Provision at least 300 GB SSD for the recommended host until expanded sizes are measured; 200 GB is a tentative cheaper ceiling with a preflight capacity gate. The full scene repository is 83.7 GB and full trajectory archive repository 483 GB; neither is needed for this smoke test.

Source listings: [scene files](https://huggingface.co/datasets/wangxiangyu0814/TravelUAV_env/tree/main), [trajectory files](https://huggingface.co/datasets/wangxiangyu0814/TravelUAV/tree/main), [split files](https://huggingface.co/datasets/wangxiangyu0814/TravelUAV_data_json/tree/main/data/uav_dataset), [adapter](https://huggingface.co/wangxiangyu0814/llama-uav-7b), [trajectory decoder](https://huggingface.co/wangxiangyu0814/traveluav-traj-model), [base model](https://huggingface.co/lmsys/vicuna-7b-v1.5).
