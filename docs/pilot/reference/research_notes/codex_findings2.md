**Recommend (a): extend drawn-by-code with a small JSON-manifest interpreter and a fixed riso character library.** Use Rhubarb directly for mouth cues. None of the alternatives verified here supplies ready-made Maharaj/devotee rigs plus deterministic episode rendering from compact JSON.

Web access worked. Verification below covers repository documentation, selected source files and licences as checked **25 October 2026**; runtime performance remains **UNVERIFIED**.

| Claimed repository | Verified existence / licence | What it offers; rigs / JSON reality | Fit |
|---|---|---|---|
| [illodev/drawn-by-code](https://github.com/illodev/drawn-by-code) | Real; MIT code, asset exceptions | Canvas engine, riso drawing kit, Chromium/FFmpeg rendering, contact sheets. Scenes are functions of time; your rig/manifest layer remains to build. | **Keep** |
| [calesthio/OpenMontage](https://github.com/calesthio/OpenMontage) | Real; AGPL-3.0 | Broad production pipelines, tools, provider integrations and manifests. No verified ready-made riso human rig system. | Excess integration for this task |
| [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) | Real; Apache-2.0 | Deterministic HTML/CSS/JS video renderer and reusable motion components. No verified devotional character rigs or turnkey actor-manifest interface. | Strong alternative renderer; migration offers little immediate saving |
| [lemomo-ai/lemo-opuscar](https://github.com/lemomo-ai/lemo-opuscar) | Real; MIT | Style prompts, coded demonstration films and production guides. Reusable inspiration/source, not a verified parameterised human animation library. | Reference only |
| [JohnHeibel/ClaudeAnimationBase](https://github.com/JohnHeibel/ClaudeAnimationBase) | Real; MIT | **Actual reusable Clawd character**: views, expressions, mouths, limbs, acting helpers; p5.js/p5.brush renderer. Code-driven, not a ready Maharaj JSON rig. | Study rig design; replacement artwork still needed |
| [remotion-dev/remotion](https://github.com/remotion-dev/remotion) | Real; special Remotion licence | React video engine with [parameterised rendering](https://www.remotion.dev/docs/parameterized-rendering). JSON props work; characters/riso visuals remain custom. | Useful if you need React editing/composition |
| [iart-ai/motion-skills](https://github.com/iart-ai/motion-skills) | Real; MIT | Agent instruction packs and verification helpers, using other renderers. No verified reusable character engine. | Read selected guidance once |
| [smwbev/framewright](https://github.com/smwbev/framewright) | Real; MIT | HTML/canvas templates, seeded frame rendering, determinism checks, contact sheets. No verified recurring human rig library. | Borrow verification ideas |
| [ahujasid/blender-mcp](https://github.com/ahujasid/blender-mcp) | Real; redirects to `mcp-for-blender`; MIT | LLM control of Blender. The connector itself supplies neither your rigs nor a compact episode renderer. | Adds unnecessary tooling here |
| [JuneYaooo/cheap-claude-video](https://github.com/JuneYaooo/cheap-claude-video) | Real; Apache-2.0 | “Capsule Cinema”: reusable production recipes, cheaper-model reproduction and media-provider workflows. Recipes still involve generation; no verified deterministic riso rig system. | Similar cost-saving idea, different mechanism |
| [unclejobs-ai/motion-video-skill](https://github.com/unclejobs-ai/motion-video-skill) | Real; MIT | Production instructions, JSON editing/audio artifacts and QA gates. README explicitly says Remotion composition code is **not included**. | QA reference |
| [awesome-claude-video-skills](https://github.com/zhuyansen/awesome-claude-video-skills) | Found as `zhuyansen/...`; CC0 list | Directory of projects, not a renderer. Linked projects retain separate licences. | Discovery only |
| [DanielSWolf/rhubarb-lip-sync](https://github.com/DanielSWolf/rhubarb-lip-sync) | Real; MIT plus permissive dependencies | Audio → timestamped mouth shapes; JSON output. You supply the mouth drawings and playback mapping. | **Use directly** |

Licence details matter: drawn-by-code excludes rendered gallery media from its MIT grant and separately covers fonts/SFX. Reuse the engine and original character code rather than gallery outputs. Remotion’s current free eligibility includes individuals, nonprofits and for-profit organisations with up to three employees. [drawn-by-code licence](https://github.com/illodev/drawn-by-code/blob/main/LICENSE), [Remotion licence](https://github.com/remotion-dev/remotion/blob/main/LICENSE.md).

**The lowest-token production design**

The current [kimi_riso.py](</D:/aai work/granthstudio/scripts/image_trials/kimi_riso.py:146>) loads style/API/example documents, requests complete scene JavaScript and can request three full corrections. That is appropriate for developing the library, but expensive as the routine shot-production path.

Have **Kimi author once**:

- Maharaj young/mature rigs with approved proportions, clothing and face geometry; reusable devotee/villager variants.
- Front, three-quarter and side views; standing, seated, walking, namaskar, blessing, listening and speaking actions.
- Approved location/prop drawings and a small set of camera/composition templates.
- A strict manifest interpreter accepting IDs, timings and bounded parameters—no generated JavaScript or expressions in episode manifests.

A shot should reference something like `maharaj_mature`, `temple_courtyard`, `seated_blessing`, camera preset, speaker/audio IDs and source IDs. Keep geometry, palette, animation curves and texture rules inside the library.

**Rendering then needs zero LLM tokens.** If approved scene breakdowns already identify characters/actions, ordinary code can compile most manifests. Use one available free coding endpoint only for unresolved mapping or compact manifest drafting; send the schema, relevant registry entries and approved scene data—not engine source or every skill. Endpoint availability and quotas were not live-tested.

Determinism requires frame-indexed time, seeded texture, fixed asset/font/browser versions and no accumulating frame state. Cache accepted shots by manifest + rig + engine + audio hashes, and resume only matching outputs. Existing drawn-by-code already documents pure-time scenes and frame review, making this a small extension to a working base. [Engine documentation](https://github.com/illodev/drawn-by-code#how-it-works).

**Audio-first, with separate Hindi and Marathi timing**

1. Produce narration/dialogue from approved text using your existing TTS path; save audio per utterance with speaker/source IDs and measured duration.
2. Force-align the **approved transcript** to that audio. Use boundaries to place actions, cuts and subtitles; avoid replacing sacred text with ASR guesses.
3. WhisperX provides alignment infrastructure and a Hindi default model. Its inspected defaults contain **no Marathi model**: Marathi needs an explicitly selected, tested alignment checkpoint. Until then, measured utterance boundaries provide usable shot timing; Marathi word alignment remains **UNVERIFIED**. [Alignment source](https://github.com/m-bain/whisperX/blob/main/whisperx/alignment.py).
4. For visible speakers, run `rhubarb -r phonetic -f json …` on isolated speech and map cues to fixed mouth drawings. Its default recognizer is English; `phonetic` is language-independent but less precise. Narration should not automatically animate Maharaj’s mouth. [Rhubarb recognizers/output](https://github.com/DanielSWolf/rhubarb-lip-sync#recognizers).
5. Share rigs, locations, shot order and reusable motion between languages; calculate each release’s holds, timing, subtitles and speaking-mouth cues independently.
6. Make **one Nemotron vision call per manageable contact sheet**, including canonical reference thumbnails and labelled shot samples. Ask for identity, anatomy, attire, clipping and composition defects. Budget one sheet per finished minute initially. Sparse sheets cannot verify lip sync or every frame; add deterministic technical checks and inspect flagged motion.

Claude need not author any animation.

**Planning costs—not measured quotations**

Using **$2/M input and $10/M output** as the planning rate, matching the current [Vercel K3.1 Pro listing](https://vercel.com/ai-gateway/models/kimi-k3.1-pro):

| Work | Estimated tokens | Estimated model spend |
|---|---:|---:|
| Initial usable engine adapter + limited rig/action library + pilot corrections | 1–5M input; 0.5–2M billable output, including reasoning | **$7–30**; reserve **$15–60** for iteration |
| Manifest drafting per finished minute, assuming 8–12 shots | 5–15k input; 2–5k output | **$0 with your free endpoint**, or **$0.03–0.08 using Kimi** |
| Render an accepted manifest | **0** | **$0 LLM spend** |
| Contact-sheet QC | One image call; image-token usage **UNVERIFIED** | $0 under the supplied free-endpoint assumption |

Allow roughly **4–10 developer days** for that initial limited library and validation. This is an engineering estimate; all characters, exceptional gestures and locations across 21 films cannot be priced without their inventory.

Your observed **$1.40 per six seconds extrapolates to $14/minute**. With reusable rigs, routine model spend can approach zero; the remaining cost is TTS, CPU rendering, review and occasional new assets/actions. A $15–60 build amortised over 600 finished minutes adds **$0.025–0.10/minute**. No defensible all-inclusive dollar/minute estimate exists yet without TTS and render measurements.

**Free-T4 generative-video practicality**

| Model/project | Verified constraint / practical assessment |
|---|---|
| [Wan2.2](https://github.com/Wan-Video/Wan2.2) | Official 5B 720p example requires ≥24GB VRAM. A stock 16GB T4 misses that requirement; optimised variants need separate verification. |
| [VACE](https://github.com/ali-vilab/VACE) | Real reference/video/mask conditioning; 1.3B variant is the plausible experiment. T4 speed, fit and riso identity retention **UNVERIFIED**. |
| [FramePack](https://github.com/lllyasviel/FramePack) | Claims 6GB memory capability, but documented hardware targets RTX 30/40/50-series. T4 support/performance **UNVERIFIED**; low memory does not imply fast generation. |
| [SkyReels-V2](https://github.com/SkyworkAI/SkyReels-V2) | Reports ~14.7GB peak for 1.3B at 540p: little T4 headroom. Runtime and recurring-character quality **UNVERIFIED**. |
| [LTX-Video](https://github.com/Lightricks/LTX-Video) | Small 2B variants are plausible experiments. Exact checkpoint/workflow matters; its optional FP8 kernels target Ada or later. T4 acceptance **UNVERIFIED**. |
| [StoryDiffusion](https://github.com/HVision-NKU/StoryDiffusion) | Character-consistent image research; documented low-memory demo expects >20GB. Poor direct fit for stock T4 episode production. |
| [Sonic](https://github.com/jixiaozhong/Sonic) | Audio-driven portrait animation; official testing used 32GB GPU. T4 and riso performance **UNVERIFIED**. |
| [EchoMimicV2](https://github.com/antgroup/echomimic_v2) | Audio/pose-driven semi-body animation; tested on V100 16GB among other GPUs. That does not establish T4 throughput or Hindi/Marathi riso quality. |

My assessment: these are optional experiments, while fixed rigs give much stronger control over recurring identity and print texture. None establishes the proposed low-token riso episode pipeline.

No files changed or workloads executed. Build estimates, Marathi alignment, endpoint quotas and actual cost per accepted minute still require a representative pilot.