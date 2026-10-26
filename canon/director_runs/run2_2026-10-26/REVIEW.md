# Director test, Adhyay 1 (3 scenes), model `nvidia/nemotron-3-ultra-550b-a55b`

DRAFT shot plans for the owner's review. Nothing is rendered or approved. VALID means only that the validator found no structural or quoting error: it does not mean the plan is faithful or good.

## Scene 1 (ovi 84-96): VALID

- call 1: HTTP 200, 72.9 s, finish stop

Reviewer `openai/gpt-oss-20b` (judged the ORIGINAL plan): **OK** (HTTP 200, 92.7 s, finish stop)

Reviewer `z-ai/glm-5.3-flash` (judged the ORIGINAL plan): **ISSUES** (HTTP 200, 277.0 s, finish stop)
- S1-1 [unsupported_fact] The assets specify a 'clear daytime sky' and 'subtle dust motes in the light', but the brief states that weather and light are not stated in this scene (the only light image in the ovis is the ovi 91 simile for Gajanan himself). Fix: Use a neutral daytime sky (daytime itself is supported by the continuity running to noon at ovi 118/123) and drop the light-specific dust-mote fx or make it non-light-specific.
- S1-4 [wrong_quote] The meaning_en for ovi 96 says 'the cloud of compassion smiled', but the ovi reads 'शितें वेंचती दयाघन' (the cloud of compassion picks the rice grains), and laughter is stated only at ovi 127 in a later scene. Fix: Correct the gloss to 'to make that known, the cloud of compassion picks the grains of rice; the common people did not grasp its meaning'.
- S1-4 [invented_detail] The staging note 'hand pose shows gentle reverence' attributes a feeling the materials do not state; ovi 93 frames the searching as his own play (केवळ निजलीलेनें) and ovi 96 as compassion (दयाघन). Fix: Describe the pose neutrally as deliberate and calm, or key it to the stated play/compassion instead of reverence.

Repair round from the reviewers' findings: **USED** (the plan below is the REPAIRED one, which the reviewers have NOT seen; the validator passed it)

**Goal:** Show Gajanan Maharaj sitting among leftover leaf plates on the road, picking up rice grains to demonstrate that food is the supreme Brahman.
**Turn (ovi 93):** Gajanan searches the leaf plates and eats fallen rice grains to make known that food is the supreme Brahman.

### S1-1: 01_establishing_shot (6 s), ovi [84, 85, 86, 87]
- action: camera dollies forward along the road revealing used leaf plates
- performance: static environment, gentle sway of foreground branch
- camera: dolly in 1.0 to 1.28
- assets: {"sky": "neutral daytime sky above Shegaon road", "mid": "road in front of Devidas's house with used leaf plates scattered", "fx": "subtle atmospheric particles", "fg": "foreground tree branch framing the road"}
- dialogue (ovi 84, narrator, exact): त्या वेळची तुम्हां कथा । सांगतों मी ऐका आतां । एक भाविक गृहस्थ होता । नाम ज्याचें देविदास / I tell the story of that time; listen now. There was a devout householder named Devidas.
- dialogue (ovi 85, narrator, exact): हा देविदास सज्जन । पातूरकरांचा वंशज जाण । शाखा ज्यांची माध्यंदिन । मठाधिपती होता तो / This Devidas is a good man, descendant of Paturkar, of the Madhyandin branch, head of a math.
- dialogue (ovi 86, narrator, exact): त्याच्या एका मुलाची । ऋतुशांति होती साची । त्यानिमित्त भोजनाची । तयारी होती त्याचे घरा / For one of his sons a Ritushanti rite was being performed; a feast was being prepared at his house.
- dialogue (ovi 87, narrator, exact): उष्टया पत्रावळी रस्त्यावर । टाकिल्या होत्या साचार । घराचिया समोर । त्या देविदास विप्राच्या / Used leaf plates were thrown on the road, in front of that Brahmin Devidas's house.
- staging: STAGING: leaf plates are visibly used and scattered; no people in frame
- transition out: cut

