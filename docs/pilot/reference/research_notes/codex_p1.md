**Not safe for the first paid run.** The AST guard permits arbitrary host access, and the ledger does not guarantee the advertised caps.

1. **BLOCKER — process, filesystem and network access.** [v5_blender.py:39](<D:/aai work/granthstudio/scripts/image_trials/v5_blender.py:39>)  
   `from random import _os as o; o.system("...")` passes `check()` unchanged. I confirmed Blender’s bundled Python exposes `random._os`. This permits shell commands, file access and network clients. Dynamic paths assembled with `chr(47)` bypass the string filter.  
   **Fix:** require review before execution and run generated code under OS-enforced restrictions: no network, no secret access, read-only assets, writes limited to the shot directory. Additional banned names cannot make this a sandbox.

2. **BLOCKER — Blender itself bypasses the restrictions.** [v5_blender.py:43](<D:/aai work/granthstudio/scripts/image_trials/v5_blender.py:43>)  
   These all passed the guard:
   - `bpy.data.images.load(ASSET("sky")).save_render(ASSET("sky"))` — can overwrite an approved asset.
   - `bpy.ops.render.render(write_still=True)` — writes during build.
   - `bpy.data.path_resolve("texts").new("p")` followed by `.write(...)` and `.as_module()` — bypasses `.texts` filtering.
   - `bpy.data.path_resolve("libraries").load(...)` — bypasses `.libraries`.
   - `from bpy import utils as u; u.register_class(C)` — bypasses `.utils`.
   - Creating `"ShaderNodeScript"` and assigning `.filepath` also passes; actual OSL execution depends on the engine.

   **Fix:** enforce filesystem isolation and allow only explicitly reviewed operations. Blender documents both [`save_render`](https://docs.staging.blender.org/api/current/bpy.types.Image.html) and [render writes/external-player execution](https://docs.blender.org/api/main/bpy.ops.render.html).

3. **BLOCKER — key confidentiality is not established.** [v5_blender.py:89](<D:/aai work/granthstudio/scripts/image_trials/v5_blender.py:89>), [v5_shots.py:193](<D:/aai work/granthstudio/scripts/image_trials/v5_shots.py:193>)  
   The API wrapper does not directly print the key. However, a guard-passing `_os.open`/`fdopen` script can read its known disk location and print it into `build_log.txt`; failure feedback then sends that log to Kimi. Environment sanitisation does not prevent this.  
   **Fix:** deny the Blender identity access to secrets; redact logs before storage and feedback as defence in depth.

4. **MAJOR — reservations are estimates, not worst-case bounds.** [v5_ledger.py:21](<D:/aai work/granthstudio/scripts/image_trials/v5_ledger.py:21>)  
   `characters // 3 + 1500/image` ignores message overhead and has no demonstrated upper bound for code, Unicode or image tokens. Settlement can exceed the reservation after money is spent.  
   **Fix:** count the exact submitted multimodal payload using the provider’s [token-count endpoint](https://platform.kimi.ai/docs/api/estimate), with documented conservative treatment of any remaining uncertainty; refuse when counting fails.

5. **MAJOR — blanket 4xx settlement releases uncertain spend.** [v5_shots.py:110](<D:/aai work/granthstudio/scripts/image_trials/v5_shots.py:110>)  
   HTTP 400 includes filtering of **model output**, according to [provider documentation](https://platform.kimi.ai/docs/api/errors). Therefore, “rejected before generation; bills nothing” is unsupported.  
   **Fix:** retain UNKNOWN unless the specific error has verified zero-billing semantics. Do not infer zero cost solely from HTTP status.

6. **MAJOR — concurrent callers can exceed caps; reservations lack crash durability.** [v5_ledger.py:53](<D:/aai work/granthstudio/scripts/image_trials/v5_ledger.py:53>), [v5_ledger.py:71](<D:/aai work/granthstudio/scripts/image_trials/v5_ledger.py:71>)  
   An in-memory interleaving reproduced two successful reservations taking P1 from `$14.50` to `$15.140004`. Checking and appending are unlocked. `flush()` also lacks `fsync()` before dispatch.  
   **Fix:** hold an interprocess lock across check-and-append and durably sync before sending. UNKNOWN retention itself is correct.

7. **MAJOR — render verification and review gates are incomplete.** [v5_blender.py:103](<D:/aai work/granthstudio/scripts/image_trials/v5_blender.py:103>), [v5_shots.py:189](<D:/aai work/granthstudio/scripts/image_trials/v5_shots.py:189>)  
   PNG existence and ffmpeg exit status do not establish exactly 48 decoded frames per chunk or 144 in the final clip. There is no disk preflight. Generated versions execute immediately without the required Codex review; restarting also resets the four-generation limit and overwrites round artifacts.  
   **Fix:** decode/count chunks and final output, enforce storage preflight, and persist generation counts plus an approval bound to each script hash.

Read-only review completed. Guard probes were checked without executing their payloads. I inspected the smoke build log; I did not independently verify its 57-second timing, decoded frame count, or rerun the 22 filesystem-writing tests.