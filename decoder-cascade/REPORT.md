# MiniMax-H3 decoder cascade: TAEH3 with sparse official-VAE anchors

Date: 2026-08-26. Hardware: one AMD MI355X (physical GPU6 only). Workload: T2VA, 1344×768, 124 frames, 5.17 seconds, 50 inference steps. Evaluation: five prompts × four seeds = 20 paired cases per arm.

## Result in one paragraph

TAEH3 replaces only the final video decoder, so the DiT latent, cascading-cache decisions, generated subject/motion trajectory, and official audio decoder are unchanged by construction. Pure TAEH3 reduces the cache-accelerated request from 33.03 s to a decoder-isolated 28.95 s (1.142×), but its reconstruction loss is content dependent. Sparse official temporal anchors recover fidelity monotonically: 2/7 anchors reaches 1.095× E2E with SSIM 0.9193, PSNR 33.24 dB, and LPIPS 0.0723; 4/7 reaches 1.055× with SSIM 0.9338 and LPIPS 0.0581. These are reconstruction metrics against the same latent, not prompt-quality scores. No arm is declared a final perceptual PASS until the 20-case review page is inspected.

## Aggregate results

| arm | official chunks | composed E2E | E2E speedup | latency reduction | decoder | SSIM | PSNR | LPIPS | sharpness | jitter |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| TAEH3 | 0/7 | 28.95 ± 2.25 s | 1.142 ± 0.012× | 12.39 ± 0.94% | 0.056 ± 0.021 s | 0.9038 ± 0.0322 | 32.11 ± 2.48 dB | 0.0879 ± 0.0335 | 0.8939 ± 0.0523 | 0.9462 ± 0.1319 |
| TAEH3 + 1/7 official | 1/7 | 29.59 ± 2.26 s | 1.117 ± 0.011× | 10.47 ± 0.86% | 0.688 ± 0.015 s | 0.9111 ± 0.0299 | 32.59 ± 2.54 dB | 0.0799 ± 0.0305 | 0.9048 ± 0.0456 | 0.9603 ± 0.1264 |
| TAEH3 + 2/7 official | 2/7 | 30.17 ± 2.25 s | 1.095 ± 0.009× | 8.70 ± 0.74% | 1.269 ± 0.028 s | 0.9193 ± 0.0269 | 33.24 ± 2.40 dB | 0.0723 ± 0.0275 | 0.9174 ± 0.0394 | 0.9750 ± 0.1290 |
| TAEH3 + 4/7 official | 4/7 | 31.31 ± 2.26 s | 1.055 ± 0.006× | 5.22 ± 0.56% | 2.413 ± 0.013 s | 0.9338 ± 0.0216 | 34.47 ± 2.33 dB | 0.0581 ± 0.0208 | 0.9399 ± 0.0288 | 0.9959 ± 0.1198 |

Reference: cache-only + official H3 VAE, E2E 33.03 ± 2.24 s and decode 4.129 ± 0.117 s.

### Why the E2E timing is composed

The decoder change cannot alter denoising, but independent requests showed occasional denoise-only long tails. For each case, composed candidate E2E is `reference E2E − reference decoder + candidate decoder`. Direct candidate wall times are retained in the manifests as a noise diagnostic but are not used to attribute decoder speedup.

## Technique

1. The order-1 cascading cache produces the final H3 video and audio latents exactly as in the reference arm.
2. TAEH3 decodes the complete video latent in roughly 0.06 s. The official H3 audio decoder is unchanged.
3. Sparse-anchor arms additionally decode selected official temporal chunks: chunk 3 for 1/7; chunks 1 and 5 for 2/7; chunks 0, 2, 4, and 6 for 4/7.
4. Each official 17-frame region replaces the corresponding TAEH3 region with a two-frame feather at each boundary. No training is used.

This is decoder-side resolution/reconstruction acceleration, not progressive resolution inside the DiT. It preserves the generated latent trajectory exactly while approximating only its RGB reconstruction.

## Arms and the question each answers

| arm | exact decoder path | question |
|---|---|---|
| official | current in-tree H3 video VAE | full-quality reference |
| TAEH3 | tiny decoder for every frame | maximum decoder speed |
| TAEH3 + 1/7 | official chunk 3 | does one central anchor fix global drift cheaply? |
| TAEH3 + 2/7 | official chunks 1, 5 | balanced sparse correction |
| TAEH3 + 4/7 | official chunks 0, 2, 4, 6 | conservative quality point that still clears 5% E2E |

## Experimental protocol

