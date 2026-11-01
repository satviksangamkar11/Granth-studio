"""Adhyay 1 audio SPEC (owner-reviewable data, 2026-10-26). Everything Marathi here is an EXACT verse segment named by (ovi, charans), filled and checked by code in a1_audio.py:
no Marathi is typed by hand except the ONE labelled paraphrase (the year line, at the owner's instruction). Hindi is a DRAFT adaptation: NOT VALIDATED, for the owner / a Hindi reviewer.
A line = (id, ovi, [first_charan, last_charan] 1-based, voice, priority, hindi, note). voice: narrator | bankatlal | damodarpant | gajanan (a character voice only where the owner's dialogue
table names that speaker for the ovi; unclear or joint speech is read by the narrator). priority: core (in the timing) | optional (kept for the owner to switch on).
Charan = one of the four half-lines of an ovi, separated by the danda."""

VOICES = {"narrator": "the storyteller (reads verse narration and every unclear or joint speech)",
          "bankatlal": "Bankatlal Agarwal (only where the table names him)", "damodarpant": "Damodarpant Kulkarni (only where the table names him)", "gajanan": "Gajanan Maharaj (only where the table names him)"}

# On-screen captions (no audio, no duration). The year ONLY; never a day or month. The year is the owner's instruction (the Granth says only 'within Shaka 1800s').
CAPTIONS = [("S1-K1", "S1", "shot 1 or 2", "१८७८", "1878", "Year only (owner's instruction); the narrator does not say it.")]

# Owner decisions that settle rows the frozen dialogue table leaves unclear (the frozen research copy itself is never edited).
# Applied on top of director_test.speaker_table(); each entry names the decision.
SPEAKER_OVERRIDES = {
    122: "Bankatlal (owner directive 2026-11-01: ovis 119-122 are Bankatlal's speech)",
    125: "Bankatlal (owner directive 2026-11-01: addresses Pant directly)",
}

