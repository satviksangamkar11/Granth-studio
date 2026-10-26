# Director run, Adhyay 1 (9 scenes), director `nvidia/nemotron-3-ultra-550b-a55b`

DRAFT shot plans for the owner's review. Nothing is rendered or approved. VALID means the validator found no structural, quoting or provenance error AND every reviewer answered every blocking question 'yes'; it does not mean the plan is good. UNRESOLVED = at least one shot is NEED_NEW (never a success). NO_CHECK = a required check is missing (the owner may answer it). UNREVIEWED = no cross-check was run (never a success).

## Scene 1 (ovi 70-83): UNREVIEWED

- generate `nvidia/nemotron-3-ultra-550b-a55b`: HTTP 200, 151.9 s, finish stop
- validator_repair `nvidia/nemotron-3-ultra-550b-a55b`: HTTP 200, 31.2 s, finish stop

Warnings (for the owner; STAGING items need your approval):
- S1-1: STAGING scenery 'village houses' needs the owner's approval
- S1-1: STAGING scenery 'distant trees' needs the owner's approval
- S1-1: STAGING light 'daylight' needs the owner's approval
- S1-2: STAGING light 'daylight' needs the owner's approval

Repair `validator_repair` (scope ['S1-1']): **USED**

**Goal:** Establish the historical setting of Shegaon in 1878 and introduce the young Gajanan Maharaj as an enigmatic figure whose origins are untraceable.
**Turn (A1:70):** The narrator states that the great man's place and caste cannot be traced historically.

### S1-1: 01_establishing_shot (6 s), ovi ['A1:70']
- action: camera dollies in slowly over the village landscape
- held pose: wide view of historical Shegaon with pond and village
- performance: held pose shows the village of Shegaon in 1878; narrator speaks ovi 70
- camera: dolly in from 1.0 to 1.28
- assets: {"fg": "shegaon_fg", "fx": "shegaon_fx", "mid": "shegaon_mid", "sky": "shegaon_sky"}
- claims: [{"kind": "scenery", "term": "Shegaon village", "source": "PACKET"}, {"kind": "scenery", "term": "pond", "source": "PACKET"}, {"kind": "scenery", "term": "village houses", "source": "STAGING"}, {"kind": "scenery", "term": "distant trees", "source": "STAGING"}, {"kind": "light", "term": "daylight", "source": "STAGING"}, {"kind": "camera", "term": "dolly in", "source": "STAGING"}, {"kind": "camera", "term": "caption 1878", "source": "STAGING"}]
- staging: STAGING: daylight lighting | STAGING: dolly in camera move | STAGING: on-screen caption 1878 | STAGING: village houses in mid layer | STAGING: distant trees in mid layer
- transition out: cut

### S1-2: 03_slow_cinematic_push (6 s), ovi ['A1:71', 'A1:72', 'A1:73', 'A1:74', 'A1:75', 'A1:76', 'A1:77', 'A1:78', 'A1:79', 'A1:80', 'A1:81', 'A1:82', 'A1:83']
- action: camera pushes in slowly on the figure
- held pose: young Gajanan Maharaj seated on the road in Shegaon, wearing worn bandi, otherwise bare, with gourd and clay chilim, calm gaze at nose tip
- performance: held pose shows the young Gajanan in Shegaon; no narration in this shot
- camera: push in from 1.0 to 1.2
- assets: {"img": "gajanan_young_shegaon"}
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "PACKET"}, {"kind": "prop", "term": "worn old bandi", "source": "PACKET"}, {"kind": "prop", "term": "gourd water vessel", "source": "PACKET"}, {"kind": "prop", "term": "unfired clay chilim", "source": "PACKET"}, {"kind": "scenery", "term": "road in Shegaon", "source": "PACKET"}, {"kind": "pose", "term": "seated calm, gaze at nose tip", "source": "PACKET"}, {"kind": "light", "term": "daylight", "source": "STAGING"}, {"kind": "camera", "term": "slow push in", "source": "STAGING"}]
- staging: STAGING: daylight lighting | STAGING: slow push in camera
- transition out: cut

**Images the owner would need to make:**
- shegaon_sky: sky layer for historical Shegaon, clear daytime (used in S1-1)
- shegaon_mid: mid layer showing Shegaon village with pond, houses, and distant trees (used in S1-1)
- shegaon_fx: fx layer for atmospheric light and dust (used in S1-1)
- shegaon_fg: foreground frame elements like foliage or archway (used in S1-1)
- gajanan_young_shegaon: young Gajanan Maharaj seated on road in Shegaon, wearing worn bandi, otherwise bare, with gourd and clay chilim, calm gaze at nose tip (used in S1-2)

## Scene 2 (ovi 84-96): UNREVIEWED

- generate `nvidia/nemotron-3-ultra-550b-a55b`: HTTP 200, 234.3 s, finish stop
- validator_repair `nvidia/nemotron-3-ultra-550b-a55b`: HTTP 200, 38.8 s, finish stop

Warnings (for the owner; STAGING items need your approval):
- S2-2: no staging line (every camera/light/pose choice should be labelled STAGING)
- S2-3: no staging line (every camera/light/pose choice should be labelled STAGING)
- S2-4: no staging line (every camera/light/pose choice should be labelled STAGING)
- S2-5: no staging line (every camera/light/pose choice should be labelled STAGING)
- S2-6: no staging line (every camera/light/pose choice should be labelled STAGING)
- S2-7: no staging line (every camera/light/pose choice should be labelled STAGING)
- S2-8: no staging line (every camera/light/pose choice should be labelled STAGING)

Repair `validator_repair` (scope ['S2-5']): **USED**

**Goal:** Show Devidas's feast preparations, the stranger Gajanan seated on the road picking leftover rice grains, and the narrator's teaching that food is Brahman.
**Turn (A1:94):** Gajanan picks up each rice grain he sees and puts it in his mouth to teach 'annaparabrahma'.

### S2-1: 01_establishing_shot (6 s), ovi ['A1:84', 'A1:85', 'A1:86', 'A1:87']
- action: camera dollies in over the road and house
- held pose: wide view of Devidas's house with leaf plates scattered on the road in front
- performance: the narrator introduces Devidas and describes the leaf plates thrown on the road
- camera: dolly in from wide to medium-wide
- assets: {"fg": "s2_estab_fg", "fx": "s2_estab_fx", "mid": "s2_estab_mid", "sky": "s2_estab_sky"}
- claims: [{"kind": "person", "term": "Devidas", "source": "A1:84"}, {"kind": "person", "term": "Devidas", "source": "A1:85"}, {"kind": "event", "term": "feast preparation for son's Ritushanti", "source": "A1:86"}, {"kind": "scenery", "term": "house", "source": "A1:87"}, {"kind": "scenery", "term": "road", "source": "A1:87"}, {"kind": "prop", "term": "leaf plates (पत्रावळी)", "source": "A1:87"}]
- staging: STAGING: early morning light suggested by context
- transition out: cut

### S2-2: 03_slow_cinematic_push (6 s), ovi ['A1:87']
- action: camera pushes in slowly on the leaf plates
- held pose: close view of used leaf plates on the road
- performance: the narrator's words about Devidas end; the view settles on the plates
- camera: slow push in
- assets: {"img": "s2_push_plates"}
- claims: [{"kind": "prop", "term": "leaf plates (पत्रावळी)", "source": "A1:87"}, {"kind": "scenery", "term": "road", "source": "A1:87"}]
- staging: 
- transition out: slide

### S2-3: 03_slow_cinematic_push (6 s), ovi ['A1:88']
- action: camera pushes in slowly on Gajanan seated
- held pose: Gajanan seated on the road, wearing a worn old bandi
- performance: the narrator describes Gajanan as a siddha yogi seated there
- camera: slow push in
- assets: {"img": "s2_push_gajanan_seated"}
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:88"}, {"kind": "prop", "term": "bandi (old worn cloth)", "source": "A1:88"}, {"kind": "scenery", "term": "road", "source": "A1:88"}]
- staging: 
- transition out: cut

### S2-4: 10_object_hand_insert (6 s), ovi ['A1:88', 'A1:89', 'A1:90', 'A1:91', 'A1:92']
- action: camera pushes in slightly on the hand holding the chilim
- held pose: Gajanan's hand holding a self-made unfired clay chilim, a gourd resting beside him
- performance: the view shows his only possessions: the chilim and gourd
- camera: slow push in
- assets: {"insert": "s2_insert_chilim_gourd"}
- claims: [{"kind": "prop", "term": "chilim (कच्ची चिलीम)", "source": "A1:90"}, {"kind": "prop", "term": "gourd (भोपळा)", "source": "A1:89"}, {"kind": "pose", "term": "hand holding chilim", "source": "A1:90"}, {"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:88"}]
- staging: 
- transition out: cut

### S2-5: 10_object_hand_insert (6 s), ovi ['A1:93', 'A1:94']
- action: camera pushes in on the hand holding a grain
- held pose: hand holding a single rice grain near the mouth
- performance: the held pose shows the grain at the mouth; the narrator explains this teaches 'annaparabrahma'
- camera: slow push in
- assets: {"insert": "s2_insert_picking_grain"}
- claims: [{"kind": "event", "term": "picking rice grain (शीत)", "source": "A1:93"}, {"kind": "prop", "term": "leaf plate (पत्रावळी)", "source": "PACKET"}, {"kind": "prop", "term": "rice grain (शीत)", "source": "A1:93"}, {"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:93"}]
- staging: 
- transition out: cut

### S2-6: 03_slow_cinematic_push (6 s), ovi ['A1:94']
- action: camera pushes in slowly on Gajanan seated
- held pose: Gajanan seated calmly after picking the grain
- performance: the narrator's teaching about food as Brahman continues visually
- camera: slow push in
- assets: {"img": "s2_push_gajanan_eating"}
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:94"}, {"kind": "pose", "term": "calm seated posture", "source": "A1:91"}, {"kind": "event", "term": "teaching annaparabrahma", "source": "A1:94"}]
- staging: 
- transition out: cut

### S2-7: 08_emotional_closeup (6 s), ovi ['A1:95']
- action: camera pushes in slowly on Gajanan's face
- held pose: Gajanan's face with gaze at nose tip, calm expression
- performance: the narrator recites the Shruti verse 'annam brahma'
- camera: slow push in with soft halo
- assets: {"face": "s2_face_gajanan_teaching"}
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:95"}, {"kind": "pose", "term": "nasagra drishti", "source": "A1:91"}, {"kind": "event", "term": "teaching", "source": "A1:95"}]
- staging: 
- transition out: cut

