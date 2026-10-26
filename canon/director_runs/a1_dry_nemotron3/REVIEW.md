# Director run, Adhyay 1 (9 scenes), director `nvidia/nemotron-3-ultra-550b-a55b`

DRAFT shot plans for the owner's review. Nothing is rendered or approved. VALID means the validator found no structural, quoting or provenance error AND every reviewer answered every blocking question 'yes'; it does not mean the plan is good. UNRESOLVED = at least one shot is NEED_NEW (never a success). NO_CHECK = a required check is missing (the owner may answer it). UNREVIEWED = no cross-check was run (never a success).

## Scene 1 (ovi 70-83): UNREVIEWED

- generate `nvidia/nemotron-3-ultra-550b-a55b`: HTTP 200, 160.4 s, finish stop

Warnings (for the owner; STAGING items need your approval):
- S1-1: STAGING scenery 'foreground tree line' needs the owner's approval
- S1-1: STAGING light 'daytime ambient light' needs the owner's approval
- S1-2: STAGING light 'midday sun' needs the owner's approval

**Goal:** Establish the historical setting of Shegaon in 1878 and introduce the young Gajanan Maharaj as an unknown yogi.
**Turn (A1:74):** Gajanan arrives in Shegaon in his prime youth on Magh Vadya Saptami.

### S1-1: 01_establishing_shot (6 s), ovi ['A1:70']
- action: camera dollies in over the village
- held pose: wide view of historical Shegaon with lake and village
- performance: the held pose shows the village and lake; narrator carries ovi 70
- camera: dolly in
- assets: {"fg": "shegaon_fg", "fx": "shegaon_fx", "mid": "shegaon_mid", "sky": "shegaon_sky"}
- claims: [{"kind": "scenery", "term": "Shegaon village", "source": "PACKET"}, {"kind": "scenery", "term": "lake (सरोवर)", "source": "PACKET"}, {"kind": "scenery", "term": "sky", "source": "PACKET"}, {"kind": "scenery", "term": "foreground tree line", "source": "STAGING"}, {"kind": "light", "term": "daytime ambient light", "source": "STAGING"}]
- staging: STAGING: caption '१८७८' appears on screen | STAGING: foreground frame includes tree line
- transition out: cut

### S1-2: 03_slow_cinematic_push (6 s), ovi ['A1:71', 'A1:72', 'A1:73', 'A1:74', 'A1:75', 'A1:76', 'A1:77', 'A1:78', 'A1:79', 'A1:80', 'A1:81', 'A1:82', 'A1:83']
- action: camera pushes in slowly on the young Gajanan
- held pose: young Gajanan seated on Shegaon road, wearing old bandi, holding clay chilim, gourd nearby
- performance: the held pose shows Gajanan as described; narrator carries ovi 71-83
- camera: push in
- assets: {"img": "gajanan_young_shegaon"}
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:74"}, {"kind": "prop", "term": "old worn bandi", "source": "PACKET"}, {"kind": "prop", "term": "unfired clay chilim", "source": "PACKET"}, {"kind": "prop", "term": "gourd water vessel", "source": "PACKET"}, {"kind": "scenery", "term": "Shegaon road", "source": "PACKET"}, {"kind": "pose", "term": "seated calm, gaze at nose tip", "source": "PACKET"}, {"kind": "light", "term": "midday sun", "source": "STAGING"}]
- staging: STAGING: midday sun lighting
- transition out: cut

**Images the owner would need to make:**
- shegaon_fg: foreground frame: tree line at village edge (used in S1-1)
- shegaon_fx: fx light: subtle dust motes in air (used in S1-1)
- shegaon_mid: mid subject: historical Shegaon village with lake (सरोवर) and clusters of houses (used in S1-1)
- shegaon_sky: sky: clear daytime sky over Vanhad region (used in S1-1)
- gajanan_young_shegaon: young Gajanan seated on Shegaon road, wearing old torn bandi, holding unfired clay chilim, gourd vessel beside him, calm posture, gaze at nose tip (used in S1-2)

## Scene 2 (ovi 84-96): UNREVIEWED

- generate `nvidia/nemotron-3-ultra-550b-a55b`: HTTP 200, 286.1 s, finish stop
- validator_repair `nvidia/nemotron-3-ultra-550b-a55b`: HTTP 200, 124.7 s, finish stop

Warnings (for the owner; STAGING items need your approval):
- S2-1: STAGING scenery 'doorway edge' needs the owner's approval

Repair `validator_repair` (scope ['S2-1', 'S2-5']): **USED**

**Goal:** Show Devidas's feast preparation, the stranger Gajanan picking leftover grains, and the teaching that food is Brahman.
**Turn (A1:94):** Gajanan picks up leftover rice grains to teach that food is Brahman.

### S2-1: 01_establishing_shot (6 s), ovi ['A1:84', 'A1:85', 'A1:86', 'A1:87']
- action: camera dollies in over the road
- held pose: the road with leaf plates in front of a house holds steady
- performance: the establishing shot reveals the feast aftermath
- camera: dolly in
- assets: {"fg": "estab_fg", "fx": "estab_fx", "mid": "estab_mid", "sky": "estab_sky"}
- claims: [{"kind": "scenery", "term": "road", "source": "A1:87"}, {"kind": "prop", "term": "leaf plates", "source": "A1:87"}, {"kind": "scenery", "term": "house front", "source": "A1:87"}, {"kind": "scenery", "term": "doorway edge", "source": "STAGING"}]
- staging: STAGING: sky layer added for depth | STAGING: foreground frame layer added | STAGING: light dust effect added
- transition out: cut

### S2-2: 02_environmental_parallax (6 s), ovi ['A1:87']
- action: camera pans laterally along the road
- held pose: leaf plates on the road remain in place across depth layers
- performance: the parallax move shows the extent of the discarded plates
- camera: pan right
- assets: {"far": "parallax_far", "mid": "parallax_mid", "near": "parallax_near", "sky": "parallax_sky"}
- claims: [{"kind": "scenery", "term": "road", "source": "A1:87"}, {"kind": "prop", "term": "leaf plates", "source": "A1:87"}]
- staging: STAGING: far layer shows distant road | STAGING: near layer shows foreground plates | STAGING: sky layer for atmosphere
- transition out: cut

### S2-3: 03_slow_cinematic_push (6 s), ovi ['A1:88', 'A1:89', 'A1:90', 'A1:91', 'A1:92', 'A1:93']
- action: camera pushes in slowly on the seated figure
- held pose: Gajanan sits on the road among leaf plates, wearing old bandi, gourd at side, chilim in hand, gaze at nose tip
- performance: the held pose shows his digambar state and ascetic radiance
- camera: push in
- assets: {"img": "gajanan_seated_wide"}
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:88"}, {"kind": "prop", "term": "old worn bandi", "source": "A1:88"}, {"kind": "prop", "term": "gourd water vessel", "source": "A1:89"}, {"kind": "prop", "term": "unfired clay chilim", "source": "A1:90"}, {"kind": "pose", "term": "nasagra drishti", "source": "A1:91"}, {"kind": "pose", "term": "calm posture", "source": "A1:91"}, {"kind": "pose", "term": "digambar", "source": "A1:92"}, {"kind": "event", "term": "searching leaf plates", "source": "A1:93"}, {"kind": "scenery", "term": "road", "source": "A1:87"}, {"kind": "prop", "term": "leaf plates", "source": "A1:87"}]
- staging: STAGING: vignette effect from preset
- transition out: cut

### S2-4: 03_slow_cinematic_push (6 s), ovi ['A1:88']
- action: camera continues pushing in slowly
- held pose: same seated pose holds
- performance: the continued push emphasizes his stillness
- camera: push in
- assets: {"img": "gajanan_seated_wide"}
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:88"}, {"kind": "prop", "term": "old worn bandi", "source": "A1:88"}, {"kind": "prop", "term": "gourd water vessel", "source": "A1:89"}, {"kind": "prop", "term": "unfired clay chilim", "source": "A1:90"}, {"kind": "pose", "term": "nasagra drishti", "source": "A1:91"}, {"kind": "pose", "term": "calm posture", "source": "A1:91"}, {"kind": "pose", "term": "digambar", "source": "A1:92"}]
- staging: STAGING: vignette effect from preset
- transition out: cut

### S2-5: 10_object_hand_insert (6 s), ovi ['A1:93', 'A1:94']
- action: camera pushes in slightly on the hand close-up
- held pose: hand picks a single rice grain from a leaf plate
- performance: the insert shows the grain-picking action that teaches annaparabrahma
- camera: push in
- assets: {"insert": "hand_picking_grain"}
- claims: [{"kind": "event", "term": "picking rice grain", "source": "A1:93"}, {"kind": "event", "term": "lifting to mouth", "source": "A1:94"}, {"kind": "prop", "term": "leaf plate", "source": "PACKET"}, {"kind": "prop", "term": "rice grain (shita)", "source": "A1:93"}, {"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:94"}]
- staging: STAGING: gloss and vignette from preset
- transition out: cut

### S2-6: 03_slow_cinematic_push (6 s), ovi ['A1:94']
- action: camera pushes in slowly on the face
- held pose: Gajanan's face calm, gaze steady, grain at lips
- performance: the close-up shows the moment of receiving the grain
- camera: push in
- assets: {"img": "gajanan_face_closeup"}
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:94"}, {"kind": "pose", "term": "calm face", "source": "A1:91"}, {"kind": "event", "term": "lifting grain to mouth", "source": "A1:94"}]
- staging: STAGING: vignette effect from preset
- transition out: cut

### S2-7: 08_emotional_closeup (6 s), ovi ['A1:95']
- action: camera pushes in closer with a soft halo
- held pose: Gajanan's face serene, eyes at nose tip
- performance: the emotional close-up underscores the teaching of annam brahma
- camera: push in with halo
- assets: {"face": "gajanan_face_closeup_transparent"}
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:95"}, {"kind": "pose", "term": "nasagra drishti", "source": "A1:91"}, {"kind": "event", "term": "teaching annam brahma", "source": "A1:95"}]
- staging: STAGING: halo effect from preset
- transition out: cut

