# Codex review 1 — eight-fix re-review (FAIL, merge after specific fixes)

- **Origin:** verbatim output of `codex exec --sandbox read-only` (codex-cli 0.163.0) run from this session by Claude Code on 2026-10-22.
- **Reviewed range:** 6998608..fa32a5a
- **Prompt:** the 'FINAL EIGHT-FIX RE-REVIEW' brief (not stored in the repository)
- **Integrity:** the text below is unedited; Claude did not re-run or rewrite it.

---

**Verdict: FAIL. Merge readiness: 2 — MERGE AFTER SPECIFIC FIXES.**

F1 is resolved. The other corrections improve protection, but do not close all required scenarios. The live-owner lock takeover is a merge blocker.

**A. Reviewed evidence**

The last completed snapshot checks showed:

- Branch: `sprint/remaining-pipeline`.
- HEAD: `fa32a5aaff87357a245cd8987ac944a9a1943508`.
- Working tree: clean.
- BASE `6998608` is an ancestor of CANDIDATE.
- After code commit `8688853`, changes are limited to `PROGRESS.md`, `COVERAGE_MATRIX.md`, JUnit and its receipt. No subsequent source or test changes.
- Frozen architecture unchanged; SHA-256: `decd0af573e7b0c882d9dc5e8c98788bcecedd924a31dfc264ec1f883404f7c1`.
- JUnit SHA-256 matches the receipt: `985b06034c2a6f8287d588254e5248708582d9a5057327fc4a5e91b363c4c2ff`.
- JUnit records 297 tests: **295 passed, 2 skipped**, zero failures/errors.

No files were changed. The full suite was not rerun. Targeted Python probes did not complete and were stopped; findings below rely on source inspection and recorded evidence.

**B. Eight-finding matrix**

1. **F1 — FIXED.** Whole-footage coverage is required when a cutaway supplies the sole required action. Both assembly and resumed verification enforce it. Evidence: [episodes.py:210](<D:/aai work/granthstudio/src/granthstudio/episodes.py:210>), [pipeline.py:326](<D:/aai work/granthstudio/src/granthstudio/pipeline.py:326>), [pipeline.py:356](<D:/aai work/granthstudio/src/granthstudio/pipeline.py:356>).
2. **F2 — PARTIAL.** Seeds change through template substitution, but the protection checks the entire graph rather than the generation node’s inputs. The fake cache cannot detect this distinction. Evidence: [comfy.py:338](<D:/aai work/granthstudio/src/granthstudio/comfy.py:338>), [test_ltx_integration.py:46](<D:/aai work/granthstudio/tests/test_ltx_integration.py:46>).
3. **F3 — PARTIAL.** Attempt counts persist and polling does not consume them. The budget limit itself is not persisted; enforcement depends on every caller supplying it. Evidence: [comfy.py:317](<D:/aai work/granthstudio/src/granthstudio/comfy.py:317>), [comfy.py:342](<D:/aai work/granthstudio/src/granthstudio/comfy.py:342>).
4. **F4 — FAILED.** An aged lock can be stolen from a living owner. The displaced owner can continue writing and submitting. Evidence: [comfy.py:50](<D:/aai work/granthstudio/src/granthstudio/comfy.py:50>), [comfy.py:71](<D:/aai work/granthstudio/src/granthstudio/comfy.py:71>).
5. **F5 — PARTIAL.** Newly created stores receive distinct durable namespaces. Copies/restores preserve the same namespace without a concurrent-clone safeguard. Evidence: [comfy.py:33](<D:/aai work/granthstudio/src/granthstudio/comfy.py:33>), [runtime.py:295](<D:/aai work/granthstudio/src/granthstudio/runtime.py:295>).
6. **F6 — PARTIAL.** CLI execution paths gate readiness correctly. Direct scheduler execution does not universally enforce resource readiness; direct SDXL execution also lacks source-pin enforcement. Evidence: [runtime.py:174](<D:/aai work/granthstudio/src/granthstudio/runtime.py:174>), [pipeline.py:191](<D:/aai work/granthstudio/src/granthstudio/pipeline.py:191>), [keyframes.py:234](<D:/aai work/granthstudio/src/granthstudio/keyframes.py:234>).
7. **F7 — PARTIAL.** Static links/junctions and existing destination files are rejected. Parent-directory replacement remains possible between checking and opening. Evidence: [integrity.py:82](<D:/aai work/granthstudio/src/granthstudio/integrity.py:82>).
8. **F8 — PARTIAL.** Normal speech provenance survives approval and release; missing runner evidence remains unverified. Incremental translation can discard existing verification evidence, and stored identity is not bound to retained runner evidence. Evidence: [translation.py:60](<D:/aai work/granthstudio/src/granthstudio/translation.py:60>), [runners.py:62](<D:/aai work/granthstudio/src/granthstudio/runners.py:62>).