### S2-8: 02_environmental_parallax (6 s), ovi ['A1:95', 'A1:96']
- action: camera pans laterally through the scene
- held pose: wide view of Gajanan on the road with plates, house in background
- performance: the narrator concludes the teaching; the scene holds on the compassionate moment
- camera: lateral parallax move
- assets: {"far": "s2_parallax_far", "mid": "s2_parallax_mid", "near": "s2_parallax_near", "sky": "s2_parallax_sky"}
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:96"}, {"kind": "scenery", "term": "road", "source": "A1:87"}, {"kind": "prop", "term": "leaf plates", "source": "A1:87"}, {"kind": "scenery", "term": "house", "source": "A1:87"}, {"kind": "event", "term": "compassion (दयाघन)", "source": "A1:96"}]
- staging: 
- transition out: cut

**Images the owner would need to make:**
- s2_estab_sky: sky layer for establishing shot, early morning (used in S2-1)
- s2_estab_mid: mid layer: Devidas's house and road with leaf plates (used in S2-1)
- s2_estab_fx: fx layer: subtle light dust (used in S2-1)
- s2_estab_fg: fg layer: foreground frame elements (used in S2-1)
- s2_push_plates: close view of used leaf plates on road (used in S2-2)
- s2_push_gajanan_seated: Gajanan seated on road wearing worn old bandi, full body (used in S2-3)
- s2_insert_chilim_gourd: close-up of hand holding unfired clay chilim, gourd beside (used in S2-4)
- s2_insert_picking_grain: close-up of hand holding a single rice grain near the mouth, leaf plate visible below (used in S2-5)
- s2_push_gajanan_eating: Gajanan seated calmly after picking grain, medium shot (used in S2-6)
- s2_face_gajanan_teaching: close-up of Gajanan's face, gaze at nose tip, calm (used in S2-7)
- s2_parallax_sky: sky layer for parallax shot (used in S2-8)
- s2_parallax_far: far layer: distant house and trees (used in S2-8)
- s2_parallax_mid: mid layer: Gajanan seated on road with plates (used in S2-8)
- s2_parallax_near: near layer: foreground grass or road texture (used in S2-8)

## Scene 3 (ovi 97-105): INVALID

- generate `nvidia/nemotron-3-ultra-550b-a55b`: HTTP 200, 227.4 s, finish stop
- validator_repair `nvidia/nemotron-3-ultra-550b-a55b`: HTTP 200, 56.9 s, finish stop

Validator ERRORS:
- S3-2: action/performance describes motion the renderer cannot do ('walking'); show it as a held pose (held_pose) or use NEED_NEW
- S3-3: the owner's table gives 'Bankatlal and Damodar' as the speaker of A1:100, not 'unclear'
- S3-3: the owner's table gives 'Bankatlal and Damodar' as the speaker of A1:101, not 'unclear'

Warnings (for the owner; STAGING items need your approval):
- S3-1: STAGING scenery 'road' needs the owner's approval
- S3-1: STAGING scenery 'morning sky' needs the owner's approval
- S3-1: STAGING light 'dust particles' needs the owner's approval
- S3-2: STAGING scenery 'road' needs the owner's approval
- S3-2: STAGING scenery 'distant road' needs the owner's approval
- S3-2: STAGING scenery 'road texture' needs the owner's approval
- S3-2: STAGING scenery 'morning sky' needs the owner's approval
- S3-3: STAGING scenery 'road' needs the owner's approval
- S3-4: STAGING scenery 'road' needs the owner's approval
- S3-5: STAGING pose 'close-up face' needs the owner's approval
- S3-6: STAGING scenery 'road' needs the owner's approval
- S3-7: STAGING scenery 'road' needs the owner's approval

Repair `validator_repair` (scope ['S3-2', 'S3-3']): **REJECTED (still invalid: S3-2: action/performance describes motion the renderer cannot do ('walking'); show it as a held pose (held_pose) or use NEED_NEW)**

**Goal:** Show Bankatlal and Damodarpant seeing Maharaj, debating his nature, and deciding to test him.
**Turn (A1:102):** Bankatlal proposes they stand on the road and test Maharaj's actions

### S3-1: 01_establishing_shot (6 s), ovi ['A1:97', 'A1:98']
- action: camera dollies in slowly
- held pose: road with leaf plates and two men walking holds steady
- performance: the held pose shows the road and the two men approaching; narrator carries ovi 97 and 98
- camera: dolly in from wide to medium
- assets: {"fg": "fg_frame", "fx": "fx_dust", "mid": "mid_road_plates", "sky": "sky_morning"}
- claims: [{"kind": "person", "term": "Bankatlal Agarwal", "source": "A1:97"}, {"kind": "person", "term": "Damodarpant Kulkarni", "source": "A1:98"}, {"kind": "prop", "term": "leaf plates", "source": "PACKET"}, {"kind": "scenery", "term": "road", "source": "STAGING"}, {"kind": "scenery", "term": "morning sky", "source": "STAGING"}, {"kind": "light", "term": "dust particles", "source": "STAGING"}, {"kind": "camera", "term": "foreground frame", "source": "STAGING"}]
- staging: STAGING: morning sky with soft light | STAGING: dust particles in air
- transition out: cut

### S3-2: 02_environmental_parallax (6 s), ovi ['A1:98']
- action: camera moves laterally through depth layers
- held pose: layers of road, men walking, and sky hold steady
- performance: the parallax reveals the men walking on the road; narrator continues ovi 98
- camera: lateral parallax move
- assets: {"far": "far_road", "mid": "mid_men_walking", "near": "near_road", "sky": "sky_morning"}
- claims: [{"kind": "person", "term": "Bankatlal Agarwal", "source": "A1:98"}, {"kind": "person", "term": "Damodarpant Kulkarni", "source": "A1:98"}, {"kind": "scenery", "term": "road", "source": "STAGING"}, {"kind": "scenery", "term": "distant road", "source": "STAGING"}, {"kind": "scenery", "term": "road texture", "source": "STAGING"}, {"kind": "scenery", "term": "morning sky", "source": "STAGING"}]
- staging: STAGING: layered road scenery
- transition out: cut

### S3-3: 03_slow_cinematic_push (6 s), ovi ['A1:99', 'A1:100', 'A1:101']
- action: camera pushes in slowly
- held pose: Maharaj seated on road holds steady
- performance: the slow push shows Maharaj seated; narrator carries ovi 99, dialogue for ovi 99,100,101
- camera: slow push in
- assets: {"img": "maharaj_seated_road"}
- dialogue (A1:99, Bankatlal Agarwal): कीं याची करणी विपरीत । वेडयापरी दिसतसे / His actions are contrary; he looks like a madman
- dialogue (A1:99, Damodarpant Kulkarni): कीं याची करणी विपरीत । वेडयापरी दिसतसे / His actions are contrary; he looks like a madman
- dialogue (A1:100, unclear): हा अन्नार्थी जरी असतां । तरी पात्र मागून घेता । देवीदासही यातें देता । कां कीं तोही सज्जन / Even if he is a beggar, he would ask for a vessel; Devidas would give; for he is a good man
- dialogue (A1:101, unclear): द्वारीं आलेला याचक । लावी ना सुज्ञ परत देख । कांहीं न चाले तर्क । कृतीवरुनी याच्या ह्या / A beggar at the door, a wise man does not send him back; no reasoning fits; from his actions
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "PACKET"}, {"kind": "prop", "term": "old torn bandi", "source": "PACKET"}, {"kind": "prop", "term": "gourd", "source": "PACKET"}, {"kind": "prop", "term": "clay chilim", "source": "PACKET"}, {"kind": "scenery", "term": "road", "source": "STAGING"}]
- staging: STAGING: Maharaj seated calmly on road
- transition out: cut

### S3-4: 09_dialogue_composition (6 s), ovi ['A1:102']
- action: camera drifts gently across the two figures
- held pose: Bankatlal and Damodarpant stand facing each other on road
- performance: the two men stand facing each other; narrator carries ovi 102 introduction
- camera: gentle drift across
- assets: {"left": "bankatlal_standing_facing_right", "right": "damodarpant_standing_facing_left"}
- claims: [{"kind": "person", "term": "Bankatlal Agarwal", "source": "A1:102"}, {"kind": "person", "term": "Damodarpant Kulkarni", "source": "A1:102"}, {"kind": "scenery", "term": "road", "source": "STAGING"}]
- staging: STAGING: two men standing on road
- transition out: cut

### S3-5: 07_character_reaction (6 s), ovi ['A1:102', 'A1:103']
- action: camera pushes in slowly on face
- held pose: Bankatlal's face close-up holds steady
- performance: Bankatlal speaks his resolve; dialogue for ovi 102 and 103
- camera: slow push in on face
- assets: {"face": "bankatlal_face_closeup"}
- dialogue (A1:102, Bankatlal Agarwal): ऐसेच उभें रस्‍त्यासी । आपण राहूं यत्कृतीसी । अजमावयाकारणें / Let us stand here on the road and test his actions
- dialogue (A1:103, unclear): खरे साधु पिशापरी । जगीं वागती वरवरी । ऐसी व्यासाची वैखरी । बोलली आहे भागवतांत / True sadhus behave like madmen in the world; such is Vyasa's statement in the Bhagavat
- claims: [{"kind": "person", "term": "Bankatlal Agarwal", "source": "A1:102"}, {"kind": "pose", "term": "close-up face", "source": "STAGING"}]
- staging: STAGING: close-up on Bankatlal's face
- transition out: cut

### S3-6: 03_slow_cinematic_push (6 s), ovi ['A1:104']
- action: camera pushes in slowly
- held pose: Maharaj seated on road holds steady
- performance: slow push on Maharaj; narrator carries ovi 104
- camera: slow push in
- assets: {"img": "maharaj_seated_road"}
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "PACKET"}, {"kind": "prop", "term": "old torn bandi", "source": "PACKET"}, {"kind": "prop", "term": "gourd", "source": "PACKET"}, {"kind": "prop", "term": "clay chilim", "source": "PACKET"}, {"kind": "scenery", "term": "road", "source": "STAGING"}]
- staging: STAGING: Maharaj seated calmly
- transition out: cut

### S3-7: 03_slow_cinematic_push (6 s), ovi ['A1:104', 'A1:105']
- action: camera pushes in slowly
- held pose: both men watching Maharaj hold steady
- performance: final visual of the two men watching; narrator carries ovi 105
- camera: slow push in
- assets: {"img": "men_watching_maharaj"}
- claims: [{"kind": "person", "term": "Bankatlal Agarwal", "source": "A1:105"}, {"kind": "person", "term": "Damodarpant Kulkarni", "source": "A1:105"}, {"kind": "person", "term": "Shri Gajanan Maharaj", "source": "PACKET"}, {"kind": "scenery", "term": "road", "source": "STAGING"}]
- staging: STAGING: two men observing Maharaj
- transition out: cut