### S2-8: 03_slow_cinematic_push (6 s), ovi ['A1:96']
- action: camera pushes in slowly on the wider scene
- held pose: Gajanan seated on road, plates around, compassionate presence
- performance: the wide shot shows the teacher of the common people
- camera: push in
- assets: {"img": "gajanan_seated_wide"}
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:96"}, {"kind": "event", "term": "compassion shows the meaning", "source": "A1:96"}, {"kind": "scenery", "term": "road with plates", "source": "A1:87"}]
- staging: STAGING: vignette effect from preset
- transition out: cut

### S2-9: 02_environmental_parallax (6 s), ovi ['A1:96']
- action: camera pans laterally away from the scene
- held pose: the road and plates remain across layers
- performance: the parallax pulls back to end the sequence
- camera: pan left
- assets: {"far": "parallax_far", "mid": "parallax_mid", "near": "parallax_near", "sky": "parallax_sky"}
- claims: [{"kind": "scenery", "term": "road", "source": "A1:87"}, {"kind": "prop", "term": "leaf plates", "source": "A1:87"}]
- staging: STAGING: far layer shows distance | STAGING: near layer shows foreground | STAGING: sky layer
- transition out: cut

### S2-10: 03_slow_cinematic_push (6 s), ovi ['A1:96']
- action: camera pushes in slowly to a final hold
- held pose: Gajanan seated, the scene settles
- performance: final push concludes the scene
- camera: push in
- assets: {"img": "gajanan_seated_wide"}
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:96"}, {"kind": "scenery", "term": "road", "source": "A1:87"}]
- staging: STAGING: vignette effect from preset
- transition out: cut

**Images the owner would need to make:**
- estab_fg: foreground frame layer: a doorway edge framing the road (used in S2-1)
- estab_fx: light dust effect layer: subtle dust motes in the air (used in S2-1)
- estab_mid: mid subject layer: the road in front of Devidas's house with used leaf plates scattered (used in S2-1)
- estab_sky: sky far layer: plain sky background (used in S2-1)
- parallax_far: far layer: distant road stretching into perspective (used in S2-2, S2-9)
- parallax_mid: mid layer: leaf plates on the road at middle distance (used in S2-2, S2-9)
- parallax_near: near layer: leaf plates close to camera (used in S2-2, S2-9)
- parallax_sky: sky layer for parallax: plain sky (used in S2-2, S2-9)
- gajanan_seated_wide: Gajanan seated on the road among leaf plates, wearing old worn bandi, gourd at side, unfired clay chilim in hand, gaze at nose tip, calm posture, digambar appearance (used in S2-3, S2-4, S2-8, S2-10)
- hand_picking_grain: close-up of a hand picking a single rice grain from a leaf plate (used in S2-5)
- gajanan_face_closeup: close-up of Gajanan's face, calm, gaze steady, grain at lips (used in S2-6)
- gajanan_face_closeup_transparent: close-up of Gajanan's face with transparent background for emotional close-up preset (used in S2-7)

## Scene 3 (ovi 97-105): INVALID

- generate `nvidia/nemotron-3-ultra-550b-a55b`: HTTP 200, 175.1 s, finish stop
- validator_repair `nvidia/nemotron-3-ultra-550b-a55b`: HTTP 200, 220.6 s, finish stop

Validator ERRORS:
- S3-1: action/performance describes motion the renderer cannot do ('walking'); show it as a held pose (held_pose) or use NEED_NEW
- S3-3: dialogue Marathi for A1:99 is not a substring of that ovi's text
- S3-3: dialogue Marathi for A1:99 is not a substring of that ovi's text
- S3-3: dialogue A1:99 by 'Bankatlal Agarwal' is not one of the character lines planned for this shot (exact Marathi, that character)
- S3-3: dialogue A1:99 by 'Damodarpant Kulkarni' is not one of the character lines planned for this shot (exact Marathi, that character)
- S3-3: dialogue A1:100 by 'unclear' is not one of the character lines planned for this shot (exact Marathi, that character)
- S3-3: dialogue A1:101 by 'unclear' is not one of the character lines planned for this shot (exact Marathi, that character)
- S3-5: dialogue A1:103 by 'unclear' is not one of the character lines planned for this shot (exact Marathi, that character)

Warnings (for the owner; STAGING items need your approval):
- S3-1: STAGING scenery 'sky' needs the owner's approval
- S3-1: STAGING light 'morning light' needs the owner's approval
- S3-2: STAGING scenery 'sky' needs the owner's approval
- S3-3: no staging line (every camera/light/pose choice should be labelled STAGING)
- S3-4: STAGING pose 'close-up face' needs the owner's approval
- S3-5: no staging line (every camera/light/pose choice should be labelled STAGING)
- S3-7: STAGING scenery 'sky' needs the owner's approval

Repair `validator_repair` (scope ['S3-1', 'S3-3', 'S3-5']): **REJECTED (still invalid: S3-1: action/performance describes motion the renderer cannot do ('walking'); show it as a held pose (held_pose) or use NEED_NEW)**

**Goal:** Show Bankatlal and Damodarpant encountering Maharaj, debating his nature, and deciding to test him.
**Turn (A1:102):** Bankatlal proposes they stand on the road and test Maharaj's conduct rather than dismiss him.

### S3-1: 01_establishing_shot (6 s), ovi ['A1:97', 'A1:98']
- action: camera dollies in slowly
- held pose: two men walk side by side on a dusty road stretching into distance
- performance: the held pose shows Bankatlal Agarwal and Damodarpant Kulkarni walking together on the road
- camera: dolly in from wide to medium
- assets: {"fg": "fg_road_frame", "fx": "fx_morning_light", "mid": "mid_bankatlal_damodarpant_walking", "sky": "sky_clear"}
- claims: [{"kind": "person", "term": "Bankatlal Agarwal", "source": "A1:97"}, {"kind": "person", "term": "Damodarpant Kulkarni", "source": "A1:97"}, {"kind": "scenery", "term": "road", "source": "A1:97"}, {"kind": "scenery", "term": "sky", "source": "STAGING"}, {"kind": "light", "term": "morning light", "source": "STAGING"}, {"kind": "pose", "term": "walking side by side", "source": "A1:97"}, {"kind": "camera", "term": "dolly in", "source": "STAGING"}]
- staging: STAGING: sky added for establishing shot | STAGING: morning light added for atmosphere | STAGING: foreground frame added for composition
- transition out: cut

### S3-2: 02_environmental_parallax (6 s), ovi ['A1:98']
- action: camera pans laterally through depth layers
- held pose: two men stand on road gazing at seated Maharaj in middle distance
- performance: the held pose shows Bankatlal and Damodarpant turned toward Maharaj with astonished posture
- camera: pan right across layers
- assets: {"far": "far_road_distant", "mid": "mid_maharaj_seated", "near": "near_bankatlal_damodarpant_standing", "sky": "sky_clear2"}
- claims: [{"kind": "scenery", "term": "road", "source": "A1:98"}, {"kind": "person", "term": "Shri Gajanan Maharaj", "source": "PACKET"}, {"kind": "person", "term": "Bankatlal Agarwal", "source": "A1:98"}, {"kind": "person", "term": "Damodarpant Kulkarni", "source": "A1:98"}, {"kind": "pose", "term": "standing gazing", "source": "A1:98"}, {"kind": "scenery", "term": "sky", "source": "STAGING"}, {"kind": "camera", "term": "lateral pan", "source": "STAGING"}]
- staging: STAGING: sky added for depth | STAGING: far road layer added for parallax
- transition out: cut

### S3-3: 09_dialogue_composition (6 s), ovi ['A1:99', 'A1:100', 'A1:101']
- action: camera drifts gently across the two faces
- held pose: Bankatlal and Damodarpant face each other, mouths closed, eyes intent
- performance: the held pose shows them in mid-conversation, each listening to the other
- camera: slow drift left to right
- assets: {"left": "left_bankatlal_facing", "right": "right_damodarpant_facing"}
- dialogue (A1:99, Bankatlal Agarwal): कीं याची करणी विपरीत। वेड्यापरी दिसतसे / His actions are contrary; he looks like a madman.
- dialogue (A1:99, Damodarpant Kulkarni): कीं याची करणी विपरीत। वेड्यापरी दिसतसे / His actions are contrary; he looks like a madman.
- dialogue (A1:100, unclear): हा अन्नार्थी जरी असतां। तरी पात्र मागून घेता। देवीदासही यातें देता। कां कीं तोही सज्जन / Even if he is a beggar, he would ask for a vessel; Devidas would give; for he is a good man.
- dialogue (A1:101, unclear): द्वारीं आलेला याचक। लावी ना सुज्ञ परत देख। कांहीं न चाले तर्क। कृतीवरुनी याच्या ह्या / A beggar came to the door; a wise host does not send him back; no reasoning fits; from his actions.
- claims: [{"kind": "person", "term": "Bankatlal Agarwal", "source": "A1:99"}, {"kind": "person", "term": "Damodarpant Kulkarni", "source": "A1:99"}, {"kind": "pose", "term": "facing each other", "source": "A1:99"}, {"kind": "event", "term": "conversation about Maharaj", "source": "A1:99"}, {"kind": "event", "term": "joint reasoning about beggar", "source": "A1:100"}, {"kind": "event", "term": "joint reasoning about host", "source": "A1:101"}]
- staging: 
- transition out: cut

### S3-4: 07_character_reaction (6 s), ovi ['A1:102']
- action: camera pushes in slowly on Bankatlal's face
- held pose: Bankatlal's face close-up, calm expression
- performance: the held pose shows Bankatlal looking thoughtful
- camera: push in
- assets: {"face": "face_bankatlal_closeup"}
- claims: [{"kind": "person", "term": "Bankatlal Agarwal", "source": "A1:102"}, {"kind": "pose", "term": "close-up face", "source": "STAGING"}, {"kind": "camera", "term": "push in", "source": "STAGING"}]
- staging: STAGING: close-up framing for character reaction
- transition out: cut

