# MiniMax-H3 15-step progressive-resolution window-location ablation

Date: 2026-08-22

## Setup

- Workload: `A red ball rolling slowly across a wooden table.`
- Dense reference: same prompt and seed, 50 full-resolution inference steps
- Candidate: 15 half-spatial-resolution steps, sigma-scaled high-frequency residual transport, 8-bin cosine blending, scheduler rewind
- Hardware isolation: physical GPU 6 only
- Coarse and local sweep: seed 0
- Final validation: seeds 0–5 for the two closest challengers, compared with the existing six-seed `[20,35)` results

## Seed-0 location sweep

All candidates have effectively the same latency, about 107.3 seconds or 1.34x versus the 143.95-second Dense reference. Changing the location therefore isolates quality rather than speed.

| Low-resolution window | E2E (s) | Speedup | SSIM | PSNR (dB) | LPIPS | Sharpness ratio | Jitter ratio | Patch-boundary ratio | Delta LUFS-I (dB) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `[10,25)` | 107.37 | 1.3407x | 0.7560 | 21.57 | 0.2552 | 1.2132 | 1.0732 | 1.1752 | -2.1 |
| `[15,30)` | 107.37 | 1.3407x | 0.8744 | 27.67 | 0.1274 | 0.9922 | 1.0203 | 1.0385 | -1.7 |
| `[18,33)` | 107.23 | 1.3425x | 0.9017 | 30.24 | 0.0989 | 0.9587 | 1.0056 | 1.0135 | -0.2 |
| `[19,34)` | 107.48 | 1.3394x | 0.9069 | 31.42 | 0.0887 | 0.9504 | 0.9880 | 1.0134 | +0.2 |
| `[20,35)` | 107.39 | 1.3404x | 0.9182 | 32.81 | 0.0796 | 0.9392 | 0.9771 | 1.0175 | +0.4 |
| `[21,36)` | 107.33 | 1.3412x | 0.9272 | 33.40 | **0.0734** | 0.9135 | 0.9523 | 1.0146 | +0.7 |
| `[22,37)` | 107.34 | 1.3411x | **0.9291** | **33.60** | 0.0737 | 0.9006 | 0.9465 | 1.0149 | +0.9 |
| `[23,38)` | 107.38 | 1.3405x | 0.9096 | 30.68 | 0.1405 | 0.9057 | 1.0282 | 1.0999 | +1.0 |
| `[24,39)` | 107.37 | 1.3407x | 0.9031 | 29.29 | 0.1639 | 0.8954 | 1.0666 | 1.1254 | +1.2 |
| `[25,40)` | 107.43 | 1.3399x | 0.8886 | 28.54 | 0.1751 | 0.8754 | 1.1053 | 1.1434 | +1.2 |
| `[30,45)` | 107.38 | 1.3406x | 0.8418 | 26.05 | 0.2886 | 0.7242 | 1.6870 | 1.2957 | +1.3 |

Seed 0 alone places the numerical SSIM/PSNR peak at start step 22 and the LPIPS peak at start step 21. Starting later than 22 degrades rapidly because too few full-resolution steps remain after the low-resolution window.

## Six-seed validation

Mean +/- population standard deviation over seeds 0–5.

| Window | E2E (s) | Speedup | SSIM | PSNR (dB) | LPIPS | Sharpness ratio | Jitter ratio | Patch-boundary ratio |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **`[20,35)` current** | about 107.45 | about 1.339x | **0.92423** | **30.3835** | **0.09045** | **0.95163** | **0.99889** | **0.99782** |
| `[21,36)` | 107.48 +/- 0.07 | 1.33847 +/- 0.00149x | 0.92433 +/- 0.00950 | 30.3814 +/- 2.0349 | 0.09283 +/- 0.01902 | 0.94465 +/- 0.04033 | 1.00159 +/- 0.09013 | 0.99975 +/- 0.04938 |
| `[22,37)` | 107.44 +/- 0.05 | 1.33898 +/- 0.00157x | 0.92286 +/- 0.00957 | 30.1741 +/- 2.2186 | 0.09717 +/- 0.01916 | 0.93842 +/- 0.04123 | 0.99947 +/- 0.08062 | 1.00183 +/- 0.05013 |

Paired `[20,35)` versus `[21,36)`:

- `[20,35)` has higher SSIM on 4/6 seeds.
- `[20,35)` has lower LPIPS on 4/6 seeds.
- `[21,36)` has higher PSNR on 4/6 seeds, but the means are effectively tied: 30.3814 versus 30.3835 dB.
- `[20,35)` retains more high-frequency detail on average: sharpness ratio 0.95163 versus 0.94465.
- Latency is indistinguishable.

## Decision

Keep **start step 20, window `[20,35)`** as the 15-step candidate.

The seed-0-only optimum at start 21–22 does not generalize. Across six seeds, moving the window one step later produces no meaningful SSIM or PSNR gain and slightly worsens LPIPS and sharpness; moving it two steps later is worse overall. The location curve also shows a sharp failure boundary after start 22.

This remains an automatic-metric decision. Any release decision still requires the existing multi-prompt human review gate for visible texture changes, blur, motion/camera changes, and audio defects.

## Raw data

- Coarse/local sweep through start 22: `metrics_through_start22.json`
- Boundary starts 23 and 24: `metrics.json`
- Six-seed starts 21 and 22: `../rewind15_location_validate/metrics.json`
- Existing six-seed start 20 and four-prompt results: `../rewind15_haiyang_6seed/metrics.json`