**Images the owner would need to make:**
- fg_frame: Foreground frame layer, subtle vignette edge, no distinct objects (used in S3-1)
- fx_dust: Dust particles floating in air, subtle (used in S3-1)
- mid_road_plates: Road with used leaf plates scattered, Bankatlal and Damodarpant walking towards viewer (used in S3-1)
- sky_morning: Morning sky, pale blue, no clouds (used in S3-1, S3-2)
- far_road: Distant road stretching into horizon, empty (used in S3-2)
- mid_men_walking: Bankatlal and Damodarpant walking side by side on road, mid-ground (used in S3-2)
- near_road: Road surface texture close, gravel and dust (used in S3-2)
- maharaj_seated_road: Shri Gajanan Maharaj seated on road, wearing old torn bandi, gourd and clay chilim nearby, gaze at nose tip (used in S3-3, S3-6)
- bankatlal_standing_facing_right: Bankatlal standing, facing right, hands folded, wearing simple attire (used in S3-4)
- damodarpant_standing_facing_left: Damodarpant standing, facing left, hands folded, wearing simple attire (used in S3-4)
- bankatlal_face_closeup: Close-up of Bankatlal's face, calm expression, eyes focused (used in S3-5)
- men_watching_maharaj: Bankatlal and Damodarpant standing on road, looking at Maharaj seated ahead (used in S3-7)

## Scene 4 (ovi 108-112): UNREVIEWED

- generate `nvidia/nemotron-3-ultra-550b-a55b`: HTTP 200, 176.6 s, finish stop
- validator_repair `nvidia/nemotron-3-ultra-550b-a55b`: HTTP 200, 78.4 s, finish stop

Repair `validator_repair` (scope ['S4-1', 'S4-2', 'S4-3', 'S4-5']): **USED**

**Goal:** Bankatlal humbly questions Gajanan about searching the plates; Gajanan gives no reply, only looks up at both visitors; his radiant, bliss-absorbed form is revealed; the two visitors bow silently in reverence.
**Turn (A1:112):** The visitors' silent bow marks their shift from testing to surrender.

### S4-1: 04_character_entrance (6 s), ovi ['A1:108']
- action: camera pans right following Bankatlal's approach
- held pose: Bankatlal in mid-stride walking pose approaching Gajanan seated among leaf plates
- performance: Bankatlal advances humbly; Gajanan remains seated, gaze on plate
- camera: pan right following Bankatlal's approach
- assets: {"char": "bankatlal_walking", "other": "gajanan_seated"}
- claims: [{"kind": "person", "term": "Bankatlal Agarwal", "source": "A1:108"}, {"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:108"}, {"kind": "prop", "term": "leaf plates (पत्रावळी)", "source": "PACKET"}, {"kind": "prop", "term": "old worn bandi (बंडी)", "source": "PACKET"}, {"kind": "prop", "term": "gourd vessel (भोपळा)", "source": "PACKET"}, {"kind": "prop", "term": "unfired clay chilim (कच्ची चिलीम)", "source": "PACKET"}, {"kind": "scenery", "term": "road in front of Brahmin's house", "source": "PACKET"}, {"kind": "pose", "term": "Bankatlal walking forward", "source": "A1:108"}, {"kind": "pose", "term": "Gajanan seated on road", "source": "PACKET"}]
- staging: STAGING: early morning light, dust on road
- transition out: cut

### S4-2: 09_dialogue_composition (6 s), ovi ['A1:109']
- action: gentle drift across the two figures facing each other
- held pose: Bankatlal speaking with hands folded; Gajanan seated, looking at him
- performance: Bankatlal asks why Gajanan searches plates and offers food; Gajanan listens silently
- camera: slow drift left to right across both figures
- assets: {"left": "bankatlal_speaking", "right": "gajanan_listening"}
- dialogue (A1:109, Bankatlal Agarwal): ह्या पत्रावळीच्या शोधना । कां हो करितां कळेना । क्षुधा असेल आपणां । तरी तरतूद करुं अन्नाची / Why search these plates? Why do you do this? If you are hungry, we will arrange food.
- claims: [{"kind": "person", "term": "Bankatlal Agarwal", "source": "A1:109"}, {"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:109"}, {"kind": "prop", "term": "leaf plates (पत्रावळी)", "source": "PACKET"}, {"kind": "prop", "term": "old worn bandi (बंडी)", "source": "PACKET"}, {"kind": "pose", "term": "Bankatlal speaking with folded hands", "source": "A1:108"}, {"kind": "pose", "term": "Gajanan seated listening", "source": "A1:110"}]
- staging: STAGING: soft morning light, plates in foreground
- transition out: cut

### S4-3: 03_slow_cinematic_push (6 s), ovi ['A1:110']
- action: slow push in on Gajanan looking up at the two visitors
- held pose: Gajanan seated, head tilted up, eyes fixed on the two standing men
- performance: narrator carries ovi 110: Gajanan thinks, gives no reply, only looks up at both faces
- camera: slow push in from medium to close-up
- assets: {"img": "gajanan_looking_up_at_visitors"}
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:110"}, {"kind": "person", "term": "Bankatlal Agarwal", "source": "A1:108"}, {"kind": "person", "term": "Damodarpant Kulkarni", "source": "PACKET"}, {"kind": "pose", "term": "Gajanan looking up (वरी पाहिलें)", "source": "A1:110"}, {"kind": "event", "term": "Gajanan gives no reply", "source": "A1:110"}]
- staging: STAGING: steady gaze, no movement
- transition out: cut

### S4-4: 08_emotional_closeup (6 s), ovi ['A1:111']
- action: slow close push with soft halo on Gajanan's radiant face
- held pose: Gajanan's face close-up: radiant complexion, muscular neck, steady gaze, attention at brow
- performance: visual only: shows ovi 111 description of his radiant body and absorbed attention
- camera: slow push in to extreme close-up with halo
- assets: {"face": "gajanan_radiant_closeup"}
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:111"}, {"kind": "pose", "term": "radiant complexion (सतेज कांती मनोहर)", "source": "A1:111"}, {"kind": "pose", "term": "muscular upper arms and neck (दंड गर्दन पिळदार)", "source": "A1:111"}, {"kind": "pose", "term": "broad chest (भव्य छाती)", "source": "A1:111"}, {"kind": "pose", "term": "steady gaze (दृष्टि स्थिर)", "source": "A1:111"}, {"kind": "pose", "term": "attention at eyebrows (भृकुटी ठायीं झाली असे)", "source": "A1:111"}]
- staging: STAGING: soft halo to suggest inner bliss
- transition out: cut

### S4-5: 05_bowing_prayer (6 s), ovi ['A1:112']
- action: camera tilts down onto the bowing figures
- held pose: Bankatlal and Damodarpant bowing in pranam before seated Gajanan
- performance: narrator carries ovi 112: absorbed in inner bliss, such a yogi seen, silent namaskar, satisfaction in heart
- camera: tilt down from faces to bowed heads
- assets: {"pose": "visitors_bowing_gajanan_seated"}
- claims: [{"kind": "person", "term": "Bankatlal Agarwal", "source": "A1:112"}, {"kind": "person", "term": "Damodarpant Kulkarni", "source": "A1:112"}, {"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:112"}, {"kind": "event", "term": "silent namaskar (मौनेंच नमस्कार केला)", "source": "A1:112"}, {"kind": "pose", "term": "bowing pranam", "source": "A1:112"}]
- staging: STAGING: silent reverence, no sound
- transition out: cut

### S4-6: 03_slow_cinematic_push (6 s), ovi ['A1:112']
- action: slow push in on Gajanan's serene face after the bow
- held pose: Gajanan's face serene, eyes half-closed, absorbed in inner bliss
- performance: visual only: continues ovi 112, showing the resulting satisfaction and bliss
- camera: slow push in
- assets: {"img": "gajanan_serene_closeup"}
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:112"}, {"kind": "pose", "term": "absorbed in inner bliss (निजानंदीं रंगलेला)", "source": "A1:112"}, {"kind": "event", "term": "visitors' silent bow completed", "source": "A1:112"}]
- staging: STAGING: quiet stillness
- transition out: cut

**Images the owner would need to make:**
- bankatlal_walking: Bankatlal Agarwal walking forward, humble posture, transparent background (used in S4-1)
- gajanan_seated: Shri Gajanan Maharaj seated on road among leaf plates, wearing old worn bandi, gourd and chilim nearby, transparent background (used in S4-1)
- bankatlal_speaking: Bankatlal Agarwal standing, hands folded in speech, facing right, transparent background (used in S4-2)
- gajanan_listening: Shri Gajanan Maharaj seated, head slightly turned listening, transparent background (used in S4-2)
- gajanan_looking_up_at_visitors: Gajanan seated looking upward at two standing visitors (Bankatlal and Damodarpant), wide composition (used in S4-3)
- gajanan_radiant_closeup: Close-up of Gajanan's face showing radiant complexion, muscular neck, steady gaze, attention at brow (used in S4-4)
- visitors_bowing_gajanan_seated: Bankatlal and Damodarpant bowing in pranam before seated Gajanan, both figures transparent (used in S4-5)
- gajanan_serene_closeup: Close-up of Gajanan's serene face after bow, eyes half-closed, absorbed in inner bliss (used in S4-6)

## Scene 5 (ovi 113-118): UNREVIEWED

- generate `nvidia/nemotron-3-ultra-550b-a55b`: HTTP 200, 257.3 s, finish stop
- validator_repair `nvidia/nemotron-3-ultra-550b-a55b`: HTTP 200, 14.5 s, finish stop

Warnings (for the owner; STAGING items need your approval):
- S5-1: STAGING pose 'standing addressing' needs the owner's approval
- S5-2: STAGING light 'daytime' needs the owner's approval
- S5-3: STAGING light 'midday sun' needs the owner's approval
- S5-4: STAGING light 'morning sun' needs the owner's approval
- S5-4: STAGING scenery 'sky' needs the owner's approval
- S5-4: STAGING light 'subtle light effect' needs the owner's approval
- S5-4: STAGING scenery 'foreground leaf plates' needs the owner's approval
- S5-5: STAGING pose 'hands mixing' needs the owner's approval
- S5-6: STAGING light 'soft halo' needs the owner's approval

Repair `validator_repair` (scope ['S5-2']): **USED**

**Goal:** Show Devidas serving a plate of rich dishes to Gajanan, who mixes them and eats without taste preference, while narrator gives two comparisons.
**Turn (A1:118):** Gajanan mixes all cooked dishes into one and eats without liking or disliking, satisfying his hunger in two prahars.

