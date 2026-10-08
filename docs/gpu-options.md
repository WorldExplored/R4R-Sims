# Available rental options

User-supplied availability snapshot from 2026-10-08. This is the allowed candidate list for the current simulator prompts, not a guarantee of later availability. Prices are transcribed exactly as shown; the screenshot does not establish whether multi-GPU prices are per GPU or per instance, or provide CPU/RAM/disk specifications.

| GPU label | VRAM shown | Displayed hourly price | Listed GPU counts |
| --- | --- | --- | --- |
| A100 | 80 GB | $1.82/hr | x8, x1 |
| A40 | 48 GB | $0.62/hr | x2, x1 |
| A6000 | 48 GB | $0.54/hr | x2, x1 |
| L40 | 48 GB | $0.86/hr | x1 |
| L40S | 48 GB | $0.82/hr | x1 |
| RTX6000 Ada | 48 GB | $0.75/hr | x1 |
| A10 | 24 GB | $1.29/hr | x1 |
| L4 | 24 GB | $0.62/hr | x1 |
| A4500 | 20 GB | $0.28/hr | x1 |

Also shown: CPU Node, x1, $0.06/hr, with spot price $0.05/hr. This is not a GPU option.

Choose the cheapest compatible configuration for the specific simulator and evaluation plan. A4500 x1 has the lowest listed GPU price; it is not automatically suitable. Confirm memory, rendering/driver/API support, OS, CPU, RAM, disk, and full-instance price. No fixed budget ceiling is imposed, but cost minimization remains required. Do not recommend an unlisted GPU without a new availability update. Do not assume Ubuntu can run Windows-only simulator releases.
