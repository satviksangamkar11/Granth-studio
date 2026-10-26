# Story split, Adhyay 1: NO_CHECK

DRAFT for the owner's approval. Nothing is directed, rendered or approved. VALID = the code coverage checks passed and the cross-check answered every question 'yes'.
Macro hash (what you approve): `bf664651e8376632ab1fd3054fc7107168f72c8f5a4b5cc9b13ca57732dfcc1b`

- macro `nvidia/nemotron-3-ultra-550b-a55b`: HTTP 200, 97.4 s, finish stop, usage None
- macro_repair `nvidia/nemotron-3-ultra-550b-a55b`: HTTP 200, 24.1 s, finish stop, usage None
- macro_review `openai/gpt-oss-20b`: HTTP 200, 43.9 s, finish stop, usage {'prompt_tokens': 11875, 'completion_tokens': 1298, 'total_tokens': 13173}

Warnings:
- A1-T1: 21 shots in total: it will be directed in several ordered parts

Reviewer `openai/gpt-oss-20b` (first split): **NO_CHECK**, missing ['M1', 'M2', 'M3', 'M4', 'M5', 'M6']

Repair `macro_repair`: **USED**

Source: chapter 1, ovi 1-146

## A1-T1: Gajanan Maharaj reveals his divine nature at Devidas's house in Shegaon (ovi 84-144, arc complete)
- boundary A1:84: Author explicitly begins the story: 'Now I tell you the story of that time; a devout householder named Devidas'
- boundary A1:144: Gajanan departs running like the wind, ending the incident: 'Maharaj went away swiftly, who can obstruct the wind's speed?'
- **S1** ovi 84-96, 5 shots: Devidas prepares a feast; Gajanan sits on the road eating leftover rice from discarded leaf plates, embodying 'food is Brahman'; Bankatlal witnesses this. (context A1:83)
- **S2** ovi 97-110, 4 shots: Bankatlal and Damodarpant debate whether Gajanan is mad or a sage; Bankatlal humbly questions him; Gajanan only gazes steadily at both.
- **S3** ovi 111-121, 4 shots: Gajanan's radiant form described; Devidas brings a full plate of delicacies; Gajanan eats without craving; Bankatlal realizes his error, comparing Gajanan to Arjuna's feigned madness.
- **S4** ovi 122-137, 5 shots: At midday Gajanan's gourd is empty; Damodar fetches water; Gajanan drinks from a cattle trough, then teaches worldly conduct must be followed; Damodar returns with scented water in a pot.
- **S5** ovi 138-144, 3 shots: Gajanan teaches non-duality: water and drinker are one Brahman; both men are moved to surrender; knowing their intent, Gajanan vanishes like the wind. (context A1:145)

## Unfilmed (narrator or omitted)
- ovi 1-32 [invocation]: Invocations to Ganesha, Saraswati, Pandurang, Shiva, Kuladevi, Dattatreya, rishis, saints; author's humility and plea for guidance
- ovi 33-41 [commentary]: Author urges listeners to hear saint-stories, praises saints as God on earth, source of liberation
- ovi 42-55 [background]: Lists of saints from Narad to Mahipati; references to author's earlier works Bhaktivijay and Bhaktamala
- ovi 56-68 [background]: Shegaon's glory described; Ramchandra Patil requests the author to write Gajanan's life during Kartiki pilgrimage
- ovi 69-83 [background]: Gajanan's mysterious arrival in youth on Magh Vadya Saptami; avatar discussion citing ayonisambhava births of Nath yogis
- ovi 145-146 [closing]: Author announces next chapter, asks for attention, signs off with colophon and 'Shri Hari Hararpanamastu'

## Direction parts (code-derived)
- A1-T1-P1: scenes S1, S2, 9 shots
- A1-T1-P2: scenes S3, S4, 9 shots
- A1-T1-P3: scenes S5, 3 shots
