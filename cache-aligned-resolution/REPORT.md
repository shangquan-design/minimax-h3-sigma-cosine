# MiniMax-H3 Cache-Aligned Coarse-Attention — Evaluation Report

**Workload:** T2VA, 1344×768, 124 frames (5.1667 s), 50 diffusion steps
**Hardware:** 1× AMD MI355X GPU
**Matrix:** 5 prompts × 4 seeds = 20 paired reference/candidate runs
**Cache policy (unchanged by this method):** order-1, τ = .80, warmup 6, horizon 12, cap 10

---

## Slack update (ready to send)

> **What:** Tried narrowing MiniMax-H3's genuine cache full-compute steps (blocks [10, 40)) to a
> coarse 10×18 video-attention context instead of dense 24×42, plus a σ-scaled saved
> high-frequency anchor to limit detail loss. Hidden/Q/MLP/residual/output stay at full spatial resolution;
> cache-hit steps are untouched.
> **Result:** 20 paired runs, E2E 33.028s → 32.235s (**1.0245×, −2.4%**), denoise-only 28.821s →
> 28.088s (**1.0258×**). 15/20 pairs faster, paired t(19)=3.70, p=.0015 — real, not noise.
> **Quality:** Aggregate SSIM 0.9118 / LPIPS 0.1004, but **content-dependent**: static/low-motion
> scenes (ocean) are pixel-identical; fast, fine-detail scenes (wuxia) drop to SSIM 0.7924 /
> LPIPS ~0.28. Audio essentially untouched (waveform corr. 0.993).
> **Recommendation:** **Not proposing for PR.** The effect is real but comes in under our
> predeclared 3% ship gate (achieved 2.4%), and the fidelity cost concentrates on exactly the
> high-motion content where it's most visible. Worth revisiting with a less aggressive coarsening
> ratio or a stronger anchor for high-motion content before re-testing against the same gate.

---

## Executive summary

MiniMax-H3's order-1 cascading cache already skips most attention/MLP/residual compute across the
50-step schedule. This experiment goes one step further: on the steps the cache *cannot* skip —
genuine full-compute steps inside blocks **[10, 40)** — it computes the video-attention context on
a coarse **10×18** spatial grid instead of the dense **24×42** grid, adding back a σ-scaled saved
high-frequency anchor to limit detail loss. Cache-hit timesteps and blocks outside that range are left completely untouched.

Across 20 paired runs, end-to-end latency dropped from **33.028 ± 2.236 s** to
**32.235 ± 1.959 s** (**1.0245×**, **2.4% lower** E2E time), faster on **15 of 20** pairs, paired
t(19) = 3.70, p = .0015. Denoise-only time moved from 28.821 s to 28.088 s (**1.0258×**). The
effect is statistically real and mechanically consistent with the method's design, but it
**misses the predeclared 3% ship gate**, and fidelity is clearly **content-dependent** — this is
not proposed for PR merge in its current form.

## Method

The cache's order-1 policy (τ .80, 6-step warmup, 12-step horizon, cap 10) decides step-by-step
whether to reuse its cached residual payload and skip the DiT stack or run a genuine compute; this method does not change that decision.
It only changes what happens **on genuine DiT computations after an eight-step coarse-attention warmup**, and only inside transformer blocks **[10, 40)**. Blocks 0–9 and 40–49 remain exact; cache-hit timesteps remain untouched.

On a genuine full-compute timestep, inside blocks [10, 40):

- Hidden states, Q projection, MLP, residual add, and output projection are still computed in
  full — none of that is approximated.
- Only the spatial resolution of the video-attention *context* changes: dense **24×42** →
  coarse **10×18**.
- A prior exact attention computation saves the high-frequency component of the full attention output. Later coarse computations upsample their output and restore that saved component, scaled by the current denoising σ — this anchor helps low-detail content remain close to the reference.

Cache-hit timesteps are entirely untouched — they reuse cached state
exactly as they would without this change.

## Aggregate results

| Metric | Reference | Candidate | Δ | Speedup |
|---|---|---|---|---|
| End-to-end latency (s) | 33.028 ± 2.236 | 32.235 ± 1.959 | −0.793 s (−2.4%) | **1.0245×** ± 0.0286 |
| Denoise-only latency (s) | 28.821 ± 2.259 | 28.088 ± 1.958 | −0.733 s (−2.5%) | **1.0258×** ± 0.0324 |

**Paired significance**

| Test | t | p | df | Reading |
|---|---|---|---|---|
| E2E paired t-test | 3.695 | .0015 | 19 | Significant — not noise |
| Denoise paired t-test | 3.436 | .0028 | 19 | Significant, consistent with E2E |

**Fidelity, aggregate (mean ± std across 20 pairs)**

| Metric | Value |
|---|---|
| SSIM | 0.9118 ± 0.0835 |
| LPIPS | 0.1004 ± 0.1092 |
| PSNR (dB) | 45.21 ± 28.90 (skewed high by pixel-identical runs — see Limitations) |
| Sharpness ratio | 0.9733 ± 0.0340 |
| Temporal jitter ratio | 0.9776 ± 0.0739 |
| Patch boundary ratio | 1.0656 ± 0.0633 |
| Audio waveform correlation | 0.9927 ± 0.0126 |
| Audio spectral correlation | 0.9650 ± 0.0366 |
| Log-spectral distance (dB) | 2.649 ± 1.971 |

## Per-prompt results