### S1-2: 03_slow_cinematic_push (6 s), ovi [88, 89, 90]
- action: Gajanan sits calmly among the leaf plates
- performance: held seated pose, slow breathing, slight sway
- camera: slow push in 1.0 to 1.2
- assets: {"img": "Gajanan sitting on the road among leaf plates, wearing an old torn bandi, a gourd vessel beside him, a raw clay chilim in hand, calm posture, subtle radiance on skin"}
- dialogue (ovi 88, narrator, exact): तो गजानन समर्थसिद्धयोगी । बसले होते तया जागीं । एक बंडी होती अंगीं । जुन्या पुराण्या कापडाची / That Gajanan, accomplished siddha yogi, was sitting at that spot. He wore a bandi of old torn cloth.
- dialogue (ovi 89, narrator, exact): कोणत्याहि उपाधीचें । नांव नव्हतें जवळीं साचें । पात्र पाणी प्यावयाचें । होता एक भोपळा / No worldly attribute's name was near him. For drinking water he had a gourd.
- dialogue (ovi 90, narrator, exact): कच्ची चिलीम हातांत । जी होती तयांची स्वकृत । कुंभाराच्या भट्टीप्रत । जिनें नव्हतें पाहिलें / A raw clay chilim in his hand, self-made, never seen a potter's kiln.
- staging: STAGING: illustration shows a subtle radiance on Gajanan's skin as per tapobal description
- transition out: cut

### S1-3: 07_character_reaction (6 s), ovi [91, 92]
- action: Gajanan holds his gaze at the tip of his nose
- performance: steady nasagra drishti, calm mudra, slow breathing
- camera: slow push in with breathing
- assets: {"face": "close-up of Gajanan's face, eyes half-closed gazing at nose tip, calm expression, subtle radiance on skin"}
- dialogue (ovi 91, narrator, exact): नासाग्र दृष्टि मुद्रा शांत । तपोबल अंगीं झळकत । प्राचीच्या वालरवीवत् । वर्णन किती करावें / Gaze at nose tip, calm posture. Austerity power shines on his body, like the young sun in the east. How much to describe?
- dialogue (ovi 92, narrator, exact): मूर्ति अवघी दिगंबर । भाव मावळला आपपर । आवडनिवड साचार । राहिली न जवळी जयाच्या / The whole form is digambar. Feeling of mine and other melted away. No like or dislike remained near him.
- staging: STAGING: eyes directed downward at nose tip, calm expression; no other figures
- transition out: cut

### S1-4: 10_object_hand_insert (6 s), ovi [93, 94, 95, 96]
- action: hand lifts a rice grain to the mouth
- performance: deliberate pick-and-place motion frozen in held pose
- camera: hold on insert
- assets: {"insert": "Gajanan's hand picking up a single rice grain from a leaf plate and lifting it to his mouth"}
- dialogue (ovi 93, narrator, exact): ती समर्थांची स्वारी । बैसोनिया रस्त्यावरी । शोधन पत्रावळीचे करी । केवळ निजलीलेनें / That samarth's presence, sitting on the road, searching the leaf plates, only as his own play.
- dialogue (ovi 94, narrator, exact): शीत पडल्या दृष्टीप्रत । तें मुखीं उचलुनी घालीत । हें करण्याचा हाच हेत । ’अन्नपरब्रह्म’ कळवावया / Whatever grain fell into his sight, he lifted it to his mouth. This is the purpose: to make known 'food is supreme Brahman'.
- dialogue (ovi 95, narrator, exact): कां कीं गर्जोन सांगे श्रुती । अन्न हेंच ब्रह्म निगुती । "अन्नम् ब्रह्मेति" ऐसी उक्ती । उपनिषदांठायीं असे / For the Shruti declares: food is Brahman. 'Annam Brahma' is the Upanishadic statement.
- dialogue (ovi 96, narrator, exact): त्याची पटवावया खण । शितें वेंचती दयाघन । त्याचा सामान्य जनांलागून । भावार्थ तो कळला नसे / To make that known, the cloud of compassion picks the rice grains. The common people did not grasp its meaning.
- staging: STAGING: leaf plate visible in background of insert; hand pose shows deliberate calm action
- transition out: cut

**Images the owner would need to make:**
- S1_sky: neutral daytime sky above Shegaon road, flat colour (used in S1-1)
- S1_mid_road_plates: road in front of Devidas's house with used leaf plates scattered, flat colour (used in S1-1)
- S1_fx_particles: subtle atmospheric particles, transparent layer (used in S1-1)
- S1_fg_branch: foreground tree branch framing the road, flat colour (used in S1-1)
- S1_gajanan_full: Gajanan sitting on the road among leaf plates, wearing old torn bandi, gourd vessel beside him, raw clay chilim in hand, calm posture, subtle radiance on skin, full body, transparent background (used in S1-2)
- S1_gajanan_face: close-up of Gajanan's face, eyes half-closed gazing at nose tip, calm expression, subtle radiance on skin, transparent background (used in S1-3)
- S1_hand_rice: Gajanan's hand picking up a single rice grain from a leaf plate and lifting it to his mouth, full-frame close-up, transparent background (used in S1-4)