### S5-1: 09_dialogue_composition (6 s), ovi ['A1:113']
- action: camera drifts gently across the two figures
- held pose: speaker addressing Devidas with hand gesture; Devidas standing attentive
- performance: speaker delivers the request to bring a plate; Devidas listens
- camera: gentle drift left to right across the two figures
- assets: {"left": "speaker_unclear_standing", "right": "devidas_standing_listening"}
- dialogue (A1:113, unclear): तुम्ही पात्र वाढून वेगेंसी। आणा एक बाहेर / You increase the plate quickly. Bring one outside.
- claims: [{"kind": "person", "term": "unclear speaker", "source": "A1:113"}, {"kind": "person", "term": "Devidas", "source": "A1:113"}, {"kind": "prop", "term": "plate (पात्र)", "source": "A1:113"}, {"kind": "scenery", "term": "door exterior", "source": "A1:113"}, {"kind": "pose", "term": "standing addressing", "source": "STAGING"}, {"kind": "camera", "term": "drift", "source": "STAGING"}]
- staging: STAGING: speaker stands on road near door, Devidas stands at door threshold
- transition out: cut

### S5-2: 04_character_entrance (6 s), ovi ['A1:114']
- action: camera pans right across the threshold following Devidas's path
- held pose: Devidas in mid-stride carrying a full plate; Gajanan seated calmly on the road
- performance: held poses show Devidas approaching with the plate and Gajanan waiting; narrator covers ovi 114
- camera: pan right following the path from house to Gajanan
- assets: {"char": "devidas_walking_with_plate", "other": "gajanan_seated_at_door"}
- claims: [{"kind": "person", "term": "Devidas", "source": "A1:114"}, {"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:114"}, {"kind": "prop", "term": "plate full of cooked dishes (पक्वान्न)", "source": "A1:114"}, {"kind": "scenery", "term": "door (द्वार)", "source": "A1:114"}, {"kind": "pose", "term": "Devidas mid-stride with plate", "source": "A1:114"}, {"kind": "pose", "term": "Gajanan seated", "source": "PACKET"}, {"kind": "light", "term": "daytime", "source": "STAGING"}]
- staging: STAGING: Devidas emerges from house doorway, plate in hands; Gajanan seated on road before door
- transition out: cut

### S5-3: 03_slow_cinematic_push (6 s), ovi ['A1:114']
- action: camera slowly pushes in on Gajanan seated at the plate
- held pose: Gajanan seated before the plate, hands resting, gaze at nose tip
- performance: held pose shows Gajanan ready to eat; narrator continues from previous ovi
- camera: slow push in
- assets: {"img": "gajanan_seated_at_plate_front"}
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:114"}, {"kind": "prop", "term": "plate with dishes", "source": "A1:114"}, {"kind": "pose", "term": "seated, gaze at nose tip", "source": "PACKET"}, {"kind": "prop", "term": "worn old bandi", "source": "PACKET"}, {"kind": "prop", "term": "unfired clay chilim", "source": "PACKET"}, {"kind": "prop", "term": "gourd", "source": "PACKET"}, {"kind": "light", "term": "midday sun", "source": "STAGING"}]
- staging: STAGING: camera pushes in to emphasize stillness
- transition out: slide

### S5-4: 01_establishing_shot (6 s), ovi ['A1:115', 'A1:116', 'A1:117']
- action: camera dollies in from wide to mid, revealing the setting
- held pose: wide view: Gajanan at door, plate before him, house exterior, road
- performance: establishing the meal scene; narrator covers ovi 115, 116, 117
- camera: dolly in 1.0 to 1.28
- assets: {"fg": "fg_foreground_elements", "fx": "fx_light_subtle", "mid": "mid_gajanan_plate_door", "sky": "sky_morning"}
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:115"}, {"kind": "prop", "term": "plate with dishes", "source": "A1:115"}, {"kind": "scenery", "term": "door, house exterior, road", "source": "A1:114"}, {"kind": "light", "term": "morning sun", "source": "STAGING"}, {"kind": "scenery", "term": "sky", "source": "STAGING"}, {"kind": "light", "term": "subtle light effect", "source": "STAGING"}, {"kind": "scenery", "term": "foreground leaf plates", "source": "STAGING"}]
- staging: STAGING: wide shot includes the road, door, Gajanan, plate, and distant leaf plates
- transition out: pan_bridge

### S5-5: 10_object_hand_insert (6 s), ovi ['A1:118']
- action: camera pushes in slightly on the close-up of hands mixing food
- held pose: Gajanan's hands mixing all dishes together into one
- performance: shows the mixing of all cooked dishes as described in ovi 118
- camera: slow push in on insert
- assets: {"insert": "hands_mixing_food_closeup"}
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj (hands)", "source": "A1:118"}, {"kind": "prop", "term": "mixed food", "source": "A1:118"}, {"kind": "event", "term": "mixing dishes", "source": "A1:118"}, {"kind": "pose", "term": "hands mixing", "source": "STAGING"}]
- staging: STAGING: close-up focuses on hands and food, no face
- transition out: cut

### S5-6: 08_emotional_closeup (6 s), ovi ['A1:118']
- action: camera pushes in slowly with soft halo on Gajanan's face
- held pose: Gajanan's face serene, eyes half-closed, expressing equanimity
- performance: held pose shows satisfaction without taste preference; narrator covers ovi 118 continued
- camera: slow push in with halo
- assets: {"face": "gajanan_face_serene_closeup"}
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:118"}, {"kind": "pose", "term": "serene face", "source": "A1:115"}, {"kind": "light", "term": "soft halo", "source": "STAGING"}]
- staging: STAGING: soft halo effect emphasizes inner bliss
- transition out: cut

**Images the owner would need to make:**
- speaker_unclear_standing: Unclear speaker (likely Bankatlal) standing on road, addressing Devidas, wearing simple clothes, hand gesturing outward (used in S5-1)
- devidas_standing_listening: Devidas standing at door threshold, listening attentively, wearing Brahmin householder attire (used in S5-1)
- devidas_walking_with_plate: Devidas walking forward carrying a plate full of cooked dishes, transparent background for parallax (used in S5-2)
- gajanan_seated_at_door: Gajanan Maharaj seated on road before door, wearing worn bandi, holding unfired clay chilim, gourd nearby, gaze at nose tip (used in S5-2)
- gajanan_seated_at_plate_front: Gajanan Maharaj seated front view, plate of dishes before him, hands resting on knees, calm posture (used in S5-3)
- sky_morning: Morning sky with soft light, flat color illustration (used in S5-4)
- mid_gajanan_plate_door: Mid layer: Gajanan seated at door with plate, house exterior, road (used in S5-4)
- fx_light_subtle: Subtle light effect layer for establishing shot (used in S5-4)
- fg_foreground_elements: Foreground elements: scattered leaf plates, road texture (used in S5-4)
- hands_mixing_food_closeup: Close-up of Gajanan's hands mixing various cooked dishes together in a plate (used in S5-5)
- gajanan_face_serene_closeup: Close-up of Gajanan Maharaj's face, serene expression, eyes half-closed, radiant complexion (used in S5-6)

## Scene 6 (ovi 119-122): UNREVIEWED

- generate `nvidia/nemotron-3-ultra-550b-a55b`: HTTP 200, 252.3 s, finish stop

Warnings (for the owner; STAGING items need your approval):
- S6-1: STAGING scenery "road near Devidas's house" needs the owner's approval
- S6-1: STAGING pose 'standing facing each other' needs the owner's approval
- S6-2: STAGING pose 'close-up face' needs the owner's approval
- S6-3: STAGING pose 'close-up face' needs the owner's approval
- S6-4: STAGING pose 'seated calm' needs the owner's approval
- S6-4: STAGING light 'daylight' needs the owner's approval
- S6-5: STAGING scenery 'Shegaon village' needs the owner's approval
- S6-5: STAGING light 'daylight' needs the owner's approval
- S6-6: STAGING pose 'seated calm' needs the owner's approval
- S6-6: STAGING light 'daylight' needs the owner's approval

**Goal:** Show Bankatlal admitting his mistake, comparing Gajanan to Arjuna, declaring no further test needed, and praising Shegaon as blessed by Hari's gift of desirelessness.
**Turn (A1:119):** Bankatlal admits calling Gajanan mad was a mistake and says no further test is needed.

### S6-1: 09_dialogue_composition (6 s), ovi ['A1:119']
- action: camera drifts gently across the two figures
- held pose: Bankatlal gesturing with hand, Damodarpant standing attentive
- performance: Bankatlal speaks the admission of mistake
- camera: gentle drift left to right
- assets: {"left": "bankatlal_facing_right", "right": "damodarpant_facing_left"}
- dialogue (A1:119, Bankatlal Agarwal): ह्या वेडा म्हणालों आपण । ती निःसंशय झाली चुकी / Calling him mad was surely our mistake.
- claims: [{"kind": "person", "term": "Bankatlal Agarwal", "source": "A1:119"}, {"kind": "person", "term": "Damodarpant Kulkarni", "source": "A1:119"}, {"kind": "scenery", "term": "road near Devidas's house", "source": "STAGING"}, {"kind": "pose", "term": "standing facing each other", "source": "STAGING"}, {"kind": "camera", "term": "gentle drift", "source": "STAGING"}, {"kind": "event", "term": "Bankatlal speaks to Damodarpant", "source": "A1:119"}]
- staging: STAGING: two men standing on road near Devidas's house | STAGING: daytime lighting
- transition out: cut

### S6-2: 07_character_reaction (6 s), ovi ['A1:120']
- action: camera pushes slowly on Bankatlal's face
- held pose: Bankatlal close-up, eyes fixed, mouth slightly open as if speaking
- performance: Bankatlal recounts Arjuna's feigned madness
- camera: slow push in
- assets: {"face": "bankatlal_face_closeup"}
- dialogue (A1:120, Bankatlal Agarwal): सुभद्रेसाठीं द्वारकेला । अर्जुन ऐसाच वेडा झाला । व्यवहाराचा विसर पडला । करुं लागला भलभलतें / For Subhadra, Arjuna went mad in Dwarka; he forgot worldly dealings and started babbling.
- claims: [{"kind": "person", "term": "Bankatlal Agarwal", "source": "A1:120"}, {"kind": "pose", "term": "close-up face", "source": "STAGING"}, {"kind": "camera", "term": "slow push in", "source": "STAGING"}, {"kind": "event", "term": "Bankatlal speaks ovi 120", "source": "A1:120"}]
- staging: STAGING: close-up framing of Bankatlal's face | STAGING: soft lighting
- transition out: cut

