# Director run, Adhyay 1 (1 scenes), director `nvidia/nemotron-3-ultra-550b-a55b`

DRAFT shot plans for the owner's review. Nothing is rendered or approved. VALID means the validator found no structural, quoting or provenance error AND every reviewer answered every blocking question 'yes'; it does not mean the plan is good. UNRESOLVED = at least one shot is NEED_NEW (never a success). NO_CHECK = a required check is missing (the owner may answer it). UNREVIEWED = no cross-check was run (never a success).

## Scene 4 (ovi 108-112): REVIEW_BLOCKED

- generate `nvidia/nemotron-3-ultra-550b-a55b`: HTTP 200, 238.0 s, finish stop
- validator_repair `nvidia/nemotron-3-ultra-550b-a55b`: HTTP 200, 40.2 s, finish stop
- review `z-ai/glm-5.3-flash`: HTTP 0, 120.1 s, finish None, error TimeoutError
- review `openai/gpt-oss-20b`: HTTP 200, 148.7 s, finish stop

Warnings (for the owner; STAGING items need your approval):
- S4-1: STAGING light 'natural daylight' needs the owner's approval
- S4-2: STAGING light 'daylight' needs the owner's approval
- S4-3: STAGING light 'soft lighting to emphasize radiance' needs the owner's approval
- S4-4: STAGING light 'calm ambient' needs the owner's approval
- S4-5: STAGING light 'morning sky' needs the owner's approval

Reviewer `openai/gpt-oss-20b` (original plan): **BLOCK**
- S4-1 [Q5] Preset 04_character_entrance requires a walking pose: "Character walks in toward a seated figure; camera pans with them." This violates the rule of no limb motion. Fix: Replace preset 04_character_entrance with a static pose preset such as 01_establishing_shot.
- S4-4 [Q5] Preset 05_bowing_prayer requires a bowing pose: "Bow / pranam: tilt down onto the contact point." Bowing involves limb motion, violating the rule. Fix: Replace preset 05_bowing_prayer with a static bow pose preset or a new preset that does not involve limb motion.

Reviewer `z-ai/glm-5.3-flash` (original plan): **NO_CHECK**, missing answers ['Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8', 'Q9', 'Q10']

Repair `validator_repair` (scope ['S4-4']): **USED**

**Goal:** Show Bankatlal humbly questioning Maharaj, Maharaj's silent radiant gaze, and the visitors' silent bow.
**Turn (A1:112):** The visitors bow silently in reverence, gaining inner satisfaction.

### S4-1: 04_character_entrance (6 s), ovi ['A1:108', 'A1:109']
- action: camera pans with Bankatlal walking toward seated Maharaj
- held pose: Bankatlal mid-step, hands folded; Maharaj seated calm, gaze forward
- performance: Bankatlal approaches humbly; Maharaj remains still, radiant
- camera: pan right following Bankatlal
- assets: {"char": "bankatlal_walking", "other": "maharaj_seated"}
- dialogue (A1:109, Bankatlal Agarwal): तुम्ही या उष्ट्या पत्रावळी का शोधत आहात ते कळत नाही; तुम्हाला भूक लागली असेल तर आम्ही जेवणाची सोय करतो. / You search these leaf plates for no clear reason; if you are hungry we will arrange food.
- claims: [{"kind": "person", "term": "Bankatlal Agarwal", "source": "A1:108"}, {"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:108"}, {"kind": "prop", "term": "old worn bandi", "source": "PACKET"}, {"kind": "prop", "term": "self-made unfired clay chilim", "source": "PACKET"}, {"kind": "prop", "term": "gourd water vessel", "source": "PACKET"}, {"kind": "scenery", "term": "road before Devidas's house", "source": "PACKET"}, {"kind": "pose", "term": "Bankatlal walking with folded hands", "source": "A1:108"}, {"kind": "pose", "term": "Maharaj seated calm", "source": "PACKET"}, {"kind": "light", "term": "natural daylight", "source": "STAGING"}, {"kind": "camera", "term": "pan right", "source": "STAGING"}, {"kind": "event", "term": "Bankatlal steps forward to question Maharaj", "source": "A1:108"}]
- staging: STAGING: natural daylight, road background with leaf plates
- transition out: cut