## Scene 4 (ovi 114-122): VALID

- call 1: HTTP 200, 105.0 s, finish stop
- call 2: HTTP 200, 19.6 s, finish stop

Reviewer `openai/gpt-oss-20b` (judged the ORIGINAL plan): **OK** (HTTP 200, 190.5 s, finish stop)

Reviewer `z-ai/glm-5.3-flash` (judged the ORIGINAL plan): **NO_CHECK** (HTTP 0, 751.4 s, finish length, error incomplete stream (finish=length))

**Goal:** Show Gajanan's total indifference to taste as he mixes and eats the rich meal, and Bankatlal's reversal from calling him mad to declaring him the king of yogis, blessing Shegaon.
**Turn (ovi 119):** Bankatlal declares that calling Gajanan mad was undoubtedly a mistake and no further testing is needed.

### S4-1: 04_character_entrance (6 s), ovi [114]
- action: Devidas carries plate to door and sets it before Gajanan
- performance: Devidas strides purposefully; Gajanan sits still, gaze downward
- camera: pan right with Devidas, then hold on Gajanan
- assets: {"char": "Devidas walking toward door carrying a full plate of rich cooked dishes, side view, transparent background", "other": "Gajanan seated on ground in front of door, plate not yet placed, neutral pose, transparent background"}
- staging: STAGING: Plate enters frame from right as Devidas approaches; door frame in foreground
- transition out: cut

### S4-2: 03_slow_cinematic_push (6 s), ovi [115, 118]
- action: Gajanan mixes dishes together and eats
- performance: Hands move steadily, no hesitation, no savoring gestures
- camera: slow push in from waist-up to chest-up
- assets: {"img": "Gajanan seated at plate, hands mixing all dishes into one mass, eating calmly, full body"}
- dialogue (ovi 116, narrator, exact): अनुपम ब्रह्मरसाला जो पिऊन तृप्त झाला तो कां मागतो गुळवण्याला मिटक्या मारीत बैसेल / One who has drunk the incomparable nectar of Brahman and been satisfied — why would he ask for jaggery-water and sit smacking his lips?
- dialogue (ovi 117, narrator, exact): जो सार्वभौम नृपवर झाला असे साचार अशा नरासी जहागीर मिळाल्यासी प्रेम नुपजे / If a supreme emperor has become such, love does not arise for a petty estate.
- staging: STAGING: No lip-smacking, no selective picking; all dishes become one
- transition out: cut

### S4-3: 07_character_reaction (6 s), ovi [115]
- action: Gajanan chews with neutral expression
- performance: No flicker of pleasure or dislike; breath even, gaze fixed
- camera: slow push in on face, breathing sway
- assets: {"face": "Close-up of Gajanan's face, neutral expression, eyes downcast at food, transparent background"}
- staging: STAGING: Hold on still face to show 'चवी न कशाची अंतरीं अणुमात्र उरली असे' — no taste-craving remains, not an atom
- transition out: cut

### S4-4: 09_dialogue_composition (6 s), ovi [119, 120, 121]
- action: Bankatlal gestures toward Gajanan while speaking to Damodarpant
- performance: Bankatlal earnest, finger pointing; Damodarpant absorbs, no interruption
- camera: gentle drift left to right across both faces
- assets: {"left": "Bankatlal standing, turned toward left, right hand raised in declarative gesture, transparent background", "right": "Damodarpant standing, turned toward right, head slightly tilted listening, transparent background"}
- dialogue (ovi 119, Bankatlal, exact): ह्या वेडा म्हणालों आपण ती निःसंशय झाली चुकी / We called him mad; that was undoubtedly a mistake.
- dialogue (ovi 120, Bankatlal, exact): सुभद्रेसाठीं द्वारकेला अर्जुन ऐसाच वेडा झाला व्यवहाराचा विसर पडला करुं लागला भलभलतें / For Subhadra's sake at Dwarka, Arjuna went just such a madman; worldly conduct was forgotten, he did odd things.
- dialogue (ovi 121, Bankatlal, exact): तैसाच हा ज्ञानजेठी मुक्तिरुप सुभद्रेसाठीं वेडा झाला कसवटी याची आतां घेणें नको / Likewise this eldest-in-knowledge went mad for liberation-form Subhadra; testing him now is not needed.
- staging: STAGING: Bankatlal's gesture includes Gajanan off-screen left; Damodarpant does not speak
- transition out: cut