### S3-5: 09_dialogue_composition (6 s), ovi ['A1:102', 'A1:103']
- action: camera drifts gently across the two faces
- held pose: Bankatlal speaks, Damodarpant listens
- performance: the held pose shows Bankatlal addressing Damodarpant
- camera: slow drift left to right
- assets: {"left": "left_bankatlal_facing", "right": "right_damodarpant_facing"}
- dialogue (A1:102, Bankatlal Agarwal): ऐसेच उभें रस्‍त्यासी । आपण राहूं यत्कृतीसी । अजमावयाकारणें / Let us stand here on the road and test his actions.
- dialogue (A1:103, unclear): खरे साधु पिशापरी। जगीं वागती वरवरी। ऐसी व्यासाची वैखरी। बोलली आहे भागवतांत / True sadhus behave like madmen in the world; such is Vyasa's statement in the Bhagavat.
- claims: [{"kind": "person", "term": "Bankatlal Agarwal", "source": "A1:102"}, {"kind": "person", "term": "Damodarpant Kulkarni", "source": "A1:102"}, {"kind": "pose", "term": "facing each other", "source": "A1:102"}, {"kind": "event", "term": "Bankatlal proposes test", "source": "A1:102"}, {"kind": "event", "term": "reference to Bhagavat about sadhus", "source": "A1:103"}]
- staging: 
- transition out: cut

### S3-6: 03_slow_cinematic_push (6 s), ovi ['A1:104']
- action: camera pushes in slowly
- held pose: both men stand on road, gazing at Maharaj
- performance: the held pose shows them reflecting
- camera: push in
- assets: {"img": "img_both_men_standing_maharaj_bg"}
- claims: [{"kind": "person", "term": "Bankatlal Agarwal", "source": "A1:104"}, {"kind": "person", "term": "Damodarpant Kulkarni", "source": "A1:104"}, {"kind": "person", "term": "Shri Gajanan Maharaj", "source": "PACKET"}, {"kind": "scenery", "term": "road", "source": "A1:104"}, {"kind": "pose", "term": "standing gazing", "source": "A1:104"}, {"kind": "camera", "term": "push in", "source": "STAGING"}]
- staging: STAGING: camera push in for reflection
- transition out: cut

### S3-7: 02_environmental_parallax (6 s), ovi ['A1:105']
- action: camera pans laterally through depth layers
- held pose: two men remain on road, Maharaj seated in distance
- performance: the held pose shows the scene continuing unchanged
- camera: pan right across layers
- assets: {"far": "far_road_distant", "mid": "mid_maharaj_seated", "near": "near_bankatlal_damodarpant_standing", "sky": "sky_clear2"}
- claims: [{"kind": "scenery", "term": "road", "source": "A1:105"}, {"kind": "person", "term": "Shri Gajanan Maharaj", "source": "PACKET"}, {"kind": "person", "term": "Bankatlal Agarwal", "source": "A1:105"}, {"kind": "person", "term": "Damodarpant Kulkarni", "source": "A1:105"}, {"kind": "pose", "term": "standing gazing", "source": "A1:105"}, {"kind": "scenery", "term": "sky", "source": "STAGING"}, {"kind": "camera", "term": "lateral pan", "source": "STAGING"}]
- staging: STAGING: sky added for depth | STAGING: far road layer added for parallax
- transition out: cut

**Images the owner would need to make:**
- fg_road_frame: Foreground frame: dusty road edges with subtle texture, wide framing (used in S3-1)
- fx_morning_light: Morning light effect: soft glow over road, full frame (used in S3-1)
- mid_bankatlal_damodarpant_walking: Mid ground: Bankatlal Agarwal and Damodarpant Kulkarni walking side by side on road, full body, medium wide (used in S3-1)
- sky_clear: Sky: clear blue sky, wide (used in S3-1)
- far_road_distant: Far layer: road stretching into horizon, wide (used in S3-2, S3-7)
- mid_maharaj_seated: Mid layer: Shri Gajanan Maharaj seated on road in yogic posture, wearing old bandi, gourd and chilim nearby, medium (used in S3-2, S3-7)
- near_bankatlal_damodarpant_standing: Near layer: Bankatlal Agarwal and Damodarpant Kulkarni standing on road, turned toward mid, medium close (used in S3-2, S3-7)
- sky_clear2: Sky: clear blue sky, wide (for parallax) (used in S3-2, S3-7)
- left_bankatlal_facing: Left figure: Bankatlal Agarwal facing right, three-quarter profile, upper body, transparent background (used in S3-3, S3-5)
- right_damodarpant_facing: Right figure: Damodarpant Kulkarni facing left, three-quarter profile, upper body, transparent background (used in S3-3, S3-5)
- face_bankatlal_closeup: Close-up: Bankatlal Agarwal face, neutral thoughtful expression, tight framing (used in S3-4)
- img_both_men_standing_maharaj_bg: Full frame: Bankatlal Agarwal and Damodarpant Kulkarni standing on road, Shri Gajanan Maharaj seated in background, wide (used in S3-6)

## Scene 4 (ovi 108-112): UNREVIEWED

- generate `nvidia/nemotron-3-ultra-550b-a55b`: HTTP 200, 159.6 s, finish stop

Warnings (for the owner; STAGING items need your approval):
- S4-1: STAGING light 'daylight' needs the owner's approval
- S4-4: STAGING light 'daylight' needs the owner's approval

**Goal:** Show Bankatlal's humble inquiry, Gajanan's silent absorption, and the visitors' silent bow.
**Turn (A1:112):** The two visitors bow silently to the radiant yogi and find inner satisfaction.

### S4-1: 01_establishing_shot (6 s), ovi ['A1:108']
- action: camera dollies in from wide to medium
- held pose: wide view of road with leaf plates, Gajanan seated, Bankatlal stepping forward
- performance: the held pose shows the setting and Bankatlal's humble approach
- camera: dolly in 1.0 to 1.28
- assets: {"fg": "fg_frame", "fx": "fx_glow", "mid": "mid_scene", "sky": "sky_bg"}
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:108"}, {"kind": "person", "term": "Bankatlal Agarwal", "source": "A1:108"}, {"kind": "prop", "term": "leaf plates", "source": "PACKET"}, {"kind": "prop", "term": "old bandi", "source": "PACKET"}, {"kind": "prop", "term": "gourd vessel", "source": "PACKET"}, {"kind": "prop", "term": "unfired clay chilim", "source": "PACKET"}, {"kind": "scenery", "term": "road", "source": "PACKET"}, {"kind": "light", "term": "daylight", "source": "STAGING"}, {"kind": "pose", "term": "seated calm", "source": "A1:111"}, {"kind": "camera", "term": "dolly in", "source": "STAGING"}]
- staging: STAGING: daylight ambient light | STAGING: sky layer for establishing shot
- transition out: cut

### S4-2: 09_dialogue_composition (6 s), ovi ['A1:109']
- action: camera drifts gently across the two figures
- held pose: Bankatlal standing with hands folded, Gajanan seated calm
- performance: Bankatlal speaks the question, Gajanan listens silently
- camera: gentle drift left to right
- assets: {"left": "bankatlal_facing", "right": "gajanan_facing"}
- dialogue (A1:109, Bankatlal Agarwal): ह्या पत्रावळीच्या शोधना । कां हो करितां कळेना । क्षुधा असेल आपणां । तरी तरतूद करुं अन्नाची / Why do you search these plates? If you are hungry, we will arrange food.
- claims: [{"kind": "person", "term": "Bankatlal Agarwal", "source": "A1:109"}, {"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:109"}, {"kind": "prop", "term": "leaf plates", "source": "A1:109"}, {"kind": "pose", "term": "standing humble", "source": "A1:108"}, {"kind": "pose", "term": "seated calm", "source": "A1:111"}, {"kind": "camera", "term": "drift", "source": "STAGING"}]
- staging: STAGING: soft focus on faces
- transition out: cut

### S4-3: 03_slow_cinematic_push (6 s), ovi ['A1:110']
- action: camera pushes in slowly on Gajanan's face
- held pose: Gajanan seated, gaze lifted toward the two visitors
- performance: the held pose shows his steady gaze and absorbed attention
- camera: slow push in 1.0 to 1.2
- assets: {"img": "gajanan_looking_up"}
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:110"}, {"kind": "person", "term": "Bankatlal Agarwal", "source": "A1:110"}, {"kind": "person", "term": "Damodarpant Kulkarni", "source": "PACKET"}, {"kind": "pose", "term": "steady gaze", "source": "A1:111"}, {"kind": "pose", "term": "attention between eyebrows", "source": "A1:111"}, {"kind": "camera", "term": "push", "source": "STAGING"}]
- staging: STAGING: subtle halo around head to suggest radiance
- transition out: cut

### S4-4: 02_environmental_parallax (6 s), ovi ['A1:111']
- action: camera pans laterally through depth layers
- held pose: road with plates, Gajanan seated, Bankatlal nearby
- performance: the held pose shows the environment and the figures in place
- camera: lateral pan with parallax
- assets: {"far": "far_road", "mid": "mid_plates", "near": "near_bankatlal", "sky": "sky_bg"}
- claims: [{"kind": "scenery", "term": "road", "source": "PACKET"}, {"kind": "prop", "term": "leaf plates", "source": "PACKET"}, {"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:111"}, {"kind": "person", "term": "Bankatlal Agarwal", "source": "A1:108"}, {"kind": "person", "term": "Damodarpant Kulkarni", "source": "PACKET"}, {"kind": "light", "term": "daylight", "source": "STAGING"}, {"kind": "camera", "term": "parallax", "source": "STAGING"}]
- staging: STAGING: midday sun angle
- transition out: cut

