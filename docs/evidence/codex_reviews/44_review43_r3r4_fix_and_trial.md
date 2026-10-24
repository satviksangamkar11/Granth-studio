Blocking issues remain.

- **MAJOR — `scripts/image_trials/nvidia_trial.py:129,162`: credential forwarding on redirects.** Default urllib redirects copy the `Authorization` header, including across hosts or HTTPS→HTTP. Refuse redirects or strictly enforce the approved HTTPS origin before forwarding credentials.

- **MAJOR — `scripts/image_trials/nvidia_trial.py:125–132`: keys can enter exception text.** An environment value containing a valid key followed by an embedded newline and extra text reaches urllib unchanged. Local Python’s `http.client` raises `ValueError` containing the full header value; this escapes uncaught. Validate key syntax and emit secret-free errors in both request paths.

- **MAJOR — `scripts/image_trials/nvidia_trial.py:159–166`: `check-key` violates the fallback rule.** It requests every key after success, 429, or 500 and ultimately returns zero. Stop after success or any status other than 401/403; return failure on 429.

- **MAJOR — `scripts/image_trials/nvidia_trial.py:89–91,214`: response bytes bypass secret protection.** A response whose image field contains base64-encoded key text is decoded and saved verbatim as `.png`. The existing test checks only receipt redaction. Validate image responses and reject secret-bearing output before writing.

- **MINOR — `src/granthstudio/ffmpeg.py:117`: odd square-pixel images are stretched.** A 65×64 image with SAR 1 becomes 64×64 before fitting because of `trunc(iw*sar/2)*2`. Preserve display geometry when normalizing dimensions; add an odd-width regression.

- **MINOR — `tests/test_episode_output_size.py:84–90,94–102`: prior coverage remains incomplete.** Anamorphic coverage exercises only `cover`; the still test still checks dimensions alone. Add anamorphic `pad` and a geometry comparison for the still-rendering path.

Prior camera/pad and timeout findings are addressed statically. No circular import found; `TaskFailed` reaches scheduler retry handling. Independent clip crop/pad references improve the earlier weak assertions. Requests use fixed local reference paths and frozen-style composition, and the receipt explicitly labels field names unverified.

Static review only. No matching executed evidence found for these new tests; no files changed, tests/media/GPU run, downloads, or network access.