### S6-3: 08_emotional_closeup (6 s), ovi ['A1:121']
- action: camera pushes slowly on Damodarpant's face
- held pose: Damodarpant close-up, eyes lowered, listening
- performance: Damodarpant listens as Bankatlal declares no further test needed
- camera: slow push in
- assets: {"face": "damodarpant_face_closeup"}
- dialogue (A1:121, Bankatlal Agarwal): तैसाच हा ज्ञानजेठी । मुक्तिरुप सुभद्रेसाठीं । वेडा झाला कसवटी । याची आतां घेणें नको / Likewise this elder of knowledge became mad for liberation in the form of Subhadra; no need to test him now.
- claims: [{"kind": "person", "term": "Damodarpant Kulkarni", "source": "A1:121"}, {"kind": "pose", "term": "close-up face", "source": "STAGING"}, {"kind": "camera", "term": "slow push in", "source": "STAGING"}, {"kind": "event", "term": "Bankatlal speaks ovi 121", "source": "A1:121"}]
- staging: STAGING: close-up framing of Damodarpant's face | STAGING: soft lighting
- transition out: cut

### S6-4: 03_slow_cinematic_push (6 s), ovi ['A1:121']
- action: camera pushes slowly on Gajanan seated
- held pose: Gajanan seated calmly, gaze on nose tip, bandi worn
- performance: Gajanan remains absorbed in inner bliss
- camera: slow push in
- assets: {"img": "gajanan_seated_full"}
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "PACKET"}, {"kind": "pose", "term": "seated calm", "source": "STAGING"}, {"kind": "camera", "term": "slow push in", "source": "STAGING"}, {"kind": "light", "term": "daylight", "source": "STAGING"}]
- staging: STAGING: Gajanan seated on road, wearing old bandi, gourd and chilim nearby
- transition out: cut

### S6-5: 01_establishing_shot (6 s), ovi ['A1:122']
- action: camera dollies in from wide to mid, revealing village and Gajanan
- held pose: Wide view of Shegaon with Gajanan seated at center, gate in foreground
- performance: The unclear voice praises Shegaon and Hari's gift
- camera: dolly in from 1.0 to 1.28
- assets: {"fg": "fg_gate", "fx": "fx_light", "mid": "mid_gajanan", "sky": "sky_shegaon"}
- dialogue (A1:122, unclear): धन्य आपुलें शेगांव । दृष्टी पाहिला योगीराव । "निरिच्छा" हा जहागीरगांव । दिला हरीनें जयाला / Blessed is our Shegaon; we saw the king of yogis; desirelessness is the estate Hari gave for victory.
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "PACKET"}, {"kind": "scenery", "term": "Shegaon village", "source": "STAGING"}, {"kind": "light", "term": "daylight", "source": "STAGING"}, {"kind": "camera", "term": "dolly in", "source": "STAGING"}, {"kind": "event", "term": "unclear speaker praises Shegaon", "source": "A1:122"}]
- staging: STAGING: wide view of Shegaon village with gate in foreground, Gajanan at center
- transition out: cut

### S6-6: 03_slow_cinematic_push (6 s), ovi ['A1:122']
- action: camera pushes slowly on Gajanan seated
- held pose: Gajanan seated calmly, same as before
- performance: Gajanan continues in silent bliss
- camera: slow push in
- assets: {"img": "gajanan_seated_full"}
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "PACKET"}, {"kind": "pose", "term": "seated calm", "source": "STAGING"}, {"kind": "camera", "term": "slow push in", "source": "STAGING"}, {"kind": "light", "term": "daylight", "source": "STAGING"}]
- staging: STAGING: Gajanan seated, same as before
- transition out: cut

**Images the owner would need to make:**
- bankatlal_facing_right: Bankatlal Agarwal standing facing right, wearing simple clothes, transparent background for dialogue composition (used in S6-1)
- damodarpant_facing_left: Damodarpant Kulkarni standing facing left, wearing simple clothes, transparent background (used in S6-1)
- bankatlal_face_closeup: Close-up of Bankatlal Agarwal's face, earnest expression, transparent background (used in S6-2)
- damodarpant_face_closeup: Close-up of Damodarpant Kulkarni's face, listening expression, transparent background (used in S6-3)
- gajanan_seated_full: Shri Gajanan Maharaj seated on road, wearing old torn bandi, digambar, with gourd and clay chilim nearby, calm posture, gaze on nose tip (used in S6-4, S6-6)
- fg_gate: Foreground gate or archway of Shegaon village, flat color (used in S6-5)
- fx_light: Soft light rays effect layer for establishing shot (used in S6-5)
- mid_gajanan: Mid-layer image of Shri Gajanan Maharaj seated, sized for parallax establishing shot (used in S6-5)
- sky_shegaon: Sky background for Shegaon, flat color (used in S6-5)

## Scene 7 (ovi 123-133): INVALID

- generate `nvidia/nemotron-3-ultra-550b-a55b`: HTTP 200, 167.9 s, finish stop
- validator_repair `nvidia/nemotron-3-ultra-550b-a55b`: HTTP 200, 20.2 s, finish stop

Validator ERRORS:
- S7-2: action/performance describes motion the renderer cannot do ('walks'); show it as a held pose (held_pose) or use NEED_NEW

Repair `validator_repair` (scope ['S7-2']): **REJECTED (still invalid: S7-2: action/performance describes motion the renderer cannot do ('walking'); show it as a held pose (held_pose) or use NEED_NEW)**

**Goal:** Show noon heat, empty gourd, Damodarpant's offer, Gajanan's laughter and teaching about Brahman and worldly conduct, Bankatlal's joy, and Damodarpant entering Devidas's house for water.
**Turn (A1:126):** Damodarpant offers to fetch water; Gajanan laughs and teaches that though all is Brahman, worldly conduct requires water after eating.

### S7-1: 01_establishing_shot (6 s), ovi ['A1:123', 'A1:124']
- action: camera dollies in slowly over the hot noon landscape
- held pose: Gajanan sits cross-legged on the heated ground, birds perched in trees above
- performance: the held pose shows the noon sun, hot ground, birds in trees, and Gajanan seated in joy
- camera: dolly in from wide to medium
- assets: {"fg": "fg_grass_foreground", "fx": "fx_heat_haze", "mid": "mid_gajanan_seated_noon", "sky": "sky_noon"}
- claims: [{"kind": "person", "term": "Gajanan", "source": "A1:124"}, {"kind": "scenery", "term": "hot ground", "source": "A1:123"}, {"kind": "scenery", "term": "birds in trees", "source": "A1:123"}, {"kind": "light", "term": "noon sun", "source": "A1:123"}, {"kind": "pose", "term": "seated cross-legged", "source": "A1:124"}, {"kind": "camera", "term": "dolly in", "source": "STAGING"}]
- staging: STAGING: camera dolly in from wide to medium | STAGING: heat haze layer added for atmosphere
- transition out: cut

### S7-2: 04_character_entrance (6 s), ovi ['A1:125', 'A1:126']
- action: Damodarpant walks toward seated Gajanan as camera pans with him
- held pose: Damodarpant mid-stride, Gajanan seated calm
- performance: the held pose shows Damodarpant approaching to offer water
- camera: pan right following Damodarpant
- assets: {"char": "char_damodarpant_walking", "other": "other_gajanan_seated"}
- claims: [{"kind": "person", "term": "Damodarpant", "source": "A1:125"}, {"kind": "person", "term": "Gajanan", "source": "A1:124"}, {"kind": "prop", "term": "gourd (empty)", "source": "A1:125"}, {"kind": "event", "term": "Damodarpant offers water", "source": "A1:126"}, {"kind": "camera", "term": "pan", "source": "STAGING"}]
- staging: STAGING: camera pans with walking figure | STAGING: gourd shown empty at Gajanan's side
- transition out: cut

### S7-3: 09_dialogue_composition (6 s), ovi ['A1:126']
- action: camera drifts gently between the two figures facing each other
- held pose: Gajanan seated, Damodarpant standing with hands folded
- performance: the held pose shows the two in conversation
- camera: gentle drift left to right
- assets: {"left": "left_gajanan_seated", "right": "right_damodarpant_standing"}
- dialogue (A1:126, Damodarpant Kulkarni): तुंब्यामध्यें नाहीं नीर । मर्जी असल्या हा चाकर । पाणी द्याया तयार असे / There is no water in your gourd; if you wish, this servant is ready to bring water.
- claims: [{"kind": "person", "term": "Damodarpant", "source": "A1:126"}, {"kind": "person", "term": "Gajanan", "source": "A1:126"}, {"kind": "prop", "term": "gourd", "source": "A1:126"}, {"kind": "event", "term": "Damodarpant speaks", "source": "A1:126"}, {"kind": "camera", "term": "drift", "source": "STAGING"}]
- staging: STAGING: gentle drift between figures
- transition out: cut

### S7-4: 07_character_reaction (6 s), ovi ['A1:127']
- action: camera pushes slowly into Gajanan's laughing face
- held pose: Gajanan smiling, eyes bright, head slightly tilted back
- performance: the held pose shows Gajanan laughing at Damodarpant's offer
- camera: slow push in
- assets: {"face": "face_gajanan_laughing"}
- claims: [{"kind": "person", "term": "Gajanan", "source": "A1:127"}, {"kind": "event", "term": "laughter", "source": "A1:127"}, {"kind": "camera", "term": "push in", "source": "STAGING"}]
- staging: STAGING: slow push into face
- transition out: cut

### S7-5: 03_slow_cinematic_push (6 s), ovi ['A1:128']
- action: camera pushes slowly toward seated Gajanan
- held pose: Gajanan seated, one hand raised in teaching gesture
- performance: the held pose shows Gajanan delivering teaching about Brahman
- camera: slow push in
- assets: {"img": "img_gajanan_seated_teaching"}
- dialogue (A1:128, Shri Gajanan Maharaj): तुम्हां गरज असेल जरी । तरी आणून घाला वारी । एक ब्रह्म जगदांतरीं । ओतप्रोत भरलें असें / Even if you need it, bring it; one Brahman pervades the world.
- claims: [{"kind": "person", "term": "Gajanan", "source": "A1:128"}, {"kind": "event", "term": "teaching", "source": "A1:128"}, {"kind": "camera", "term": "push in", "source": "STAGING"}]
- staging: STAGING: slow cinematic push
- transition out: cut

### S7-6: 02_environmental_parallax (6 s), ovi ['A1:128']
- action: camera moves laterally through layers of trees, ground, and sky
- held pose: environmental layers static, Gajanan seated in mid layer
- performance: the held pose shows the noon environment around Gajanan
- camera: lateral parallax move
- assets: {"far": "far_trees", "mid": "mid_gajanan_seated_env", "near": "near_ground", "sky": "sky_noon"}
- claims: [{"kind": "scenery", "term": "trees", "source": "A1:123"}, {"kind": "scenery", "term": "hot ground", "source": "A1:123"}, {"kind": "person", "term": "Gajanan", "source": "A1:124"}, {"kind": "light", "term": "noon sun", "source": "A1:123"}, {"kind": "camera", "term": "parallax", "source": "STAGING"}]
- staging: STAGING: lateral parallax through depth layers
- transition out: cut

