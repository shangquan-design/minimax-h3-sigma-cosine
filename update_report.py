from pathlib import Path

p=Path("index.html")
s=p.read_text()
s=s.replace("<title>MiniMax-H3 Sigma Cosine</title>","<title>MiniMax-H3 Progressive Resolution</title>")
s=s.replace("<div class='warn'><b>Provisional:</b> performance and automated gates pass. Seed 1 visual/audio review passes. Seeds 0,2,3,4,5 remain pending; no final perceptual PASS is declared.</div>","<div class='warn'><b>Current result:</b> the original six-seed middle-window candidate passed human visual/audio review on 6/6 seeds. A broader four-prompt, 24-pair evaluation now identifies the same method plus scheduler rewind as the leading automated-metric candidate; multi-prompt human review is still pending. FL2VA has not yet been evaluated.</div>")
s=s.replace("<div class='big'>1.099×</div>end-to-end speedup vs full-resolution Dense","<div class='big'>1.092×</div>end-to-end speedup vs full-resolution Dense")
s=s.replace("<div class='big'>131.88 ± 0.06 s</div>candidate end-to-end latency","<div class='big'>131.737 ± 0.144 s</div>candidate end-to-end latency")
s=s.replace("<div class='big'>0.9477</div>same-seed structural similarity (SSIM) vs Dense","<div class='big'>0.9369 ± 0.0156</div>SSIM over 24 paired outputs")
s=s.replace("<div class='big'>0.0561</div>same-seed perceptual distance (LPIPS) vs Dense","<div class='big'>0.0499 ± 0.0121</div>LPIPS over 24 paired outputs")
s=s.replace("<div class='big'>34.72 ± 0.97 dB</div>same-seed peak signal-to-noise ratio (PSNR) vs Dense","<div class='big'>32.67 ± 2.10 dB</div>PSNR over 24 paired outputs")
s=s.replace("<b>Current candidate; multi-seed human review pending</b>","<b>Human visual/audio review PASS on 6/6 seeds</b>")
s=s.replace("<td>pending</td>","<td>PASS</td>")
s=s.replace("human review pending","human PASS").replace("tag '","tag pass'")
s=s.replace("The 5-step rewind method now has paired T2VA, FL2VA, and Ref2VA results. An 8-step rewind candidate reaches 1.155× and passes automated metrics; broader human review is still pending.","The 5-step rewind method has paired T2VA, FL2VA, and Ref2VA results. The 8-step rewind candidate reaches 1.155× and passed human review. A 15-step location ablation retains [20,35) at 1.339×; its broader multi-prompt human gate remains pending.")
marker="<h2>Current method</h2>"
new="""<h2>What changed after the original report</h2>
<p>The initial report covered one prompt and six seeds. The follow-up adds a direct reproduction of the documented SGLang DCT transition, an early-window residual-transport ablation, a scheduler-rewind ablation, and a four-prompt × six-seed paired evaluation.</p>
<h3>Direct SGLang-style progressive resolution does not transfer cleanly to H3</h3>
<p>The documented method starts at half spatial resolution, fills missing DCT frequencies with noise, and optionally rewinds the scheduler at the transition. It retains the same approximately 1.09× speedup on H3, but strongly changes the joint video-audio trajectory.</p>
<table><tr><th>prompt</th><th>method</th><th>window</th><th>speedup</th><th>SSIM</th><th>PSNR</th><th>LPIPS</th><th>outcome</th></tr>
<tr><td>red ball</td><td>documented DCT refill</td><td>[0,5)</td><td>1.093×</td><td>0.5101</td><td>9.86 dB</td><td>0.7256</td><td>reject</td></tr>
<tr><td>red ball</td><td>documented DCT + rewind</td><td>[0,5)</td><td>1.093×</td><td>0.4742</td><td>9.00 dB</td><td>0.7464</td><td>reject</td></tr>
<tr><td>raincoat dialogue</td><td>documented DCT refill</td><td>[0,5)</td><td>1.093×</td><td>0.3253</td><td>9.43 dB</td><td>0.7657</td><td>reject</td></tr>
<tr><td>raincoat dialogue</td><td>documented DCT + rewind</td><td>[0,5)</td><td>1.092×</td><td>0.3523</td><td>8.78 dB</td><td>0.7442</td><td>reject</td></tr></table>
<h3>Residual transport alone does not rescue an early window</h3>
<p>Starting from the same full-resolution noise, transporting its saved high-frequency residual, scaling it by σ-exit/σ-entry, and cosine-blending it back still fails at [0,5). Early low-resolution denoising changes H3's global video-audio trajectory before restoration.</p>
<table><tr><th>prompt</th><th>speedup</th><th>SSIM</th><th>PSNR</th><th>LPIPS</th><th>jitter ratio</th></tr>
<tr><td>red ball</td><td>1.093×</td><td>0.4820</td><td>11.42 dB</td><td>0.6739</td><td>1.3761</td></tr>
<tr><td>raincoat dialogue</td><td>1.091×</td><td>0.3644</td><td>11.40 dB</td><td>0.7265</td><td>0.2888</td></tr></table>
<h3>Four prompts × six seeds: middle residual with and without rewind</h3>
<p>These are 24 same-prompt, same-seed comparisons per arm (72 measured generations total). Runtime spread is across all four prompts and seeds 0–5.</p>
<table><tr><th>arm</th><th>E2E</th><th>speedup</th><th>SSIM</th><th>PSNR</th><th>LPIPS</th><th>sharpness ratio</th><th>jitter ratio</th><th>patch boundary</th></tr>
<tr><td>Dense</td><td>143.883 ± 0.129 s</td><td>1.000×</td><td>reference</td><td>reference</td><td>reference</td><td>reference</td><td>reference</td><td>reference</td></tr>
<tr><td>middle residual</td><td>131.747 ± 0.135 s</td><td>1.0921×</td><td>0.9285 ± 0.0167</td><td>31.99 ± 1.86 dB</td><td>0.0578 ± 0.0125</td><td>0.9861 ± 0.0190</td><td>0.9921 ± 0.0313</td><td>0.9953 ± 0.0142</td></tr>
<tr><td><b>middle residual + scheduler rewind</b></td><td><b>131.737 ± 0.144 s</b></td><td><b>1.0922×</b></td><td><b>0.9369 ± 0.0156</b></td><td><b>32.67 ± 2.10 dB</b></td><td><b>0.0499 ± 0.0121</b></td><td>0.9794 ± 0.0233</td><td><b>0.9995 ± 0.0416</b></td><td>0.9905 ± 0.0137</td></tr></table>
<p>Rewind improves SSIM on 23/24 pairs, PSNR on 18/24, LPIPS on 21/24, temporal delta error on 19/24, and distance-to-ideal jitter on 16/24. The non-rewind arm is closer to ideal sharpness on 14/24. Rewind changes mean loudness by +0.22 ± 0.35 LUFS and true peak by +0.08 ± 0.40 dBFS versus Dense.</p>
<div class='warn'><b>Decision status:</b> the non-rewind middle residual arm has a 6/6 human PASS on the original prompt. The rewind hybrid is the leading 24-pair automated-metric candidate, but the full multi-prompt human gate remains pending. FL2VA condition-row support and evaluation are also pending and are not represented as completed results.</div>
<h3>New review artifacts</h3><div class='videos'>
<section><h3>Red ball: all transition methods</h3><video controls preload='metadata' src='videos/p1_dense_official_dct_rewind_sigma.mp4'></video><p class='muted'>Dense · documented DCT · DCT+rewind · early residual · middle residual. Five selectable audio tracks.</p></section>
<section><h3>Raincoat dialogue: all transition methods</h3><video controls preload='metadata' src='videos/p2_dense_official_dct_rewind_sigma.mp4'></video><p class='muted'>Dense · documented DCT · DCT+rewind · early residual · middle residual. Five selectable audio tracks.</p></section>
<section><h3>Red ball: isolated rewind ablation</h3><video controls preload='metadata' src='videos/p1_middle_rewind.mp4'></video><p class='muted'>Dense · middle residual · middle residual+rewind. Three selectable audio tracks.</p></section>
<section><h3>Raincoat dialogue: isolated rewind ablation</h3><video controls preload='metadata' src='videos/p2_middle_rewind.mp4'></video><p class='muted'>Dense · middle residual · middle residual+rewind. Three selectable audio tracks.</p></section>
</div>
"""
if new not in s:
 s=s.replace(marker,new+marker)
location_marker="<h2>Completed modality and aggressive-window evaluation</h2>"
location_section=Path("location_section.html").read_text()
if location_section not in s:
 s=s.replace(location_marker,location_section+location_marker)
p.write_text(s)