### S4-5: 08_emotional_closeup (6 s), ovi [122]
- action: Bankatlal looks upward with folded hands
- performance: Eyes soft, lips move silently; pride and reverence blended
- camera: slower push in, soft halo bloom at edges
- assets: {"face": "Close-up of Bankatlal's face, reverent expression, hands folded at chest, eyes uplifted, transparent background"}
- dialogue (ovi 122, unclear, exact): धन्य आपुलें शेगांव दृष्टी पाहिला योगीराव निरिच्छा हा जहागीरगांव दिला हरीनें जयाला / Blessed is our Shegaon; we have seen the king of yogis with our eyes; Hari gave him the estate of desirelessness.
- staging: STAGING: 'आपुलें' (our) marks Bankatlal as Shegaon resident; halo suggests grace, not miracle
- transition out: cut

**Images the owner would need to make:**
- devidas_walking_plate: Devidas walking toward door carrying a full plate of rich cooked dishes, side view, transparent background (used in S4-1)
- gajanan_seated_door: Gajanan seated on ground in front of door, plate not yet placed, neutral pose, transparent background (used in S4-1)
- gajanan_mixing_eating: Gajanan seated at plate, hands mixing all dishes into one mass, eating calmly, full body (used in S4-2)
- gajanan_face_neutral: Close-up of Gajanan's face, neutral expression, eyes downcast at food, transparent background (used in S4-3)
- bankatlal_facing: Bankatlal standing, turned toward left, right hand raised in declarative gesture, transparent background (used in S4-4)
- damodarpant_facing: Damodarpant standing, turned toward right, head slightly tilted listening, transparent background (used in S4-4)
- bankatlal_face_reverent: Close-up of Bankatlal's face, reverent expression, hands folded at chest, eyes uplifted, transparent background (used in S4-5)

## Scene 6 (ovi 133-137): VALID

- call 1: HTTP 200, 36.3 s, finish stop

Reviewer `openai/gpt-oss-20b` (judged the ORIGINAL plan): **ISSUES** (HTTP 200, 107.9 s, finish stop)
- S6-2 [unexecutable] Shot S6-2 attempts to animate a head lift and throat movement (belch) within a single image, which is not possible with the 03_slow_cinematic_push preset. Fix: Split the action into two separate shots: one for drinking, one for the belch, or use a static drinking pose only.
- S6-3 [unexecutable] Shot S6-3 includes a gentle drift across both figures, but the 09_dialogue_composition preset is static and cannot show movement across the frame. Fix: Remove the drift; use a cut between two static poses or replace the preset with one that supports camera movement.
- S6-1 [unsupported_fact] The description specifies a stone well with a long stone trough and cows/buffaloes, none of which are mentioned in the ovi text. Fix: Use a generic well and trough without specifying material or length, and describe the animals generically as cattle.

Reviewer `z-ai/glm-5.3-flash` (judged the ORIGINAL plan): **ISSUES** (HTTP 200, 361.2 s, finish stop)
- S6-2 [unexecutable] The performance 'held pose of drinking, then head lifted, throat moving' and the staging 'after drink, hold pose with chest slightly expanded for belch' require a pose change and throat movement inside one preset 03 shot, which is a single image with no limb or facial animation. Fix: Split into two shots with two images (drinking pose, then a separate head-lifted post-drink/belch pose), or keep only the single drinking held pose and drop the in-shot change.
- S6-3 [unexecutable] The performance 'Damodar steps forward, arms extended offering' (with the asset described as 'walking up') requires walking and arm movement inside preset 09, which only drifts across two static facing poses with no limb animation. Fix: Use a static arrived pose of Damodar standing facing Gajanan holding the gadva in both hands, and let the camera drift or a separate entrance image carry the approach.
- S6-3 (also S6-5, images S6_Damodar_arriving_gadva and S6_gadva_hands_vetiver) [other] The plan specifies a clay/earthen gadva, but the owner's frozen research records 'video prop choice: brass' for Damodar's gadva at ovi 135. Fix: Change all gadva depictions to brass, or have the owner re-freeze the prop choice before the images are made.

Repair round from the reviewers' findings: **USED** (the plan below is the REPAIRED one, which the reviewers have NOT seen; the validator passed it)

**Goal:** Show Gajanan drinking at the cattle trough and Damodar returning with scented water to stop him.
**Turn (ovi 135):** Gajanan drinks the muddy trough water and belches; Damodar arrives with a gadva of clear vetiver water.