| item | setting |
|---|---|
| cases per arm | 20: five prompts × seeds 79552, 48407, 1337, 20260819 |
| pairing | same prompt, seed, model build, cache configuration, and requested output geometry |
| warmup | one excluded seed-999 request per prompt and arm |
| GPU | physical GPU6 only; GPUs 4, 5, and 7 untouched |
| cache | order-1 cascade: τ=0.80, warmup 6, horizon 12, cap 10 |
| audio | original H3 audio decoder in every arm |
| metrics | all 124 decoded frame pairs; AlexNet LPIPS; no frame subsampling |

## Per-prompt results


### red ball

| arm | speedup | reduction | SSIM | PSNR | LPIPS | sharpness | jitter |
|---|---:|---:|---:|---:|---:|---:|---:|
| TAEH3 | 1.139 ± 0.002× | 12.22 ± 0.17% | 0.9433 ± 0.0100 | 36.09 ± 0.80 dB | 0.0518 ± 0.0121 | 0.9710 ± 0.0037 | 0.9782 ± 0.0229 |
| TAEH3 + 1/7 official | 1.115 ± 0.001× | 10.31 ± 0.11% | 0.9474 ± 0.0094 | 36.66 ± 0.74 dB | 0.0477 ± 0.0113 | 0.9723 ± 0.0036 | 0.9828 ± 0.0228 |
| TAEH3 + 2/7 official | 1.094 ± 0.001× | 8.57 ± 0.10% | 0.9518 ± 0.0082 | 37.15 ± 0.70 dB | 0.0443 ± 0.0102 | 0.9761 ± 0.0056 | 0.9867 ± 0.0154 |
| TAEH3 + 4/7 official | 1.053 ± 0.001× | 5.08 ± 0.09% | 0.9586 ± 0.0062 | 38.24 ± 0.68 dB | 0.0382 ± 0.0089 | 0.9821 ± 0.0042 | 0.9932 ± 0.0123 |

### neon rain (speech)

| arm | speedup | reduction | SSIM | PSNR | LPIPS | sharpness | jitter |
|---|---:|---:|---:|---:|---:|---:|---:|
| TAEH3 | 1.152 ± 0.010× | 13.18 ± 0.73% | 0.9089 ± 0.0193 | 31.51 ± 2.10 dB | 0.0799 ± 0.0204 | 0.9137 ± 0.0208 | 1.0542 ± 0.2385 |
| TAEH3 + 1/7 official | 1.127 ± 0.010× | 11.27 ± 0.82% | 0.9155 ± 0.0181 | 31.92 ± 2.22 dB | 0.0721 ± 0.0182 | 0.9199 ± 0.0184 | 1.0642 ± 0.2387 |
| TAEH3 + 2/7 official | 1.105 ± 0.008× | 9.49 ± 0.69% | 0.9256 ± 0.0128 | 32.98 ± 1.70 dB | 0.0632 ± 0.0153 | 0.9329 ± 0.0163 | 1.0902 ± 0.2541 |
| TAEH3 + 4/7 official | 1.062 ± 0.007× | 5.87 ± 0.62% | 0.9371 ± 0.0110 | 33.98 ± 1.99 dB | 0.0513 ± 0.0133 | 0.9493 ± 0.0100 | 1.1030 ± 0.2502 |

### drummer (percussion)

| arm | speedup | reduction | SSIM | PSNR | LPIPS | sharpness | jitter |
|---|---:|---:|---:|---:|---:|---:|---:|
| TAEH3 | 1.133 ± 0.006× | 11.76 ± 0.51% | 0.9113 ± 0.0180 | 31.40 ± 0.96 dB | 0.0629 ± 0.0027 | 0.8699 ± 0.0192 | 0.9478 ± 0.0610 |
| TAEH3 + 1/7 official | 1.110 ± 0.005× | 9.87 ± 0.38% | 0.9187 ± 0.0162 | 31.90 ± 0.97 dB | 0.0568 ± 0.0025 | 0.8853 ± 0.0162 | 0.9639 ± 0.0590 |
| TAEH3 + 2/7 official | 1.089 ± 0.004× | 8.16 ± 0.30% | 0.9257 ± 0.0147 | 32.49 ± 0.96 dB | 0.0515 ± 0.0022 | 0.9007 ± 0.0141 | 0.9718 ± 0.0559 |
| TAEH3 + 4/7 official | 1.051 ± 0.002× | 4.89 ± 0.20% | 0.9403 ± 0.0110 | 33.91 ± 0.92 dB | 0.0410 ± 0.0019 | 0.9265 ± 0.0121 | 0.9906 ± 0.0487 |

### ocean (scenery)

