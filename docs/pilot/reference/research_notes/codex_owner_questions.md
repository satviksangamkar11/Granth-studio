I found **13 decisions that affect Phase 1 contracts or the Phase 2–4 work they must support**. The paid Kimi test, $3 cap, banned word, frozen research and owner-supplied images are treated as settled.

**SOURCE/CANON**

**1. How should passages recorded as thoughts—or not clearly spoken aloud—be heard in the film?**  
Why: the speech contract must distinguish narration, dialogue and inner speech; the packet explicitly preserves this distinction. [adhyay_02_analysis_v3.md:580](</D:/aai work/granthstudio/canon/packets/adhyay_02/frozen_copies/adhyay_02_analysis_v3.md:580>)  
Options: narrator describes them; character voices read them as thoughts; affected passages wait for your individual instructions. **Recommend:** narrator describes them, preserving the research’s uncertainty and adding no attribution.

**DIRECTOR CONTRACT**

**2. May the director propose neutral visual details that the research does not name, such as background sky or an unspecified object’s colour?**  
Why: the plan allows unnamed scenery if labelled `STAGING`, while the handoff requires packet-backed scenery and props—these produce different validator rules. [Approved plan:27](</C:/Users/Satvik/.claude/plans/elegant-doodling-dream.md:27>), [HANDOFF.md:38](</D:/aai work/granthstudio/docs/pilot/HANDOFF.md:38>)  
Options: forbid all unnamed details; allow labelled neutral details for your approval; require your approval of each detail before the director can use it. **Recommend:** allow labelled proposals, with approval required before production; never let staging add events, motives or miraculous causes.

**3. May a character speak an approved paraphrase, or must character speech always use the exact Marathi words?**  
Why: the existing contract permits marked paraphrases inside dialogue, but the future narration/quote distinction needs one unambiguous rule. [DIRECTOR_PROMPT_CHAIN.md:52](</D:/aai work/granthstudio/docs/pilot/DIRECTOR_PROMPT_CHAIN.md:52>), [director_test.py:174](</D:/aai work/granthstudio/scripts/source/director_test.py:174>)  
Options: exact words for characters, paraphrases through the narrator; approved paraphrases in character voices too. **Recommend:** exact character quotations, with paraphrases narrated.

**VALIDATOR/REVIEW**

**4. If a reviewer model times out or leaves a required question unanswered, may you complete that check yourself?**  
Why: missing checks must block approval, but the documents also make second-model checking optional in some circumstances. The runner needs a defined route to resolve that state. [DECISIONS.md:75](</D:/aai work/granthstudio/docs/DECISIONS.md:75>), [HANDOFF.md:38](</D:/aai work/granthstudio/docs/pilot/HANDOFF.md:38>)  
Options: wait for a complete model review; let you explicitly answer the missing checks; require both. **Recommend:** let you complete documented missing checks; a timeout itself never counts as a pass.

**RUNS/MANIFEST**

**5. Should your storyboard and Marathi narration approvals cover individual scenes or a whole chapter at once?**  
Why: Phase 1 must record exactly what you approved and invalidate affected approvals after changes; scene-by-scene narration approval remains an unapproved A3 reduction. [HANDOFF.md:39](</D:/aai work/granthstudio/docs/pilot/HANDOFF.md:39>), [HANDOFF.md:58](</D:/aai work/granthstudio/docs/pilot/HANDOFF.md:58>)  
Options: individual scenes; whole chapters; the complete combined film. **Recommend:** individual scenes, plus a separate combined-film approval for coverage, omissions and continuity. Source wording, narration and images still need distinct approval records.

**MONEY/PROVIDER**

**6. After you inspect Moonshot’s data terms, which project material may the adapter send there?**  
Why: today’s director receives frozen research, final answers, glossary and verse text—not merely public verses; Moonshot data terms remain open. [director_test.py:210](</D:/aai work/granthstudio/scripts/source/director_test.py:210>), [HANDOFF.md:58](</D:/aai work/granthstudio/docs/pilot/HANDOFF.md:58>)  
Options: the complete necessary text packet and drafts; public verses only; no transmission until the terms are acceptable. **Recommend:** approve the necessary text packet only after reviewing the terms. Verses alone would change the approved comparison’s inputs.