### S4-2: 03_slow_cinematic_push (6 s), ovi ['A1:109']
- action: slow push in on the wide scene
- held pose: same composition as previous shot, all figures static
- performance: scene holds, narrator continues Bankatlal's question
- camera: slow push in
- assets: {"img": "scene_wide_1"}
- claims: [{"kind": "person", "term": "Bankatlal Agarwal", "source": "A1:109"}, {"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:109"}, {"kind": "person", "term": "Damodarpant Kulkarni", "source": "PACKET"}, {"kind": "prop", "term": "used leaf plates", "source": "PACKET"}, {"kind": "prop", "term": "old worn bandi", "source": "PACKET"}, {"kind": "prop", "term": "self-made unfired clay chilim", "source": "PACKET"}, {"kind": "prop", "term": "gourd water vessel", "source": "PACKET"}, {"kind": "scenery", "term": "road before Devidas's house", "source": "PACKET"}, {"kind": "light", "term": "daylight", "source": "STAGING"}, {"kind": "camera", "term": "push in", "source": "STAGING"}]
- staging: STAGING: maintain same lighting and background
- transition out: cut

### S4-3: 07_character_reaction (6 s), ovi ['A1:110', 'A1:111']
- action: slow push on Maharaj's face
- held pose: Maharaj's face radiant, steady gaze, attention at brow
- performance: Maharaj looks up at both visitors silently; narrator describes his radiant form
- camera: slow push in
- assets: {"face": "maharaj_face_closeup"}
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:110"}, {"kind": "pose", "term": "radiant complexion", "source": "A1:111"}, {"kind": "pose", "term": "muscular upper arms and neck", "source": "A1:111"}, {"kind": "pose", "term": "broad chest", "source": "A1:111"}, {"kind": "pose", "term": "steady gaze", "source": "A1:111"}, {"kind": "pose", "term": "attention at eyebrows", "source": "A1:111"}, {"kind": "event", "term": "Maharaj looks up at both faces", "source": "A1:110"}, {"kind": "light", "term": "soft lighting to emphasize radiance", "source": "STAGING"}, {"kind": "camera", "term": "push in", "source": "STAGING"}]
- staging: STAGING: soft lighting to emphasize radiance
- transition out: cut

### S4-4: 05_bowing_prayer (6 s), ovi ['A1:112']
- action: camera tilts down to the bowed visitors
- held pose: Bankatlal and Damodarpant bowed in pranam, heads lowered, hands folded
- performance: held pose shows both visitors in silent reverence; narrator describes their inner satisfaction
- camera: tilt down
- assets: {"pose": "visitors_bowing"}
- claims: [{"kind": "person", "term": "Bankatlal Agarwal", "source": "A1:112"}, {"kind": "person", "term": "Damodarpant Kulkarni", "source": "A1:112"}, {"kind": "event", "term": "silent namaskar", "source": "A1:112"}, {"kind": "pose", "term": "bowing with folded hands", "source": "A1:112"}, {"kind": "light", "term": "calm ambient", "source": "STAGING"}, {"kind": "camera", "term": "tilt down", "source": "STAGING"}]
- staging: STAGING: quiet atmosphere, no extra effects
- transition out: cut

### S4-5: 02_environmental_parallax (6 s), ovi ['A1:112']
- action: lateral parallax move through depth layers
- held pose: layers hold: distant road, mid leaf plates, near Maharaj seated, sky above
- performance: scene lingers on the peaceful aftermath; narrator concludes
- camera: pan right with parallax
- assets: {"far": "far_road", "mid": "mid_plates", "near": "near_maharaj", "sky": "sky_morning"}
- claims: [{"kind": "scenery", "term": "road", "source": "PACKET"}, {"kind": "scenery", "term": "used leaf plates", "source": "PACKET"}, {"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:112"}, {"kind": "light", "term": "morning sky", "source": "STAGING"}, {"kind": "camera", "term": "parallax pan", "source": "STAGING"}]
- staging: STAGING: morning sky, gentle parallax
- transition out: cut

**Images the owner would need to make:**
- bankatlal_walking: Bankatlal Agarwal walking forward with folded hands, transparent pose, wearing simple cloth (used in S4-1)
- maharaj_seated: Shri Gajanan Maharaj seated on road, old worn bandi, self-made unfired clay chilim in hand, gourd water vessel nearby, radiant calm (used in S4-1)
- scene_wide_1: Wide view of road before Devidas's house with used leaf plates, Maharaj seated, Bankatlal standing near, Damodarpant behind, daylight (used in S4-2)
- maharaj_face_closeup: Close-up of Maharaj's face showing radiant complexion, steady gaze, attention at eyebrows, muscular neck (used in S4-3)
- visitors_bowing: Bankatlal and Damodarpant bowing in pranam, heads lowered, hands folded, transparent pose (used in S4-4)
- far_road: Distant road layer with perspective, empty, morning light (used in S4-5)
- mid_plates: Midground layer of used leaf plates scattered on road (used in S4-5)
- near_maharaj: Near layer showing Maharaj seated with bandi, chilim, gourd (used in S4-5)
- sky_morning: Morning sky layer, soft light, no clouds (used in S4-5)