| arm | speedup | reduction | SSIM | PSNR | LPIPS | sharpness | jitter |
|---|---:|---:|---:|---:|---:|---:|---:|
| TAEH3 | 1.156 ± 0.003× | 13.52 ± 0.20% | 0.8616 ± 0.0255 | 31.39 ± 1.64 dB | 0.1225 ± 0.0196 | 0.8249 ± 0.0202 | 0.7987 ± 0.0444 |
| TAEH3 + 1/7 official | 1.129 ± 0.003× | 11.40 ± 0.21% | 0.8723 ± 0.0234 | 31.82 ± 1.65 dB | 0.1112 ± 0.0176 | 0.8452 ± 0.0180 | 0.8300 ± 0.0422 |
| TAEH3 + 2/7 official | 1.104 ± 0.004× | 9.41 ± 0.30% | 0.8816 ± 0.0212 | 32.26 ± 1.62 dB | 0.1008 ± 0.0156 | 0.8665 ± 0.0170 | 0.8627 ± 0.0430 |
| TAEH3 + 4/7 official | 1.060 ± 0.002× | 5.67 ± 0.22% | 0.9017 ± 0.0167 | 33.35 ± 1.59 dB | 0.0813 ± 0.0121 | 0.9014 ± 0.0139 | 0.9183 ± 0.0402 |

### wuxia (fast motion + music)

| arm | speedup | reduction | SSIM | PSNR | LPIPS | sharpness | jitter |
|---|---:|---:|---:|---:|---:|---:|---:|
| TAEH3 | 1.127 ± 0.001× | 11.28 ± 0.04% | 0.8939 ± 0.0206 | 30.17 ± 1.55 dB | 0.1225 ± 0.0177 | 0.8899 ± 0.0221 | 0.9523 ± 0.0321 |
| TAEH3 + 1/7 official | 1.105 ± 0.000× | 9.49 ± 0.04% | 0.9015 ± 0.0206 | 30.66 ± 1.63 dB | 0.1116 ± 0.0169 | 0.9015 ± 0.0242 | 0.9606 ± 0.0279 |
| TAEH3 + 2/7 official | 1.086 ± 0.000× | 7.88 ± 0.03% | 0.9119 ± 0.0146 | 31.31 ± 1.45 dB | 0.1017 ± 0.0152 | 0.9107 ± 0.0162 | 0.9637 ± 0.0273 |
| TAEH3 + 4/7 official | 1.048 ± 0.001× | 4.62 ± 0.10% | 0.9316 ± 0.0106 | 32.86 ± 1.38 dB | 0.0789 ± 0.0070 | 0.9400 ± 0.0096 | 0.9742 ± 0.0140 |

## Audio verification

TAEH3 changes only the video decoder. Across 20 cases, integrated loudness deltas round to 0.00 dB, clipping remains zero, and waveform/spectral comparisons remain near identity. Small nonzero differences come from separately executed requests rather than a candidate audio code path.

| arm | waveform correlation | spectral correlation | LSD | Δ LUFS-I | Δ RMS | clipping Δ |
|---|---:|---:|---:|---:|---:|---:|
| TAEH3 | 0.999875 ± 0.000281 | 0.996475 ± 0.003918 | 0.502 ± 0.587 dB | 0.000 ± 0.000 dB | 0.000014 ± 0.000039 | 0.000000 ± 0.000000 |
| TAEH3 + 1/7 official | 0.999900 ± 0.000212 | 0.997350 ± 0.003731 | 0.427 ± 0.591 dB | -0.005 ± 0.022 dB | 0.000007 ± 0.000066 | 0.000000 ± 0.000000 |
| TAEH3 + 2/7 official | 0.999888 ± 0.000257 | 0.996868 ± 0.004294 | 0.415 ± 0.473 dB | -0.005 ± 0.022 dB | -0.000001 ± 0.000019 | 0.000000 ± 0.000000 |
| TAEH3 + 4/7 official | 0.999872 ± 0.000278 | 0.996585 ± 0.004072 | 0.490 ± 0.532 dB | -0.005 ± 0.022 dB | 0.000008 ± 0.000037 | 0.000000 ± 0.000000 |

## Metric definitions

- SSIM and PSNR measure same-latent RGB reconstruction fidelity. Higher is closer to the official decoder.
- LPIPS is AlexNet perceptual distance over every frame pair. Lower is closer.
- Sharpness and temporal-jitter ratios have an ideal value of 1.0; below one indicates smoothing.
- Temporal delta error compares candidate and reference frame-to-frame changes in 0–255 pixel units. Lower is better.
- Patch-boundary ratio has ideal 1.0 and checks for added tile seams.
- Audio LSD is log-spectral distance in dB. Lower is better.

