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
