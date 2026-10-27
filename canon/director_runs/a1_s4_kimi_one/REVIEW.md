# Director run, Adhyay 1 (1 scenes), director `kimi-k3.1-pro`

DRAFT shot plans for the owner's review. Nothing is rendered or approved. VALID means the validator found no structural, quoting or provenance error AND every reviewer answered every blocking question 'yes'; it does not mean the plan is good. UNRESOLVED = at least one shot is NEED_NEW (never a success). NO_CHECK = a required check is missing (the owner may answer it). UNREVIEWED = no cross-check was run (never a success).

## Scene 4 (ovi 108-112): VALID

- generate `kimi-k3.1-pro`: HTTP 200, 121.6 s, finish stop
- review `nvidia/nemotron-3-ultra-550b-a55b`: HTTP 200, 308.0 s, finish stop

Warnings (for the owner; STAGING items need your approval):
- S4-1: STAGING light 'soft neutral daylight' needs the owner's approval
- S4-2: STAGING pose 'sustained humble questioning stance and seated stillness' needs the owner's approval
- S4-4: STAGING light 'soft close-up halo' needs the owner's approval

Reviewer `nvidia/nemotron-3-ultra-550b-a55b` (original plan): **PASS**

**Goal:** Bankatlal humbly questions Maharaj; Maharaj answers only with a steady look, and the visitors silently bow to the yogi absorbed in inner bliss.
**Turn (A1:112):** Seeing the yogi absorbed in inner bliss, the visitors gain satisfaction and bow to him in silence.

### S4-1: 01_establishing_shot (6 s), ovi ['A1:108', 'A1:109']
- action: Dollying toward Bankatlal standing before the seated Maharaj
- held pose: Bankatlal stands humbly ahead of Damodarpant, facing Maharaj among the used leaf plates.
- performance: The narrator introduces Bankatlal; his held questioning pose carries his offer to arrange food.
- camera: Slow dolly in across the layered road scene
- assets: {"fg": "s4_leafplates_foreground", "fx": "s4_soft_daylight", "mid": "s4_bankatlal_ahead", "sky": "s4_road_sky"}
- dialogue (A1:109, Bankatlal Agarwal): तुम्ही या उष्ट्या पत्रावळी का शोधत आहात ते कळत नाही; तुम्हाला भूक लागली असेल तर आम्ही जेवणाची सोय करतो. / I do not understand why you search these used plates; if you are hungry, we will arrange food.
- claims: [{"kind": "person", "term": "Bankatlal Agarwal", "source": "A1:108"}, {"kind": "person", "term": "Damodarpant Kulkarni and Shri Gajanan Maharaj", "source": "PACKET"}, {"kind": "event", "term": "Bankatlal is the first to come forward, with humility", "source": "A1:108"}, {"kind": "event", "term": "Bankatlal asks about the plate-searching and offers food", "source": "A1:109"}, {"kind": "prop", "term": "used leaf plates; old worn bandi; self-made unfired clay chilim; gourd", "source": "PACKET"}, {"kind": "scenery", "term": "road in front of Devidas's house", "source": "PACKET"}, {"kind": "pose", "term": "Bankatlal stands ahead with humility", "source": "A1:108"}, {"kind": "light", "term": "soft neutral daylight", "source": "STAGING"}, {"kind": "camera", "term": "layered dolly toward the group", "source": "STAGING"}]
- staging: STAGING: Fill the foreground with used plates, the midground with all three figures and the far layer with the house front.
- transition out: cut

### S4-2: 02_environmental_parallax (6 s), ovi ['A1:109']
- action: Panning laterally across Bankatlal and the silently seated Maharaj
- held pose: Bankatlal keeps his humble questioning stance while Damodarpant waits behind him and Maharaj remains seated.
- performance: The same question continues across the cut; Maharaj has not yet answered.
- camera: Gentle lateral move through the road layers
- assets: {"far": "s4_house_road_far", "mid": "s4_question_group", "near": "s4_leafplates_foreground", "sky": "s4_road_sky"}
- claims: [{"kind": "person", "term": "Bankatlal Agarwal, Damodarpant Kulkarni and Shri Gajanan Maharaj", "source": "PACKET"}, {"kind": "event", "term": "Bankatlal questions the searching of the plates and offers to arrange food", "source": "A1:109"}, {"kind": "prop", "term": "used leaf plates; old worn bandi; self-made unfired clay chilim; gourd", "source": "PACKET"}, {"kind": "scenery", "term": "road in front of Devidas's house", "source": "PACKET"}, {"kind": "pose", "term": "sustained humble questioning stance and seated stillness", "source": "STAGING"}, {"kind": "camera", "term": "lateral parallax across the group", "source": "STAGING"}]
- staging: STAGING: Preserve the opening poses and keep house, figures and plates in separate filled depth layers.
- transition out: cut

