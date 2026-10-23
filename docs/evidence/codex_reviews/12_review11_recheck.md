No blocking issue remains; a fresh painted gpu0 run may proceed.

- **MINOR — [.gitignore:25](D:/aai%20work/granthstudio/.gitignore:25):** The evidence exceptions still use `*.png`/`*.mp4`, admitting arbitrary files in `gpu0_attempt4`. Replace these with explicit filenames. This prior finding is only partially closed.

The other five findings are closed. Synthetic dry-run → painted execution correctly refuses mismatched inputs; painted gpu0 → retry with identical painted arguments remains accepted. Retry diagnostics, its screen check, `preview_retry`, shell copies, whitespace documentation and validator `samefile()` protection are present.

Input SSIM `None` or below `0.50` flags suspicion. Uncalibrated thresholds can falsely FAIL a good clip, but previews and the clip remain available and the shell copies evidence on FAIL.

Read-only mocked checks passed. The saved suite predates these fixes; media tests were not rerun. No modifications, GPU use or downloads.