Blocking issues remain:

- **MAJOR — `src/granthstudio/keyframes.py:176`**: Only full canonical names of participating characters/locations are checked. `"Gajanan sits by Devidas's house"` passes: aliases are ignored, and Devidas is absent from Scene 1’s character list. Research labels such as `"Source detail:"` also pass directly into conditioning. Validate aliases, possessives and prohibited bookkeeping text before composing. Use name boundaries to avoid substring false positives; current tests cover only an exact canonical name.

- **MAJOR — `scripts/pilot/build_pilot_project.py:129`**: Scene 1 places the clay pipe beside him, contradicting `research()` at line 73, which specifies the chilam **in his hand**. Restore that placement and regenerate the manifest.

- **MINOR — `scripts/kaggle/sdxl_first_test.sh:24`**: The regex accepts invalid configurations such as CFG `0`, duplicate `7,7`, or six seeds × four CFGs. Python eventually refuses these, but only after downloads and GPU startup. Apply the existing range, uniqueness and image-count limits before provisioning.

Other checks: both frozen style files have identical Git blobs across HEAD/parent; composition still uses `style.compose`, with unchanged negative text. Identities, reference records and fact IDs remain in requests. Missing descriptions retain the previous prompt behavior; description edits affect request hashes/task inputs and are covered by drift checks. Bash defaults remain four seeds and `6.5,9.0`; the validation constructs are compatible with `set -e/-u`. The audit separates the two failures and marks chunk weakening unproven.

Read-only inspection; no test suite, GPU, downloads or network run. Fix the MAJOR findings before authorizing the pinned SDXL experiment.