MAJOR issues remain:

- **MAJOR — [pipeline.py:207](/D:/aai%20work/granthstudio/src/granthstudio/pipeline.py:207):** Camera shots ignore `output.fit`. With `fit: pad`, a 16:9 still and a held camera rendered at 3:2 are centre-cropped by `motion.video_filter`; assembly cannot restore the discarded edges. Pass and honour the configured fit.

- **MAJOR — [ffmpeg.py:118](/D:/aai%20work/granthstudio/src/granthstudio/ffmpeg.py:118):** Conforming does not preserve display aspect for non-square-pixel sources. For example, 720×576 with SAR 16:15 is fitted using pixel dimensions, then `setsar=1` discards its display correction, distorting the picture. Normalize using display aspect before fitting; cover both fit modes with an anamorphic fixture.

- **MAJOR — [motion.py:121](/D:/aai%20work/granthstudio/src/granthstudio/motion.py:121):** The newly integrated camera renderer calls `subprocess.run` without a timeout. A stalled FFmpeg blocks the scheduler indefinitely, bypassing the existing 300-second media timeout and retry handling. Use the bounded media execution path.

- **MINOR — [test_episode_output_size.py:57](/D:/aai%20work/granthstudio/tests/test_episode_output_size.py:57):** The “cropped not stretched” assertion checks dimensions only; a stretched render passes. Compare image geometry against crop and stretch references.

Static review only; no modifications, tests, media probes, GPU, downloads, or network access.