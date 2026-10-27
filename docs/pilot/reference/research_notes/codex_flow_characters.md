**Executive summary — 26 October 2026**

1. **Use Flow’s saved Characters, `@name` references and project Agent Instructions:** Google now documents all three.
2. Create and approve the 14 reference sheets once; bundle each character’s body/head pair into one saved Character.
3. Keep the three places and three prop sheets as named project assets; reuse them from the project.
4. Set the style image, art-direction rules, default image model and 16:9 aspect ratio once; these are guidance/defaults, not guaranteed locks.
5. Leave **Clear prompt on submit** off so the current scene’s references remain available.
6. Generate one tailored full-frame image per shot, changing the shot instructions while retaining the relevant references.
7. Use small edits from accepted images; return to the approved references whenever identity drifts.
8. Google’s current model list names **Nano Banana Pro, Nano Banana 2 Lite and Nano Banana 2.1**; check the actual selection and cost.
9. Saved references reduce uploading; Google’s consistency claims do not establish identical faces, clothes or line work.
10. Keep local originals, accepted outputs, exact prompts and SHA-256 hashes; Flow must remain a convenience layer over the local canon.

Sources for these conclusions are linked below. Research only: no files modified, no login, paid generation or Google-service automation performed.

**Evidence and date conventions**

“Documented” means stated in Google’s own documentation, not independently tested in the owner’s account. “Vendor claim” identifies a quality assertion. “Recommendation” or “inference” identifies my judgment.

All linked help pages were checked on **26 October 2026**; where Google exposes no publication/update date, that is the citation date. Dated announcements are identified separately. Account-specific availability, output quality and exact clicks remain untested.

The local catalog contains **122 draft entries: eight character sheets, three prop sheets, three place references, 59 shot images and 49 layers**. The reference designs remain `DRAFT_NOT_APPROVED`.

**1. What Flow’s agent mode actually does**

