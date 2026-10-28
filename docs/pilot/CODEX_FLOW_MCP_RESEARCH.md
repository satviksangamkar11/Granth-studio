# Flow MCP research report

## Answer

**Maybe for a limited trial, but no switch yet:** `flow-mcp` can drive Flow and claims 2K downloads, but it has not demonstrated GranthStudio’s full image workflow, and an open wrong-download report directly concerns the project’s exact-title filing requirement.

Research date: 28 October 2026. No project code was run, installed, cloned or downloaded. The workspace is read-only, so I could not write the requested report file; the report is provided here.

## 1. What `flow-mcp` is

[`flow-mcp`](https://github.com/GTAI-1/flow-mcp) is a third-party, local MCP server that controls **Google Flow’s web interface** in a dedicated Chrome window. Its documented path is MCP over standard input/output to the server, then Chrome DevTools Protocol to Chrome and Flow. It is browser automation, not a documented official Flow API. Its README describes button interaction; I did not verify every source file well enough to rule out other web calls.

Flow uses Google models including Nano Banana for images and Veo for video. The server also has substantial video and audio functionality that GranthStudio does not need. Its documented image-relevant tools include:

- `flow_status`, `flow_assets`, `flow_generate`, `flow_wait`, `flow_cancel` and `flow_retry`.
- `flow_download`, which **claims** an existing image can be downloaded with a 2K upscale.
- `flow_agent_images`, which claims batches of up to 50 scenes with references.
- Character creation, listing and character portrait editing. The documented `flow_edit` is **video-to-video**, so its name alone does not establish still-image edit support. [Tool list](https://github.com/GTAI-1/flow-mcp#tools)

The project is TypeScript/Node.js. Its [package manifest](https://github.com/GTAI-1/flow-mcp/blob/main/package.json) lists the MCP SDK, `playwright-core` and Zod, with TypeScript for building. The documented Windows setup is to obtain the repository, install Node dependencies, build, run its login command, sign into its Chrome window manually, open a Flow project and configure the MCP client to start `dist/index.js`. Chrome and Node 22+ are required; FFmpeg and other tools are optional for unrelated functions. The display must remain awake. **The README says Windows support has not been run on a real PC**, and says Codex integration has not been tried. [Installation and platform notes](https://github.com/GTAI-1/flow-mcp#what-you-need)

## 2. Authentication, safety and maintenance

The owner signs in manually; the project says it does not type the password. However, it deliberately retains the authenticated Chrome profile at `~/.flow-mcp/chrome-profile`. That profile may contain reusable Google session material, so **it conflicts with the literal “no stored credentials” requirement unless the owner explicitly accepts that interpretation or a reviewed session-only procedure is established**. A separate per-run local control token is documented at `~/.flow-mcp/token`. An optional Gemini API key is used for a separate narration feature and is unnecessary for this image investigation. [Authentication and local server](https://github.com/GTAI-1/flow-mcp#install)

The README says the program is local and has no hosted service. I cannot independently establish that credentials, prompts or files are never sent to a third party: I did not conduct a complete source, dependency, build-script or network audit. The authenticated Chrome connection itself is a significant trust boundary. Do not infer safety from the local-server claim.

At the time viewed, GitHub showed **357 stars and four open issues**. Two especially relevant reports describe [a wrong download](https://github.com/GTAI-1/flow-mcp/issues/19) and [generation failure after a Flow UI change](https://github.com/GTAI-1/flow-mcp/issues/18); these are reports, not independently reproduced findings. The package declares `ISC`, but I did not find a separate license file in the displayed repository listing, so the licensing position should be checked before reliance. A third-party [maintenance snapshot](https://upstar.dev/r/GTAI-1/flow-mcp) reported one commit author over its preceding 90-day window; that is **not proof of the number of maintainers**. I could not verify the exact latest commit date. The [security page](https://github.com/GTAI-1/flow-mcp/security) reports no security policy.

## 3. Fit to GranthStudio

- **2K:** `flow_download` documents 2K upscaling, but the exact output dimensions and behavior on Windows remain untested. The current [filing script](<D:/aai work/granthstudio/scripts/flow/file_flow_download.py>) requires exactly **2752 × 1536** and a complete JPEG before filing. A 2K label alone is insufficient.
- **Exact-title filing:** Default documented outputs use `scene-NN` names. The existing [regen filing script](<D:/aai work/granthstudio/scripts/flow/file_regen.sh>) instead fails closed on the exact `<shot>__<version>` title. Whether the MCP can preserve that binding without ambiguity is unverified, especially in light of the open wrong-download issue.
- **Edit-first:** References and character portrait restyling are documented. A targeted edit of an existing **shot still**, preserving its identity and returning its edit ID, is not established by the documented `flow_edit`, which is for video. This is a material gap.
- **About 60 images:** The claimed agent batch limit is 50, so a chapter would require at least two batches. Its automatic re-asks and fallback generation need review against the project’s stop and reconciliation rules. Reference-to-scene matching and handling of duplicate prompts require proof before use. [Batch behavior](https://github.com/GTAI-1/flow-mcp#tools)
- **Model choice:** `flow_generate` documents a model parameter, but I could not establish that the current Pro and 2.1 Flow choices are both correctly selectable and recorded in the actual returned results. Google notes that Flow can switch to a compatible model, so the **actual** model needs verification. [Google Flow help](https://support.google.com/flow/answer/16353333?hl=en)
- **Provenance:** File paths and results are documented, but a complete per-chosen-image record containing the actual prompt hash, actual model, edit ID and raw/clean hashes is not demonstrated. Existing filing and catalog checks would still be needed, with a verified binding to each result.
- **Watermarks:** Google says Flow outputs carry invisible SynthID, and that a visible watermark is automatically applied to users in India except those on the specified Ultra 20x plan. The existing cleaner and rights treatment need review for the actual output; MCP does not establish that requirement is satisfied. [Google watermark policy](https://support.google.com/flow/answer/16353333?hl=en)
- **Two languages:** The image route does not inherently require separate Marathi and Hindi pictures. The existing shared-image pipeline and approval process must remain responsible for enforcing that.

The local pipeline also requires reference chips, initial scene review, owner approval and stop conditions. The public claims do not establish equivalent behavior for all of them. See [pipeline section 9](<D:/aai work/granthstudio/docs/pilot/PIPELINE_README.md>) and the [Flow runbook](<D:/aai work/granthstudio/docs/pilot/FLOW_RUNBOOK.md>).

## 4. Terms and rights

The project itself warns that automated Flow use **may be against Google’s terms**. I cannot conclude from the reviewed material that this particular automation definitively violates them, nor that Google authorizes it. Account restrictions or unusual-activity challenges are possible; Google documents rate limits and unusual-activity messages. The existing Haiku browser automation also warrants terms review rather than an assumption that its automation is explicitly permitted. [Project risk statement](https://github.com/GTAI-1/flow-mcp#licence-and-risk), [Google Flow help](https://support.google.com/flow/answer/16353333?hl=en)

Google’s Flow help says its terms govern commercial use and that Google does not claim ownership of original generated content. That is useful but **does not by itself guarantee film rights**, copyright protection, clearance of reference material, or permission for a particular watermark alteration. Review the applicable Flow terms, local law, reference rights and the intended published-film use before adopting a route. [Google Flow commercial-use guidance](https://support.google.com/flow/answer/16353333?hl=en)

The [Gemini API terms](https://ai.google.dev/gemini-api/terms) apply to the official API and related developer services; they should not be automatically treated as the sole governing terms for browser-driven Flow. They prohibit bypassing protective measures and state that Google does not claim ownership of original generated content. Whether a particular Flow automation breaches an applicable term remains unresolved.

## 5. Comparison with Haiku-low browser agents

The current method is already documented for this PC, including one tab per agent, owner sign-in, reference attachment, edit-first, 2K download and fail-closed filing. `flow-mcp` might reduce repetitive interaction through queued calls or Flow Agent batches, but its Windows behavior and chapter-scale reliability are unproven.

Its documented architecture has **one process owning a Chrome tab and job queue**, with other clients forwarding requests to it. It does not map directly to one independent tab per Haiku agent. Ordinary generations are documented as serial with 25–70 second pauses; the separate agent-batch tool claims parallel rendering and a sample timing, but that is not a benchmark for GranthStudio’s prompts, references or PC. [Architecture and pacing](https://github.com/GTAI-1/flow-mcp#behaviour-and-settings)

Both Flow routes consume whatever Flow credits the selected actions currently cost. The repository’s zero-credit still-image claims should not be assumed to apply to this account or selected model: Google says costs evolve and should be checked in Flow. Haiku usage costs, MCP orchestration cost, elapsed time and retry rates have not been measured comparatively. Automatic retries could also create ambiguity after an interrupted or unknown result. [Google credit guidance](https://support.google.com/flow/answer/16353333?hl=en)

## 6. Recommendation

**TRIAL FIRST**, with the existing Haiku workflow retained until the gates below pass. This is a recommendation for a later, separately authorized trial—not a claim that the current research has validated the tool.

An official alternative exists: the [Gemini API image-generation API](https://ai.google.dev/gemini-api/docs/generate-content/image-generation) documents image generation and editing, reference images, model selection, 16:9 and 2K output. Its published 16:9 2K dimensions for Nano Banana 2.1 are **2752 × 1536**. It uses API authentication and separate API pricing and terms; it is not the same Flow subscription-credit workflow, does not automatically supply Flow tile/edit IDs, and would need its own provenance, integration, rights and quality assessment. I have not established an official Google Flow MCP that provides the same workflow.

## Risks

1. **Wrong image bound to a shot** would undermine exact-title filing and provenance; the open download report makes this a concrete concern.
2. **Persistent Google session exposure** conflicts with the stated credential requirement and gives untrusted code access to an authenticated browser.
3. **UI changes, Windows-specific failures and automatic retries** could produce failed, duplicate or unknown paid results.
4. **Still editing, actual model, reference binding and provenance remain unproven.**
5. **Terms and film-use clearance remain unresolved**, including watermark handling.

## Smallest safe next step

First, perform a **read-only review of a pinned commit** and its lockfile, install/build scripts, browser profile handling, network destinations, logging, retry behavior, download matching and tool schemas; check current issues and applicable Google terms. Confirm whether persistent session storage is acceptable under the owner’s requirement.

Only after those reviews and explicit authorization for a live trial, use an isolated test project and owner-performed sign-in to generate **one disposable image**, then perform **one local-defect edit** if supported. Verify the actual model, reference bindings, 2K dimensions, exact title-to-file association, edit ID, prompt and raw/clean hashes, watermark handling, credit change and interruption recovery. Stop on sign-in, CAPTCHA, payment, terms or uncertain result; do not run a chapter batch. Compare the result and effort with one equivalent existing Haiku run.

## What I could not verify

- Exact latest commit date, current maintainer count, or a complete license grant.
- All code paths, dependencies and network destinations; absence of credential exfiltration cannot be asserted.
- Actual Windows execution, 2K bytes, shot-image edit support, model selection, exact-title mapping, full provenance or 60-image recovery.
- A definitive legal conclusion on Flow automation or film rights for this account and its reference assets.