# (id, scene, ovi, [c1, c2], voice, priority, hindi, note)
LINES = [
    ("S1-L1", "S1", 70, [1, 4], "narrator", "core", "इन महापुरुष का ठौर-ठिकाना कहाँ था, या उनकी जाति का पता क्या था, यह इतिहास की दृष्टि से पता नहीं चलता।", "Origins cannot be traced. The year appears only as the caption S1-K1."),

    ("S2-L1", "S2", 84, [3, 4], "narrator", "core", "वहाँ एक श्रद्धालु गृहस्थ थे, उनका नाम देविदास था।", ""),
    ("S2-L2", "S2", 86, [1, 4], "narrator", "core", "उनके एक पुत्र का ऋतुशांति संस्कार था; उसी उपलक्ष्य में उनके घर भोजन की तैयारी थी।", "Ritushanti: a rite of passage for a boy of 13-16 (owner's final answer S5-3)."),
    ("S2-L3", "S2", 87, [1, 4], "narrator", "core", "देविदास ब्राह्मण के घर के सामने रास्ते पर जूठी पत्तलें फेंकी गई थीं।", ""),
    ("S2-L4", "S2", 88, [1, 4], "narrator", "core", "समर्थ सिद्ध योगी गजानन उसी जगह बैठे थे; उनके बदन पर पुराने-धुराने कपड़े की एक बंडी थी।", "The worn old bandi (88)."),
    ("S2-L5", "S2", 91, [1, 4], "narrator", "optional", "दृष्टि नासिका के अग्रभाग पर, मुद्रा शांत; तपोबल देह में झलक रहा था, जैसे पूर्व दिशा का बाल सूर्य — कितना वर्णन करें!", "The sunrise comparison is not a time-of-day instruction."),
    ("S2-L6", "S2", 92, [1, 4], "narrator", "core", "पूरी मूर्ति दिगंबर थी; अपने-पराये का भाव अस्त हो गया था, पसंद-नापसंद उनके पास रही ही नहीं।", "Digambar (92)."),
    ("S2-L7", "S2", 93, [1, 4], "narrator", "core", "वे समर्थ रास्ते पर बैठकर, केवल अपनी लीला से, पत्तलों को टटोल रहे थे।", ""),
    ("S2-L8", "S2", 94, [1, 4], "narrator", "core", "जो भी चावल का दाना नज़र में आता, उसे उठाकर मुँह में डालते; इसका हेतु यही था — 'अन्न ही परब्रह्म है' यह समझाना।", "Teaching 1: food is Brahman."),
    ("S2-L9", "S2", 95, [1, 4], "narrator", "core", "क्योंकि श्रुति गरजकर कहती है कि अन्न ही निश्चय से ब्रह्म है — 'अन्नं ब्रह्मेति' यह उक्ति उपनिषदों में है।", "Teaching 1: the Upanishad words."),
    ("S2-L10", "S2", 96, [1, 4], "narrator", "core", "उसकी प्रतीति कराने के लिए वे दयाघन दाने चुन रहे थे; पर उसका भावार्थ साधारण लोगों को समझ में नहीं आया था।", ""),

    ("S3-L1", "S3", 97, [1, 2], "narrator", "core", "बंकटलाल अगरवाला रास्ते से जा रहा था।", ""),
    ("S3-L2", "S3", 98, [1, 2], "narrator", "core", "उसके मित्र का नाम दामोदरपंत कुलकर्णी था।", ""),
    ("S3-L3", "S3", 98, [3, 4], "narrator", "core", "दोनों यह प्रकार देखकर आश्चर्यचकित हो गए।", ""),
    ("S3-L4", "S3", 99, [3, 4], "narrator", "core", "'इसकी करनी विपरीत है; यह पागल जैसा दिखता है।'", "Joint speech of the two men (table: speaker not split): read by the narrator."),
    ("S3-L5", "S3", 100, [1, 4], "narrator", "optional", "यदि यह अन्न का इच्छुक होता, तो पत्तल माँग लेता; देविदास भी इसे दे देते, क्योंकि वे भी सज्जन हैं।", "Joint reasoning (100-101): narrator."),
    ("S3-L6", "S3", 102, [1, 1], "narrator", "core", "बंकटलाल पंत से बोला —", ""),
    ("S3-L7", "S3", 102, [2, 4], "bankatlal", "core", "'ऐसे ही रास्ते पर खड़े रहकर हम इसकी करनी को परखें।'", "Table: Bankatlal to Damodarpant."),
    ("S3-L8", "S3", 104, [1, 2], "narrator", "core", "कर्म से यह पागल दिखता है, पर ज्ञान का भंडार लगता है।", "Table: speaker unclear (103-104): narrator."),
    ("S3-L9", "S3", 105, [1, 4], "narrator", "optional", "वे आपस में ऐसा विचार करने लगे; रत्न सामने हो, तो उसे पारखी ही पहचानता है।", ""),

    ("S4-L1", "S4", 108, [1, 2], "narrator", "core", "सबसे पहले बंकटलाल अगरवाला आगे आया।", ""),
    ("S4-L2", "S4", 109, [1, 4], "bankatlal", "core", "'इन पत्तलों को आप क्यों टटोल रहे हैं, यह समझ नहीं आता; यदि आपको भूख हो, तो हम अन्न का प्रबंध कर दें।'", "Table: Bankatlal to Gajanan."),
    ("S4-L3", "S4", 110, [1, 4], "narrator", "core", "उसने ऐसा पूछा, पर उत्तर नहीं मिला; उन्होंने बस ऊपर दोनों के मुख की ओर देखा।", "The silence."),
    ("S4-L5", "S4", 111, [1, 4], "narrator", "optional", "उनकी कांति तेजस्वी और मनोहर थी; भुजाएँ और गर्दन पुष्ट, छाती भव्य, दृष्टि भृकुटी पर स्थिर थी।", ""),
    ("S4-L4", "S4", 112, [1, 4], "narrator", "core", "निजानंद में रंगे हुए ऐसे योगी को देखकर, उन्होंने मन में संतोष पाकर मौन ही नमस्कार किया।", "The silent bow by the two visitors (read from the verse; the subject is implicit)."),

    ("S5-L1", "S5", 113, [1, 4], "narrator", "core", "वे देविदासबुवा से प्रेम से कहने लगे — 'तुम शीघ्र एक पत्तल परोसकर बाहर ले आओ।'", "Table: speaker unclear (113): narrator."),
    ("S5-L2", "S5", 114, [1, 4], "narrator", "core", "देविदास ने वैसा ही किया; पक्वान्नों से भरी पत्तल लाकर द्वार के सामने स्वामी के आगे रख दी।", "Dishes: 'pakvanna' (rich cooked dishes); the narrower meaning is left open in the research."),
    ("S5-L3", "S5", 115, [1, 2], "narrator", "core", "रखी हुई पत्तल पर समर्थ भोजन करने बैठे।", ""),
    ("S5-L4", "S5", 116, [1, 4], "narrator", "core", "अनुपम ब्रह्मरस पीकर जो तृप्त हो गया, वह क्या गुड़ का पानी माँगेगा, या चटकारे लेता बैठेगा?", "Narrator's comparison."),
    ("S5-L5", "S5", 117, [1, 4], "narrator", "core", "जो सचमुच सार्वभौम राजा हो गया, उसे जागीर मिल जाने पर प्रेम (हर्ष) नहीं उपजता।", "Narrator's comparison."),
    ("S5-L6", "S5", 118, [1, 2], "narrator", "core", "उन्होंने सब पक्वान्न एक कर दिए; पसंद-नापसंद नहीं रही।", "The mixing of the dishes (118)."),

    ("S6-L1", "S6", 119, [1, 2], "narrator", "core", "बंकटलाल यह देखकर पंत से बोला —", ""),
    ("S6-L2", "S6", 119, [3, 4], "bankatlal", "core", "'इसे हमने पागल कहा — यह निःसंदेह हमारी भूल हुई।'", "Table: Bankatlal to Damodarpant."),
    ("S6-L3", "S6", 120, [1, 2], "bankatlal", "core", "'सुभद्रा के लिए द्वारका में अर्जुन भी ऐसे ही पागल हो गया था।'", "Table: Bankatlal (continuing)."),
    ("S6-L4", "S6", 121, [1, 4], "bankatlal", "core", "'वैसे ही यह ज्ञानजेठी मुक्तिरूपी सुभद्रा के लिए पागल हुआ है; अब इसकी कसौटी लेने की ज़रूरत नहीं।'", "Table: Bankatlal (continuing)."),
    ("S6-L5", "S6", 122, [1, 2], "bankatlal", "core", "धन्य है हमारा शेगाँव, जहाँ योगीराज के दर्शन हुए।", "Owner directive 2026-11-01: 119-122 are Bankatlal's speech."),

    ("S7-L1", "S7", 123, [1, 2], "narrator", "core", "सूर्य मध्याह्न पर आ गया; भूमि का भाग तप गया।", ""),
    ("S7-L3", "S7", 124, [1, 2], "narrator", "core", "ऐसी भरी धूप में वह आनंद में बैठा है।", "Table: speaker unclear (123-124): narrator."),
    ("S7-L4", "S7", 125, [1, 4], "bankatlal", "core", "यह इच्छा भर जीम चुका; तुंबे में पानी नहीं है; पंत, यह हम इसके लिए ला दें।", "Owner directive 2026-11-01: Bankatlal (addresses Pant directly); core."),
    ("S7-L5", "S7", 126, [1, 1], "narrator", "core", "दामोदर पूछने लगे —", ""),
    ("S7-L6", "S7", 126, [2, 4], "damodarpant", "core", "'तुंबे में पानी नहीं है; आपकी मर्ज़ी हो तो यह सेवक पानी देने को तैयार है।'", "Table: Damodarpant to Gajanan."),
    ("S7-L7", "S7", 127, [1, 3], "narrator", "core", "ये शब्द सुनकर समर्थ हँसे और दोनों को देखकर बोले —", ""),
    ("S7-L8", "S7", 128, [1, 4], "gajanan", "core", "'आपको ज़रूरत हो तो पानी ले आकर दीजिए; एक ही ब्रह्म जगत के भीतर ओतप्रोत भरा है।'", "Table: Gajanan (127-131)."),
    ("S7-L9", "S7", 129, [1, 4], "gajanan", "core", "'वहाँ आप और हम में थोड़ा भी भेद नहीं रहा; फिर भी जगत का व्यवहार ठीक तरह निभाना चाहिए।'", "Teaching: practical conduct."),
    ("S7-L10", "S7", 130, [1, 2], "gajanan", "core", "'देह ने अन्न खाया है, इसलिए उसे पानी चाहिए।'", "Teaching: practical conduct."),
    ("S7-L11", "S7", 131, [1, 4], "gajanan", "core", "'इसलिए आपकी चतुराई को ज़रूरत लगे तो पानी का प्रबंध कर लीजिए — बस, सब समाप्त।'", ""),
    ("S7-L12", "S7", 132, [4, 4], "bankatlal", "core", "'हमारा भाग्य धन्य है।'", "Table: Bankatlal (132)."),
    ("S7-L13", "S7", 133, [1, 2], "narrator", "core", "पानी लाने के लिए दामोदर घर के अंदर गए।", "Damodarpant enters Devidas's house (owner's final answer A1-5)."),

    ("S8-L1", "S8", 134, [1, 4], "narrator", "core", "कुएँ के पास एक हौद था, जहाँ सब जानवर पानी पी रहे थे।", ""),
    ("S8-L2", "S8", 135, [1, 2], "narrator", "core", "वहाँ जाकर उन्होंने पानी पिया और तृप्ति की डकार ली।", "The satisfied belch is in the verse; whether to sound it is the owner's choice."),
    ("S8-L3", "S8", 135, [3, 4], "narrator", "core", "इतने में पंत गड़वे में पानी लेकर आ गए।", ""),
    ("S8-L4", "S8", 136, [1, 4], "damodarpant", "core", "'अरे, अरे! वह गँदला पानी, समर्थ, मुख से न लगाइए; वह तो जानवरों के पीने योग्य है।'", "Table: Damodarpant (confirmed by the owner)."),
    ("S8-L5", "S8", 137, [1, 4], "damodarpant", "core", "'मैं यह देखिए जल ले आया — मीठा, निर्मल, ठंडा; इसमें खस डालकर सुगंधित किया है।'", "Table: Damodarpant (confirmed by the owner)."),

    ("S9-L1", "S9", 138, [1, 2], "narrator", "core", "यह भाषण सुनकर महाराज बोले —", ""),
    ("S9-L2", "S9", 138, [3, 4], "gajanan", "core", "'ये सारी व्यावहारिक बातें आप हमें न सुनाइए।'", "Table: Gajanan (138-142)."),
    ("S9-L3", "S9", 139, [1, 4], "gajanan", "core", "'यह सारा चराचर ब्रह्म से व्याप्त है; वहाँ गँदला, निर्मल, सुगंधित जल — ये भेद नहीं रहे।'", "Teaching 2."),
    ("S9-L4", "S9", 140, [1, 4], "gajanan", "core", "'पानी तो वही है; निर्मल हो या गँदला, वही देखो; सुगंध और दुर्गंध — दोनों उसी के रूप हैं, इसमें संदेह नहीं।'", "Teaching 2."),
    ("S9-L5", "S9", 141, [1, 4], "gajanan", "core", "'पीने वाला भी अलग नहीं है, उससे जुदा नहीं; ईश्वर की अगाध लीला इसी मनुष्य-जन्म में समझ आती है।'", "Teaching 2."),
    ("S9-L6", "S9", 142, [1, 4], "gajanan", "core", "'उसे आपने छोड़ दिया और मन को व्यवहार में उलझा लिया; इसी का सदा मनन कीजिए कि जगत किससे उत्पन्न हुआ।'", "Teaching 2."),
    ("S9-L7", "S9", 143, [1, 4], "narrator", "core", "समर्थ की ऐसी वाणी सुनकर दोनों भाव-विह्वल हो गए; अनन्य भाव से समर्थ के चरणों में लोटने को तैयार हो गए।", "The men are READY to fall at his feet."),
    ("S9-L8", "S9", 144, [1, 4], "narrator", "core", "उनका भाव जानकर महाराज दौड़ते-दौड़ते निकल पड़े; वायु की उस गति को जगत में कौन रोक सकता है?", "He runs; no destination."),
]

