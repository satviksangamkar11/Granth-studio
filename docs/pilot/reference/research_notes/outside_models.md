(OUTSIDE MODEL RECOMMENDATION pasted by the owner, 2026-10-26; claims NOT verified)
- z-ai/glm-5-3 (our reviewer) is retiring from NVIDIA NIM; swap to z-ai/glm-5-3-flash or deepseek-v4.1-flash.
- Nemotron 3 Ultra 550B has gateway timeouts on heavy reasoning and "multilingual token soup" with Devanagari + English JSON.
- Scene director: nvidia/nemotron-3.5-super-vl-120b-a12b (120B/12B active, 200-370 tok/s, reasoning off|medium|on, native image input) or Qwen3.6/3.8-27B (better Devanagari tokenizer); backup deepseek-v4.1-flash.
- Macro planner S1/S2: nemotron-3-ultra (RULER 95%) or deepseek-v4-pro, once per Adhyay.
- Reviewers: openai/gpt-oss-120b + z-ai/glm-5-3-flash or deepseek-v4.1-flash; repair with gpt-oss-120b.
- Translation Marathi->Hindi: IndicTrans2 1B indic-indic + glossary masking + Sarvam-Translate/Qwen polish; nvidia/riva-translate-4b-instruct-v2 on NIM.
- TTS: ai4bharat/indic-parler-tts (Apache 2.0, local/Kaggle) for scratch audio and duration measurement; Sarvam Bulbul V4 Flash (API, ~INR 140 per 1M chars, "ranked #1"); Azure mr-IN-AarohiNeural / hi-IN-MadhurNeural.
- Video: Wan 2.2 / Wan 2.1 FLF2V (first-last-frame), LTX-2.5; keyframes FLUX 3 Klein (NIM free) or Qwen-Image.
- Actions: swap GLM slug; test 3.5-super-vl on a 1-scene slice; do the 60-90 s bilingual storyboard with Indic Parler-TTS or the owner reading.