**C. Top three remaining risks**

1. Duplicate GPU submission after displacement of a living journal owner.
2. Outside-root reference writes during a junction/symlink swap.
3. GPU execution through direct scheduler paths despite failed resource readiness.

**D. Confirmed defects and minimum corrections**

**F4 — Critical: live-owner takeover permits duplicate submission.**  
Location: [comfy.py:69](<D:/aai work/granthstudio/src/granthstudio/comfy.py:69>), [comfy.py:325](<D:/aai work/granthstudio/src/granthstudio/comfy.py:325>).

Reproducible interleaving:

1. Process A acquires ownership and reads an absent or retryable journal.
2. A pauses for more than 300 seconds before persisting its new intent.
3. Process B renames A’s lock, acquires ownership, reads that same journal and submits.
4. A resumes using its previously read state, overwrites the journal and submits again.

The claim that persisted `submitting` always prevents duplication does not cover interruption **before** that write. A checks its owner token only during cleanup.

Reclamation also has a race between `stat()` and `os.replace()`: a contender can remove a replacement owner’s fresh lock. Attempting to restore it afterward does not preserve continuous exclusion.

**Minimal fix:** use ownership that remains exclusive while its process is alive and is released on process death; remove age-only takeover. Any reclamation/release must avoid replacing another owner’s lock.

**Regression:** two real CPU child processes; pause A after journal read, exceed the recovery threshold, start B, resume A. Assert one POST. Add interruption before/after POST and journal-write-failure cases.

**F2 — High: changed graph does not establish fresh generation.**  
Location: [comfy.py:338](<D:/aai work/granthstudio/src/granthstudio/comfy.py:338>), [test_ltx_integration.py:215](<D:/aai work/granthstudio/tests/test_ltx_integration.py:215>).

A workflow can retain a constant generation seed while placing `{{SEED}}` on an unrelated node. The retry changes the graph hash and passes the rejection guard, while generation inputs remain cached.

The regression fixture demonstrates the testing gap: `seeded()` adds node `3`, but the designated output remains connected to node `1`. The fake cache counts any whole-graph change as a new execution, so this disconnected seed passes its “fresh generation” assertion.

**Minimal fix:** validate an explicit seed/noise input on the generation dependency path to the designated output, and verify that input changes after rejection.

**Regression:** model cache reuse per node/dependency. Changing a disconnected node must neither establish fresh inference nor satisfy the retry gate.

**F6 — High: direct scheduler paths bypass readiness.**  
Location: [pipeline.py:430](<D:/aai work/granthstudio/src/granthstudio/pipeline.py:430>), [keyframes.py:424](<D:/aai work/granthstudio/src/granthstudio/keyframes.py:424>), [lipsync.py:92](<D:/aai work/granthstudio/src/granthstudio/lipsync.py:92>).

`gate_gpu_tasks()` is applied by entry-point wrappers. Direct `Scheduler.run(plan_tasks(...))` does not apply it. LTX’s own preflight checks source pins but not resource readiness. SDXL’s preflight checks its model/workflow configuration without enforcing either complete host readiness or source consistency.

Thus matching source pins with insufficient VRAM, missing session readiness or another failed resource check can still reach direct execution.

**Minimal fix:** enforce readiness in the GPU tasks’ own preflight/submission path.

**Regression:** matching pins plus an independently failed resource check, through direct LTX, SDXL and lip-sync scheduler execution. Assert zero submissions and blocked dependents.

**F7 — High: reference creation has a parent-directory race.**  
Location: [integrity.py:87](<D:/aai work/granthstudio/src/granthstudio/integrity.py:87>), [integrity.py:90](<D:/aai work/granthstudio/src/granthstudio/integrity.py:90>).

After the final component check, another process can replace an ancestor directory with a junction/symlink before `target.open("xb")`. Exclusive creation protects the final filename; it does not prevent following redirected parents.

The containment check at line 95 runs **after copying**. Deleting the destination afterward cannot undo an outside-root write. A similar swap before `mkdir()` can create outside-root directories before the next check rejects it.

**Minimal fix:** anchor creation to directory handles that cannot be redirected during the operation, with platform-appropriate reparse/link protection.

**Regression:** synchronize parent replacement immediately before directory creation and destination opening; assert no outside-root creation or write.

Interrupted copies are not registered as approved, which is correct. They can leave unregistered partial targets that block retry.

**F3 — Medium: the durable journal does not retain its budget limit.**  
Location: [comfy.py:317](<D:/aai work/granthstudio/src/granthstudio/comfy.py:317>), [comfy.py:342](<D:/aai work/granthstudio/src/granthstudio/comfy.py:342>).

After exhausting a limit, a reconstructed backend call that omits `max_attempts` uses `None`, disabling enforcement. Supplying a larger value also permits more attempts without `reset-budget`.