# closed sound palette (nothing here is sourced yet: the owner records or licence-checks each file before use)
PALETTE = [
    ("bed_roadside_quiet", "bed", "soft wind and a faint, distant village on a dusty road"),
    ("bed_courtyard_feast_murmur", "bed", "low murmur of a household feast, far off"),
    ("bed_village_noon_heat", "bed", "hot still noon: faint wind, a far-off bird, nothing else"),
    ("bed_village_morning", "bed", "soft early-day village ambience (unused so far; growth)"),
    ("bed_interior_quiet", "bed", "quiet house interior (unused so far; growth)"),
    ("bed_well_and_cattle", "bed", "a well-side place with cattle shuffling far off (unused so far; growth)"),
    ("fx_leaf_plate_rustle", "effect", "dry leaf plates being moved"),
    ("fx_footsteps_road_dust", "effect", "two people walking on a dusty road"),
    ("fx_cloth_bow_rustle", "effect", "soft cloth rustle of a respectful bow"),
    ("fx_plate_set_down", "effect", "a leaf plate set down on the ground"),
    ("fx_birds_flutter_to_trees", "effect", "birds flutter and settle in trees"),
    ("fx_door_wood_creak", "effect", "a wooden door opening, someone stepping in"),
    ("fx_cattle_distant", "effect", "cattle drinking and shuffling at a trough"),
    ("fx_water_trough_drink", "effect", "water lapping at a trough"),
    ("fx_brass_pot_clink", "effect", "a brass pot (gadva) carried and set down"),
    ("fx_wind_rush_run", "effect", "a rush of wind as someone runs away"),
    ("fx_gourd_hollow_tap", "effect", "a dry gourd tapped (unused so far; growth)"),
    ("fx_well_rope_bucket", "effect", "a rope and bucket at a well (unused so far; growth)"),
    ("fx_distant_crowd_murmur", "effect", "a small distant crowd (unused so far; growth)"),
    ("fx_wind_gust_soft", "effect", "a soft gust of wind (unused so far; growth)"),
    ("fx_cow_bell_distant", "effect", "a distant cow bell (unused so far; growth)"),
    ("fx_sandal_steps_stone", "effect", "sandals on a stone floor (unused so far; growth)"),
]

