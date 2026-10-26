# Story split, Adhyay 1: VALID

DRAFT for the owner's approval. Nothing is directed, rendered or approved. VALID = the code coverage checks passed and the cross-check answered every question 'yes'.
Macro hash (what you approve): `acb32841c7ccb81597935b0f180c764ab0b02038a1dcbd90c98860141267d39d`

- macro `kimi-k3.1-pro`: HTTP 200, 250.9 s, finish stop, usage {'prompt_tokens': 14163, 'completion_tokens': 7145}
- macro_repair `kimi-k3.1-pro`: HTTP 200, 28.9 s, finish stop, usage {'prompt_tokens': 15295, 'completion_tokens': 1064}
- macro_review `nvidia/nemotron-3-ultra-550b-a55b`: HTTP 200, 152.1 s, finish stop, usage None

Warnings:
- A1-T1: 33 shots in total: it will be directed in several ordered parts

Reviewer `nvidia/nemotron-3-ultra-550b-a55b` (first split): **PASS**

Repair `macro_repair`: **USED**

Source: chapter 1, ovi 1-146

## A1-T1: The first recognition at Devidas's feast (ovi 84-144, arc complete)
- boundary A1:84: The narrative introduces Devidas, whose household feast establishes the roadside encounter.
- boundary A1:144: After the teaching and the men's move toward surrender, Gajanan runs off like the wind, closing the encounter.
- **S1** ovi 84-94, 5 shots: Devidas prepares his son's ritual feast; outside, the nearly naked stranger searches discarded leaf plates and eats leftover rice grains to reveal food's sacredness. (context A1:74, A1:83)
- **S2** ovi 97-105, 4 shots: Bankatlal and Damodarpant see him, debate whether he is mad or profoundly wise, and resolve to test his conduct rather than dismiss him. (context A1:94)
- **S3** ovi 108-112, 4 shots: Bankatlal humbly asks why he searches the plates; an unanswered question, a steady look and radiant, blissful silence turn the test into reverence. (context A1:102)
- **S4** ovi 113-115, 3 shots: At the visitors' request Devidas places a full plate before Gajanan; he sits to eat without attraction or aversion toward its tastes.
- **S5** ovi 118-122, 3 shots: He finishes the mixed meal; Bankatlal withdraws the charge of madness, invokes Arjuna's example and honours the desireless yogi. (context A1:99)
- **S6** ovi 123-133, 5 shots: At noon the gourd is empty; Damodar offers water, Gajanan laughingly explains practical conduct, and Damodar joyfully goes to fetch it. (context A1:89, A1:118)
- **S7** ovi 134-137, 4 shots: Gajanan drinks at the cattle trough; Damodar returns with cool, vetiver-scented water and protests that the muddy water is fit only for animals. (context A1:133)
- **S8** ovi 138-144, 5 shots: Gajanan declares water, its qualities and the drinker undivided in Brahman; as the men move to surrender, he speeds away like the wind. (context A1:137)

## Unfilmed (narrator or omitted)
- ovi 1-32 [invocation]: Invocations to deities and saints, with the author's humility and prayer for guidance in composing the work.
- ovi 33-38 [commentary]: The author exhorts listeners and praises saints; these verses narrate no story event.
- ovi 39-57 [background]: Lists of earlier saints, earlier books and the author's plan explain the lineage and purpose of this biography.
- ovi 58-83 [background]: Shegaon, Patil's request, the appearance date and speculation about Gajanan's origin are narrated setup for the encounter.
- ovi 95-96 [commentary]: The Upanishadic explanation of food as Brahman adds no new action beyond the filmed grain-picking.
- ovi 106-107 [commentary]: The narrator contrasts unobservant passers-by with the discerning gem-picker; this is reflective narration, not required action.
- ovi 116-117 [commentary]: Two analogies explain freedom from taste and possession; the meal itself resumes at ovi 118.
- ovi 145-146 [closing]: The next-chapter announcement and the author's prayerful dedication close the chapter.

## Direction parts (code-derived)
- A1-T1-P1: scenes S1, S2, 9 shots
- A1-T1-P2: scenes S3, S4, 7 shots
- A1-T1-P3: scenes S5, S6, 8 shots
- A1-T1-P4: scenes S7, S8, 9 shots