### S4-5: 05_bowing_prayer (6 s), ovi ['A1:112']
- action: camera tilts down onto the bowing figures
- held pose: Bankatlal and Damodarpant bowing silently before Gajanan
- performance: the held pose shows silent namaskar and inner satisfaction
- camera: tilt down 1.12 to 1.26
- assets: {"pose": "both_bowing"}
- claims: [{"kind": "person", "term": "Bankatlal Agarwal", "source": "A1:112"}, {"kind": "person", "term": "Damodarpant Kulkarni", "source": "PACKET"}, {"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:112"}, {"kind": "pose", "term": "bowing", "source": "A1:112"}, {"kind": "event", "term": "silent namaskar", "source": "A1:112"}, {"kind": "camera", "term": "tilt", "source": "STAGING"}]
- staging: STAGING: soft halo around Gajanan
- transition out: cut

### S4-6: 03_slow_cinematic_push (6 s), ovi ['A1:112']
- action: camera pushes in slowly on the bowing figures
- held pose: both visitors remain bowed in silence
- performance: the held pose sustains the silent reverence
- camera: slow push in 1.0 to 1.2
- assets: {"img": "both_bowing"}
- claims: [{"kind": "person", "term": "Bankatlal Agarwal", "source": "A1:112"}, {"kind": "person", "term": "Damodarpant Kulkarni", "source": "PACKET"}, {"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:112"}, {"kind": "pose", "term": "bowed", "source": "A1:112"}, {"kind": "camera", "term": "push", "source": "STAGING"}]
- staging: STAGING: lingering silence
- transition out: cut

**Images the owner would need to make:**
- sky_bg: clear sky background for establishing and parallax shots (used in S4-1, S4-4)
- mid_scene: mid layer: road with leaf plates, Gajanan seated in old bandi, Bankatlal stepping forward (used in S4-1)
- fx_glow: fx layer: subtle glow around Gajanan to suggest radiance (used in S4-1)
- fg_frame: foreground frame: faint foliage edge for depth (used in S4-1)
- bankatlal_facing: Bankatlal standing, hands folded, facing Gajanan, transparent (used in S4-2)
- gajanan_facing: Gajanan seated calm, facing Bankatlal, transparent (used in S4-2)
- gajanan_looking_up: Gajanan seated, gaze lifted toward two visitors, steady gaze (used in S4-3)
- far_road: far layer: road stretching into distance (used in S4-4)
- mid_plates: mid layer: leaf plates scattered on road (used in S4-4)
- near_bankatlal: near layer: Bankatlal standing near plates (used in S4-4)
- both_bowing: both visitors bowing silently before Gajanan, Gajanan seated radiant (used in S4-5, S4-6)

## Scene 5 (ovi 113-118): UNREVIEWED

- generate `nvidia/nemotron-3-ultra-550b-a55b`: HTTP 200, 235.3 s, finish stop
- validator_repair `nvidia/nemotron-3-ultra-550b-a55b`: HTTP 200, 79.3 s, finish stop

Warnings (for the owner; STAGING items need your approval):
- S5-1: STAGING light 'subtle morning light' needs the owner's approval
- S5-2: STAGING light 'morning light' needs the owner's approval
- S5-3: no staging line (every camera/light/pose choice should be labelled STAGING)
- S5-4: STAGING light 'soft ambient light' needs the owner's approval
- S5-5: STAGING light 'soft halo' needs the owner's approval
- S5-6: STAGING light 'gentle light' needs the owner's approval
- S5-7: STAGING scenery 'road' needs the owner's approval
- S5-7: STAGING light 'midday light' needs the owner's approval
- S5-8: no staging line (every camera/light/pose choice should be labelled STAGING)
- S5-9: STAGING light 'subtle evening light' needs the owner's approval

Repair `validator_repair` (scope ['S5-5', 'S5-6', 'S5-7']): **USED**

**Goal:** Show Devidas bringing a plate of rich dishes to Gajanan, who mixes and eats without preference, while narrator gives two comparisons.
**Turn (A1:118):** Gajanan mixes all dishes and eats without like or dislike, satisfying his hunger.

### S5-1: 01_establishing_shot (6 s), ovi ['A1:113']
- action: camera dollies in slowly
- held pose: Gajanan Maharaj seated on the road, wearing old bandi, gourd and chilim at side, leaf plates scattered
- performance: shows Gajanan waiting calmly as the request to bring a plate is spoken
- camera: dolly in
- assets: {"fg": "fg_frame_road", "fx": "fx_light_subtle", "mid": "mid_gajanan_seated_road", "sky": "sky_morning"}
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:113"}, {"kind": "prop", "term": "old worn bandi", "source": "PACKET"}, {"kind": "prop", "term": "gourd vessel", "source": "PACKET"}, {"kind": "prop", "term": "unfired clay chilim", "source": "PACKET"}, {"kind": "scenery", "term": "road with leaf plates", "source": "PACKET"}, {"kind": "light", "term": "subtle morning light", "source": "STAGING"}]
- staging: STAGING: subtle morning light on road
- transition out: cut

### S5-2: 02_environmental_parallax (6 s), ovi ['A1:114']
- action: camera pans laterally through depth layers
- held pose: Devidas carries a plate of cooked dishes toward the door, Gajanan seated on road in background
- performance: shows Devidas bringing the full plate to place before Gajanan
- camera: pan right
- assets: {"far": "far_house_exterior", "mid": "mid_devidas_with_plate", "near": "near_plate_detail", "sky": "sky_morning"}
- claims: [{"kind": "person", "term": "Devidas", "source": "A1:114"}, {"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:114"}, {"kind": "prop", "term": "plate of cooked dishes", "source": "A1:114"}, {"kind": "scenery", "term": "house exterior with door", "source": "A1:114"}, {"kind": "scenery", "term": "road", "source": "PACKET"}, {"kind": "light", "term": "morning light", "source": "STAGING"}]
- staging: STAGING: morning light across layers
- transition out: slide

### S5-3: 10_object_hand_insert (6 s), ovi ['A1:114']
- action: camera pushes in on the plate
- held pose: close-up of plate filled with variety of rich cooked dishes
- performance: shows the richness of the offered food
- camera: push in
- assets: {"insert": "insert_plate_dishes"}
- claims: [{"kind": "prop", "term": "plate of cooked dishes", "source": "A1:114"}, {"kind": "prop", "term": "rich sweet dishes", "source": "A1:114"}]
- staging: 
- transition out: cut

### S5-4: 03_slow_cinematic_push (6 s), ovi ['A1:115']
- action: camera pushes in slowly
- held pose: Gajanan seated before the placed plate, calm posture, no taste preference
- performance: shows Gajanan beginning to eat with equanimity
- camera: push in
- assets: {"img": "img_gajanan_at_plate"}
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:115"}, {"kind": "prop", "term": "plate of cooked dishes", "source": "A1:115"}, {"kind": "pose", "term": "calm seated posture", "source": "A1:115"}, {"kind": "light", "term": "soft ambient light", "source": "STAGING"}]
- staging: STAGING: soft ambient light on figure
- transition out: slide

### S5-5: 08_emotional_closeup (6 s), ovi ['A1:116']
- action: camera pushes in closer with soft halo
- held pose: close-up of Gajanan's radiant face, steady gaze, attention between eyebrows
- performance: reflects the narrator's comparison of Brahman rasa
- camera: push in
- assets: {"face": "face_gajanan_closeup"}
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:116"}, {"kind": "pose", "term": "radiant complexion, steady gaze", "source": "PACKET"}, {"kind": "light", "term": "soft halo", "source": "STAGING"}]
- staging: STAGING: soft halo around face
- transition out: cut

### S5-6: 07_character_reaction (6 s), ovi ['A1:117']
- action: camera pushes in on face
- held pose: close-up of Gajanan's face, calm, absorbed
- performance: carries the narrator's second comparison of universal emperor
- camera: push in
- assets: {"face": "face_gajanan_closeup"}
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:117"}, {"kind": "pose", "term": "absorbed in inner bliss", "source": "PACKET"}, {"kind": "light", "term": "gentle light", "source": "STAGING"}]
- staging: STAGING: gentle light on face
- transition out: slide

### S5-7: 02_environmental_parallax (6 s), ovi ['A1:117']
- action: camera pans laterally through depth layers
- held pose: Gajanan eating from plate, road and house in background
- performance: continues the scene of the meal without narration
- camera: pan left
- assets: {"far": "far_house_exterior", "mid": "mid_gajanan_eating", "near": "near_plate_detail", "sky": "sky_morning"}
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:117"}, {"kind": "prop", "term": "plate of cooked dishes", "source": "A1:114"}, {"kind": "scenery", "term": "house exterior with door", "source": "A1:114"}, {"kind": "scenery", "term": "road", "source": "STAGING"}, {"kind": "light", "term": "midday light", "source": "STAGING"}]
- staging: STAGING: midday light across scene
- transition out: cut

### S5-8: 10_object_hand_insert (6 s), ovi ['A1:118']
- action: camera pushes in on the mixed food
- held pose: close-up of all dishes mixed into one in the plate
- performance: shows the mixing of dishes and absence of like or dislike
- camera: push in
- assets: {"insert": "insert_mixed_food"}
- claims: [{"kind": "prop", "term": "mixed cooked dishes", "source": "A1:118"}, {"kind": "event", "term": "mixing of all dishes", "source": "A1:118"}, {"kind": "pose", "term": "no taste preference", "source": "A1:118"}]
- staging: 
- transition out: slide

### S5-9: 01_establishing_shot (6 s), ovi ['A1:118']
- action: camera dollies in slowly
- held pose: Gajanan seated peacefully after meal, plate with mixed food before him
- performance: concludes the meal scene with satisfaction of digestive fire
- camera: dolly in
- assets: {"fg": "fg_frame_road", "fx": "fx_light_subtle", "mid": "mid_gajanan_satisfied", "sky": "sky_morning"}
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:118"}, {"kind": "prop", "term": "mixed cooked dishes", "source": "A1:118"}, {"kind": "scenery", "term": "road with leaf plates", "source": "PACKET"}, {"kind": "light", "term": "subtle evening light", "source": "STAGING"}]
- staging: STAGING: subtle evening light
- transition out: cut

