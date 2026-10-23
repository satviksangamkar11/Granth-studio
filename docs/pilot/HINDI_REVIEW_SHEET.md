# Hindi language-review sheet for the provisional 45-second pilot (review PENDING)

Decision (owner, 2026-10-23): the assistant's Hindi drafts are the provisional WORKING text. IndicTrans2 execution = PASS (pinned revision `24d73292…`, identity verified). IndicTrans2 translation quality = FAIL. Hindi human review = PENDING. The six original model outputs are kept unchanged as evaluation evidence in `docs/evidence/audio_translate/run1_b4dd57aa/`; they are not edited here and must not replace the drafts.

**d_0006: the model's line reverses the meaning (Bankatlal admits his own mistake; the model says someone was astonished). It must never enter a soundtrack. Every one of the six lines needs this review, not only a protected-term check.**

Reviewer checklist per line: (1) meaning faithful to the Marathi; (2) subject/who acts and who is addressed; (3) speaker attribution (narration vs quoted speech, first/second person); (4) protected devotional terms (परब्रह्म etc.) in an allowed form; (5) natural, reverent Hindi for narration; (6) length suitable for the shot.

## d_0001

| | |
|---|---|
| Marathi (assistant transcription, to be proofread) | उष्ट्या पत्रावळी रस्त्यावर । टाकिल्या होत्या साचार । घराचिया समोर । त्या देविदास विप्राच्या |
| **Working Hindi (assistant draft)** | देविदास ब्राह्मण के घर के सामने रास्ते पर जूठी पत्तलें फेंकी हुई थीं। |
| IndicTrans2 output (evidence only, failed review) | सड़कों पर तितर-बितर हो रहे पर्चे। घर के सामने तितर-बितर किए जा रहे थे। वे थे देवीदास विप्र के। |
| Automatic checks on the model output | none raised (this is not a meaning check) |
| Reviewer verdict on the working Hindi | PENDING |
| Reviewer name / date | (unsigned) |
| Corrections | |

## d_0002

| | |
|---|---|
| Marathi (assistant transcription, to be proofread) | शीत पडल्या दृष्टीप्रत । तें मुखी उचलुनी घालीत । हे करण्याचा हाच हेत । अन्न परब्रह्म कळवावया |
| **Working Hindi (assistant draft)** | जो भी भात का दाना उनकी दृष्टि में आता, उसे उठाकर वे मुँह में डाल लेते; ऐसा करने का उद्देश्य यही था कि अन्न ही परब्रह्म है, यह बताया जाए। |
| IndicTrans2 output (evidence only, failed review) | आँखों में ठंड लग रही है। वह अपना मुँह हिलाता है। यही उसका उद्देश्य है। अन्न ब्रह्म को बताएँ। |
| Automatic checks on the model output | d_0002: protected term term_parabrahma lacks an allowed Hindi form |
| Reviewer verdict on the working Hindi | PENDING |
| Reviewer name / date | (unsigned) |
| Corrections | |

## d_0003

| | |
|---|---|
| Marathi (assistant transcription, to be proofread) | बंकटलाल आगरवाला । होता रस्त्यानें चालला । त्याने हा प्रकार पाहिला । आपल्या त्या स्नेह्यासह |
| **Working Hindi (assistant draft)** | बंकटलाल अग्रवाल रास्ते से चले जा रहे थे; उन्होंने अपने उस मित्र के साथ यह सब देखा। |
| IndicTrans2 output (evidence only, failed review) | बंकटलाल अग्रवाल। वह सड़क पर चल रहा था। उसने यह देखा। अपने प्यार के साथ। |
| Automatic checks on the model output | none raised (this is not a meaning check) |
| Reviewer verdict on the working Hindi | PENDING |
| Reviewer name / date | (unsigned) |
| Corrections | |

## d_0004

| | |
|---|---|
| Marathi (assistant transcription, to be proofread) | ह्या पत्रावळीच्या शोधना । कां हो करितां कळेना । क्षुधा असेल आपणां । तरी तरतूद करूं अन्नाची |
| **Working Hindi (assistant draft)** | "इन पत्तलों को आप क्यों खंगाल रहे हैं, समझ नहीं आता। यदि आपको भूख हो तो हम अन्न का प्रबंध कर देंगे।" |
| IndicTrans2 output (evidence only, failed review) | इन पत्रों की खोज न करें। मुझे नहीं पता कि क्यों। हमें भूख लगेगी। फिर भी हम भोजन की व्यवस्था करेंगे। |
| Automatic checks on the model output | none raised (this is not a meaning check) |
| Reviewer verdict on the working Hindi | PENDING |
| Reviewer name / date | (unsigned) |
| Corrections | |

## d_0005

| | |
|---|---|
| Marathi (assistant transcription, to be proofread) | देविदासें तैसें केलें । पक्कान्नांनीं भरलेले । पात्र आणून ठेविलें । द्वारासमोर स्वामींपुढे |
| **Working Hindi (assistant draft)** | देविदास ने वैसा ही किया; पकवानों से भरी थाली लाकर द्वार के सामने स्वामी के आगे रख दी। |
| IndicTrans2 output (evidence only, failed review) | देवीदास ने ऐसा ही किया। पकौड़ों से भरा हुआ। मैंने दरवाजा खोलकर स्वामी के सामने बर्तन लाए। |
| Automatic checks on the model output | none raised (this is not a meaning check) |
| Reviewer verdict on the working Hindi | PENDING |
| Reviewer name / date | (unsigned) |
| Corrections | |

## d_0006

| | |
|---|---|
| Marathi (assistant transcription, to be proofread) | बंकटलाल तें पाहून । पंताशी करी भाषण । ह्या वेडा म्हणालो आपण । ती नि:संशय झाली चुकी |
| **Working Hindi (assistant draft)** | यह देखकर बंकटलाल पंत से बोले: "हमने इन्हें पागल कहा, वह निःसंशय हमारी भूल थी।" |
| IndicTrans2 output (evidence only, failed review) | उसे देख कर वह दंग रह गया। उसे पूछने पर उसने कहा, "यह तो पागल है।" वह हैरान रह गई। |
| Automatic checks on the model output | none raised (this is not a meaning check) |
| Reviewer verdict on the working Hindi | PENDING |
| Reviewer name / date | (unsigned) |
| Corrections | |