**7. What production route should the provider adapter anticipate after the evaluation?**  
Why: the handoff requires a production-permitted route, while Phase 1 currently specifies a Moonshot adapter for testing. [HANDOFF.md:39](</D:/aai work/granthstudio/docs/pilot/HANDOFF.md:39>), [HANDOFF.md:53](</D:/aai work/granthstudio/docs/pilot/HANDOFF.md:53>)  
Options: paid Moonshot, subject to verified terms; another provider you name; evaluation only, with production blocked until later. **Recommend:** keep Phase 1 evaluation-only unless you already choose a verified production route; preserve provider/model provenance so evaluation output cannot silently become production-approved.

**AUDIO/TIMING**

**8. Do you want one video with switchable Marathi/Hindi audio, or two separate videos?**  
Why: this directly determines shared versus independent picture schedules, speech coverage, captions and sound timing. [Approved plan:52](</C:/Users/Satvik/.claude/plans/elegant-doodling-dream.md:52>)  
Options: one video with two audio tracks; separate Marathi and Hindi videos using shared artwork. **Recommend:** two videos, allowing natural pacing in each language while reusing the pictures.

**9. For the first audio test, do you want one storyteller’s voice or separate voices for the characters—and recorded speech or synthetic speech?**  
Why: the contract needs stable speaker-to-voice assignments, voice references and approvals before measured timing can be trusted. [Approved plan:37](</C:/Users/Satvik/.claude/plans/elegant-doodling-dream.md:37>), [Approved plan:51](</C:/Users/Satvik/.claude/plans/elegant-doodling-dream.md:51>)  
Options: one synthetic narrator; your recorded narration; separate character voices with approved references. **Recommend:** one Indic Parler-TTS narrator candidate, compared with your recorded baseline; expand the cast only after listening approval.

**10. Who will approve Hindi meaning and pronunciation, and what must be reviewed again after an edit?**  
Why: Hindi approval remains open, and the contract must bind approval to the actual text and audio version. [DECISIONS.md:77](</D:/aai work/granthstudio/docs/DECISIONS.md:77>), [HANDOFF.md:58](</D:/aai work/granthstudio/docs/pilot/HANDOFF.md:58>)  
Options: you review every line; a named Hindi reviewer checks them and you approve; automated checks only. For revisions: whole scenes again, or changed lines with context. **Recommend:** human review of every line initially, then changed lines with surrounding context; listen again to changed audio.

**11. Which sound sources may the first test use?**  
Why: the closed sound palette needs real files and rights evidence, and its source policy remains unapproved. [Approved plan:54](</C:/Users/Satvik/.claude/plans/elegant-doodling-dream.md:54>), [DECISIONS.md:77](</D:/aai work/granthstudio/docs/DECISIONS.md:77>)  
Options: your recordings only; your recordings plus individually licence-checked CC0/CC-BY files; generated sound as well. **Recommend:** your recordings plus licence-checked CC0/CC-BY files, starting with two ambience beds and four to six effects—the smaller palette needs your A3 approval.

**IMAGES**

**12. May a storyboard pass review while its requested pictures are still missing?**  
Why: images are supplied only after storyboard approval, yet Phase 1 must validate asset bindings and distinguish executable shots from unresolved work. [HANDOFF.md:22](</D:/aai work/granthstudio/docs/pilot/HANDOFF.md:22>), [HANDOFF.md:38](</D:/aai work/granthstudio/docs/pilot/HANDOFF.md:38>)  
Options: storyboard approval may include clearly listed pending pictures; only shots using existing approved pictures may pass. **Recommend:** allow storyboard approval with explicit pending artwork; keep rendering blocked and report actual asset readiness separately from renderer capability.

**13. What artwork limit should the director work within, and which reuse methods are acceptable?**  
Why: reuse rules must be frozen before comparison, and new drawings versus adaptations must be counted separately. [Approved plan:60](</C:/Users/Satvik/.claude/plans/elegant-doodling-dream.md:60>), [HANDOFF.md:58](</D:/aai work/granthstudio/docs/pilot/HANDOFF.md:58>)  
Options: a hard number of new pictures per scene; an owner-hours budget; estimates and warnings until accepted-image time is measured. Reuse can permit crops/camera moves and repeated approved poses, or require fresh compositions. **Recommend:** permit faithful crops, camera moves and approved-pose reuse; track new drawings and adaptation time separately, with warnings until measurements support a hard budget.

No files modified, tests executed or provider calls made.