### S7-7: 07_character_reaction (6 s), ovi ['A1:129']
- action: camera pushes slowly into Gajanan's teaching face
- held pose: Gajanan serene, eyes focused, slight smile
- performance: the held pose shows Gajanan explaining no difference between them
- camera: slow push in
- assets: {"face": "face_gajanan_teaching"}
- dialogue (A1:129, Shri Gajanan Maharaj): तुम्ही आम्ही भेद तेथ । नाहीं उरला यत्किंचित । परी जगव्यवहार सत्य । आचरिला पाहिजे / There is no difference between you and me; yet worldly conduct must be followed.
- claims: [{"kind": "person", "term": "Gajanan", "source": "A1:129"}, {"kind": "event", "term": "teaching", "source": "A1:129"}, {"kind": "camera", "term": "push in", "source": "STAGING"}]
- staging: STAGING: slow push into face
- transition out: cut

### S7-8: 03_slow_cinematic_push (6 s), ovi ['A1:130', 'A1:131']
- action: camera pushes slowly toward seated Gajanan
- held pose: Gajanan seated, hand gesture continuing
- performance: the held pose shows Gajanan explaining need for water after eating
- camera: slow push in
- assets: {"img": "img_gajanan_seated_teaching"}
- dialogue (A1:130, Shri Gajanan Maharaj): अन्न भक्षिलें देहानीं । म्हणून त्या पाहिजे पाणी । हा व्यवहार चतुरांनीं । अवश्य पाहिजे जाणिला / Bodies have eaten food, therefore they need water; this conduct must be known.
- dialogue (A1:131, Shri Gajanan Maharaj): म्हणून तुमच्या चातुर्यासी । गरज असल्या तुम्हां साची । तरतूद करा पाण्याची । म्हणजे अवघें संपलें / Therefore, with your cleverness, if you have need, arrange water; that is all.
- claims: [{"kind": "person", "term": "Gajanan", "source": "A1:130"}, {"kind": "person", "term": "Gajanan", "source": "A1:131"}, {"kind": "event", "term": "teaching", "source": "A1:130"}, {"kind": "event", "term": "teaching", "source": "A1:131"}, {"kind": "camera", "term": "push in", "source": "STAGING"}]
- staging: STAGING: slow cinematic push
- transition out: cut

### S7-9: 07_character_reaction (6 s), ovi ['A1:132']
- action: camera pushes slowly into Bankatlal's joyful face
- held pose: Bankatlal smiling, eyes bright, hands folded
- performance: the held pose shows Bankatlal expressing blessed fortune
- camera: slow push in
- assets: {"face": "face_bankatlal_joyful"}
- dialogue (A1:132, Bankatlal Agarwal): आपुलें आहे भाग्य धन्य / Our fortune is blessed.
- claims: [{"kind": "person", "term": "Bankatlal", "source": "A1:132"}, {"kind": "event", "term": "speaks", "source": "A1:132"}, {"kind": "camera", "term": "push in", "source": "STAGING"}]
- staging: STAGING: slow push into face
- transition out: cut

### S7-10: 01_establishing_shot (6 s), ovi ['A1:133']
- action: camera dollies in slowly over the house exterior where Damodarpant enters
- held pose: Damodarpant at the doorway of Devidas's house, gourd in hand
- performance: the held pose shows Damodarpant entering the house to fetch water
- camera: dolly in from wide to medium
- assets: {"fg": "fg_path_foreground", "fx": "fx_subtle_dust", "mid": "mid_house_exterior", "sky": "sky_noon"}
- claims: [{"kind": "person", "term": "Damodarpant", "source": "A1:133"}, {"kind": "scenery", "term": "house exterior", "source": "A1:133"}, {"kind": "prop", "term": "gourd/gadva", "source": "A1:133"}, {"kind": "event", "term": "Damodarpant goes into house", "source": "A1:133"}, {"kind": "camera", "term": "dolly in", "source": "STAGING"}]
- staging: STAGING: camera dolly in to house entrance
- transition out: cut

**Images the owner would need to make:**
- fg_grass_foreground: Foreground grass and low plants at noon, flat colour (used in S7-1)
- fx_heat_haze: Subtle heat haze layer for noon atmosphere (used in S7-1)
- mid_gajanan_seated_noon: Gajanan seated cross-legged on ground, wearing old bandi, gourd beside him, birds in trees above (used in S7-1)
- sky_noon: Bright noon sky with harsh light (used in S7-1, S7-6, S7-10)
- char_damodarpant_walking: Damodarpant walking toward camera, transparent pose, carrying empty gourd (used in S7-2)
- other_gajanan_seated: Gajanan seated calm, transparent pose for entrance preset (used in S7-2)
- left_gajanan_seated: Gajanan seated facing right, transparent pose for dialogue composition (used in S7-3)
- right_damodarpant_standing: Damodarpant standing facing left, hands folded, transparent pose (used in S7-3)
- face_gajanan_laughing: Close-up of Gajanan's face laughing, eyes bright (used in S7-4)
- img_gajanan_seated_teaching: Full-body Gajanan seated, one hand raised in teaching gesture (used in S7-5, S7-8)
- far_trees: Distant trees line for parallax (used in S7-6)
- mid_gajanan_seated_env: Gajanan seated in mid-ground for environment parallax (used in S7-6)
- near_ground: Cracked hot ground near layer (used in S7-6)
- face_gajanan_teaching: Close-up of Gajanan serene teaching expression (used in S7-7)
- face_bankatlal_joyful: Close-up of Bankatlal smiling joyfully (used in S7-9)
- fg_path_foreground: Foreground path leading to house entrance (used in S7-10)
- fx_subtle_dust: Subtle dust motes for house exterior (used in S7-10)
- mid_house_exterior: Exterior of Devidas's house with doorway, Damodarpant at threshold (used in S7-10)

## Scene 8 (ovi 134-137): UNREVIEWED

- generate `nvidia/nemotron-3-ultra-550b-a55b`: HTTP 200, 112.3 s, finish stop

Warnings (for the owner; STAGING items need your approval):
- S8-1: STAGING light 'afternoon sunlight' needs the owner's approval
- S8-6: STAGING pose 'serene gaze' needs the owner's approval

**Goal:** Show Gajanan drinking at the cattle trough and Damodarpant returning with vetiver-scented water to protest the muddy water.
**Turn (A1:136):** Damodarpant protests the muddy trough water and offers sweet, clear, cool vetiver-scented water.

### S8-1: 01_establishing_shot (6 s), ovi ['A1:134']
- action: camera dollies in slowly over the well and trough
- held pose: well and trough with animals drinking, early afternoon light
- performance: establishes the cattle trough beside the well where animals drink
- camera: dolly in
- assets: {"fg": "well_fg", "fx": "well_fx", "mid": "well_mid", "sky": "well_sky"}
- claims: [{"kind": "scenery", "term": "well (कूप)", "source": "A1:134"}, {"kind": "scenery", "term": "trough (हाळ)", "source": "A1:134"}, {"kind": "person", "term": "cattle (जनावरें)", "source": "A1:134"}, {"kind": "light", "term": "afternoon sunlight", "source": "STAGING"}, {"kind": "camera", "term": "dolly in", "source": "STAGING"}]
- staging: STAGING: afternoon sunlight on well and trough | STAGING: camera dolly in
- transition out: cut

### S8-2: 03_slow_cinematic_push (6 s), ovi ['A1:135']
- action: camera pushes in slowly on Gajanan drinking
- held pose: Gajanan stands at trough, bandi worn, drinking water, belching
- performance: shows Gajanan drinking the muddy trough water and belching with satisfaction
- camera: push in
- assets: {"img": "gajanan_at_trough"}
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:134"}, {"kind": "prop", "term": "old bandi (बंडी)", "source": "PACKET"}, {"kind": "prop", "term": "gourd (भोपळा)", "source": "PACKET"}, {"kind": "event", "term": "drinks trough water", "source": "A1:135"}, {"kind": "event", "term": "belches audibly", "source": "A1:135"}, {"kind": "camera", "term": "push in", "source": "STAGING"}]
- staging: STAGING: Gajanan's bandi and digambar appearance | STAGING: camera push in
- transition out: cut

### S8-3: 04_character_entrance (6 s), ovi ['A1:135']
- action: camera pans with Damodarpant as he approaches
- held pose: Damodarpant walks toward trough carrying a gadva, Gajanan remains at trough
- performance: shows Damodarpant arriving with a gadva of cool vetiver-scented water
- camera: pan right
- assets: {"char": "damodarpant_walking", "other": "gajanan_seated_trough"}
- claims: [{"kind": "person", "term": "Damodarpant Kulkarni", "source": "A1:135"}, {"kind": "prop", "term": "gadva (गडवा)", "source": "A1:135"}, {"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:134"}, {"kind": "camera", "term": "pan right", "source": "STAGING"}]
- staging: STAGING: Damodarpant walking pose with gadva | STAGING: camera pan right
- transition out: cut

### S8-4: 09_dialogue_composition (6 s), ovi ['A1:136']
- action: camera drifts gently across the two figures
- held pose: Damodarpant and Gajanan face each other, Damodarpant gesturing
- performance: shows Damodarpant protesting that the trough water is fit only for animals
- camera: drift across
- assets: {"left": "damodarpant_facing", "right": "gajanan_facing"}
- dialogue (A1:136, Damodarpant Kulkarni): हां हां तें गढूळ पाणी । समर्था न लावा वदनीं । तें जनावरालागुनी । योग्य आहे प्यावया / Oh oh, that muddy water. Samarth, don't put it to your mouth. It is fit for animals to drink.
- claims: [{"kind": "person", "term": "Damodarpant Kulkarni", "source": "A1:136"}, {"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:136"}, {"kind": "event", "term": "protests muddy water", "source": "A1:136"}, {"kind": "camera", "term": "drift across", "source": "STAGING"}]
- staging: STAGING: two figures facing each other | STAGING: camera drift across
- transition out: cut

### S8-5: 07_character_reaction (6 s), ovi ['A1:137']
- action: camera pushes in slowly on Damodarpant's face
- held pose: Damodarpant close-up, calm expression
- performance: shows Damodarpant offering his sweet, clear, cool water scented with vetiver
- camera: push in
- assets: {"face": "damodarpant_closeup"}
- dialogue (A1:137, Damodarpant Kulkarni): मीं हें पहा आणिलें नीर । गोड निर्मळ थंडगार । वासित केलें साचार । वाळा घालून यामध्यें / See, I have brought this water. Sweet, pure, cool. I have scented it with vetiver.
- claims: [{"kind": "person", "term": "Damodarpant Kulkarni", "source": "A1:137"}, {"kind": "prop", "term": "vetiver (वाळा)", "source": "A1:137"}, {"kind": "prop", "term": "cool water (थंडगार)", "source": "A1:137"}, {"kind": "event", "term": "offers scented water", "source": "A1:137"}, {"kind": "camera", "term": "push in", "source": "STAGING"}]
- staging: STAGING: Damodarpant close-up face | STAGING: camera push in
- transition out: cut

