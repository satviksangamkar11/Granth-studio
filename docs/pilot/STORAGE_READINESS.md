# Storage readiness (2026-10-23): C: was full, D: is nearly full. INITIAL ASSESSMENT first (nothing deleted at that point); the scoped cleanup that followed is recorded at the end.

Measured: C: 292 GB total, 0.24 GB free; D: 9.6 GB free. Tests and git need free space on C: (the temp directory); an earlier full-suite run failed 14 tests with "GPU preflight not passed: disk fail" for this reason, and git-bash briefly failed to fork.

Largest items I could see (sizes measured, owners not changed):
| Location | Size | What it is | Suggested handling |
|---|---|---|---|
| `C:\ProgramData\Ableton`, `Arturia` | 11.3 GB, 6.2 GB | installed music software content | leave alone |
| `C:\Users\Satvik\Downloads` | 22.6 GB | personal downloads: an incomplete browser download `Unconfirmed 178721.crdownload` (2.53 GB, from 2026-08-08), music-plugin archives with extracted duplicates (Plug-ins zip 1.75 GB + its extracted folder 1.74 GB), installers (UVR 1.58 GB) | your files: your decision; the zip + extracted-folder duplicates and the abandoned `.crdownload` are the obvious candidates |
| `C:\Users\Satvik\.cache` | 6.05 GB | `huggingface` 1.85 GB, `whisper` 1.49 GB, `puppeteer` 1.35 GB, `codex-runtimes` 1.35 GB | re-downloadable caches; puppeteer is the safest, huggingface/whisper only if no other tool of yours needs them |
| `C:\Users\Satvik\AppData\Local\npm-cache` | 1.1 GB | npm download cache | safe to clear (re-downloaded on demand) |
| `C:\Users\Satvik\.claude`, `.codex` | 4.05 GB, 2.08 GB | session history of the coding assistants | do not touch |
| `C:\Users\Satvik\AppData\Local\Temp\claude` | 0.6 GB | this app's scratch for the running session | leave until the session ends |

Safe, no-permission measures I already use: pytest scratch on D: (`--basetemp D:\kaggle_upload\pytest_tmp`), deleted only my own earlier pytest temp directory; large model files and ComfyUI work go to Kaggle `/kaggle/temp`; only small verified evidence (clips, frames, receipts) is copied into the repository.

Smallest safe cleanup to ask for: npm-cache (1.1 GB) + puppeteer cache (1.35 GB) = about 2.5 GB, plus, if you agree, the abandoned `.crdownload` (2.53 GB) = about 5 GB. D: cannot absorb a relocation of Downloads (22.6 GB vs 9.6 GB free); an external drive or cloud folder would be needed for that.

Gate: no large download and no full local test run until you either free about 3-5 GB on C: or tell me to proceed with only the D:-based measures.

## Scoped cleanup executed 2026-10-23 (authorized: npm cache, Puppeteer cache and the abandoned August .crdownload, only after checking they are inactive)
- Free space on C: before 0.195 GB, after 4.081 GB.
- DELETED `C:\Users\Satvik\Downloads\Unconfirmed 178721.crdownload` (2 717 826 030 B; last written 2026-08-08, not locked, no browser download in progress) and `C:\Users\Satvik\.cache\puppeteer` (1 453 564 979 B; `chrome` and `chrome-headless-shell` from 2026-09-19; no file modified in the last 3 days, no process running from or using it).
- NOT DELETED: `C:\Users\Satvik\AppData\Local\npm-cache` (1.1 GB). The inactivity check FAILED: two running `node` processes (the Desktop Commander MCP server, started 2026-10-23 08:06 and 10:25) execute directly from `npm-cache\_npx\4b4c857f...`, npm logs inside it were written minutes before the check, and 524 files changed in the last 3 days. Deleting it would break those running tools. Only `_cacache` (0.34 GB) is plainly a download cache; `_npx` (0.76 GB) is in use. Nothing else was touched.