**Documented:** Google Flow Agent is a conversational interface for planning, generating, editing and organizing project media. Google announced it for all Flow users globally on **19 May 2026**. It can perform multi-step tasks, generate variations, batch-edit assets, and rename/group them. These capabilities are directly relevant to reducing repetitive work. Its brainstorming and story-development functions are unnecessary for this source-locked film. [Google’s Flow announcement, 19 May 2026](https://blog.google/innovation-and-ai/models-and-research/google-labs/flow-updates/)

The features mentioned in the brief are distinct:

- **Agent/chat assistant:** directs work through conversation.
- **Flow TV:** showcases films and prompts; it does not save the owner’s character canon.
- **Scenebuilder:** arranges and edits video sequences; it is not an image identity registry.
- **Ingredients to video:** conditions video generation on supplied media.
- **Saved Characters:** packages reusable character references.
- **Whisk subject/scene/style:** an earlier image-remixing interface. Its original implementation captioned references through Gemini and generated through Imagen 3; Google explicitly described capturing a subject’s essence rather than an exact replica. Do not assume Whisk’s controls or behavior describe current Flow. [Flow FAQ, checked 26 October 2026](https://support.google.com/flow/answer/16353333?hl=en), [Scenebuilder help, checked 26 October 2026](https://support.google.com/flow/answer/16935718?hl=en), [Whisk announcement, 16 December 2024](https://blog.google/innovation-and-ai/models-and-research/google-labs/whisk/)

**Availability and accounts:** Flow requires age verification for users aged 18+. India is supported. Google recommends English prompts; Marathi and Hindi are also listed interface languages. The availability page lists supported territories and feature-specific regional restrictions; it does not provide a separate saved-Characters entitlement matrix. [Regional availability, checked 26 October 2026](https://support.google.com/flow/answer/16353544?hl=en)

Google’s current documentation is inconsistent about subscriptions: the getting-started page lists Plus/Pro/Ultra and qualifying Workspace plans, whereas the credits page expressly describes non-subscriber access. Consequently, **neither a subscription requirement for every image feature nor universal free-account access can be established cleanly from those pages**. Qualifying Workspace plans include Business/Enterprise Starter, Standard and Plus, certain Education plans and G Suite Legacy Free Edition. The owner’s actual entitlement remains unverified. [Getting started](https://support.google.com/flow/answer/16353333?hl=en), [Credits help](https://support.google.com/flow/answer/16526234?hl=en), both checked 26 October 2026.

**Credits and limits:**

- Agent queries currently cost no credits but have an unpublished daily quota.
- Generated media uses the relevant generation allowance; one request can produce multiple billable generations.
- The credits page lists 50 daily Flow credits, plus monthly allowances of 200 for Plus, 1,000 for Pro, 10,000 for Ultra $100 and 25,000 for Ultra $200. Unused daily/monthly allocations do not roll over.
- It does **not** establish an unambiguous current image price for every Nano Banana variant. Google directs users to the generation settings for current costs.
- Numerical Agent quota, image throughput cap, maximum batch size and maximum saved-Character count were not verified. [Agent help](https://support.google.com/flow/answer/17093911?hl=en-PH), [Credits help](https://support.google.com/flow/answer/16526234?hl=en), checked 26 October 2026.

Google also offers native reusable **Tools**: subscribers can build them; other users can use existing ones. This could eventually simplify a repeated workflow, but building a custom tool is unnecessary for the present 59 shots. [Tools help, checked 26 October 2026](https://support.google.com/flow/answer/17104535?hl=en)

**2. Saving characters and reusing them without uploading again**

**Documented:** Flow’s Characters interface accepts **one or two appearance images**, requires at least one, and lets the owner assign a name and character information. The documented creation sequence also includes selecting a voice. For this image-only task, such a voice must not replace the project’s approved audio workflow.

Google’s image-generation instructions explicitly support typing **`@` followed by a saved character name**. Therefore, this feature works for **still images**, not only video. [Character management](https://support.google.com/flow/answer/16935308?hl=en), [Image references](https://support.google.com/flow/answer/16729550?hl=en), checked 26 October 2026.

**Recommendation:** create four saved Characters:

- `GM_v01`: `CH_GM` and `CH_GM_HEAD`
- `BA_v01`: `CH_BA` and `CH_BA_HEAD`
- `DK_v01`: `CH_DK` and `CH_DK_HEAD`
- `DV_v01`: `CH_DV` and `CH_DV_HEAD`

These are proposed names, not verified naming-syntax requirements. Select the actual autocomplete reference; merely pasting an arbitrary `@GM_v01` string is not evidence that Flow bound it to the saved Character.

**Persistence and sharing:** documentation locates character creation/editing within projects. I could not verify account-wide Character reuse, cross-project synchronization, Character export/import, or collaborative editing. Treat Characters as **project-bound unless the owner confirms otherwise**. Image/video sharing can include inputs, but that is not proof of a transferable saved Character.

**Vendor claim:** Google says saved Characters preserve face, clothing and voice “strictly consistent.” This report does not endorse that as a production guarantee. No flat-colour, four-character benchmark supports it here. [Project and Character help, checked 26 October 2026](https://support.google.com/flow/answer/16935308?hl=en)

**Places and props:** save the existing six reference sheets as ordinary named project assets. Google documents searching uploaded project assets with `@` for video ingredients; for still images, **Add to Prompt** is explicitly documented. Generic image-asset `@` behavior for still images should therefore be checked in the owner’s interface, with Add to Prompt as the documented fallback. [Video references](https://support.google.com/flow/answer/16353334?hl=en), [Image references](https://support.google.com/flow/answer/16729550?hl=en), checked 26 October 2026.

**3. Setting style and aspect ratio once**

**Documented:** Agent Instructions accept a reference image and written guidelines across the project. Agent settings also expose default image aspect ratio, output count and model. This provides a documented place to store the base style instead of repeatedly pasting its entire paragraph. Neither feature is described as an immutable style or aspect-ratio lock. [Agent help, checked 26 October 2026](https://support.google.com/flow/answer/17093911?hl=en-PH)

**Recommended instruction text:**

> Produce still images only in the approved flat-colour Indian devotional storybook style. Follow the attached style reference: steady dark navy contours, flat earth-colour fills, sparse hatching and one shade tone; no gradients or painterly texture. Every shot is a complete 16:9 composition with foreground, midground and background. White backgrounds apply only to explicitly requested reference sheets and isolated layers. Preserve the selected characters’ approved faces, proportions and costumes. Add no story events, dialogue, text, modern objects, halos or personal glow. Follow each shot’s specified gaze, pose, lighting and screen geography.

Use one representative approved style image there; keep all three original style references locally and in the project. Whether multiple instruction images are supported was not verified.

**Important local detail:** Maharaj’s default nose-tip gaze cannot override shots that explicitly require looking up or laughing. Likewise, “his only belongings” should not make Flow put both props into every shot. Shot-specific instructions must control presence, hands and gaze.

**4. Best workflow for the 59 shots and 49 layers**

**Recommendation:** organize by scene and generate in the catalog’s order. Reuse scene references while changing only the shot-specific action, framing and light.

The most useful documented convenience is **Clear prompt on submit**: turning it on removes text and references after generation. Leave it **off**, then replace the previous shot’s changing instructions and retain the scene’s references. This reduces repeated attachment even if generic image `@` lookup is unavailable. [Project settings, checked 26 October 2026](https://support.google.com/flow/answer/16935308?hl=en)

Use these generation patterns:

- **New composition:** approved Characters + relevant place/props + shot instructions.
- **Nearby pose or expression:** edit an accepted shot while retaining canonical identity references.
- **Small defect:** use the image selection/edit control to target the affected area.
- **Layer:** derive from its accepted full shot, preserving pose, scale, costume and lighting.
- **Drift recovery:** restart from the last accepted image and approved sheets, rather than extending a chain of rejected edits.

Flow documents image-to-image editing, selected-region changes, drawing annotations, edit history and saved versions. The Agent can edit multiple selected images; Google even gives a 20-variation example, but this is **not a documented maximum**. [Image creation/editing help, checked 26 October 2026](https://support.google.com/flow/answer/16729550?hl=en)

Google’s November 2025 announcement also describes changing pose, clothing, angle or lighting through image edits. Those are advertised capabilities, not proof that untouched details remain pixel-identical. [Flow image-editing announcement, November 2025](https://blog.google/innovation-and-ai/models-and-research/google-labs/flow-refine-videos/)

**Identity checks for this film:** compare the accepted sheets for face, build, hairstyle, costume shape/colour, headwear, sacred thread/tilak where applicable, and bare feet. Check Damodarpant against Devidas especially. For locations, check the house/door and well/trough geography; for props, check the gourd, unfired clay chilim and gadva rather than accepting plausible substitutes.

**Organization:** retain the existing catalog IDs. Suggested output names are `<existing_image_id>__v01__candidate` and `<existing_image_id>__v02__accepted`; file extensions must match the downloaded format. Keep References, Shots/S1–S9, Layers and Rejected collections. Google documents nested collections and collection/project downloads. A project download should be treated as an additional backup, not a verified restorable Character registry.

**Resolution and downloads:** download the actual image asset, not a screenshot or preview. Record its decoded pixel dimensions. I could not verify a current Flow-specific promise that every plan/model offers full-resolution 2K/4K still downloads, nor a desktop image-resolution selector’s exact behavior. Gemini-app download entitlements and API model capabilities must not be substituted for Flow entitlements.

**Watermarks and metadata:** Flow says generated Nano Banana outputs contain invisible SynthID. Its visible-watermark documentation is inconsistent: one page says automatic watermarking applies in India, South Korea and Vietnam; another specifies an exception for the Google One AI Ultra 20x plan. **Do not promise watermark-free Indian exports.** A prompt saying “no watermark” cannot override platform watermarking. Prompt/model/reference metadata surviving inside downloaded files was not verified; maintain the catalog separately. [Flow FAQ](https://support.google.com/flow/answer/16353333?hl=en), [alternate official watermark guidance](https://support.google.com/flow/answer/16353333?co=GENIE.Platform%3DAndroid&hl=en-GB), checked 26 October 2026.

**Transparency:** Google’s legacy Gemini image-generation documentation explicitly states that transparent backgrounds are unsupported. Its newer image-generation page omits that statement, so I cannot establish a blanket prohibition for every current Flow variant. **For planning, require white-background cut-outs and a separate alpha-extraction step; do not describe them as transparent assets until an actual alpha channel is verified.** [Legacy image-generation documentation, checked 26 October 2026](https://ai.google.dev/gemini-api/docs/generate-content/image-generation?hl=en)

**5. Current Nano Banana models, reference limits and failure modes**

**Current Flow documentation lists:**

- **Nano Banana Pro:** default for Ultra subscribers.
- **Nano Banana 2 Lite:** default model available at no charge.
- **Nano Banana 2.1:** standard generation/editing model.

The generic image-creation page instead says Pro is the default. Thus, **there is no defensible universal default**; record the owner’s actual selection. [Flow model list](https://support.google.com/flow/answer/16352836?hl=en), [Image creation help](https://support.google.com/flow/answer/16729550?hl=en), checked 26 October 2026.

For model-family context, Google’s developer documentation maps Pro to Gemini 3 Pro Image, Lite to Gemini 3.1 Flash Lite Image, and 2.1 to `gemini-nano-banana-2.1`. Earlier Nano Banana 2 is Gemini 3.1 Flash Image. API documentation describes 1K/2K/4K output for the larger models and 1K for Lite; these are **model capabilities, not verified Flow export options**. [Google image-generation documentation, updated 9 October 2026](https://ai.google.dev/gemini-api/docs/image-generation), [model-selection documentation, checked 26 October 2026](https://ai.google.dev/gemini-api/docs/generate-content/image-generation?hl=en)

**Maximum references:** developer documentation specifies up to **14 input reference images**. Its character-consistency guidance identifies up to four character images for 2.1/3.1 Flash and five for Pro; Lite does not receive the same character-consistency allocation in that table. **Flow’s actual attachment ceiling and how a two-image Character consumes that budget were not verified.** Do not infer that four saved Characters plus all their sheets, style images, locations and props necessarily fit. [Google image-generation documentation, updated 9 October 2026](https://ai.google.dev/gemini-api/docs/image-generation)

**Text rendering:** Google advertises improved legible/stylized text. The film requires none; continue prohibiting lettering and add the 1878 caption later. Accurate Marathi/Devanagari rendering is not established by these claims.

**Vendor claim:** the February 2026 Nano Banana 2 announcement promotes subject consistency and high-resolution output; its statement that Flow images cost zero credits is historical, not sufficient evidence of current pricing for all variants. [Nano Banana 2 announcement, 26 February 2026](https://blog.google/innovation-and-ai/technology/ai/nano-banana-2/)

**Expected failure modes—inferences requiring owner checks:**

- Similar white garments or turbans blend between characters.
- A multi-view sheet becomes several people in the scene.
- Faces simplify differently in close-up and wide shots.
- Flat fills acquire gradients; navy outlines become heavier or black.
- Cloth borders, moustaches, shikha, sacred thread or tilak disappear.
- Referenced props appear when absent from the shot instructions.
- An edit changes untouched features or reverses screen geography.
- Successive edits accumulate small identity changes.

No Google source located establishes a measured failure rate for this particular illustrated style.

**6. Manual effort estimate**

These are **planning estimates**, not measured Flow performance.

For an unchanged scene reference set, expect approximately **four to six manual actions per accepted image**: replace/paste the shot instructions, submit, inspect, name/mark the accepted result, download and record it. Reference selection at a scene change adds several actions. Text entry, autocomplete choices and review are not single mouse clicks.

Allow:

- **Setup and reference approval:** roughly 1–3 hours, potentially longer if designs need revision.
- **59 shots:** around 3–6 minutes of active work each, or approximately 3–6 hours before substantial retries.
- **49 layers:** separately budget about 2–4 minutes each, plus alpha extraction where required.
- Generation latency, throttling and difficult corrections are additional elapsed time.

The largest savings come from retained references, reusable instructions, short shot templates, scene order and immediate acceptance checks. Start with one output per shot; request two alternatives only when composition is uncertain. A large variation batch increases inspection work.

**7. Strongest case against relying on saved Characters**

**The central weakness is that a saved Character is a reference mechanism, not a frozen, reproducible identity model.** It can save uploads while still producing a different face or garment. Cross-project portability, model-version pinning and deterministic reconstruction were not established.

Other dependencies include unpublished quotas, model routing/default changes, regional restrictions, account access and changes to the service. Google’s terms expressly allow features and limits to change. They also prohibit bypassing protective measures and certain automated access; they do not justify claiming that every form of automation is universally prohibited. The brief’s manual-only rule remains sufficient here. [Google Terms of Service, effective 30 July 2026](https://policies.google.com/terms)

**Recommended backup for every approved reference and accepted output:**

- Original downloaded bytes, local path and SHA-256.
- Stable catalog ID and canon/style version.
- Exact submitted prompt, actual model label, generation date and dimensions.
- Reference IDs and hashes, including the parent image for edits.
- Flow project/asset identifier or URL where available.
- Acceptance status and rejection/correction notes.

Keep an independent backup copy. Hashes establish file integrity, not visual correctness or reproducibility. Preserve accepted work; account loss should require rebuilding reference bindings, not recreating approved artwork.

**8. Proposed changes to our catalog and prompts**

These are recommendations only; no files were changed.

Keep the full existing prompts as portable masters. Add a short **Flow submission prompt**, with bindings to the full canon, rather than replacing the canon with `@names`.

Suggested additional fields:

`flow_project`, `flow_character_name`, `reference_ids`, `reference_hashes`, `style_version`, `submitted_prompt`, `model_label`, `generated_at`, `parent_image_id`, `output_path`, `output_sha256`, `pixel_dimensions`, `acceptance_status`.

Use one saved Character per person, containing the existing two sheets. Preserve `GM`, `BA`, `DK` and `DV`; do not rename local IDs to match a display name. Preserve source references, owner-choice labels and bilingual visual reuse.

A proposed short template is:

> **[Existing image ID].** One complete 16:9 frame. [Selected Character references]. [Selected location and required props]. [Approved action, expression and gaze]. [Framing and screen positions]. [Approved lighting block]. Preserve canonical faces, proportions and costumes; change only what this shot specifies. Approved flat-colour style. No text, modern objects, halo or glow.

Keep distinguishing costume cues in each submission—for example, Bankatlal’s sage-green angarkha versus Damodarpant’s red pagadi. Full identity paragraphs belong in the Character information and portable master; repeat the complete paragraph when references fail, a new project is used or drift needs correction.

The existing instruction to attach the previous scene shot should become **conditional continuity reference**. It must not displace the canonical sheets or perpetuate an already drifting face.

**Numbered owner procedure — minimum repeated work**

1. **Open Flow on desktop and create one Adhyay 1 project.** Check that Characters, Agent Instructions and the desired image model are present. Record the displayed cost before generating.

2. **Set image defaults:** 16:9, one output and one chosen model. Turn **Clear prompt on submit off**. These controls are documented; exact layout may differ. [Agent settings](https://support.google.com/flow/answer/17093911?hl=en-PH), [project settings](https://support.google.com/flow/answer/16935308?hl=en), checked 26 October 2026.

3. **Add the style instruction above and the approved style reference.** Keep the three original style files available in the project.

4. **Generate the 14 references in the catalog’s prescribed order.** Derive each head sheet from its accepted body sheet. Approve all identities, costumes, places and props before starting shots.

5. **Save four Characters through Characters → New Character.** Use each approved body/head pair, enter its proposed versioned name and identity information, complete the displayed creation controls, then Done. Use any required voice selection solely as a Flow field.

6. **Keep the six place/prop references under their existing IDs.** Arrange references, scene shots and layers into collections. Keep rejected candidates separately.

7. **For the first shot of a scene, select its cast using `@` autocomplete.** Add the relevant location/props from the project. Try named asset lookup for stills; use Add to Prompt if unavailable. Uploading again should be unnecessary.

8. **Paste the short shot prompt and generate.** Check that the intended references and model are active. If Agent proposes extra media or story content, keep the request restricted to the specified still.

9. **Inspect identity and continuity before accepting.** For a small defect, edit the affected region. For face/costume drift, return to the canonical sheets and last accepted image.

10. **For the next shot, retain the references and replace the changing instructions.** Remove absent people/props explicitly. Change the reference set only when the cast or location changes.

11. **Save each accepted result locally under its catalog ID.** Record prompt, references, model, dimensions and acceptance; compute its SHA-256 through the local catalog workflow. Download the actual asset at the highest available resolution.

12. **Create layers from the accepted full shot, then finish the scene backup.** Verify alpha separately for cut-outs. Reuse the same accepted visual masters for Marathi and Hindi, and reuse the approved reference files in later Adhyayas.