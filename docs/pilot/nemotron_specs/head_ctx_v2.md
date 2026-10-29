# TASK: return ONLY ONE FILE: scripts/pipeline/stage1/context.py (complete). Reply with exactly one block `FILE: scripts/pipeline/stage1/context.py` then the python fenced. Keep everything that works; ADD ONE ctx key (checklist V2).
Change: `build_ctx` also returns `voice_genders`: a dict voice_key -> gender for every voice library entry whose `voice_key` is a string and whose `gender` is the string 'male' or 'female' (other entries are left out). It comes from the same guarded library read as `saved_voices`; a missing or bad library gives {} (the existing library problems stay). It is part of the returned ctx dict like the other keys (an `extra` override still wins). Nothing else changes; it must never raise.

## CURRENT scripts/pipeline/stage1/context.py
