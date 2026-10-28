# Haiku final read-only review: Stage 1 aggregate and context

Scope: `scripts/pipeline/stage1/aggregate.py` (rules X1, X3-X11) and `scripts/pipeline/stage1/context.py` (spec `docs/pilot/nemotron_specs/context.md`). Read-only; no file edited except this report. No network. `secrets` not opened.

## Test run
`uv run pytest -q --tb=short -p no:cacheprovider tests/test_stage1_*.py`: 575 passed in 0.95s.

## Checks run (in-memory, on the live files, base `docs/pilot/nemotron_specs/stage1_base.json`)
- Base document set with base ctx: `validate_all` returns `[]`.
- X1 kind-aware: STORY ovi 1 covered only by a discourse event -> `story_map: ovi 1 is typed STORY but is in no story event`. TEACHING ovi 6 covered only by a story event -> `story_map: ovi 6 is typed TEACHING but is in no discourse event`. PASS.
- X2 removed: owner-approved omission of STORY ovi 1 (PROPOSE_OMISSION + unfilmed_ovis [1]) gives no `omission is proposed` error. PASS.
- X3: proposal not approved -> `coverage: ovi 3 omission is not approved by the owner`; approved unfilmed with no proposal -> `coverage: ovi 9 is approved as unfilmed but has no omission proposal`. PASS.
- X4: VISUALISED ovi 2 in no shot -> error; ovi 5 in no scene -> error. PASS.
- X5: key ovi 3 of E1 outside scenes -> error. PASS.
- X6: ambiguous E1 with question only on a non-overlapping scene -> `story_map: ambiguous event E1 has no question`. PASS.
- X7 recurring: gajanan_maharaj assigned to a different voice -> `voices: recurring character gajanan_maharaj has a different voice than the series`. X7 NEW_PROPOSED already having a series voice -> error. X7 NEW_PROPOSED reusing a series voice -> `voices: character narrator reuses the series voice gajanan`. PASS.
- X8: 6-word run copied from a `script_texts` entry into `looks` -> `looks: free text copies script wording (entries/0/look)`. PASS.
- X9: E2 range outside chapter_ovis -> error; key ovi 7 outside chapter_ovis -> `story_map: key ovi 7 of event E2 is outside the chapter`. PASS.
- X10: scene S1 section_kind discourse over story-only events -> `scenes: scene S1 is discourse but its events are not discourse`. PASS.
- X11: verified_voices without gajanan -> `voices: voice gajanan is not verified for Marathi and Hindi`. PASS.
- Wrong-typed ctx (None, list, int, str, dicts/lists/None inside chapter_ovis, unfilmed_ovis, verified_voices, script_texts, known_states): no raise. Sentinel `aggregate: internal error` appears for one case, see defect A1.
- Wrong-typed docs (None, list, scalars, `story_map: None`): no raise.
- Context: real root adhyay 1 -> 35 saved voices, 9 verified, 4 series, `01_establishing_shot` in preset_ids, problems `[]`. Invalid adhyay (0, 22, True, "x") -> `({}, ["adhyay must be an int in 1..21"])`. Missing root -> problems `source_ovis: missing`, `voice_library: missing`, `presets: missing`, empty values, no raise. Extra non-dict ignored; extra dict overrides (script_texts, unfilmed_ovis). Omissions with approved sha -> ovis `[3, 4]` (non-int items dropped), no problem. Stale sha -> `[]` with `omissions: STALE ...`. Approvals missing -> `[]` with `omissions: DRAFT ...`. Absent omissions file -> `[]`, no problem. Approvals record compared by sha256 as required.

## aggregate.py
1. `aggregate.py:304` `series_voice_keys = set(series_voices.values())`. When a `ctx.series_voices` value is unhashable (for example `{"a": [1]}`), this raises inside the X7 try block and the sentinel `aggregate: internal error in X7` is emitted. The prompt says the sentinel must NOT appear for wrong-typed ctx values. Verified: `validate_all(1, base_docs, {... "series_voices": {"a": [1]}})` returns `['aggregate: internal error in X7']`.
   Fix: `series_voice_keys = {v for v in series_voices.values() if isinstance(v, str)}`.

Blocking defects for aggregate: 1.

## context.py
1. `context.py:78-80` `_read_omissions`: `omissions_data.get("ovis", [])` runs outside any try. A top-level JSON list or null raises `AttributeError`. `build_ctx` (line 233) does not guard the call, so `build_ctx` raises. Verified: `_read_omissions` on `[1,2]` and on `null` raises. Violates "NEVER raises".
   Fix: after the json load, `if not isinstance(omissions_data, dict): problems.append("omissions: not an object"); return [], problems`.
2. `context.py:123` `_read_voice_library`: `data.get("voices", [])` with a non-dict top-level JSON raises `AttributeError`, which `build_ctx` (line 238) does not catch. Verified: `_read_voice_library` on `[1,2]` raises. Violates "NEVER raises".
   Fix: `if not isinstance(data, dict): problems.append("voice_library: not an object"); return {}, {}, [], problems`.
3. `context.py:44-59` `_read_ovis`: a JSON line that is not an object (`null`, `[1]`) passes `json.loads`, then `obj.get` raises inside the outer try. The whole loop aborts with `source_ovis: AttributeError`, so later valid lines are dropped. Spec requires `source_ovis: bad line <n>`, skip, and continue. Verified: input `{"ovi":1}\n[1]\n{"ovi":2}` returns `[1]` (ovi 2 lost). Fix: after `obj = json.loads(line)`, add `if not isinstance(obj, dict): problems.append(f"source_ovis: bad line {i}"); continue`.

Blocking defects for context: 3.

## Non-blocking notes
- `aggregate.py` X9 wording and X8 messages are fine. The X8 message uses `looks: free text copies script wording (entries/0/look)`; no change needed.
- With an owner-approved omission of a mid-range ovi, the coverage unit emits `note: ovi 3 omission proposed, owner approval needed` and the scenes unit emits `S1: ovi 3 is unfilmed but inside the range`. These come from the coverage and scenes units, not from X1-X11, and the X2 check (no `omission is proposed` error) passes. Whether an approved omission may sit inside a scene range is a scenes-spec question for the owner; not a blocker here.
- `_read_presets` and `_read_sound_palette` silently skip non-dict items; acceptable under the spec.
- Schema enum and bound gaps were not raised as blockers, per the STOP RULE.

## Verdict per unit (BLOCKING)
- aggregate: 1
- context: 3

## Verdict: FIX FIRST