### S6-1: 01_establishing_shot (6 s), ovi [134]
- action: camera dollies in on well and trough
- performance: cattle stand still drinking; water surface calm
- camera: slow dolly 1.0 to 1.28
- assets: {"sky": "pale midday sky, no clouds", "mid": "well with a trough (haal) beside it; cattle drinking at the trough", "fx": "none", "fg": "thin foreground frame of grass blades"}
- staging: STAGING: hold on the trough water to show it is muddy (gaDhuuL)
- transition out: cut

### S6-2: 03_slow_cinematic_push (6 s), ovi [135]
- action: Gajanan drinks from trough
- performance: held pose of drinking, head bent, hands at water
- camera: slow push in 1.0 to 1.2
- assets: {"img": "Gajanan standing at the trough, bent forward, hands cupped, drinking water; old torn bandi on near-naked body"}
- staging: STAGING: pose shows drinking action only; belch is separate beat
- transition out: cut

### S6-3: 03_slow_cinematic_push (6 s), ovi [135]
- action: Gajanan belches with satisfaction
- performance: held pose of post-drink belch (truptateche Dhekar)
- camera: slow push in 1.0 to 1.2
- assets: {"img": "Gajanan upright after drinking, head lifted, chest slightly expanded, one hand at throat, calm face; old torn bandi"}
- staging: STAGING: chest expanded, hand at throat shows belch completed
- transition out: cut

### S6-4: 09_dialogue_composition (6 s), ovi [135]
- action: Damodar stands before Gajanan offering water
- performance: both figures still, facing each other; gadva held forward in Damodar's hands
- camera: gentle drift across both figures
- assets: {"left": "Gajanan upright, calm face, old torn bandi, facing right", "right": "Damodarpant standing, holding brass gadva in both hands, concerned expression, facing left"}
- staging: STAGING: brass gadva clearly visible in Damodar's hands
- transition out: cut

### S6-5: 07_character_reaction (6 s), ovi [136]
- action: Damodar gestures to trough warning
- performance: held alarm pose, breathing visible
- camera: slow push in with breathing sway
- assets: {"face": "Damodarpant close-up, eyebrows raised, mouth open in alarm, one hand pointing sideways toward trough"}
- dialogue (ovi 136, Damodarpant, exact): हां हां तें गढूळ पाणी । समर्था न लावा वदनीं । तें जनावरालागुनी । योग्य आहे प्यावया / Oh oh, that muddy water. Samarth, do not put it to your mouth. It is fit for animals to drink.
- staging: STAGING: eyes wide, hand pointing off-screen to trough
- transition out: cut

### S6-6: 10_object_hand_insert (6 s), ovi [137]
- action: Damodar presents water pot
- performance: hands steady, gadva tilted slightly to show water clarity and vetiver
- camera: hold, full-frame insert
- assets: {"insert": "pair of hands holding brass gadva, clear water visible inside, a few vetiver roots (vaalaa) lying on the rim"}
- dialogue (ovi 137, Damodarpant, exact): मीं हें पहा आणिलें नीर । गोड निर्मळ थंडगार । वासित केलें साचार । वाळा घालून यामध्यें / See, I have brought this water. Sweet, clear, cool. Made fragrant with vetiver placed inside.
- staging: STAGING: vetiver roots visible on rim to show scenting
- transition out: cut

**Images the owner would need to make:**
- S6_well_trough_cattle: Wide establishing illustration: well with trough (haal) beside it, cattle drinking at trough, pale midday sky, grass foreground frame. Flat colour, layers separable for parallax. (used in S6-1)
- S6_Gajanan_drinking_trough: Gajanan standing at trough, bent forward, hands cupped drinking water; wearing old torn bandi, otherwise near-naked (digambar), muscular arms and neck, calm posture. Flat colour, transparent background. (used in S6-2)
- S6_Gajanan_postdrink_belch: Gajanan upright after drinking, head lifted, chest slightly expanded, one hand at throat, calm face; old torn bandi. Flat colour, transparent background. (used in S6-3)
- S6_Gajanan_upright_facing_right: Gajanan upright, calm face, old torn bandi, facing right. Flat colour, transparent background. (used in S6-4)
- S6_Damodar_standing_gadva_facing_left: Damodarpant standing, holding brass gadva in both hands, concerned expression, facing left. Flat colour, transparent background. (used in S6-4)
- S6_Damodar_closeup_alarm: Damodarpant close-up face, eyebrows raised, mouth open in alarm, one hand pointing sideways (toward trough). Flat colour, transparent background. (used in S6-5)
- S6_gadva_hands_vetiver: Close-up insert: pair of hands holding brass gadva, clear water visible inside, a few vetiver roots (vaalaa) lying on the rim. Flat colour, full frame. (used in S6-6)

