# Read-only RESEARCH: can the Flow image step use `flow-mcp` instead of a Haiku browser agent? (do NOT edit, install, clone, download or run anything; write only your own report file)

## Question from the owner
Today the image-generation step of the GranthStudio pipeline is done by **Haiku agents at LOW effort that operate Google Flow in the Claude built-in browser** (one tab per agent, the owner signs in; model Nano Banana Pro x1, then 2.1 x1 at the limit; 2K download; exact-title filing; edit-first for local defects). The owner asks: **can the same step be done in an easy way with the open-source project https://github.com/GTAI-1/flow-mcp ? If yes, we will switch to that way.**

## What we do today (read these local files first)
`docs/pilot/PIPELINE_README.md` section 9; `docs/pilot/HAIKU_FLOW_AGENT_BRIEF.md`; `docs/pilot/FLOW_RUNBOOK.md`; `docs/pilot/IMAGE_PROMPT_RULES.md`; scripts in `scripts/flow/`. Hard requirements: 2K output (never smaller), exact-title filing and a provenance record per chosen image (prompt hash, model, edit id, raw and cleaned hash), watermark handling, no stored credentials, the owner signs in himself, rights/terms must allow film use, runs on Windows, one picture for two audio languages (no per-language image work).

## Find out (use the web; cite URLs)
1. What `flow-mcp` actually is and does: tools it exposes, which Google product it drives (Flow / Imagen / Veo / Nano Banana), how it works (official API? browser automation? reverse-engineered web calls?), install and run steps on Windows, language and dependencies.
2. **Authentication and safety:** what credentials, cookies or tokens it needs and where it stores them; does it send them anywhere; any sign of risky behaviour. Maintenance state: stars, last commit date, open issues, license, number of maintainers. Treat it as UNTRUSTED third-party code.
3. **Fit:** can it do our hard requirements above (2K, exact filenames, edit-first of an existing image, batch of ~60 images per Adhyay, model choice, provenance data), and what it cannot.
4. **Terms and rights:** does using it violate Google's terms for Flow or the Gemini/Imagen APIs; any risk to the owner's Google account or to the rights to use the images in a published film.
5. **Compare** with the current Haiku-low browser method: effort for the owner, reliability, cost (credits), speed, failure modes, how the "one tab per agent" model maps.
6. **Recommendation**, honestly: ADOPT / TRIAL FIRST (describe the smallest safe trial and what must be reviewed before running anything) / DO NOT USE; and if there is an official, supported alternative (for example an official Google API or MCP for the same models) say so with the link.

## Output
A markdown report: a short **Answer** (yes/no/maybe in one line), then findings per question 1-6 with URLs, then `## Risks`, `## Smallest safe next step`, `## What I could not verify`. Be honest about uncertainty; do not guess. Do not reproduce long copyrighted text; summarise.