### S8-6: 03_slow_cinematic_push (6 s), ovi ['A1:137']
- action: camera pushes in slowly on Gajanan's face
- held pose: Gajanan close-up, serene gaze
- performance: shows Gajanan listening silently, unchanged
- camera: push in
- assets: {"img": "gajanan_reaction"}
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:137"}, {"kind": "pose", "term": "serene gaze", "source": "STAGING"}, {"kind": "camera", "term": "push in", "source": "STAGING"}]
- staging: STAGING: Gajanan serene close-up | STAGING: camera push in
- transition out: cut

### S8-7: 01_establishing_shot (6 s), ovi ['A1:137']
- action: camera dollies in slowly over the well and trough
- held pose: well and trough with gadva placed beside, vetiver scent implied
- performance: shows the two waters side by side at the trough
- camera: dolly in
- assets: {"fg": "well_fg", "fx": "well_fx", "mid": "well_mid", "sky": "well_sky"}
- claims: [{"kind": "scenery", "term": "well (कूप)", "source": "A1:134"}, {"kind": "scenery", "term": "trough (हाळ)", "source": "A1:134"}, {"kind": "prop", "term": "gadva (गडवा)", "source": "A1:135"}, {"kind": "prop", "term": "vetiver (वाळा)", "source": "A1:137"}, {"kind": "camera", "term": "dolly in", "source": "STAGING"}]
- staging: STAGING: two waters side by side at trough | STAGING: camera dolly in
- transition out: cut

**Images the owner would need to make:**
- well_fg: Foreground frame: edge of trough with muddy water, flat colour (used in S8-1, S8-7)
- well_fx: Light effect: sunlight glint on water surface (used in S8-1, S8-7)
- well_mid: Mid layer: well structure, trough, cattle drinking (used in S8-1, S8-7)
- well_sky: Sky far: clear afternoon sky (used in S8-1, S8-7)
- gajanan_at_trough: Gajanan standing at trough, wearing old bandi, digambar, drinking, belching (used in S8-2)
- damodarpant_walking: Damodarpant walking toward trough, carrying a gadva (used in S8-3)
- gajanan_seated_trough: Gajanan at trough, same pose as previous shot, for entrance composition (used in S8-3)
- damodarpant_facing: Damodarpant facing Gajanan, gesturing protest (used in S8-4)
- gajanan_facing: Gajanan facing Damodarpant, calm (used in S8-4)
- damodarpant_closeup: Close-up of Damodarpant's face, calm expression (used in S8-5)
- gajanan_reaction: Close-up of Gajanan's face, serene gaze (used in S8-6)

## Scene 9 (ovi 138-144): INVALID

- generate `nvidia/nemotron-3-ultra-550b-a55b`: HTTP 200, 210.7 s, finish stop
- validator_repair `nvidia/nemotron-3-ultra-550b-a55b`: HTTP 200, 107.8 s, finish stop

Validator ERRORS:
- S9-1: the owner's table gives 'Gajanan' as the speaker of A1:138, not 'unclear'
- S9-1: pose 'standing listening' is not in the owner's research (cite an ovi, or label it STAGING if it is only scenery/light/pose/camera)
- S9-2: pose 'standing listening' is not in the owner's research (cite an ovi, or label it STAGING if it is only scenery/light/pose/camera)
- S9-4: pose 'standing listening' is not in the owner's research (cite an ovi, or label it STAGING if it is only scenery/light/pose/camera)
- S9-6: pose 'standing listening' is not in the owner's research (cite an ovi, or label it STAGING if it is only scenery/light/pose/camera)
- S9-8: pose 'standing listening' is not in the owner's research (cite an ovi, or label it STAGING if it is only scenery/light/pose/camera)
- S9-11: action/performance describes motion the renderer cannot do ('running'); show it as a held pose (held_pose) or use NEED_NEW

Warnings (for the owner; STAGING items need your approval):
- S9-1: STAGING light 'sunlight' needs the owner's approval
- S9-2: STAGING light 'sunlight' needs the owner's approval
- S9-3: STAGING light 'soft light' needs the owner's approval
- S9-4: STAGING light 'sunlight' needs the owner's approval
- S9-5: STAGING light 'soft light' needs the owner's approval
- S9-6: STAGING light 'sunlight' needs the owner's approval
- S9-7: STAGING light 'soft light' needs the owner's approval
- S9-8: STAGING light 'sunlight' needs the owner's approval
- S9-9: STAGING light 'soft light' needs the owner's approval
- S9-10: STAGING light 'soft halo light' needs the owner's approval
- S9-11: STAGING light 'sunlight' needs the owner's approval
- S9-12: STAGING light 'sunlight' needs the owner's approval
- S9-13: STAGING light 'sunlight' needs the owner's approval

Repair `validator_repair` (scope ['S9-1', 'S9-11', 'S9-2', 'S9-4', 'S9-6', 'S9-8']): **REJECTED (still invalid: S9-11: action/performance describes motion the renderer cannot do ('running'); show it as a held pose (held_pose) or use NEED_NEW)**

**Goal:** Show Gajanan's teaching on water and Brahman, the men's emotional readiness to surrender, and his sudden departure like the wind.
**Turn (A1:144):** Maharaj runs off at wind speed, leaving the men without a destination.

### S9-1: 01_establishing_shot (6 s), ovi ['A1:138']
- action: camera dollies in slowly from wide to medium
- held pose: Gajanan seated on road, two men standing before him, leaf plates scattered, gourd and chilim near him
- performance: The wide view establishes the teaching setting with all figures in place
- camera: dolly in 1.0 to 1.28
- assets: {"fg": "fg_frame", "fx": "fx_light", "mid": "mid_scene_teaching", "sky": "sky_bg"}
- dialogue (A1:138, unclear): ऐसें भाषण ऐकतां । महाराज वदले तत्त्वतां / Such speech hearing, Maharaj spoke the principle
- dialogue (A1:138, Shri Gajanan Maharaj): व्यावहारिक अवघ्या कथा । ह्या न सांगा आम्हां तुम्ही / Worldly tales all, do not tell us
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:138"}, {"kind": "person", "term": "Bankatlal Agarwal", "source": "PACKET"}, {"kind": "person", "term": "Damodarpant Kulkarni", "source": "PACKET"}, {"kind": "prop", "term": "leaf plates (पत्रावळी)", "source": "PACKET"}, {"kind": "prop", "term": "gourd (भोपळा)", "source": "PACKET"}, {"kind": "prop", "term": "clay chilim (कच्ची चिलीम)", "source": "PACKET"}, {"kind": "scenery", "term": "road", "source": "PACKET"}, {"kind": "light", "term": "sunlight", "source": "STAGING"}, {"kind": "pose", "term": "seated teaching", "source": "A1:138"}, {"kind": "pose", "term": "standing listening", "source": "PACKET"}, {"kind": "camera", "term": "dolly in", "source": "STAGING"}]
- staging: STAGING: soft sunlight glow
- transition out: cut

### S9-2: 09_dialogue_composition (6 s), ovi ['A1:139']
- action: camera drifts gently across the two figures
- held pose: Gajanan seated teaching, Bankatlal standing listening
- performance: The composition shows the teacher and listener in dialogue
- camera: gentle drift left to right
- assets: {"left": "gajanan_seated_left", "right": "bankatlal_standing_right"}
- dialogue (A1:139, Shri Gajanan Maharaj): हें अवघें चरचर । ब्रह्में व्याप्त साचार । तेथें गढुळ,निर्मळ वासित नीर । हे न भेद राहिले / All this moving world is pervaded by Brahman; there muddy and pure water reside; no distinction remains
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:139"}, {"kind": "person", "term": "Bankatlal Agarwal", "source": "PACKET"}, {"kind": "prop", "term": "chilim", "source": "PACKET"}, {"kind": "scenery", "term": "road", "source": "PACKET"}, {"kind": "light", "term": "sunlight", "source": "STAGING"}, {"kind": "pose", "term": "seated teaching", "source": "A1:139"}, {"kind": "pose", "term": "standing listening", "source": "PACKET"}, {"kind": "camera", "term": "gentle drift", "source": "STAGING"}]
- staging: STAGING: soft sunlight glow
- transition out: cut

### S9-3: 03_slow_cinematic_push (6 s), ovi ['A1:139']
- action: camera pushes in slowly on Gajanan's face
- held pose: Close-up of Gajanan's face, calm, gaze on nose tip
- performance: Shows the intensity of his teaching
- camera: push in 1.0 to 1.2
- assets: {"img": "gajanan_closeup_teaching1"}
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:139"}, {"kind": "pose", "term": "close-up face, gaze on nose tip", "source": "A1:139"}, {"kind": "light", "term": "soft light", "source": "STAGING"}, {"kind": "camera", "term": "push in", "source": "STAGING"}]
- staging: STAGING: soft light on face
- transition out: cut

### S9-4: 09_dialogue_composition (6 s), ovi ['A1:140']
- action: camera drifts gently across the two figures
- held pose: Gajanan seated teaching, Bankatlal standing listening
- performance: Continues the teaching on water
- camera: gentle drift left to right
- assets: {"left": "gajanan_seated_left", "right": "bankatlal_standing_right"}
- dialogue (A1:140, Shri Gajanan Maharaj): पाणी तरी तोच आहे । निर्मळ गढुळ तोच पाहे । सुवास कुवास दोन्ही हें । रुप त्याचें निःसंशय / Water is that alone; pure or muddy, both are its form; good and bad smell both are its form, without doubt
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:140"}, {"kind": "person", "term": "Bankatlal Agarwal", "source": "PACKET"}, {"kind": "prop", "term": "chilim", "source": "PACKET"}, {"kind": "scenery", "term": "road", "source": "PACKET"}, {"kind": "light", "term": "sunlight", "source": "STAGING"}, {"kind": "pose", "term": "seated teaching", "source": "A1:140"}, {"kind": "pose", "term": "standing listening", "source": "PACKET"}, {"kind": "camera", "term": "gentle drift", "source": "STAGING"}]
- staging: STAGING: soft sunlight glow
- transition out: cut

