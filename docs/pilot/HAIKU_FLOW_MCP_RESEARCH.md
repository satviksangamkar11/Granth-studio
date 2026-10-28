# Research: can the Flow image step use flow-mcp instead of the Haiku browser agents?

Read-only research. Nothing was installed, cloned, downloaded or run. Sources are the local pilot files and public web pages (cited inline).

## Answer

**DO NOT USE** for the production image step. flow-mcp is an unofficial browser-automation tool with no stated license, untested on Windows, and it drives Flow on the owner's Google account in a way Google's terms say may be prohibited. It does not solve any hard requirement that the current Haiku method does not already cover. Revisit only if Google publishes an official Flow or Gemini image API that supports our models and 2K download.

## 0. Current method (local files read)

- `docs/pilot/PIPELINE_README.md` section 9: Haiku agents at LOW effort operate Google Flow in the Claude built-in browser, one tab per agent, owner signs in himself. Model Nano Banana Pro x1, fallback Nano Banana 2.1 x1, 16:9, 2K download, exact-title filing via `scripts/flow/file_flow_download.py` and `file_regen.sh` (fail closed, provenance log lines).
- `docs/pilot/HAIKU_FLOW_AGENT_BRIEF.md` (UPDATES 1-15): per-job @ chips, prompt pasted from job file, rename tile to `<ID>__vNN`, edit-first for local defects, regenerate for identity/framing, progress file, stop on sign-in/CAPTCHA/payment/terms pages.
- `docs/pilot/FLOW_RUNBOOK.md` sections 12-17: exact @ method, 2K download menu path, edit-first procedure, known download glitch (first click after load often does nothing), settings reset after PC restart.
- `docs/pilot/IMAGE_PROMPT_RULES.md`: template built by code; review rubric; automatic gates list (provenance per version still "to build").
- `scripts/flow/`: `build_shot_jobs.py`, `build_regen_jobs.py`, `file_flow_download.py`, `file_regen.sh`, `audit_flow_outputs.py`, `build_final_set.py`, `build_final_manifest.py`, `build_image_binding.py`.

Its weaknesses are real (slow, fragile clicks, Pro daily limit, Maharaj drift), but its risk profile is the same kind as flow-mcp: it already drives Flow in the browser on the owner's account.

## 1. What flow-mcp is (source: https://github.com/GTAI-1/flow-mcp, README and linked docs, fetched)

- A local Node.js program (TypeScript/JavaScript, Node 22+) exposing about 25 MCP tools to Claude, Codex or similar apps: status/queue (`flow_status`, `flow_wait`, `flow_cancel`, `flow_retry`), generation (`flow_generate`, `flow_agent_images`, `flow_edit`, `flow_continue`, `flow_techniques`), project media (`flow_assets`, `flow_download`, `flow_trash`), characters (`flow_character`, `flow_character_edit`, `flow_characters`), audio and post (`flow_narrate`, `flow_voices`, `flow_transcribe`, `flow_captions`, `flow_assemble`).
- Google product: Google Flow (flow.google.com) for image and video. Optional narration uses the Google AI Studio text-to-speech API. The README does not name the underlying image model; the model is a parameter.
- How it works: **browser automation, not an official API.** It starts a dedicated Chrome window and drives it via Chrome DevTools Protocol, clicking Flow's UI at "human-like pace", finding buttons by English labels, and adding `?hl=en` to URLs. It says it does not evade reCAPTCHA.
- Install on Windows (per README): clone, `npm install`, `npm run build`, `npm run login` (owner signs in by hand in the dedicated profile). Optional FFmpeg, whisper.cpp for captions, AI Studio key for Google voices. Config via `claude mcp add` or editing Claude Desktop config.
- Windows status: the README says it was developed and tested on macOS and "hasn't been run on a real PC yet".
- Source: https://github.com/GTAI-1/flow-mcp (README, GETTING-STARTED.md, OVERVIEW.md linked from it).

## 2. Authentication, safety, maintenance

- **Credentials:** no password is typed by the tool (per README). The Google session lives in a local Chrome profile at `~/.flow-mcp/chrome-profile`. A per-run local API token is at `~/.flow-mcp/token`; the local API listens on 127.0.0.1 only. A Google AI Studio key is stored locally or read from `GEMINI_API_KEY`, and the README says it is checked with Google when saved. Narration text goes to Google's TTS service. The README does not fully explain every outbound destination of the session data.
- **Our rule:** no stored credentials by us, owner signs in himself. flow-mcp's profile would hold the owner's live Google session on disk in a folder we do not control, and a second tool would have the same session. This is a step backwards from the current setup, where the built-in browser holds the session.
- **Maintenance:** public repo, 358 stars, 144 forks, 76 commits on `main`, 4 open issues, 12 open PRs. Last commit date and contributor count were NOT visible in the fetched page (not verified). Single-maintainer-looking; not verified.
- **License: NOT IDENTIFIED.** The README has a "Licence and risk" section but names no license, and no LICENSE file was found in the fetched material. With no license, we have no right to copy, modify or redistribute the code. This alone blocks adoption into the repository.
- **Risk signs:** no malware or exfiltration evidence was seen in the README. But the code was not read (only the README and linked docs), so this is not a code audit. Treat as untrusted third-party code.

## 3. Fit with our hard requirements