### S4-3: 03_slow_cinematic_push (6 s), ovi ['A1:110', 'A1:111']
- action: Pushing slowly toward Maharaj's raised, steady gaze
- held pose: Seated Maharaj looks up at both waiting faces, his broad chest, muscular upper arms and neck, and absorbed brow held still.
- performance: The narrator carries the unanswered question and the body description; everyone remains silent.
- camera: Slow push toward Maharaj with both visitors still visible
- assets: {"img": "s4_maharaj_looks_up"}
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj, Bankatlal Agarwal and Damodarpant Kulkarni", "source": "PACKET"}, {"kind": "event", "term": "Maharaj gives no answer and looks up at both faces", "source": "A1:110"}, {"kind": "light", "term": "radiant, charming complexion", "source": "A1:111"}, {"kind": "pose", "term": "muscular upper arms and neck, broad chest, steady gaze and attention between the eyebrows", "source": "A1:111"}, {"kind": "prop", "term": "used leaf plates; old worn bandi; self-made unfired clay chilim; gourd", "source": "PACKET"}, {"kind": "scenery", "term": "road in front of Devidas's house", "source": "PACKET"}, {"kind": "camera", "term": "slow push on the silent look", "source": "STAGING"}]
- staging: STAGING: Keep both visitors at the frame edges so Maharaj's look plainly addresses each face.
- transition out: cut

### S4-4: 08_emotional_closeup (6 s), ovi ['A1:112']
- action: Pushing slowly toward Maharaj's face absorbed in inner bliss
- held pose: Maharaj holds a steady, quiet expression absorbed in inner bliss.
- performance: The narrator begins the visitors' satisfaction and silent bow over this close view of the yogi.
- camera: Close, slow push with the preset soft halo
- assets: {"face": "s4_maharaj_inner_bliss_face"}
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:112"}, {"kind": "pose", "term": "a yogi absorbed in inner bliss", "source": "A1:112"}, {"kind": "light", "term": "soft close-up halo", "source": "STAGING"}, {"kind": "camera", "term": "quiet emotional close-up push", "source": "STAGING"}]
- staging: STAGING: Use a deliberate full-frame face close-up, keeping the expression unchanged.
- transition out: cut

### S4-5: 03_slow_cinematic_push (6 s), ovi ['A1:112']
- action: Pushing slowly toward the two visitors bowed before Maharaj
- held pose: Bankatlal and Damodarpant hold a silent namaskar before seated Maharaj, who remains absorbed in inner bliss.
- performance: The completed silent bow holds as the narration ends; nobody speaks.
- camera: Slow push across the full roadside composition
- assets: {"img": "s4_visitors_silent_bow"}
- claims: [{"kind": "person", "term": "Bankatlal Agarwal, Damodarpant Kulkarni and Shri Gajanan Maharaj", "source": "PACKET"}, {"kind": "event", "term": "the visitors silently bow after seeing the yogi", "source": "A1:112"}, {"kind": "pose", "term": "both visitors hold namaskar while Maharaj remains absorbed in inner bliss", "source": "A1:112"}, {"kind": "prop", "term": "used leaf plates; old worn bandi; self-made unfired clay chilim; gourd", "source": "PACKET"}, {"kind": "scenery", "term": "road in front of Devidas's house", "source": "PACKET"}, {"kind": "camera", "term": "slow push on the held silent bow", "source": "STAGING"}]
- staging: STAGING: Show the bow as a completed held pose, with the house front, seated Maharaj and used plates filling the background and foreground.
- transition out: cut

**Images the owner would need to make:**
- s4_road_sky: Quiet sky layer for the road outside Devidas's house, flat-colour illustration, no figures or text. (used in S4-1, S4-2)
- s4_soft_daylight: Subtle neutral daylight texture layer for the establishing shot, without rays or a suggested supernatural source. (used in S4-1)
- s4_bankatlal_ahead: Full roadside midground: humble Bankatlal stands ahead of Damodarpant before seated Maharaj; house front behind them, all three clearly drawn. (used in S4-1)
- s4_leafplates_foreground: Foreground layer of used leaf plates on the road, arranged to frame the group without hiding their feet or seated posture. (used in S4-1, S4-2)
- s4_house_road_far: Far layer showing the front of Devidas's house and road, fully drawn and consistent with the opening wide view. (used in S4-2)
- s4_question_group: Midground group continuing Bankatlal's question: Bankatlal humbly facing seated Maharaj, Damodarpant waiting behind; worn bandi, chilim and gourd consistent. (used in S4-2)
- s4_maharaj_looks_up: Full roadside scene: seated Maharaj looks up at both men's faces, radiant complexion, muscular upper arms and neck, broad chest, steady gaze and absorbed brow; visitors at edges. (used in S4-3)
- s4_maharaj_inner_bliss_face: Deliberate close-up of Maharaj's face, steady gaze and quiet absorption in inner bliss, unchanged held expression, transparent background. (used in S4-4)
- s4_visitors_silent_bow: Complete roadside illustration of Bankatlal and Damodarpant holding silent namaskar before seated Maharaj; house front, used plates, gourd and unfired clay chilim visible. (used in S4-5)