## Content dependence

The red-ball kill test was optimistic: pure TAEH3 averaged SSIM 0.943 there, but only 0.862 on ocean and 0.894 on wuxia. Ocean is also the binding sharpness/jitter case. A single-prompt decoder verdict would therefore be unreliable. Sparse anchors improve every aggregate image metric monotonically, but they do not remove content dependence.

## Tried and rejected

- Naive motion-compensated temporal smoothing at strengths 0.25 and 0.50: rejected. The CPU prototype added about 8.28 s and worsened SSIM/LPIPS while risking ghosting.
- Full official decode followed by output averaging: rejected conceptually because it retains essentially all of the 4.13 s official decoder cost.
- Treating direct independently rerun E2E as the decoder timing: rejected after denoise-only long tails were observed.

## Relationship to existing Hedra work

- PR #5 already shipped the ROCm flash-SDPA path for the official decoder.
- PR #12 added an opt-in fused GroupNorm+SiLU path inside the official decoder.
- PR #25 is encoder-only, but records decoder tiling fragmentation as a separate investigation.
- Closed PR #3 was an earlier official-decoder attention optimization.
- No existing PR integrates TAEH3 or sparse official temporal anchors. This work should be presented as an optional lossy decoder cascade, not as the first H3 VAE optimization.

## Decision

Automated Pareto ordering is clear: pure TAEH3 is fastest; 4/7 is closest to official; 2/7 is the balanced numerical point. The current engineering recommendation is to human-review 2/7 first, with 1/7 as the faster fallback and 4/7 as the conservative control. Reject any arm that introduces visible pixel shimmer, decoder-boundary transitions, texture loss, or motion instability even if its aggregate metrics pass.


## Public artifacts

- `index.html`: public interactive report and 20-case five-arm video review.
- `data/summary.json`: aggregate and per-prompt statistics only.

Raw manifests, logs, local paths, and run identifiers are intentionally excluded from the public repository.

## Temporal Position Bias and Front-Loaded Decoding

### New hypothesis

**H1: TAEH3 reconstruction artifacts are temporally non-uniform and are disproportionately concentrated near the beginning of the decoded video.** If true, a front-loaded decoder cascade should outperform uniformly or arbitrarily distributed official chunks under matched compute. This section only adds results; all earlier results remain unchanged.

### Temporal error profile

Pure TAEH3 was compared frame-by-frame with the full official decoder for all 20 existing videos (five prompts × four seeds, 124 frames each).

| region | frames | MAE ↓ | PSNR ↑ | SSIM ↑ | LPIPS ↓ | temporal Δ error ↓ | jitter ratio |
|---|---:|---:|---:|---:|---:|---:|---:|
| 0-20% | 0–24 | 4.1958 | 31.83 | 0.8953 | 0.0900 | 3.8435 | 0.9466 |
| 20-40% | 25–49 | 4.0508 | 32.05 | 0.9026 | 0.0919 | 3.8651 | 0.9384 |
| 40-60% | 50–74 | 3.8017 | 32.64 | 0.9093 | 0.0878 | 3.5283 | 0.9421 |
| 60-80% | 75–99 | 3.7578 | 32.76 | 0.9074 | 0.0845 | 3.2895 | 0.9777 |
| 80-100% | 100–123 | 3.7148 | 33.10 | 0.9045 | 0.0853 | 3.1008 | 1.0054 |

The first quintile has 12.9% more absolute error and 24.0% more temporal-delta error than the final quintile; PSNR is 1.27 dB lower. However, LPIPS is slightly worse in the second quintile and SSIM peaks in the middle. H1 is therefore **weakly supported**: early reconstruction is harder on average, but the first chunk is not universally worst. The public page includes frame-wise curves for all six metrics.

### Matched-budget decoder allocation

Fixed 1/7 uses official chunk 3; Front-1 uses chunk 0. Fixed 2/7 uses chunks 1 and 5; Front-2 uses chunks 0 and 1; Front+Late uses chunks 0 and 5. Indices are zero-based; every hybrid uses identical two-frame feathering.