**Images the owner would need to make:**
- sky_morning: sky far layer, early morning light (used in S5-1, S5-2, S5-7, S5-9)
- fg_frame_road: foreground frame: road edge with leaf plates (used in S5-1, S5-9)
- mid_gajanan_seated_road: mid subject: Gajanan Maharaj seated on road, wearing old bandi, digambar, with gourd and chilim (used in S5-1)
- fx_light_subtle: fx light layer: subtle glow (used in S5-1, S5-9)
- far_house_exterior: far layer: Devidas's house exterior with door (used in S5-2, S5-7)
- mid_devidas_with_plate: mid layer: Devidas walking with plate of cooked dishes (used in S5-2)
- near_plate_detail: near layer: plate with rich dishes (used in S5-2, S5-7)
- insert_plate_dishes: insert: close-up of plate filled with variety of cooked sweet dishes (used in S5-3)
- img_gajanan_at_plate: single image: Gajanan Maharaj seated before plate, calm posture, old bandi, gourd and chilim nearby (used in S5-4)
- face_gajanan_closeup: close-up face of Gajanan Maharaj, radiant complexion, steady gaze, attention between eyebrows (used in S5-5, S5-6)
- mid_gajanan_eating: mid layer: Gajanan Maharaj eating from plate, calm (used in S5-7)
- insert_mixed_food: insert: close-up of mixed dishes in plate, all combined into one (used in S5-8)
- mid_gajanan_satisfied: mid subject: Gajanan Maharaj seated after meal, peaceful, plate with mixed food (used in S5-9)

## Scene 6 (ovi 119-122): UNREVIEWED

- generate `nvidia/nemotron-3-ultra-550b-a55b`: HTTP 200, 184.5 s, finish stop

Warnings (for the owner; STAGING items need your approval):
- S6-6: preset 03_slow_cinematic_push used 3 times in a row

**Goal:** Bankatlal admits calling Gajanan mad was a mistake, compares him to Arjuna for Subhadra, declares no further test needed, and praises Shegaon as blessed by Hari.
**Turn (A1:119):** Bankatlal declares the 'mad' verdict a mistake and says no more testing is needed.

### S6-1: 09_dialogue_composition (6 s), ovi ['A1:119']
- action: camera drifts gently across the two figures
- held pose: Bankatlal and Damodarpant face each other, Bankatlal speaking
- performance: Bankatlal speaks, Damodarpant listens
- camera: gentle drift left to right
- assets: {"left": "bankatlal_left", "right": "damodarpant_right"}
- dialogue (A1:119, Bankatlal Agarwal): ह्या वेडा म्हणालों आपण । ती निःसंशय झाली चुकी / Calling him mad was surely our mistake.
- claims: [{"kind": "person", "term": "Bankatlal", "source": "A1:119"}, {"kind": "person", "term": "Damodarpant", "source": "A1:119"}, {"kind": "pose", "term": "Bankatlal speaking", "source": "A1:119"}, {"kind": "pose", "term": "Damodarpant listening", "source": "A1:119"}, {"kind": "scenery", "term": "road", "source": "PACKET"}, {"kind": "camera", "term": "gentle drift", "source": "STAGING"}]
- staging: STAGING: place figures on road with Devidas house door in background
- transition out: cut

### S6-2: 07_character_reaction (6 s), ovi ['A1:120']
- action: camera pushes in slowly on Bankatlal's face
- held pose: Bankatlal close-up, calm expression
- performance: Bankatlal continues speaking
- camera: slow push in
- assets: {"face": "bankatlal_face_closeup"}
- dialogue (A1:120, Bankatlal Agarwal): सुभद्रेसाठीं द्वारकेला । अर्जुन ऐसाच वेडा झाला / Like Arjuna went mad for Subhadra.
- claims: [{"kind": "person", "term": "Bankatlal", "source": "A1:120"}, {"kind": "pose", "term": "Bankatlal close-up speaking", "source": "A1:120"}, {"kind": "camera", "term": "slow push in", "source": "STAGING"}]
- staging: STAGING: close-up framing on Bankatlal face
- transition out: cut

### S6-3: 08_emotional_closeup (6 s), ovi ['A1:121']
- action: camera pushes in slowly with soft halo on Bankatlal's face
- held pose: Bankatlal close-up, earnest expression
- performance: Bankatlal finishes his argument
- camera: slow push in with halo
- assets: {"face": "bankatlal_face_emotional"}
- dialogue (A1:121, Bankatlal Agarwal): तैसाच हा ज्ञानजेठी । मुक्तिरुप सुभद्रेसाठीं । वेडा झाला कसवटी । याची आतां घेणें नको / Similarly this great knower became mad for liberation in the form of Subhadra; no need to test him now.
- claims: [{"kind": "person", "term": "Bankatlal", "source": "A1:121"}, {"kind": "pose", "term": "Bankatlal close-up earnest", "source": "A1:121"}, {"kind": "camera", "term": "slow push with halo", "source": "STAGING"}]
- staging: STAGING: soft halo effect for emotional beat
- transition out: cut

### S6-4: 03_slow_cinematic_push (6 s), ovi ['A1:121']
- action: camera pushes in slowly on the two figures
- held pose: Bankatlal and Damodarpant stand on road, silent
- performance: Silent pause as narration continues
- camera: slow push in
- assets: {"img": "both_figures_wide"}
- claims: [{"kind": "person", "term": "Bankatlal", "source": "A1:121"}, {"kind": "person", "term": "Damodarpant", "source": "A1:121"}, {"kind": "scenery", "term": "road", "source": "PACKET"}, {"kind": "pose", "term": "both standing", "source": "A1:121"}, {"kind": "camera", "term": "slow push in", "source": "STAGING"}]
- staging: STAGING: hold wide two-shot on road
- transition out: cut

### S6-5: 03_slow_cinematic_push (6 s), ovi ['A1:122']
- action: camera pushes in slowly on Shegaon village
- held pose: Wide view of Shegaon village
- performance: Narrator praises Shegaon
- camera: slow push in
- assets: {"img": "shegaon_landscape"}
- claims: [{"kind": "scenery", "term": "Shegaon village", "source": "A1:122"}, {"kind": "camera", "term": "slow push in", "source": "STAGING"}]
- staging: STAGING: establish Shegaon village landscape
- transition out: cut

### S6-6: 03_slow_cinematic_push (6 s), ovi ['A1:122']
- action: camera continues slow push on Shegaon village
- held pose: Shegaon village landscape held
- performance: Silent reflection
- camera: slow push in
- assets: {"img": "shegaon_landscape"}
- claims: [{"kind": "scenery", "term": "Shegaon village", "source": "A1:122"}, {"kind": "camera", "term": "slow push in", "source": "STAGING"}]
- staging: STAGING: continue Shegaon village landscape
- transition out: cut

**Images the owner would need to make:**
- bankatlal_left: Bankatlal standing, facing right, transparent pose for dialogue composition (used in S6-1)
- damodarpant_right: Damodarpant standing, facing left, transparent pose for dialogue composition (used in S6-1)
- bankatlal_face_closeup: Close-up of Bankatlal's face, calm expression, transparent (used in S6-2)
- bankatlal_face_emotional: Close-up of Bankatlal's face, earnest expression, transparent (used in S6-3)
- both_figures_wide: Wide shot of Bankatlal and Damodarpant standing on road, silent (used in S6-4)
- shegaon_landscape: Landscape of Shegaon village, establishing shot (used in S6-5, S6-6)

## Scene 7 (ovi 123-133): INVALID

- generate `nvidia/nemotron-3-ultra-550b-a55b`: HTTP 200, 257.2 s, finish stop

Validator ERRORS:
- shots/0/claims/3/kind: 'animal' is not one of ['person', 'prop', 'scenery', 'light', 'pose', 'camera', 'event']
- shots/0/claims/6/kind: 'fx' is not one of ['person', 'prop', 'scenery', 'light', 'pose', 'camera', 'event']

**Goal:** Show noon heat, empty gourd, Damodarpant's offer, Gajanan's teaching on worldly conduct, Bankatlal's joy, Damodarpant fetching water.
**Turn (A1:126):** Damodarpant offers to fetch water and Gajanan teaches that worldly conduct requires water after eating.

### S7-1: 01_establishing_shot (6 s), ovi ['A1:123', 'A1:124']
- action: camera dollies in slowly
- held pose: Gajanan seated calmly on hot ground, birds perched in trees above
- performance: shows Gajanan sitting blissfully in midday heat
- camera: dolly in slowly
- assets: {"sky": "sky_noon", "mid": "gajanan_seated_wide", "fx": "heat_haze_fx", "fg": "tree_birds_fg"}
- claims: [{"kind": "person", "term": "Gajanan", "source": "A1:124"}, {"kind": "scenery", "term": "hot ground", "source": "A1:123"}, {"kind": "scenery", "term": "trees", "source": "A1:123"}, {"kind": "animal", "term": "birds", "source": "A1:123"}, {"kind": "light", "term": "noon sun", "source": "A1:123"}, {"kind": "pose", "term": "seated calmly", "source": "A1:124"}, {"kind": "fx", "term": "heat haze", "source": "STAGING"}]
- staging: STAGING: heat haze shimmer on ground | STAGING: bright noon sky
- transition out: cut

### S7-2: 09_dialogue_composition (6 s), ovi ['A1:125', 'A1:126']
- action: camera drifts gently across both figures
- held pose: Bankatlal gesturing toward Damodarpant, Damodarpant standing attentively
- performance: shows Bankatlal urging Damodarpant to fetch water for Gajanan
- camera: gentle drift across both
- assets: {"left": "bankatlal_gesturing", "right": "damodarpant_listening"}
- claims: [{"kind": "person", "term": "Bankatlal", "source": "A1:125"}, {"kind": "person", "term": "Damodarpant", "source": "A1:125"}, {"kind": "pose", "term": "gesturing", "source": "A1:125"}, {"kind": "pose", "term": "standing attentively", "source": "STAGING"}]
- staging: STAGING: Bankatlal hand gesture indicating Gajanan's gourd
- transition out: cut

