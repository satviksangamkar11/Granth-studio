**Keep Blender v2 and reuse its existing builder. Don’t pay Kimi to recreate camera/zoom/motion code.** The older toolkit already handles eased camera moves and depth parallax, but Blender v2 covers substantially more of your requested motion.

I checked all **10 local Git branch refs**, repository code/docs/tests, and relevant folders under `D:/aai work`, `D:/local model`, and `D:/kaggle_upload`. No files changed.

1. **Existing Ken Burns / eased camera toolkit**
   
   [src/granthstudio/motion.py](</D:/aai work/granthstudio/src/granthstudio/motion.py:1>), with CLI wrapper `scripts/animation/motion.py`.
   
   Implements exact JSON-controlled pan, tilt and zoom; smoothstep/linear/hold easing; aspect cropping; bounded framing; 4× upscaling to reduce stepping. Already connected to Tier 0 in `src/granthstudio/pipeline.py:208`. The older `ffmpeg.py:130` supplies a simpler fixed push-in.
   
   **Windows evidence:** `D:/kaggle_upload/code_motion_v1/pilot_code_motion_preview.mp4`: **42.125 s, 1152×768, 24 fps**, nine shots. Its SHA-256 matches the saved report, verified during this inspection. CPU/FFmpeg rendering needs no GPU.
   
   **Gaps:** no independent character animation, dust, glow or layered transitions. No saved render-time or peak-RAM measurement found.

2. **Existing depth-map parallax**
   
   [scripts/animation/parallax.py](</D:/aai work/granthstudio/scripts/animation/parallax.py:1>).
   
   Uses **Depth-Anything-V2-Small on CPU**, cached depth maps, and PyTorch image warping combined with the existing eased camera path. Dependencies were accepted under D-012(e).
   
   **Windows evidence:** `D:/kaggle_upload/parallax_v2/pilot_parallax_preview.mp4`: another **42.125-second, 1152×768** output; hash matches its report. Three cached maps exist in `D:/kaggle_upload/depth_cache/`.
   
   **Gaps:** this bends one flattened picture; it cannot reveal hidden background or animate limbs. Large displacement stretches edges; the script limits shifts to ±2%. It remains a host script, outside the production pipeline’s motion path. No inference-time or peak-RAM receipt found. Its implementation uses no CUDA, so 6 GB VRAM is not a constraint.

3. **Current Blender builder v2 — the closest existing solution**
   
   [builder.py](</D:/kaggle_upload/v5_phase1_v2/builder.py:1>), rendered through [v5_blender.py](</D:/aai work/granthstudio/scripts/image_trials/v5_blender.py:1>).
   
   Already implements **perspective layer parallax, eased camera moves, bottom-anchored breathing, hanging sway, local soft deformation, pulsing halo, glow, drifting dust, vignette, slide and pan-bridge transitions**. These are reusable operations controlled by shot JSON.
   
   **Windows evidence:** `SA/gen1`, `SB/gen1`, `SC/gen1` each contain **144 PNG frames and a completed six-second MP4**, configured at **1280×720/24 fps**. Build logs identify **Blender 5.2.3 LTS**. First-to-last frame write intervals are approximately **101 / 248 / 284 seconds**—filesystem evidence, **not complete render benchmarks**.
   
   Exact builder approval is recorded for hash `eb996528…fa927ff`. Current v2 peak memory was not measured. An earlier, much simpler Blender proof in [p1_small/receipt.json](</D:/kaggle_upload/p1_small/receipt.json>) measured **2,412 MiB VRAM, 473 MiB process RAM and 4.8 seconds for 24 frames at 640×360**. That supports local feasibility, not v2 memory estimates.
   
   **Gaps:** visual acceptance of the richer motion remains unproven; static “SAFE TO EXECUTE” review is not quality approval. The runner deletes frame outputs and rerenders when invoked, rather than resuming completed chunks. `SB/gen2` also contains rejected JSON with an unsupported `soft_warp.ease` field.

4. **Earlier drawn-by-code / riso library**
   
   [dbc/engine/core.js](</D:/kaggle_upload/dbc/engine/core.js:1>), `engine/transitions.js`, `styles/risograph/riso.js`; working copy under `D:/kaggle_upload/riso_stage/`.
   
   Provides deterministic Canvas animation, camera transforms, eased keyframes, layers, seeded noise, perspective-like deformation and elaborate transitions. The existing Maharaj scene includes breathing, blessing, blink and halo animation.
   
   **Windows evidence:** `D:/kaggle_upload/riso_run3/maharaj_riso.mp4`; receipt records successful rendering. `round3_auto.md` reports **109 ms/frame warm painting at 960×960**, estimating 16 seconds for 144 frames. That is a painting estimate, not measured end-to-end encoding time.
   
   **Gaps:** no ready general-purpose V5 shot-JSON interpreter or complete approved character/action library. Returning here adds integration work and revives a look dropped by D-016.

5. **Additional reusable puppet prototype**
   
   [hybrid_rig.py](</D:/aai work/granthstudio/scripts/image_trials/hybrid_rig.py:1>) renders bounded rig JSON through SVG/resvg and FFmpeg.
   
   `D:/kaggle_upload/hybrid/rig_young2/receipt.json` records **73 frames, MP4 present, FFmpeg exit 0**. CPU-based and locally demonstrated. It handles parented parts, pivots and eased rotations, but needs suitable separated artwork and seam review. No resource benchmark found. It is currently untracked.

Tests exist in `tests/test_motion_toolkit.py`, `test_parallax.py`, `test_episode_output_size.py`, `test_v5_guards.py` and `test_hybrid_rig.py`. They cover useful geometry, continuity, validation and rig behaviour. **I did not find saved execution evidence establishing that these newer tests all passed.** No reusable FFmpeg `xfade`/cross-dissolve implementation surfaced; V5 v2 deliberately uses cuts/slides/pan bridges to avoid ghosted poses.

**Cheapest path:** freeze the existing Blender v2 builder, reuse approved art, and make reusable JSON presets for establishing shots, blessing poses, close-ups and transitions. Rendering those presets requires **zero Kimi tokens**. Keep the FFmpeg/depth toolkit as a simpler still-animation fallback; replacing Blender with it would require rebuilding the richer effects.

Kimi is technically optional even for planning: existing templates can supply routine shot JSON. If retained, use it for **compact, source-locked scene JSON and exceptional staging**, with builder changes only for a demonstrated missing capability. D-015’s Kimi-authorship rule is a recorded project choice, not a renderer requirement.

No new renders or tests were run; full-film quality, v2 peak memory and production recovery remain unverified.