| Method | Official chunks | Decoder | Composed E2E | reduction | SSIM ↑ | PSNR ↑ | LPIPS ↓ | jitter | temporal Δ ↓ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Full Official | 7/7 | 4.129 s | 33.03 s | 0.00% | 1.0000 | reference | 0.0000 | 1.0000 | 0.0000 |
| TAEH3 | 0/7 | 0.056 s | 28.95 s | 12.39% | 0.9038 | 32.11 dB | 0.0879 | 0.9462 | 3.5263 |
| Fixed 1/7 | 1/7 | 0.688 s | 29.59 s | 10.47% | 0.9111 | 32.59 dB | 0.0799 | 0.9603 | 3.3232 |
| **Front-1** | 1/7 | 0.683 s | 29.58 s | 10.48% | 0.9125 | 32.70 dB | 0.0798 | 0.9575 | 3.3234 |
| Fixed 2/7 | 2/7 | 1.269 s | 30.17 s | 8.70% | 0.9193 | 33.24 dB | 0.0723 | 0.9750 | 3.1198 |
| **Front-2** | 2/7 | 1.280 s | 30.18 s | 8.67% | 0.9208 | 33.41 dB | 0.0718 | 0.9708 | 3.0842 |
| **Front+Late** | 2/7 | 1.263 s | 30.16 s | 8.72% | 0.9196 | 33.20 dB | 0.0728 | 0.9710 | 3.1608 |

Matched decoder cost is effectively identical: Front-1 versus Fixed 1/7 differs by 0.004 s; Front-2 versus Fixed 2/7 differs by 0.011 s.

### Same-case paired result

| comparison | Δ SSIM / wins | Δ PSNR / wins | Δ LPIPS / wins | Δ temporal error / wins |
|---|---:|---:|---:|---:|
| Front-1 − Fixed 1/7 | +0.0015 · 14/20 | +0.11 dB · 13/20 | -0.0001 · 8/20 | +0.0002 · 8/20 |
| Front-2 − Fixed 2/7 | +0.0015 · 12/20 | +0.17 dB · 11/20 | -0.0005 · 12/20 | -0.0356 · 13/20 |
| Front+Late − Fixed 2/7 | +0.0003 · 14/20 | -0.04 dB · 13/20 | +0.0005 · 7/20 | +0.0410 · 5/20 |

Front-1 has small SSIM/PSNR gains but no consistent LPIPS or temporal-stability win. Front-2 is directionally better on SSIM, PSNR, LPIPS, and temporal-delta error, but the effects are small. Front+Late has no matched-baseline advantage.

### Boundary analysis

| candidate | switch | official-tail MAE | feather MAE | first TAE MAE | brightness | color | texture | motion |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Front-1 | frame 17 | 1.878 | 2.588 | 4.079 | 0.645 | 0.643 | 0.105 | 3.324 |
| Front-2 | frame 34 | 1.805 | 2.416 | 3.855 | 0.713 | 0.706 | 0.060 | 3.163 |
| Front+Late | frame 17 | 1.877 | 2.588 | 4.079 | 0.644 | 0.643 | 0.105 | 3.323 |

The feather avoids a catastrophic one-frame cut, but error rises from about 1.8–1.9 MAE in the official tail to 2.4–2.6 in the feather and 3.9–4.1 after pure TAEH3 resumes. Mean brightness/color jump errors remain below one 8-bit level; human review is still required for texture shimmer and motion continuity.

### Per-prompt front-loaded result

| prompt | Front-1 SSIM / LPIPS | Front-2 SSIM / LPIPS | Front+Late SSIM / LPIPS |
|---|---:|---:|---:|
| red ball | 0.9474 / 0.0485 | 0.9517 / 0.0447 | 0.9514 / 0.0451 |
| neon rain (speech) | 0.9198 / 0.0697 | 0.9310 / 0.0593 | 0.9244 / 0.0649 |
| drummer (percussion) | 0.9195 / 0.0566 | 0.9267 / 0.0510 | 0.9267 / 0.0511 |
| ocean (scenery) | 0.8723 / 0.1121 | 0.8827 / 0.1014 | 0.8823 / 0.1012 |
| wuxia (fast motion + music) | 0.9036 / 0.1122 | 0.9117 / 0.1026 | 0.9131 / 0.1016 |

### Prefix sweep

The optional 4/8/16-frame sweep was not run. The official H3 VAE is temporally chunked with overlap/state assumptions; arbitrary prefixes would not preserve the valid decoder operation and could manufacture boundary artifacts. One complete 17-frame chunk is the smallest deterministic unit tested.

### Decision and Pareto update

This is a **weak positive** result. Temporal-position bias exists in aggregate pixel and temporal-delta error, but is not consistent enough across LPIPS, SSIM, content, and paired wins to make front-loaded allocation the new default. Front-2 remains a diagnostic/perceptual candidate: no training, additional model, runtime predictor, or adaptive logic, at the same official-decoder budget as Fixed 2/7. Fixed 2/7 remains the balanced default pending multi-case human review. If review confirms less initial shimmer for Front-2 without a visible transition, it can become an early-stability preset; otherwise future work should select chunks content-adaptively.