### S7-3: 09_dialogue_composition (6 s), ovi ['A1:126']
- action: camera drifts gently across both figures
- held pose: Damodarpant speaking with folded hands, Gajanan seated listening
- performance: shows Damodarpant humbly offering to bring water
- camera: gentle drift across both
- assets: {"left": "damodarpant_speaking", "right": "gajanan_listening"}
- dialogue (A1:126, Damodarpant Kulkarni): तुंब्यामध्यें नाहीं नीर । मर्जी असल्या हा चाकर । पाणी द्याया तयार असे / There is no water in your gourd; if you wish, this servant is ready to bring water.
- claims: [{"kind": "person", "term": "Damodarpant", "source": "A1:126"}, {"kind": "person", "term": "Gajanan", "source": "A1:126"}, {"kind": "prop", "term": "gourd (tumba)", "source": "A1:126"}, {"kind": "pose", "term": "speaking with folded hands", "source": "A1:126"}, {"kind": "pose", "term": "seated listening", "source": "A1:126"}]
- staging: STAGING: Damodarpant's folded hands gesture of service
- transition out: cut

### S7-4: 07_character_reaction (6 s), ovi ['A1:127']
- action: camera pushes in slowly on face
- held pose: Gajanan's face smiling in laughter, eyes looking toward both men
- performance: shows Gajanan laughing at Damodarpant's offer
- camera: push in slowly
- assets: {"face": "gajanan_face_laughing"}
- claims: [{"kind": "person", "term": "Gajanan", "source": "A1:127"}, {"kind": "pose", "term": "laughing", "source": "A1:127"}, {"kind": "event", "term": "Gajanan laughs", "source": "A1:127"}]
- staging: STAGING: soft morning light on face
- transition out: cut

### S7-5: 03_slow_cinematic_push (6 s), ovi ['A1:128']
- action: camera pushes in slowly
- held pose: Gajanan seated, one hand raised in teaching gesture, looking at both men
- performance: shows Gajanan explaining that one Brahman fills the world
- camera: push in slowly
- assets: {"img": "gajanan_teaching_medium"}
- dialogue (A1:128, Shri Gajanan Maharaj): तुम्हां गरज असेल जरी । तरी आणून घाला वारी । एक ब्रह्म जगदांतरीं । ओतप्रोत भरलें असें / Even if you need it, bring it; one Brahman pervades the world.
- claims: [{"kind": "person", "term": "Gajanan", "source": "A1:128"}, {"kind": "pose", "term": "teaching gesture", "source": "A1:128"}, {"kind": "event", "term": "Gajanan teaches oneness of Brahman", "source": "A1:128"}]
- staging: STAGING: calm background, no distractions
- transition out: cut

### S7-6: 03_slow_cinematic_push (6 s), ovi ['A1:128']
- action: camera pushes in slowly
- held pose: Gajanan seated, hand raised in teaching gesture, looking at both men
- performance: holds Gajanan's teaching pose as narration continues
- camera: push in slowly
- assets: {"img": "gajanan_teaching_medium"}
- claims: [{"kind": "person", "term": "Gajanan", "source": "A1:128"}, {"kind": "pose", "term": "teaching gesture", "source": "A1:128"}]
- staging: STAGING: continued calm background
- transition out: cut

### S7-7: 09_dialogue_composition (6 s), ovi ['A1:129']
- action: camera drifts gently across both figures
- held pose: Gajanan teaching, Bankatlal listening intently
- performance: shows Gajanan teaching no difference between them, worldly conduct must be followed
- camera: gentle drift across both
- assets: {"left": "gajanan_teaching_facing", "right": "bankatlal_listening"}
- dialogue (A1:129, Shri Gajanan Maharaj): तुम्ही आम्ही भेद तेथ । नाहीं उरला यत्किंचित । परी जगव्यवहार सत्य । आचरिला पाहिजे / There is no difference between you and me; yet worldly conduct is true and must be followed.
- claims: [{"kind": "person", "term": "Gajanan", "source": "A1:129"}, {"kind": "person", "term": "Bankatlal", "source": "A1:129"}, {"kind": "pose", "term": "teaching", "source": "A1:129"}, {"kind": "pose", "term": "listening intently", "source": "STAGING"}]
- staging: STAGING: Damodarpant also present but not in frame
- transition out: cut

### S7-8: 03_slow_cinematic_push (6 s), ovi ['A1:130', 'A1:131']
- action: camera pushes in slowly
- held pose: Gajanan seated, hand raised in teaching gesture
- performance: shows Gajanan explaining bodies ate food so need water, arrange it
- camera: push in slowly
- assets: {"img": "gajanan_teaching_medium"}
- dialogue (A1:130, Shri Gajanan Maharaj): अन्न भक्षिलें देहानीं । म्हणून त्या पाहिजे पाणी / Bodies have eaten food; therefore water is needed.
- claims: [{"kind": "person", "term": "Gajanan", "source": "A1:130"}, {"kind": "pose", "term": "teaching gesture", "source": "A1:130"}, {"kind": "event", "term": "Gajanan teaches practical conduct", "source": "A1:130"}]
- staging: STAGING: calm background
- transition out: cut

### S7-9: 09_dialogue_composition (6 s), ovi ['A1:132']
- action: camera drifts gently across both figures
- held pose: Bankatlal speaking joyfully, Damodarpant standing nearby
- performance: shows Bankatlal declaring their fortune blessed
- camera: gentle drift across both
- assets: {"left": "bankatlal_speaking_joyful", "right": "damodarpant_standing"}
- dialogue (A1:132, Bankatlal Agarwal): आपुलें आहे भाग्य धन्य / Our fortune is blessed.
- claims: [{"kind": "person", "term": "Bankatlal", "source": "A1:132"}, {"kind": "person", "term": "Damodarpant", "source": "A1:132"}, {"kind": "pose", "term": "speaking joyfully", "source": "A1:132"}, {"kind": "pose", "term": "standing", "source": "STAGING"}]
- staging: STAGING: both men emotionally moved
- transition out: cut

### S7-10: 02_environmental_parallax (6 s), ovi ['A1:133']
- action: camera pans laterally through depth layers
- held pose: Damodarpant walking toward house entrance, house exterior visible
- performance: shows Damodarpant entering Devidas's house to fetch water
- camera: pan right across layers
- assets: {"far": "house_exterior_far", "mid": "damodarpant_walking_mid", "near": "foreground_path_near", "sky": "sky_noon"}
- claims: [{"kind": "person", "term": "Damodarpant", "source": "A1:133"}, {"kind": "scenery", "term": "house exterior", "source": "A1:133"}, {"kind": "event", "term": "Damodarpant enters house", "source": "A1:133"}, {"kind": "light", "term": "noon sun", "source": "A1:123"}]
- staging: STAGING: house entrance visible, path in foreground
- transition out: cut

**Images the owner would need to make:**
- sky_noon: Bright noon sky, no clouds, for establishing and final shots (used in )
- gajanan_seated_wide: Gajanan seated on ground in worn bandi, wide framing showing hot ground around him (used in )
- heat_haze_fx: Subtle heat haze shimmer layer for midday heat effect (used in )
- tree_birds_fg: Tree branches with birds perched, foreground framing (used in )
- bankatlal_gesturing: Bankatlal standing, hand gesturing toward Damodarpant, transparent pose facing right (used in )
- damodarpant_listening: Damodarpant standing attentively, transparent pose facing left (used in )
- damodarpant_speaking: Damodarpant with folded hands speaking humbly, transparent pose facing right (used in )
- gajanan_listening: Gajanan seated listening calmly, transparent pose facing left (used in )
- gajanan_face_laughing: Close-up of Gajanan's face smiling in laughter, eyes directed sideways (used in )
- gajanan_teaching_medium: Gajanan seated, one hand raised in teaching gesture, medium framing (used in )
- gajanan_teaching_facing: Gajanan seated teaching, transparent pose facing right for dialogue composition (used in )
- bankatlal_listening: Bankatlal standing listening intently, transparent pose facing left (used in )
- bankatlal_speaking_joyful: Bankatlal standing speaking joyfully, transparent pose facing right (used in )
- damodarpant_standing: Damodarpant standing calmly, transparent pose facing left (used in )
- house_exterior_far: Devidas's house exterior at a distance, doorway visible (used in )
- damodarpant_walking_mid: Damodarpant walking toward house entrance, mid-ground (used in )
- foreground_path_near: Dirt path in foreground with subtle texture (used in )

## Scene 8 (ovi 134-137): UNREVIEWED

- generate `nvidia/nemotron-3-ultra-550b-a55b`: HTTP 200, 78.6 s, finish stop

Warnings (for the owner; STAGING items need your approval):
- S8-1: STAGING light 'daylight' needs the owner's approval
- S8-2: STAGING pose 'crouched drinking posture' needs the owner's approval

**Goal:** Show Gajanan drinking at the cattle trough, Damodarpant returning with vetiver-scented water and protesting the muddy water.
**Turn (A1:136):** Damodarpant objects to Gajanan drinking muddy trough water and offers his own clear, cool, vetiver-scented water.

### S8-1: 01_establishing_shot (6 s), ovi ['A1:134']
- action: camera dollies in slowly across the well and trough
- held pose: wide view of well with trough, cattle drinking, Gajanan approaching
- performance: narrator speaks ovi 134 describing the trough where animals drink
- camera: dolly in 1.0 to 1.28
- assets: {"fg": "fg_well_trough_frame", "fx": "fx_dust_light", "mid": "mid_cattle_trough", "sky": "sky_background"}
- claims: [{"kind": "scenery", "term": "well (कूप)", "source": "A1:134"}, {"kind": "scenery", "term": "trough (हाळ)", "source": "A1:134"}, {"kind": "person", "term": "cattle (जनावरें)", "source": "A1:134"}, {"kind": "person", "term": "Gajanan Maharaj", "source": "A1:134"}, {"kind": "event", "term": "cattle drinking water", "source": "A1:134"}, {"kind": "light", "term": "daylight", "source": "STAGING"}]
- staging: STAGING: daylight illumination | STAGING: dust motes in air
- transition out: cut