The built-in LTX/SDXL callers consistently supply limits, so a new unchanged scheduler instance does **not** itself reset their counts. The durable backend contract nevertheless remains bypassable.

**Minimal fix:** persist the established cap and retain it when callers omit the parameter. Require the authorized reset path to extend the budget.

**Regression:** exhaust the cap, reconstruct the backend, omit or increase the argument, and assert no POST.

The CLI reset correctly requires `--confirm`, a reviewer, one selected shot journal and a failed/rejected state. It records the reviewer and attempt baseline.

**F5 — Medium: copied stores can share submission identity.**  
Location: [comfy.py:33](<D:/aai work/granthstudio/src/granthstudio/comfy.py:33>), [runtime.py:277](<D:/aai work/granthstudio/src/granthstudio/runtime.py:277>).

Export/restore preserves `.store_namespace`. Two active copies therefore can have identical namespace, journal name, graph and attempt, producing identical tokens. Their local journal locks do not coordinate across directories, and reconciliation cannot distinguish the copies.

**Minimal fix:** preserve identity for genuine recovery while explicitly preventing concurrent active copies; an independent fork must receive a new identity with outstanding work handled deliberately.

**Regression:** restore/copy a store while the original remains active, then exercise submission and reconciliation from both.

**F8 — Medium: incremental translation loses verification evidence.**  
Location: [translation.py:59](<D:/aai work/granthstudio/src/granthstudio/translation.py:59>).

Verification is stored once for the entire candidate document. If an existing verified candidate is retained while a later batch supplies no evidence, line 61 changes the document identity to `unverified`. Approval of the unchanged earlier candidate then loses its actual verification evidence.

**Minimal fix:** retain identity evidence per candidate/run and carry the selected candidate’s exact evidence through approval and release.

**Regression:** generate a verified first candidate, incrementally add an unverified second candidate, and verify that both retain their respective evidence through release.

Stored-identity tampering is also only partially checked: `require_consistent_identity()` compares the block against model/revision fields in the same editable record. A fabricated matching `verified` block is accepted without consulting retained runner-response evidence. Bind identity to the exact request/result using the existing receipt mechanism and check that binding during approval and release.

**E. Specific verdicts**

- **Does cache rejection cause genuine fresh inference?** Not established. Unrelated graph changes satisfy the current guard and fake cache.
- **Can stale-lock takeover cause duplicate submission?** **Yes**, through the live-owner interleaving above.
- **Can retry budget reset unexpectedly?** Counts survive normal scheduler restart. Enforcement can disappear or expand through an omitted/increased backend cap.
- **Can an unready GPU task execute or appear successful?** Direct execution can bypass readiness. Where `not_validated` is assigned, downstream blocking and overall failure handling are correct.
- **Can references escape the artifact root?** **Yes**, during a parent-directory replacement race.
- **Can unverified identity appear verified?** Missing runner evidence stays unverified in normal flow. A forged matching stored block is not independently authenticated.

**F. Test credibility and preserved protections**

The receipt and JUnit are internally consistent and correspond to unchanged source/tests after `8688853`. They support the reported synthetic results, not complete closure.

- F1’s negative trimming checks are meaningful. Its resume assertion accepts either `resumed` or `failed`, weakening positive resume coverage.
- F2’s whole-graph cache and disconnected sampler cannot establish cache-aware inference.
- F3 tests always supply the cap.
- F4 tests use threads and a fabricated aged lock; they do not test a living displaced process.
- F5 tests cover newly initialized stores, not concurrent restored copies.
- F6’s direct-scheduler test fails source pins; it does not isolate resource-readiness bypass.
- F7’s Windows junction tests ran. The two skipped tests were symlink tests; symlink behavior remains unverified on this host. No replacement-race test exists.
- F8 tests cover complete batches and a mismatched revision, not mixed-evidence incremental generation or forged matching evidence.

Affected-path inspection found the existing research/source-hash gates, Marathi lock, Hindi review, snapshot-bound reuse, benchmark restrictions, independent FLF gate, human production GO and speech-duration protections retained. Ambiguous-submission recovery remains conservative under uncontested ownership; F4 breaks that ownership assumption.

**G–H. Minimum correction handoff**

Fix F4, F2, F6 and F7 before merge. Persist the F3 cap, define safe F5 clone handling, and preserve/bind F8 evidence. Add the focused regressions above, then regenerate the source-bound CPU evidence and correct the documentation’s closure claims.

**I. Remaining external gates**

Real ComfyUI cache behavior; exact checkpoint/hash/model-family and node-version compatibility; T4 resource and throughput measurements; GPU interruption recovery; real IndicF5/IndicTrans2 `_commit_hash` compatibility; bilingual quality review; independent FLF acceptance; and human production GO remain **NOT VALIDATED**.

No GPU, real model, download, production approval or historical architecture audit was performed.