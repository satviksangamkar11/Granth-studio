Web access worked. I checked repository READMEs and licence files; **hardware fit below is my assessment, not a tested installation**.

**My recommendation: build recurring characters as reusable rigs, then animate and assemble shots through code.** Blender and Synfig are the strongest foundations. AI identity tools can supplement them, but do not provide the same control over costumes, hands, expressions, and continuity.

Kaggle’s current practical baseline is **T4 ×2, with 16 GB per GPU**; that does not automatically become one 32 GB GPU. Kaggle announced P100 retirement for September 15, 2026. ([Kaggle announcement](https://www.kaggle.com/product-announcements/735239))

“Preview” links below point directly to images/GIFs embedded by the repository. Where I could not verify a suitable preview, I say so rather than inventing one.

**Code-driven 2D rigs and puppets**

These generally **animate supplied artwork**; they do not generate a finished human design themselves.

- **[Inochi2D](https://github.com/Inochi2D/inochi2d)** — **BSD-2-Clause SDK**. Deforms layered artwork into expressive puppets; use [Inochi Creator](https://github.com/Inochi2D/inochi-creator) for rigging. Good for recurring illustrated characters, especially dialogue. **Windows:** good through its authoring tools; SDK integration needs work. **Kaggle:** little benefit. [Creator preview](https://user-images.githubusercontent.com/7032834/194462402-74c4a3e0-50ca-4b50-8e8d-164d97371f5a.png).

- **[DragonBonesJS](https://github.com/DragonBones/DragonBonesJS)** — **MIT runtime**. Skeletal animation, reusable movements, interchangeable character parts, JavaScript control. Good for economical full-body storytelling. **Windows:** browser/PixiJS/Phaser route fits well. **Kaggle:** unnecessary. Runtime availability does not establish an entirely open-source editor workflow. [Preview](https://dragonbones.github.io/demo/demos.jpg).

- **[Spine runtimes](https://github.com/EsotericSoftware/spine-runtimes)** — **custom Spine licence; not unrestricted open source**. Strong skeletal animation and skins, but production use has Spine licensing conditions. **Windows:** excellent technical fit. **Kaggle:** unnecessary. **Preview:** no suitable directly embedded image verified in the inspected READMEs. ([Licence explanation](https://github.com/EsotericSoftware/spine-runtimes/blob/4.2/README.md))

- **[Synfig](https://github.com/synfig/synfig)** — **GPL-3.0**. Complete vector/bitmap animation application with bones, interpolation, editable scene files, and command-line rendering. Strong candidate for complete illustrated films; procedural scene generation requires integration work. **Windows:** good. **Kaggle:** possible headless rendering, usually little advantage. **Preview:** no output preview found in the main README.

- **[Rive runtime](https://github.com/rive-app/rive-runtime)** — **MIT runtime**. Vector rigs, state machines, and programmatic animation inputs. Useful for expressive reusable characters; film sequencing/export needs an additional layer. Its editor is a separate proprietary product. **Windows:** good. **Kaggle:** unnecessary. **Preview:** main README shows a [logo](https://cdn.rive.app/rive_logo_dark_bg.png), not an animation-output preview.

- **[Lottie-web](https://github.com/airbnb/lottie-web)** — **MIT**. Plays JSON vector animations through SVG/canvas. Useful for simple puppets, decorative motion, titles, and scene overlays; not a human generator or complete film system. The usual After Effects authoring workflow is proprietary. **Windows:** good browser fit. **Kaggle:** unnecessary. [Preview GIF](https://raw.githubusercontent.com/airbnb/lottie-web/master/gifs/Example1.gif).

- **[Animated Drawings](https://github.com/facebookresearch/AnimatedDrawings)** — **MIT code and model weights**. Converts supplied human drawings into deformable characters, applies motion, and exports MP4 through configuration files. Strong proof that reusable drawn characters can be animated through code. **Windows:** less straightforward; upstream tested Ubuntu/macOS. **Kaggle:** plausible with headless OpenGL setup. **Archived/unmaintained.** [Preview GIF](https://user-images.githubusercontent.com/6675724/219223438-2c93f9cb-d4b5-45e9-a433-149ed76affa6.gif).

**Parametric human generation**

- **[MakeHuman](https://github.com/makehumancommunity/makehuman)** — **AGPL-3.0 code; bundled character assets CC0**. Generates human bodies from reusable bases and numerical parameters, with export for animation. Particularly useful for a permanent cast. **Windows:** good; combine with Blender. **Kaggle:** character creation gains little; subsequent rendering may benefit. **Preview:** none in the main README. The repository explicitly distinguishes bundled assets/output from separately licensed community assets. ([Licence](https://github.com/makehumancommunity/makehuman/blob/master/LICENSE.md))

- **[MB-Lab](https://github.com/animate1978/MB-Lab)** — **GPL-3.0 code; AGPL character database/models**, with a stated exception allowing ordinary rendered images/videos to use other licences. Parametric humans inside Blender. **Windows:** viable with a compatible Blender version; README targets Blender 4.0+, lists BVH/hair issues, and says development moved to [CharMorph](https://github.com/Upliner/CharMorph). **Kaggle:** potential batch rendering after setup. **Preview:** none in the current main README. ([Licence](https://github.com/animate1978/MB-Lab/blob/master/license.txt))

- **[UniVRM / VRM](https://github.com/vrm-c/UniVRM)** — **MIT implementation; individual avatar licences vary**. VRM is an avatar format, **not a human generator**. Provides reusable humanoids, expressions, and animation exchange in Unity. **Windows:** good. **Kaggle:** poor authoring fit. **Preview:** no character-output image in the main README. VRoid Studio can author VRM characters, but is not open source.

- **[SMPL-X](https://github.com/vchoutas/smplx)** — **non-commercial scientific-research licence**, not general-purpose open source. Numerical body, face, and hand model; useful for pose/motion research, not a production-ready clothed actor generator. **Windows/Kaggle:** technically plausible with PyTorch; licence makes it unsuitable as the default film foundation. [Preview](https://raw.githubusercontent.com/vchoutas/smplx/main/images/teaser_fig.png). ([Licence statement](https://github.com/vchoutas/smplx#license))

- **[Universal LPC Character Generator](https://github.com/LiberatedPixelCup/Universal-LPC-Spritesheet-Character-Generator)** — **GPL-3.0 code; artwork has per-asset CC0/CC-BY/CC-BY-SA/OGA-BY/GPL licences**. Actual paper-doll human generation: combine bodies, hair, clothes, equipment, and animation sheets. Excellent consistency, visibly pixel-art style. **Windows:** good browser fit. **Kaggle:** unnecessary. [Preview](https://raw.githubusercontent.com/LiberatedPixelCup/Universal-LPC-Spritesheet-Character-Generator/master/readme-images/example.png).

**Story pipelines and LLM-written animation code**

- **[Blender](https://github.com/blender/blender)** — **GPL-3.0-or-later**. The most complete option here: Python can build scenes, manipulate human meshes, drive rigs, animate cameras, render shots, and assemble films. It still needs good character assets and animation direction. **Windows:** excellent. **Kaggle:** plausible for headless rendering; benchmark representative scenes first. [Repository preview](https://code.blender.org/wp-content/uploads/2018/12/springrg.jpg).

- **[MCP for Blender, formerly Blender MCP](https://github.com/ahujasid/blender-mcp)** — **MIT integration; Blender retains its own licence**. Lets an LLM execute Blender Python and inspect the scene, including animation and rigging. A useful coding assistant, not a finished autonomous filmmaker. **Windows:** explicitly supported. **Kaggle:** interactive bridge is a poor fit; generated scripts can potentially render separately. Optional asset/model services may cost money. [Interface preview](https://raw.githubusercontent.com/ahujasid/blender-mcp/main/assets/codex-screenshot.png).

- **[Manim Community](https://github.com/ManimCommunity/manim)** — **MIT**. Precise Python animation, excellent for narration, scripture explanations, diagrams, and simple SVG/paper-doll characters. Detailed acting requires custom character code. **Windows:** good after dependencies. **Kaggle:** plausible CPU rendering; GPU usually unnecessary. **Preview:** main README supplies a [logo](https://raw.githubusercontent.com/ManimCommunity/manim/main/logo/cropped.png), not a character-animation preview.

- **[Remotion](https://github.com/remotion-dev/remotion)** — **custom source-available licence**, free under specified individual/small-company/nonprofit conditions. React code defines animation and complete video timelines; useful for puppets, narration, captions, and editing. **Windows:** good. **Kaggle:** possible headless Chromium setup, but local use is simpler. [README animation—logo only](https://raw.githubusercontent.com/remotion-dev/logo/main/animated-logo-banner-light.gif). ([Licence](https://github.com/remotion-dev/remotion/blob/main/LICENSE.md))

- **[StoryDiffusion](https://github.com/HVision-NKU/StoryDiffusion)** — **Apache-2.0 code; underlying model terms also apply**. Generates related story images/comics using consistent attention. The paper and README show video results, but the documented runnable workflow chiefly covers comics; do not assume a complete released movie pipeline. **Windows:** possible CUDA setup. **Kaggle:** constrained—the documented low-memory version expects **over 20 GB VRAM**, tested at 24 GB. [Preview](https://github.com/HVision-NKU/StoryDiffusion/assets/49511209/b3771cbc-b6ca-4e26-bdc5-d944daf9f266).

- **[MovieAgent](https://github.com/showlab/MovieAgent)** — **licence not found in the inspected repository**; cannot certify open-source reuse rights. Plans scenes/shots from scripts and character banks, then orchestrates image/video models. Relevant research, but still dependent on generative shots and external LLM/model configuration. **Windows:** likely WSL/Linux-oriented integration work. **Kaggle:** model-dependent; no verified complete free-T4 recipe. [Preview GIF](https://raw.githubusercontent.com/showlab/MovieAgent/main/assets/demo.gif).

- **[MoneyPrinter](https://github.com/FujiwaraChoki/MoneyPrinter)** — **MIT**. Automates topic-to-Shorts production; current README describes Ollama and a persistent generation queue. Useful assembly infrastructure, **not recurring human-character acting**. **Windows:** feasible with dependencies/Docker. **Kaggle:** awkward for persistent services. **Preview:** no suitable output image verified; README imagery includes sponsorship material.

**Character-consistency tools**

These help produce references or individual shots. They do not replace a rig, story timeline, or continuity system.

- **[IP-Adapter](https://github.com/tencent-ailab/IP-Adapter)** — **Apache-2.0 code; base-model terms apply**. Reference-image conditioning for SD1.5/SDXL; useful for costumes, faces, and visual style. **Windows:** good CUDA/ecosystem fit. **Kaggle:** promising for single-image inference. FaceID variants introduce additional face-model restrictions. [Face preview](https://raw.githubusercontent.com/tencent-ailab/IP-Adapter/main/assets/demo/sd15_face.jpg).

- **[PuLID](https://github.com/ToTheBeginning/PuLID)** — **Apache-2.0 code**, with separate base/face-model terms. Identity-conditioned image generation for SDXL/FLUX; implementation uses InsightFace models. **Windows:** possible with CUDA setup. **Kaggle:** plausible; project documents optimized FLUX operation on 16 GB, including a 12 GB mode. [Preview](https://github.com/ToTheBeginning/PuLID/assets/11482921/65610b0d-ba4f-4dc3-a74d-bd60f8f5ce37).

- **[InstantID](https://github.com/instantX-research/InstantID)** — **Apache-2.0 code; released checkpoints research-only; downloaded InsightFace models non-commercial research-only**. Single-reference face identity preservation, not complete character consistency. **Windows/Kaggle:** plausible with CUDA and memory optimization. [Preview](https://raw.githubusercontent.com/instantX-research/InstantID/main/assets/applications.png). ([Restrictions](https://github.com/instantX-research/InstantID#usage-tips))

- **[ConsisID](https://github.com/PKU-YuanGroup/ConsisID)** — **Apache-2.0 repository/model-card declaration**, with dependent face-model terms still requiring attention. Identity-preserving video generation; a shot generator, not a story engine. **Windows:** CUDA integration work. **Kaggle:** experimental—the README reports roughly 44 GB reserved normally, falling to 7 GB with aggressive offloading/tiling, with speed/quality tradeoffs. Its BF16 examples also need adaptation for T4. [Demo thumbnail](https://github.com/user-attachments/assets/634248f6-1b54-4963-88d6-34fa7263750b).

**Talking and gesture avatars**

- **[TalkingHead](https://github.com/met4citizen/TalkingHead)** — **MIT code; example avatars/assets have separate terms**. Browser-based 3D humans with lipsync, expressions, gestures, and animation controls. Strong candidate for code-directed dialogue scenes. **Windows:** good WebGL browser fit. **Kaggle:** unnecessary. Hindi/Sanskrit lipsync needs validation. [Preview](https://raw.githubusercontent.com/met4citizen/TalkingHead/main/images/screenshot5.jpg).

- **[SadTalker](https://github.com/OpenTalker/SadTalker)** — **Apache-2.0, with third-party component exceptions**. Portrait plus audio produces talking-face video. Useful for narrator/saint close-ups; its “full image” mode does not imply articulated full-body acting. **Windows:** documented setup. **Kaggle:** plausible GPU inference after dependency setup. [Preview GIF](https://user-images.githubusercontent.com/4397546/222490039-b1f6156b-bf00-405b-9fda-0c9a9156f991.gif).

- **[LivePortrait](https://github.com/KwaiVGI/LivePortrait)** — **MIT**, but its licence explicitly requires replacing InsightFace detection models for commercial use. Transfers facial performance from driving inputs; not inherently audio-driven or a body-animation system. **Windows:** packaged installer available. **Kaggle:** plausible GPU inference. [Preview GIF](https://raw.githubusercontent.com/KwaiVGI/LivePortrait/main/assets/docs/showcase2.gif). ([Licence](https://github.com/KwaiVGI/LivePortrait/blob/main/LICENSE))

**My top five for your devotional film**

1. **Blender** — best complete foundation for recurring actors, precise poses, camera work, and full scenes. Use Python/MCP to automate repeated work.
2. **MakeHuman** — strongest starting point for a reusable human cast, with clearly stated CC0 bundled assets. Period clothing, hair, jewellery, and styling still need work.
3. **Synfig** — strongest economical route to an illustrated devotional film with full scenes and repeatable characters.
4. **Inochi2D** — attractive for expressive illustrated dialogue and narration; broader body actions need deliberate rig design.
5. **TalkingHead** — fastest promising route to programmable speaking characters with gestures; needs custom assets and film composition.

**Can code-first human animation actually work?**

**Yes.** Parametric meshes, layered drawings, rigs, expressions, and reusable motion are already practical ways to create and animate humans. Code can reliably orchestrate those assets across an entire film.

The difficult part is art and performance: appealing faces, convincing cloth, hand contact, emotional timing, and culturally accurate gestures. For this project, I would create an approved cast once, lock costumes and iconography, and build reusable actions such as walking, bowing, seated dialogue, and namaste. Let code place, time, and render them. Use generative AI selectively for concepts, backgrounds, or reviewed shots.

I did not run these repositories or validate every preview download. Missing previews and unverified reuse rights are identified above.