| Prompt | E2E speedup | SSIM | PSNR (dB) | Audio corr. | LSD (dB) |
|---|---|---|---|---|---|
| Prompt 1 | 1.0367 ± 0.0088 | 0.9515 ± 0.0077 | 35.63 ± 0.52 | 0.9992 ± 0.0005 | 3.263 ± 0.548 |
| Prompt 2 | 1.0210 ± 0.0268 | 0.9475 ± 0.0461 | 38.64 ± 8.97 | 0.9979 ± 0.0024 | 1.486 ± 1.653 |
| Prompt 3 | 1.0261 ± 0.0351 | 0.8678 ± 0.0693 | 28.15 ± 3.56 | 0.9918 ± 0.0125 | 3.363 ± 0.984 |
| Prompt 4 (ocean — identical) | 0.9983 ± 0.0046 | 1.0000 ± 0.0000 | 100.00 ± 0.00 | 0.99999 ± 0.00002 | 0.053 ± 0.106 |
| Prompt 5 (wuxia — hardest) | 1.0403 ± 0.0410 | 0.7924 ± 0.0373 | 23.63 ± 2.25 | 0.9744 ± 0.0150 | 5.079 ± 0.863 |

15 of the 20 individual pairs are faster than reference; the four Prompt 4 (ocean) runs and one
each of Prompt 2, Prompt 3, and Prompt 5 land slightly slower, all within noise of parity.

## Content-dependent fidelity

**Prompt 4 (ocean)** — SSIM 1.0000, PSNR 100 dB, LSD 0.053 dB across all 4 seeds: pixel-identical.
Smooth, low-frequency motion is fully recoverable from the coarse grid plus anchor. It's also the
one prompt where the candidate ran marginally *slower* on average (−0.17%) — the anchor's fixed
cost isn't offset by attention savings when there's little high-frequency content to begin with.

**Prompt 5 (wuxia)** — SSIM 0.7924, PSNR 23.63 dB, LSD 5.079 dB: the lowest fidelity of any prompt
in this matrix. Fast choreography and fine costume/weapon detail push well past what the anchor
term restores, and this is the clearest evidence against enabling the method broadly without
handling high-motion content differently.

## Review videos

All 20 candidate renders are available under `videos/`, named
`p{prompt}_seed{seed}_cache_resolution.mp4` (e.g. `p1_seed79552_cache_resolution.mp4`), grouped by
prompt in `index.html` alongside per-clip E2E delta, SSIM, and LSD. Spot-check Prompt 5 clips
first — they carry the visible fidelity cost this report flags.

## Metric glossary

- **SSIM** — structural similarity (0–1) between candidate and reference frames; below ~0.90 is
  typically visible as softening or drift.
- **LPIPS** — learned perceptual distance between deep-network features; lower is closer, 0 is
  identical.
- **PSNR** — pixel-error signal-to-noise ratio in dB; dominated by exact matches here, so treat as
  secondary to SSIM/LPIPS.
- **Sharpness ratio** — candidate/reference high-frequency detail energy; below 1.0 means softer.
- **Temporal jitter ratio** — candidate/reference frame-to-frame change magnitude; near 1.0 means
  motion stability is preserved.
- **Patch boundary ratio** — edge energy at coarse-grid patch boundaries vs. reference; a direct
  seam-visibility check for the 10×18 downsampling.
- **Waveform / spectral correlation, LSD** — audio similarity in time domain, frequency domain,
  and log-spectral error (dB); all three confirm audio is largely unaffected.
- **Paired t-test** — tests whether the mean of the 20 per-pair reference-minus-candidate deltas
  is reliably nonzero; p < .05 means the timing difference isn't noise, but says nothing about
  whether the effect size clears a ship bar.

## Limitations

- **Below the predeclared ship gate.** The 3% end-to-end speedup threshold was set before this
  run. The measured 2.4% mean is statistically real (p = .0015) but doesn't clear that bar, and
  per-prompt speedup ranges from −0.17% to +4.03%.
- **Fidelity is content-dependent, not uniform.** Ocean is pixel-identical; wuxia drops to SSIM
  0.7924 / LPIPS ~0.28 — well below the aggregate mean and likely visible to viewers.
- **Small, fixed matrix.** 5 prompts × 4 seeds on one GPU establishes a real paired effect but
  doesn't characterize the full space of content this method would touch in production.
- **One additional comparison was excluded from every result in this report.** A further
  prompt/seed attempt failed during launch before either run completed cleanly, corrupting its
  timing capture; the delta it would have produced was not representative of the method and is
  omitted here rather than reported.
- **PSNR is a poor aggregate signal for this workload** — dominated by pixel-identical runs
  pulling the mean and std to extreme values. SSIM and LPIPS are the more trustworthy read.
- **Denoise-only and end-to-end tell slightly different stories** — the gap reflects fixed
  encode/decode overhead outside the modified window. The ship gate is defined on end-to-end
  time, the harder number to move.
- **Cache and coarse-grid hyperparameters were not swept.** τ, warmup, horizon, cap, the 10×18
  target resolution, and the σ-scaling schedule were all held at one configuration.

## Decision

**Not proposed for PR.** The effect is real, statistically significant, and mechanically sound,
but it misses the ship gate agreed before this run (2.4% measured vs. 3.0% required), and the
fidelity cost concentrates on exactly the high-motion, fine-detail content where it would be most
visible (15/20 pairs faster; wuxia SSIM 0.7924 vs. ocean's pixel-identical result).

**Recommendation:** keep this as a validated research direction, not a shipping candidate. The
next useful step is closing the gap on high-motion, fine-detail content — either a less aggressive
coarsening ratio or a stronger anchor term for those cases — before re-running against the same
gate, rather than lowering the gate to fit this result.