### S9-5: 03_slow_cinematic_push (6 s), ovi ['A1:140']
- action: camera pushes in slowly on Gajanan's face
- held pose: Close-up of Gajanan, calm
- performance: Emphasizes the teaching on water's unity
- camera: push in 1.0 to 1.2
- assets: {"img": "gajanan_closeup_teaching2"}
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:140"}, {"kind": "pose", "term": "close-up face, calm", "source": "A1:140"}, {"kind": "light", "term": "soft light", "source": "STAGING"}, {"kind": "camera", "term": "push in", "source": "STAGING"}]
- staging: STAGING: soft light on face
- transition out: cut

### S9-6: 09_dialogue_composition (6 s), ovi ['A1:141']
- action: camera drifts gently across the two figures
- held pose: Gajanan seated teaching, Bankatlal standing listening
- performance: Teaching on drinker and Brahman
- camera: gentle drift left to right
- assets: {"left": "gajanan_seated_left", "right": "bankatlal_standing_right"}
- dialogue (A1:141, Shri Gajanan Maharaj): पिणाराही वेगळा । त्यापासून ना निराळा । ईश्वराची अगाध लीला । ती कळे या नरजन्मीं / The drinker is not separate; from Him not apart; God's unfathomable play is known in this human birth
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:141"}, {"kind": "person", "term": "Bankatlal Agarwal", "source": "PACKET"}, {"kind": "prop", "term": "chilim", "source": "PACKET"}, {"kind": "scenery", "term": "road", "source": "PACKET"}, {"kind": "light", "term": "sunlight", "source": "STAGING"}, {"kind": "pose", "term": "seated teaching", "source": "A1:141"}, {"kind": "pose", "term": "standing listening", "source": "PACKET"}, {"kind": "camera", "term": "gentle drift", "source": "STAGING"}]
- staging: STAGING: soft sunlight glow
- transition out: cut

### S9-7: 03_slow_cinematic_push (6 s), ovi ['A1:142']
- action: camera pushes in slowly on Gajanan's face
- held pose: Close-up of Gajanan, calm
- performance: Final teaching on worldly mind and origin of world
- camera: push in 1.0 to 1.2
- assets: {"img": "gajanan_closeup_teaching3"}
- dialogue (A1:142, Shri Gajanan Maharaj): तें दिलें टाकून । व्यवहारीं गोविलें मन । यांचेंच करा सदा मनन । कशापासून जग झालें / Having dropped that, the mind is caught in dealings; reflect on them always; from what did the world arise
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:142"}, {"kind": "pose", "term": "close-up face, calm", "source": "A1:142"}, {"kind": "light", "term": "soft light", "source": "STAGING"}, {"kind": "camera", "term": "push in", "source": "STAGING"}]
- staging: STAGING: soft light on face
- transition out: cut

### S9-8: 02_environmental_parallax (6 s), ovi ['A1:142']
- action: camera moves laterally through depth layers
- held pose: Wide view of teaching scene with foreground plates
- performance: Shows the environment as teaching concludes
- camera: lateral parallax
- assets: {"far": "far_bg", "mid": "mid_scene_teaching", "near": "near_fg", "sky": "sky_bg"}
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "PACKET"}, {"kind": "person", "term": "Bankatlal Agarwal", "source": "PACKET"}, {"kind": "person", "term": "Damodarpant Kulkarni", "source": "PACKET"}, {"kind": "prop", "term": "leaf plates (पत्रावळी)", "source": "PACKET"}, {"kind": "prop", "term": "gourd (भोपळा)", "source": "PACKET"}, {"kind": "prop", "term": "clay chilim (कच्ची चिलीम)", "source": "PACKET"}, {"kind": "scenery", "term": "road", "source": "PACKET"}, {"kind": "scenery", "term": "sky", "source": "PACKET"}, {"kind": "light", "term": "sunlight", "source": "STAGING"}, {"kind": "pose", "term": "seated teaching", "source": "A1:142"}, {"kind": "pose", "term": "standing listening", "source": "PACKET"}, {"kind": "camera", "term": "lateral parallax", "source": "STAGING"}]
- staging: STAGING: soft sunlight glow
- transition out: cut

### S9-9: 07_character_reaction (6 s), ovi ['A1:143']
- action: camera pushes in slowly on Bankatlal's face
- held pose: Bankatlal's face emotional, eyes downcast, ready to prostrate
- performance: Shows his moved state
- camera: push in 1.0 to 1.14
- assets: {"face": "bankatlal_face_emotional"}
- dialogue (A1:143, unclear): ऐसी ऐकतां समर्थवाणी । दोघे गेले गहिंवरोनी । अनन्यभावें समर्थचरणीं । लोळावया तयार झाले / Hearing such Samarth's words, both went to prostrate; with exclusive devotion to Samarth's feet, they became ready to roll
- claims: [{"kind": "person", "term": "Bankatlal Agarwal", "source": "A1:143"}, {"kind": "pose", "term": "emotional close-up, ready to prostrate", "source": "A1:143"}, {"kind": "light", "term": "soft light", "source": "STAGING"}, {"kind": "camera", "term": "push in", "source": "STAGING"}]
- staging: STAGING: soft light on face
- transition out: cut

### S9-10: 08_emotional_closeup (6 s), ovi ['A1:143']
- action: camera pushes in slower with soft halo on Damodarpant's face
- held pose: Damodarpant's face emotional, ready to prostrate
- performance: Shows his moved state
- camera: slow push in with halo
- assets: {"face": "damodarpant_face_emotional"}
- claims: [{"kind": "person", "term": "Damodarpant Kulkarni", "source": "A1:143"}, {"kind": "pose", "term": "emotional close-up, ready to prostrate", "source": "A1:143"}, {"kind": "light", "term": "soft halo light", "source": "STAGING"}, {"kind": "camera", "term": "slow push in with halo", "source": "STAGING"}]
- staging: STAGING: soft halo light
- transition out: cut

### S9-11: 03_slow_cinematic_push (6 s), ovi ['A1:144']
- action: camera pushes in slowly on Maharaj running
- held pose: Maharaj in mid-stride running, bandi fluttering
- performance: Shows his sudden departure like wind
- camera: push in 1.0 to 1.2
- assets: {"img": "maharaj_running_pose"}
- dialogue (A1:144, unclear): तो त्यांचा जाणोन हेत । महाराज निघाले पळत पळत । वायूच्या त्या गतिप्रत । अडथळा जगीं कोण करी ? / Knowing their intent, Maharaj departed running, running; at wind's speed, who can obstruct in the world?
- claims: [{"kind": "person", "term": "Shri Gajanan Maharaj", "source": "A1:144"}, {"kind": "event", "term": "Maharaj runs off", "source": "A1:144"}, {"kind": "prop", "term": "bandi (old worn vest)", "source": "PACKET"}, {"kind": "scenery", "term": "road", "source": "PACKET"}, {"kind": "light", "term": "sunlight", "source": "STAGING"}, {"kind": "pose", "term": "running mid-stride", "source": "A1:144"}, {"kind": "camera", "term": "push in", "source": "STAGING"}]
- staging: STAGING: soft sunlight glow
- transition out: cut

### S9-12: 02_environmental_parallax (6 s), ovi ['A1:144']
- action: camera moves laterally through empty road layers
- held pose: Empty road with leaf plates, gourd, chilim, no figures
- performance: Shows the scene after Maharaj left
- camera: lateral parallax
- assets: {"far": "far_bg", "mid": "mid_scene_empty", "near": "near_fg", "sky": "sky_bg"}
- claims: [{"kind": "scenery", "term": "road", "source": "PACKET"}, {"kind": "prop", "term": "leaf plates (पत्रावळी)", "source": "PACKET"}, {"kind": "prop", "term": "gourd (भोपळा)", "source": "PACKET"}, {"kind": "prop", "term": "clay chilim (कच्ची चिलीम)", "source": "PACKET"}, {"kind": "scenery", "term": "sky", "source": "PACKET"}, {"kind": "light", "term": "sunlight", "source": "STAGING"}, {"kind": "camera", "term": "lateral parallax", "source": "STAGING"}]
- staging: STAGING: soft sunlight glow
- transition out: cut

### S9-13: 01_establishing_shot (6 s), ovi ['A1:144']
- action: camera dollies in slowly on empty road
- held pose: Wide empty road, leaf plates, gourd, chilim remain
- performance: Final establishing shot of the place after departure
- camera: dolly in 1.0 to 1.28
- assets: {"fg": "fg_frame", "fx": "fx_light", "mid": "mid_scene_empty", "sky": "sky_bg"}
- claims: [{"kind": "prop", "term": "leaf plates (पत्रावळी)", "source": "PACKET"}, {"kind": "prop", "term": "gourd (भोपळा)", "source": "PACKET"}, {"kind": "prop", "term": "clay chilim (कच्ची चिलीम)", "source": "PACKET"}, {"kind": "scenery", "term": "road", "source": "PACKET"}, {"kind": "light", "term": "sunlight", "source": "STAGING"}, {"kind": "camera", "term": "dolly in", "source": "STAGING"}]
- staging: STAGING: soft sunlight glow
- transition out: cut

**Images the owner would need to make:**
- fg_frame: Foreground frame layer: leaf plates and dust on road (used in S9-1, S9-13)
- fx_light: Light effect layer: soft sunlight glow (used in S9-1, S9-13)
- mid_scene_teaching: Mid layer: Gajanan seated on road, Bankatlal and Damodarpant standing before him, gourd and chilim nearby (used in S9-1, S9-8)
- sky_bg: Sky layer: clear sky (used in S9-1, S9-8, S9-12, S9-13)
- gajanan_seated_left: Gajanan seated, facing right, calm teaching pose, wearing old bandi, chilim in hand (used in S9-2, S9-4, S9-6)
- bankatlal_standing_right: Bankatlal standing, facing left, hands folded, listening (used in S9-2, S9-4, S9-6)
- gajanan_closeup_teaching1: Close-up of Gajanan's face, gaze on nose tip, calm (used in S9-3)
- gajanan_closeup_teaching2: Close-up of Gajanan's face, slight variation, calm (used in S9-5)
- gajanan_closeup_teaching3: Close-up of Gajanan's face, calm, eyes steady (used in S9-7)
- far_bg: Far background: distant road and horizon (used in S9-8, S9-12)
- near_fg: Near foreground: scattered leaf plates and gourd (used in S9-8, S9-12)
- bankatlal_face_emotional: Close-up of Bankatlal's face, emotional, eyes downcast (used in S9-9)
- damodarpant_face_emotional: Close-up of Damodarpant's face, emotional, eyes downcast (used in S9-10)
- maharaj_running_pose: Maharaj in running pose, mid-stride, bandi fluttering, barefoot (used in S9-11)
- mid_scene_empty: Mid layer: empty road with leaf plates, gourd, chilim, no figures (used in S9-12, S9-13)