| Requirement | flow-mcp | Current Haiku method |
|---|---|---|
| 2K output, never smaller | Not stated in README; not verified | Yes, verified in runbook |
| Exact-title filing | `flow_download`, `flow_assets` exist; naming behaviour not verified | Yes, fail-closed script |
| Provenance (prompt hash, model, edit id, raw/clean hash) | Not provided by the tool; we would still build it | Partly, script logs hashes and edit id |
| Edit-first of an existing image | `flow_edit` exists | Yes, runbook section 15/17 |
| Batch of about 60 per Adhyay | Possible via tools; untested | Yes, done for Adhyay 1 |
| Model choice (Nano Banana Pro, 2.1) | Model is a parameter; Pro availability not verified | Yes, verified in UI |
| Owner signs in himself | Yes (login step) | Yes |
| Runs on Windows | Not yet run on a real PC (author says) | Yes, Adhyay 1 ran on this PC |

Cannot do from the README: guarantee 2K, guarantee exact filenames, provide provenance, or guarantee Pro model choice. These would still need our own checks.

## 4. Terms and rights

- **Flow terms:** Flow is a consumer tool, used via browser or app, requiring a Google AI plan in supported regions (Google Flow help: https://support.google.com/flow/answer/16353333). No official automation or developer access to Flow was found. Third-party sites mention a Flow API, but none is official and it could not be confirmed (https://www.stork.ai/es/google-flow, unverified).
- **General Google terms:** Google's terms restrict automated access and scraping, especially where machine-readable instructions prohibit it, and violations may lead to account suspension (secondary analysis: https://conductatlas.com/platform/google/google-terms-of-service/user-conduct-and-prohibited-behavior/ ; SEJ coverage of Google's warning on automated queries: https://searchenginejournal.com/google-warns-automated-queries-mean-third-party-tools/181385). No Flow-specific automation clause was found in the search results; the Flow product terms were not read. The flow-mcp README itself says automated use "may be against Google's terms of service".
- **Risk to the owner's account:** real. A suspension would cut off all linked Google services. The Haiku browser method carries similar exposure, so this is a shared risk we should state to the owner, but flow-mcp adds an unlicensed third-party program running against the account.
- **Rights in published film:** not decided by the tool. The README gives no image-use rights statement for Flow outputs. Flow's own output terms were not read; this must be checked by the owner before any film use of flow-mcp outputs.
- **Official alternative:** Nano Banana Pro is a Gemini-family model, which would normally be reached through Google's Gemini API or Vertex AI (documented route, not verified here for image generation or 2K output or pricing). Verify on https://ai.google.dev before relying on it. This would be the supported path if we ever want programmatic images.

## 5. Comparison

- **Owner effort:** flow-mcp needs Node 22+, Chrome, npm build, a login step, MCP config, and a persistent awake display. Current method needs the owner to sign in once per PC restart and check settings after restart.
- **Reliability:** flow-mcp is untested on Windows and breaks when Google changes Flow's labels. Current method also breaks on UI change, but the runbook coordinates are verified on this PC and the team has a working fallback.
- **Cost (credits):** both use Flow credits from the owner's plan. flow-mcp's stated goal is to use Flow credits instead of paid API. Neither is cheaper for the owner. Not measured.
- **Speed:** not measured for flow-mcp. Current method is slow (one generation at a time, 40-60 s each, many clicks) but has been run for Adhyay 1.
- **Failure modes:** flow-mcp adds a new one: a stale or broken Chrome profile on disk and an MCP tool that acts without the agent seeing each click. The current method keeps every step visible in screenshots and logs.
- **One tab per agent:** flow-mcp drives its own dedicated Chrome window, so the one-tab-per-agent model would not map directly; it would need its own multi-agent design.

## 6. Recommendation

**DO NOT USE.** Reasons, in order of weight: no license; Google terms risk on the owner's account; untested on Windows; session stored in a tool-controlled profile; no advantage on any hard requirement. Keep the Haiku-low browser method for Adhyay 2+ and fix its known faults inside the current pipeline (provenance per version, fewer clicks via tested runbook steps).

Not a TRIAL FIRST: the smallest trial would still run an unlicensed program against the owner's real Google account, which we should not do without a license and a code read.

## Risks

- Account suspension from automated use of Flow (Google terms; flow-mcp README itself warns).
- Unlicensed code: cannot legally adopt it.
- Unreviewed code: only the README was read. A code audit is needed before any run, which this task did not do.
- Session exposure: `~/.flow-mcp/chrome-profile` and `~/.flow-mcp/token` hold live session material on disk.
- Film rights for outputs: not established by the tool or by our reading of Flow's terms.
- Speculative API claims (Flow API, pricing) come from third-party sites and are not confirmed.

## Smallest safe next step

1. Owner decision: keep the Haiku-low browser method (no change to tooling).
2. Ask Google, via its official developer docs (https://ai.google.dev), whether an official image API gives Nano Banana Pro at 2K. If yes, that is the only route worth a trial, with a small paid-free test on one shot and our own provenance checks.
3. If the owner still wants flow-mcp: first get a license answer from its author, then read the code (not only the README) in a sandbox, and do not run it on the owner's real account.

## What I could not verify

- Last commit date and contributor count of flow-mcp (not shown in the fetched page).
- Whether flow-mcp's code matches its README (code not read; no install or run, per the research rules).
- Whether Flow outputs are watermarked or what the owner's usage rights are for film use.
- Whether flow-mcp can produce 2K downloads, exact filenames, or Pro model selection on Flow.
- Flow's own product terms (only general Google terms were found via search).
- Whether an official Google API exists for Flow or for Nano Banana Pro image generation at 2K, and its pricing. Searches found only third-party claims.
- Whether the Haiku browser method's account risk is acceptable to Google terms; that is a separate question not covered here.