# cues: (id, scene, sound, anchor_type, anchor, label, ovi)   anchor_type: scene_bed | picture_event | before_line | after_line   label: verse-named | STAGING
CUES = [
    ("C1", "S1", "bed_roadside_quiet", "scene_bed", "", "STAGING", None),
    ("C2", "S2", "bed_courtyard_feast_murmur", "scene_bed", "", "verse-named", 86),
    ("C3", "S2", "fx_leaf_plate_rustle", "picture_event", "he searches the leaf plates", "verse-named", 93),
    ("C4", "S3", "bed_roadside_quiet", "scene_bed", "", "STAGING", None),
    ("C5", "S3", "fx_footsteps_road_dust", "picture_event", "the two men walk along the road", "verse-named", 97),
    ("C6", "S4", "bed_roadside_quiet", "scene_bed", "", "STAGING", None),
    ("C7", "S4", "fx_cloth_bow_rustle", "after_line", "S4-L4", "verse-named", 112),
    ("C8", "S5", "bed_courtyard_feast_murmur", "scene_bed", "", "STAGING", None),
    ("C9", "S5", "fx_plate_set_down", "after_line", "S5-L2", "verse-named", 114),
    ("C10", "S6", "bed_roadside_quiet", "scene_bed", "", "STAGING", None),
    ("C11", "S7", "bed_village_noon_heat", "scene_bed", "", "verse-named", 123),
    ("C12", "S7", "fx_birds_flutter_to_trees", "picture_event", "birds settle in the trees at noon", "verse-named", 123),
    ("C13", "S7", "fx_door_wood_creak", "after_line", "S7-L13", "STAGING", None),
    ("C14", "S8", "fx_cattle_distant", "picture_event", "cattle drink at the trough", "verse-named", 134),
    ("C15", "S8", "fx_water_trough_drink", "before_line", "S8-L2", "verse-named", 135),
    ("C16", "S8", "fx_brass_pot_clink", "before_line", "S8-L4", "STAGING", None),
    ("C17", "S9", "bed_village_noon_heat", "scene_bed", "", "STAGING", None),
    ("C18", "S9", "fx_wind_rush_run", "after_line", "S9-L8", "verse-named", 144),
]