### S8-2: 03_slow_cinematic_push (6 s), ovi ['A1:135']
- action: camera pushes in slowly on Gajanan drinking
- held pose: Gajanan crouched at trough, drinking water, belching with satisfaction
- performance: narrator speaks ovi 135 first half: Gajanan drinks and belches
- camera: push in 1.0 to 1.2
- assets: {"img": "gajanan_drinking_trough"}
- claims: [{"kind": "person", "term": "Gajanan Maharaj", "source": "A1:135"}, {"kind": "event", "term": "drinking trough water", "source": "A1:135"}, {"kind": "event", "term": "belch (ढेकर)", "source": "A1:135"}, {"kind": "pose", "term": "crouched drinking posture", "source": "STAGING"}]
- staging: STAGING: held pose shows belch as subtle body movement
- transition out: cut

### S8-3: 04_character_entrance (6 s), ovi ['A1:135']
- action: camera pans with Damodarpant walking toward Gajanan
- held pose: Damodarpant carrying gadva approaches Gajanan at trough
- performance: narrator speaks ovi 135 second half: Damodarpant brings water in gadva
- camera: pan with character, zoom 1.0 to 1.14
- assets: {"char": "damodarpant_walking_gadva", "other": "gajanan_at_trough"}
- claims: [{"kind": "person", "term": "Damodarpant Kulkarni", "source": "A1:135"}, {"kind": "prop", "term": "gadva (earthen pot)", "source": "A1:135"}, {"kind": "person", "term": "Gajanan Maharaj", "source": "A1:135"}, {"kind": "event", "term": "Damodarpant arrives with water", "source": "A1:135"}]
- staging: STAGING: Damodarpant walking pose, Gajanan stationary
- transition out: cut

### S8-4: 09_dialogue_composition (6 s), ovi ['A1:136']
- action: camera drifts gently across the two figures
- held pose: Damodarpant gesturing protest, Gajanan listening calmly
- performance: Damodarpant speaks ovi 136; narrator carries any remaining narration
- camera: gentle drift, zoom 1.0 to 1.13
- assets: {"left": "damodarpant_facing_gajanan", "right": "gajanan_facing_damodarpant"}
- dialogue (A1:136, Damodarpant Kulkarni): हां हां तें गढूळ पाणी । समर्था न लावा वदनीं । तें जनावरालागुनी । योग्य आहे प्यावया / Oh! That muddy water. Samarth, don't put it to your mouth. It is fit for animals to drink.
- claims: [{"kind": "person", "term": "Damodarpant Kulkarni", "source": "A1:136"}, {"kind": "person", "term": "Gajanan Maharaj", "source": "A1:136"}, {"kind": "prop", "term": "muddy water (गढूळ पाणी)", "source": "A1:136"}, {"kind": "event", "term": "Damodarpant protests", "source": "A1:136"}]
- staging: STAGING: Damodarpant gesturing toward trough, Gajanan calm
- transition out: cut

### S8-5: 07_character_reaction (6 s), ovi ['A1:137']
- action: camera pushes in slowly on Damodarpant's face
- held pose: Damodarpant close-up, offering gadva, expression earnest
- performance: Damodarpant speaks ovi 137; narrator carries any remaining narration
- camera: push in 1.0 to 1.14
- assets: {"face": "damodarpant_face_closeup"}
- dialogue (A1:137, Damodarpant Kulkarni): मीं हें पहा आणिलें नीर । गोड निर्मळ थंडगार । वासित केलें साचार । वाळा घालून यामध्यें / See, I brought this water. Sweet, clear, cool. Scented with vetiver.
- claims: [{"kind": "person", "term": "Damodarpant Kulkarni", "source": "A1:137"}, {"kind": "prop", "term": "clear water (नीर)", "source": "A1:137"}, {"kind": "prop", "term": "vetiver (वाळा)", "source": "A1:137"}, {"kind": "event", "term": "offering vetiver-scented water", "source": "A1:137"}]
- staging: STAGING: close-up shows earnest expression, gadva in hand
- transition out: cut

### S8-6: 10_object_hand_insert (6 s), ovi ['A1:137']
- action: camera pushes in on the two water vessels
- held pose: close-up of gadva and trough water side by side
- performance: visual only, narrator silent
- camera: push in 1.04 to 1.18
- assets: {"insert": "gadva_trough_water_closeup"}
- claims: [{"kind": "prop", "term": "gadva with clear water", "source": "A1:137"}, {"kind": "prop", "term": "trough muddy water", "source": "A1:136"}, {"kind": "scenery", "term": "trough edge", "source": "A1:134"}]
- staging: STAGING: insert framing shows contrast of waters
- transition out: cut

### S8-7: 03_slow_cinematic_push (6 s), ovi ['A1:137']
- action: camera pushes in slowly on the two figures at trough
- held pose: Gajanan and Damodarpant at trough, gadva offered, moment suspended
- performance: visual only, narrator silent
- camera: push in 1.0 to 1.2
- assets: {"img": "both_at_trough_wide"}
- claims: [{"kind": "person", "term": "Gajanan Maharaj", "source": "A1:137"}, {"kind": "person", "term": "Damodarpant Kulkarni", "source": "A1:137"}, {"kind": "prop", "term": "gadva", "source": "A1:137"}, {"kind": "scenery", "term": "well and trough", "source": "A1:134"}]
- staging: STAGING: held pose shows tension of offer
- transition out: cut

**Images the owner would need to make:**
- fg_well_trough_frame: Foreground frame: well stones and trough edge, flat color (used in S8-1)
- fx_dust_light: Light dust layer with subtle glow (used in S8-1)
- mid_cattle_trough: Mid layer: cattle drinking at trough, Gajanan approaching (used in S8-1)
- sky_background: Sky far layer, plain daylight (used in S8-1)
- gajanan_drinking_trough: Gajanan crouched at trough drinking, belching, wearing old bandi, digambar (used in S8-2)
- damodarpant_walking_gadva: Damodarpant walking toward trough carrying gadva, transparent background (used in S8-3)
- gajanan_at_trough: Gajanan stationary at trough, transparent background (used in S8-3)
- damodarpant_facing_gajanan: Damodarpant facing right, gesturing, transparent (used in S8-4)
- gajanan_facing_damodarpant: Gajanan facing left, calm, transparent (used in S8-4)
- damodarpant_face_closeup: Close-up of Damodarpant face, earnest expression (used in S8-5)
- gadva_trough_water_closeup: Close-up insert of gadva and trough water side by side (used in S8-6)
- both_at_trough_wide: Wide shot of both figures at trough, gadva offered (used in S8-7)

## Scene 9 (ovi 138-144): INVALID

- generate `nvidia/nemotron-3-ultra-550b-a55b`: HTTP 200, 319.7 s, finish stop
- validator_repair `nvidia/nemotron-3-ultra-550b-a55b`: HTTP 200, 64.5 s, finish stop

Validator ERRORS:
- S9-9: action/performance describes motion the renderer cannot do ('point'); show it as a held pose (held_pose) or use NEED_NEW
- S9-11: action/performance describes motion the renderer cannot do ('run'); show it as a held pose (held_pose) or use NEED_NEW
- S9-13: scenery 'open landscape' is not in the owner's research (cite an ovi, or label it STAGING if it is only scenery/light/pose/camera)

Warnings (for the owner; STAGING items need your approval):
- S9-1: STAGING pose 'seated teaching' needs the owner's approval
- S9-1: STAGING pose 'seated listening' needs the owner's approval
- S9-2: STAGING pose 'close-up face' needs the owner's approval
- S9-2: STAGING light 'soft frontal light' needs the owner's approval
- S9-3: STAGING pose 'seated teaching full body' needs the owner's approval
- S9-4: STAGING pose 'seated teaching' needs the owner's approval
- S9-4: STAGING pose 'seated listening' needs the owner's approval
- S9-5: STAGING pose 'seated teaching full body' needs the owner's approval
- S9-6: STAGING pose 'emotional close-up face' needs the owner's approval
- S9-6: STAGING light 'soft halo' needs the owner's approval
- S9-7: STAGING pose 'close-up face' needs the owner's approval
- S9-7: STAGING light 'soft frontal light' needs the owner's approval
- S9-8: STAGING pose 'seated teaching full body' needs the owner's approval

Repair `validator_repair` (scope ['S9-11', 'S9-13', 'S9-9']): **REJECTED (still invalid: S9-9: action/performance describes motion the renderer cannot do ('point'); show it as a held pose (held_pose) or use NEED_NEW; S9-11: action/performance describes motion the renderer cannot do ('run'); show it as a held pose (held_pose) or use NEED_NEW)**

**Goal:** Maharaj teaches oneness of water and drinker in Brahman; men ready to surrender; Maharaj runs off like wind.
**Turn (A1:143):** Both men become ready to fall at Maharaj's feet

### S9-1: 09_dialogue_composition (6 s), ovi ['A1:138']
- action: camera drifts gently across the two figures facing each other
- held pose: Maharaj seated teaching, Bankatlal seated listening
- performance: Maharaj speaks the first teaching lines; Bankatlal listens attentively
- camera: gentle drift left to right
- assets: {"left": "maharaj_teaching_left", "right": "bankatlal_listening_right"}
- dialogue (A1:138, Shri Gajanan Maharaj): व्यावहारिक अवघ्या कथा । ह्या न सांगा आम्हां तुम्ही / Don't tell us worldly tales; all is pervaded by Brahman
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "PACKET"}, {"kind": "person", "term": "Bankatlal Agarwal", "source": "PACKET"}, {"kind": "pose", "term": "seated teaching", "source": "STAGING"}, {"kind": "pose", "term": "seated listening", "source": "STAGING"}, {"kind": "scenery", "term": "well area", "source": "PACKET"}]
- staging: STAGING: well and trough visible in background | STAGING: soft morning light
- transition out: cut

