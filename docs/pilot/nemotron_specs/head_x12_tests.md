# TASK: return ONLY ONE FILE: tests/test_stage1_aggregate.py (complete). Reply with exactly one block `FILE: tests/test_stage1_aggregate.py` then the python fenced. The MODULE scripts/pipeline/stage1/aggregate.py gained rule X12 (shown for reference below, do NOT return it); keep EVERY existing test unchanged (70 pass) and ADD tests for X12:
- ctx `voice_genders` is a dict voice_key -> 'male'|'female'. Base cast: narrator (voice_key narrator) and gajanan_maharaj (voice_key gajanan), both with gender 'male' in the base voices document.
- Mismatch: ctx voice_genders {"narrator": "male", "gajanan": "female"} -> exactly one X12 error that names `gajanan_maharaj` and `gajanan` (message `voices: <character_id> is <cast gender> but voice <voice_key> is <library gender>`), and the valid twin {"narrator": "male", "gajanan": "male"} -> no X12 error.
- Skips: a voice_key missing from voice_genders; a library gender that is not 'male'/'female'; a cast gender that is not male/female (use a copy of the voices document whose cast entry has gender 'female' while the library says 'male' ONLY in the mismatch test); voice_genders absent -> rule skipped.
- Robustness: voice_genders None, 5, 'x', ['a'], {'a': []}, {'gajanan': 5}, {1: 'male'} each -> a list, no exception and no 'internal error' in any message.
- The rule is skipped when the voices document fails its schema (corrupt it with plain assignment, e.g. docs['voices']['cast'] = 'x', and assert no X12 message and no exception).
Use copy.deepcopy and plain assignment; never a helper that rejects no-effect mutations; remember True == 1.

## CURRENT tests/test_stage1_aggregate.py
