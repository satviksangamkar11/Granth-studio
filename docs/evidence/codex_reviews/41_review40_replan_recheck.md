**MAJOR remains; no BLOCKER found.**

- **MAJOR — `scripts/pilot/make_reference_spec.py:12`**: Frozen negatives still omit CGI, shiny plastic skin, modern photography, harsh lens flare, neon colors and oil impasto. The generated spec at `docs/pilot/REFERENCE_LIBRARY_SPEC.md:18` incorrectly claims unchanged meaning. Restore these exclusions or explicitly include their removal in the proposed exception. The border exception is now disclosed, pending owner approval.

- **MAJOR — `scripts/pilot/render_motion_preview.py:76` / `scripts/animation/parallax.py:51`**: Parallax restarts each shot. At the first boundary, shift jumps from `+0.005` to `−0.008` despite identical camera windows—a 1.3% source-width discontinuity at depth extremes. Preserve displacement across adjacent shots and test boundary continuity.

- **MINOR — `scripts/animation/parallax.py:105`, `tests/test_parallax.py:63`**: Depths 0 and 1 receive equal displacement magnitude in opposite directions, contradicting “near things move more.” Increasing shift moves near content left because this is inverse sampling. Brightness differences do not verify direction or magnitude. Correct or document the intended mapping and test known feature coordinates.

- **MINOR — `scripts/animation/parallax.py:81`**: Relative paths bypass the confinement added to `motion.render`; `../a.png` remains accepted. Apply the same resolved-path check.

Prior three MINOR findings are closed by inspection. Generated spec matches its generator. No package dependency added; subprocess arguments avoid shell interpolation. Image-hash caching and border padding are present.

No files changed; no rendering, tests, GPU, downloads or network used. Cache reuse and rendered edge quality remain unverified.