### S9-2: 07_character_reaction (6 s), ovi ['A1:139']
- action: camera pushes slowly into Maharaj's face
- held pose: Maharaj close-up, calm expression
- performance: Maharaj delivers the verse on Brahman pervading all
- camera: slow push in
- assets: {"face": "maharaj_face_closeup"}
- dialogue (A1:139, Shri Gajanan Maharaj): हें अवघें चरचर । ब्रह्में व्याप्त साचार । तेथें गढुळ,निर्मळ वासित नीर । हे न भेद राहिले / All this moving world is pervaded by Brahman; there muddy and clear water abide; no distinction remains
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "PACKET"}, {"kind": "pose", "term": "close-up face", "source": "STAGING"}, {"kind": "light", "term": "soft frontal light", "source": "STAGING"}]
- staging: STAGING: tight framing on eyes and forehead
- transition out: slide

### S9-3: 03_slow_cinematic_push (6 s), ovi ['A1:139']
- action: camera pushes slowly on full figure of Maharaj
- held pose: Maharaj seated teaching, hands resting on knees
- performance: Continued teaching, narrator carries the verse
- camera: slow push in
- assets: {"img": "maharaj_teaching_full"}
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "PACKET"}, {"kind": "pose", "term": "seated teaching full body", "source": "STAGING"}, {"kind": "scenery", "term": "well area", "source": "PACKET"}]
- staging: STAGING: maintain same background as previous
- transition out: cut

### S9-4: 09_dialogue_composition (6 s), ovi ['A1:140']
- action: camera drifts gently across the two figures
- held pose: Maharaj seated teaching, Bankatlal listening
- performance: Maharaj speaks on water's nature
- camera: gentle drift left to right
- assets: {"left": "maharaj_teaching_left", "right": "bankatlal_listening_right"}
- dialogue (A1:140, Shri Gajanan Maharaj): पाणी तरी तोच आहे । निर्मळ गढुळ तोच पाहे । सुवास कुवास दोन्ही हें । रुप त्याचें निःसंशय / Water is water in any form; muddy or clear, both are its forms; fragrance and stench both are its nature
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "PACKET"}, {"kind": "person", "term": "Bankatlal Agarwal", "source": "PACKET"}, {"kind": "pose", "term": "seated teaching", "source": "STAGING"}, {"kind": "pose", "term": "seated listening", "source": "STAGING"}, {"kind": "scenery", "term": "well area", "source": "PACKET"}]
- staging: STAGING: well and trough in background
- transition out: slide

### S9-5: 03_slow_cinematic_push (6 s), ovi ['A1:140']
- action: camera pushes slowly on Maharaj full figure
- held pose: Maharaj seated teaching
- performance: Narrator continues the teaching
- camera: slow push in
- assets: {"img": "maharaj_teaching_full"}
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "PACKET"}, {"kind": "pose", "term": "seated teaching full body", "source": "STAGING"}, {"kind": "scenery", "term": "well area", "source": "PACKET"}]
- staging: STAGING: consistent lighting
- transition out: cut

### S9-6: 08_emotional_closeup (6 s), ovi ['A1:141']
- action: camera pushes slowly closer with soft halo
- held pose: Maharaj close-up, serene emotional expression
- performance: Maharaj speaks on drinker and God's play
- camera: slow push in with halo
- assets: {"face": "maharaj_face_emotional"}
- dialogue (A1:141, Shri Gajanan Maharaj): पिणाराही वेगळा । त्यापासून ना निराळा । ईश्वराची अगाध लीला । ती कळे या नरजन्मीं / The drinker is not separate; God's unfathomable play is known in this human birth
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "PACKET"}, {"kind": "pose", "term": "emotional close-up face", "source": "STAGING"}, {"kind": "light", "term": "soft halo", "source": "STAGING"}]
- staging: STAGING: subtle halo around head
- transition out: slide

### S9-7: 07_character_reaction (6 s), ovi ['A1:142']
- action: camera pushes slowly into Maharaj's face
- held pose: Maharaj close-up, calm
- performance: Maharaj concludes teaching, urging reflection
- camera: slow push in
- assets: {"face": "maharaj_face_closeup"}
- dialogue (A1:142, Shri Gajanan Maharaj): तें दिलें टाकून । व्यवहारीं गोविलें मन । यांचेंच करा सदा मनन । कशापासून जग झालें / You dropped that; your mind is caught in dealings; reflect always on the origin of the world
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "PACKET"}, {"kind": "pose", "term": "close-up face", "source": "STAGING"}, {"kind": "light", "term": "soft frontal light", "source": "STAGING"}]
- staging: STAGING: tight framing on eyes
- transition out: cut

### S9-8: 03_slow_cinematic_push (6 s), ovi ['A1:142']
- action: camera pushes slowly on Maharaj full figure
- held pose: Maharaj seated teaching
- performance: Narrator carries the concluding verse
- camera: slow push in
- assets: {"img": "maharaj_teaching_full"}
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "PACKET"}, {"kind": "pose", "term": "seated teaching full body", "source": "STAGING"}, {"kind": "scenery", "term": "well area", "source": "PACKET"}]
- staging: STAGING: same background
- transition out: slide

### S9-9: 05_bowing_prayer (6 s), ovi ['A1:143']
- action: camera tilts down onto the contact point of their prostration
- held pose: Both men on knees, heads lowered toward Maharaj's feet
- performance: Men are ready to fall at his feet in surrender
- camera: tilt down
- assets: {"pose": "both_men_bowing_pose"}
- claims: [{"kind": "person", "term": "Bankatlal Agarwal", "source": "PACKET"}, {"kind": "person", "term": "Damodarpant Kulkarni", "source": "PACKET"}, {"kind": "pose", "term": "prostrate bowing", "source": "A1:143"}, {"kind": "scenery", "term": "well area", "source": "PACKET"}]
- staging: STAGING: dust motes in light
- transition out: cut

### S9-10: 03_slow_cinematic_push (6 s), ovi ['A1:143']
- action: camera pushes slowly on the bowing figures
- held pose: Both men remain bowed
- performance: Narrator describes their readiness
- camera: slow push in
- assets: {"img": "both_men_bowing_pose"}
- claims: [{"kind": "person", "term": "Bankatlal Agarwal", "source": "PACKET"}, {"kind": "person", "term": "Damodarpant Kulkarni", "source": "PACKET"}, {"kind": "pose", "term": "prostrate bowing", "source": "A1:143"}, {"kind": "scenery", "term": "well area", "source": "PACKET"}]
- staging: STAGING: hold the pose
- transition out: slide

### S9-11: 03_slow_cinematic_push (6 s), ovi ['A1:144']
- action: camera pushes slowly on Maharaj in mid-run
- held pose: Maharaj running swiftly, bandi fluttering
- performance: Maharaj runs off like the wind
- camera: slow push in
- assets: {"img": "maharaj_running_pose"}
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "PACKET"}, {"kind": "pose", "term": "running pose", "source": "A1:144"}, {"kind": "prop", "term": "old bandi", "source": "PACKET"}, {"kind": "scenery", "term": "open road", "source": "PACKET"}]
- staging: STAGING: motion blur suggested by pose
- transition out: cut

### S9-12: 01_establishing_shot (6 s), ovi ['A1:144']
- action: camera dollies forward revealing the wide landscape
- held pose: Wide view of Maharaj running away on road, well behind
- performance: Establishing his departure into the distance
- camera: dolly forward 1.0 to 1.28
- assets: {"fg": "fg_layer_ground", "fx": "fx_layer_dust", "mid": "mid_layer_running", "sky": "sky_layer"}
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "PACKET"}, {"kind": "scenery", "term": "road and well", "source": "PACKET"}, {"kind": "light", "term": "midday sun", "source": "PACKET"}, {"kind": "camera", "term": "dolly forward", "source": "STAGING"}]
- staging: STAGING: dust rising from road | STAGING: bright midday light
- transition out: pan_bridge

### S9-13: 02_environmental_parallax (6 s), ovi ['A1:144']
- action: camera pans laterally through depth layers
- held pose: Layered landscape with Maharaj disappearing into distance
- performance: Final view of his departure, no destination shown
- camera: lateral parallax
- assets: {"far": "far_layer", "mid": "mid_layer_parallax", "near": "near_layer", "sky": "sky_layer"}
- claims: [{"kind": "scenery", "term": "open landscape", "source": "PACKET"}, {"kind": "person", "term": "Shri Gajanan Maharaj", "source": "PACKET"}, {"kind": "camera", "term": "parallax pan", "source": "STAGING"}]
- staging: STAGING: layers move at different speeds
- transition out: cut

**Images the owner would need to make:**
- maharaj_teaching_left: Maharaj seated teaching, facing right, transparent layer for dialogue composition (used in S9-1, S9-4)
- bankatlal_listening_right: Bankatlal seated listening, facing left, transparent layer for dialogue composition (used in S9-1, S9-4)
- maharaj_face_closeup: Close-up of Maharaj's face, calm expression, transparent (used in S9-2, S9-7)
- maharaj_teaching_full: Full body of Maharaj seated teaching, hands on knees (used in S9-3, S9-5, S9-8)
- maharaj_face_emotional: Close-up of Maharaj's face with serene emotional expression, transparent (used in S9-6)
- both_men_bowing_pose: Both Bankatlal and Damodarpant on knees, heads lowered toward Maharaj's feet (used in S9-9, S9-10)
- maharaj_running_pose: Maharaj in mid-run, old bandi fluttering, dynamic pose (used in S9-11)
- sky_layer: Sky layer for establishing and parallax shots (used in S9-12, S9-13)
- mid_layer_running: Midground layer showing road and well for establishing shot (used in S9-12)
- fx_layer_dust: Dust effect layer for establishing shot (used in S9-12)
- fg_layer_ground: Foreground ground layer for establishing shot (used in S9-12)
- far_layer: Far distance landscape layer for parallax (used in S9-13)
- mid_layer_parallax: Midground landscape layer for parallax (used in S9-13)
- near_layer: Near foreground layer for parallax (used in S9-13)

