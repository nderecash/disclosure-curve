---
title: "Context Instead of Disclosure: Applying the Fringe Vocabulary Problem to Context-Aware AAC"
subtitle: "Research design note, grounded in a mechanism test run on MovieLens 1M"
author: "Moses Nderemani, Pervasive Interaction Research Group, Tampere University"
date: "8 October 2026"
geometry: margin=2.3cm
fontsize: 10pt
linestretch: 1.1
colorlinks: true
---

## 1 What this applies

The SDLCAI result found that within a personalisation system the informative signal and the identifying signal are the same signal. Items common enough not to identify anyone are also too common to personalise. Items specific enough to be useful are specific enough to name the person. Better selection of what to retain does not escape this, because selection only reorders the same material.

Context is a different kind of material. A room, a time of day, a recurring timetable slot are properties of the environment, not statements made by the person. If context can supply specificity, the trade-off has a third term.

This note tests whether that is true, maps it onto communication aids, and sets out the study.

## 2 The mapping

Augmentative and alternative communication research already has the head-and-tail distinction, under different names. Boenisch et al. analysed roughly 55,500 words from children with and without physical disabilities and found that the 100 most frequent words account for 66% of spoken words and the 200 most frequent for 80% [1]. Those 200 words are the core vocabulary: want, go, stop, help, more. The remaining 20% is fringe vocabulary, mostly specific nouns, and it is where individual circumstances enter. Core vocabulary is described as independent of personal living circumstances; fringe vocabulary selection is described as needing to take personal interests into account [1].

Core vocabulary is the popularity head. It is shared, it identifies nobody, and it is already on every board. Fringe vocabulary is the long tail. It is what makes a board usable for one particular person in one particular situation, and it is exactly what a disclosure argument has to be about. In a communication aid the fringe entries are names of people, medications, routines, the ward, the diagnosis. The content that makes the aid work is the content that should not have to be handed over.

APP2Speak, a photograph-based aid for adults with stroke, aphasia, ALS, Parkinson's and related conditions, illustrates the structure [2]. It ships preloaded pages for immediate wants and needs, and the user or a family member builds custom pages for specific situations. The preloaded pages are core. The custom pages are fringe, and they are built by hand, by the person or a carer, item by item.

## 3 Mechanism test

Before designing a study around context, the mechanism was tested on the dataset already in hand. The question: does group-level popularity retrieve long-tail items that global popularity cannot, without any individual disclosure?

MovieLens 1M, the EASE model and the cohort from the earlier study (1,012 users, 2,380 items, items below the 80th popularity percentile counted as tail). Occupation stands in for a shared setting. It is a structural proxy only, chosen because it is the one grouping in the dataset that is not derived from the behaviour being predicted. The ethical argument in the communication case requires a grouping that is a property of the environment, such as a room.

**Table 1. Long-tail Recall@20 and identification cost.**

| Condition | Individual disclosure | Tail Recall@20 | Identified at rank 1 |
|---|---|---|---|
| Global popularity, whole catalogue | none | 0.0000 | 0% |
| Group popularity, whole catalogue | none | 0.0000 | <= 3% |
| Global popularity, tail only | none | 0.0408 | 0% |
| Shuffled groups, tail only (20 runs) | none | 0.0368 | <= 3% |
| **Real groups, tail only** | **none** | **0.0476** | **<= 3%** |
| 8 random disclosed items | 8 items | 0.0251 | 90.3% |
| 13 random disclosed items | 13 items | 0.0216 | 98.0% |
| Full history | everything | 0.0212 | 100% |

Four things follow, and the third was only visible because of a control.

**Context as a ranking signal does nothing.** Group popularity over the whole catalogue retrieves 0.0000 on tail targets, the same as global popularity. The group's top 20 overlaps the global top 20 by 72% on average. The head dominates every grouping, so a context-ranked list is a popularity list.

**Reserving capacity for the tail is what recovers tail performance.** The gain comes from excluding head items from the slate, not from knowing anything about the user. An unrestricted ranked list spends most of its twenty slots on head items, which cannot be tail targets by definition. This is a slot allocation finding rather than a personalisation finding, and it should be read that way.

**The grouping contributes, but modestly.** Real groups reach 0.0476 against 0.0408 for global popularity with the same tail restriction, a relative gain of 17%. Shuffled group labels reach 0.0368, below the global baseline, because small random groups are noisy estimates of the same distribution. Without this control the headline would have been the 0.0476 figure against the 0.0000 unrestricted baseline, which would have attributed the tail restriction's effect to the grouping.

**Naive combination of context and disclosure is harmful.** Adding a normalised group score to a disclosure-based score lowered tail recall at every profile size tested, from -0.0172 at one item to -0.0225 at eight. The context score pulls the slate back toward the head.

The comparison in Table 1 is not like for like, and the caveat matters. Tail-restricted conditions are guaranteed to spend all twenty slots on tail items; unrestricted conditions are not. The finding is therefore about how slates are allocated, not a demonstration that context outperforms personalisation.

## 4 What this says for the design

A context-aware communication aid should not let context rank the vocabulary. It should let context fill the fringe.

Core vocabulary stays permanently available, which is already standard practice in the field. The fringe slots are the ones that change, and they can be populated from a shared description of the setting rather than from the person's own stored history. In the university case, a lecture hall has projector, slides, handout, question, seat. A clinic reception has appointment, waiting, form, interpreter. Those entries are fringe globally and core locally. They are properties of the room, and a room is not a person.

This converts a disclosure problem into a different problem, which is maintaining shared descriptions of places. That problem has owners: estates, accessibility services, the people who already maintain room booking systems.

Three claims from the mechanism test carry into the design, and they are the parts worth testing with people:

1. Reserved fringe capacity matters more than better ranking.
2. Shared setting descriptions supply fringe content at low individual identification cost.
3. Context and personal history cannot be fused by score addition.

## 5 Prior work, and what is left

**Context-aware AAC is not new.** Hossain et al. built a system using GPS and the Google Place API to filter categories by proximity, and ranked items by usage frequency within four daily time slots: morning, afternoon, evening and night [3]. They tested with four adults with aphasia and reported one case in detail, with roughly 95% location accuracy and 80% navigation rate, and noted that automatic suggestions had the lowest accuracy of any component. Location plus time of day plus routine frequency is their design. It is also, in outline, the idea in your notes.

What they did not do is measure what the context was substituting for. Context was added to improve ranking. Whether it reduces how much a person has to disclose was not asked, and the mechanism test above indicates that ranking is the wrong place to put it.

**Ability-based design already covers part of your notes.** Wobbrock et al. state seven principles [4]. Principle 3, Adaptation, covers interfaces that adapt themselves or are adapted by a user, therapist or carer. Principle 4, Transparency, states that users can inspect, override, discard, revert, store, retrieve, preview and test adaptations. Principle 6, Context, states that systems may proactively sense context and anticipate its effects on users' abilities, and the authors name sensing for all relevant context as a major area of future work.

Your notes on meaningful control, clear human contribution, oversight, and updating the pipeline are restatements of principles 3 and 4. This is useful rather than disappointing. You cite them instead of arguing for them, and the citation is stronger than the argument.

**The current AAC and AI literature names the gap.** Mao et al. ran design probes with 11 people with aphasia across two phases [5]. Their prototypes did not sense context automatically; context came only from user input, and participants asked for context-aware alternatives, including more options within a category when the exact word is unavailable. The paper gives little attention to privacy. Trust rose when systems captured intent and offered multiple options, and fell when suggestions were irrelevant or mistimed. Usefulness varied with severity, so no single design suited every participant.

**What is left after all of that.** Not context-aware vocabulary, which exists. Not the principles, which are published. The open question is whether environment-derived specificity substitutes for person-derived specificity, measured as a rate: how much fringe coverage does a shared setting description buy per unit of personal disclosure, compared with the same coverage bought from the person's own stored vocabulary.

## 6 Study design

A user study rather than a benchmark, since the quantity that matters is whether people can say what they came to say, and what they had to give up to do it.

**Design.** Within-subjects, three conditions, order counterbalanced. Participants are adults who use or are candidates for photograph-based AAC. Recruitment through TACCU contacts and clinical partners. Target 12 to 16 participants, which is in the range of the comparable studies cited here.

**Conditions.**

- **A, personal baseline.** The aid as it works now: core board plus fringe pages the participant or a carer built by hand.
- **B, context only.** Core board plus fringe slots filled from a shared description of the room, with no stored personal vocabulary.
- **C, context plus minimum personal.** Condition B plus a small, participant-chosen set of personal fringe entries, with the number chosen by the participant and recorded.

**Setting.** Three rooms with different affordances on campus: a lecture hall, a cafe counter, and a service desk. Each visited once per condition. Real tasks defined with participants beforehand, not scripted phrases.

**Measures.**

| Measure | How |
|---|---|
| Communication success | Did the message get across, rated by participant and by partner, with disagreements kept rather than averaged |
| Fringe coverage | Proportion of intended fringe items that were available without manual entry |
| Repair cost | Time and turns spent when the needed item was absent |
| Disclosure volume | Number of personal fringe entries stored, by condition |
| Perceived exposure | Participant rating of how much the system knows about them, and how that feels |
| Control | Wobbrock principle 4 items: could they inspect, override, revert |

The substitution rate is the ratio that connects this to the earlier work: fringe coverage per personal entry stored, in condition C against condition A.

**Analysis.** Within-subject comparison of the primary measures; participants are the unit. Interview material analysed thematically, with particular attention to cases where context supplied the wrong word, since the mechanism test says irrelevant suggestions are the main failure mode and Mao et al. found that trust falls when they occur [5].

**Ethics.** This involves disabled adults and health-adjacent vocabulary. TAU ethics review needed, consent procedures adapted for communication impairment, and a decision made in advance about what room databases may contain. Start this in parallel with the design, not after it.

## 7 Risks

**Context is itself disclosure.** Knowing that a person is in the accessibility unit at 14:00 every Tuesday is sensitive, and location traces are strongly re-identifying. The honest framing is a trade between kinds of disclosure, not an elimination of it. The 3% figure in Table 1 is a single categorical membership; a continuous location trace is a different object and should not be described with that number.

**Shared room databases have an owner problem.** Someone has to write and maintain them. An unmaintained room database is worse than no room database, because it fills fringe slots with wrong content, which is the failure mode that loses trust.

**Reserved fringe capacity costs something.** Slots given to context are slots not given to the person's own high-value entries. Condition C exists to find where that balance sits, and it may sit close to condition A.

**Narrowing.** A system that predicts what someone needs in a room has decided in advance what needs exist there. This is the tunnel vision in your notes and it is the strongest objection to the whole approach. It should be measured, not mentioned: count the occasions where participants wanted something the room description had no slot for.

**Generality.** MovieLens films are not vocabulary, and occupation is not a room. The mechanism test says the structure is plausible, not that the numbers transfer.

## 8 Your notes

**Belongs, and is the contribution.** Translating input, as a parallel to prompt engineering aimed at the user rather than the model. This is the framing that distinguishes the work from Hossain et al., who added context without asking what it replaced.

**Belongs, and is now measurable.** Measuring and moderating inputs gives better outputs: this is the substitution rate in section 6. Better understanding of what the user needs: fringe coverage. Easy identification of gaps at the planning stage: the count of occasions where the room description had no slot.

**Belongs, but cite rather than claim.** Meaningful control with clear human contribution, ease of oversight, ease of updating the pipeline. These are Wobbrock principles 3 and 4 [4].

**Needs defining before it can be used.** Latent skill. If this means the person's residual communicative competence, it is principle 1, Ability. If it means something the system infers that the person has not demonstrated, it is a different and more contestable claim and needs stating separately.

**Cut.** Shifting from a linear point of view to systems thinking. It is unsupported, it is not measurable in this design, and it invites the one question in the room that no figure answers.

## References

[1] Boenisch, J. and Sachse, S. K. 2020. Core vocabulary: importance for daily communication. In *Kompendium Unterstützte Kommunikation*, Kohlhammer, 108–116. English translation. Reports Boenisch et al. 2007, approximately 55,500 words analysed.

[2] APP2Speak. Photograph-based AAC application. https://app2speak.com/ (accessed 8 October 2026).

[3] Hossain, M. S., Takanokura, M., Sakai, H. and Katagiri, H. 2018. Using Context History and Location in Context-aware AAC Systems for Speech-language Impairments. In *Proceedings of IMECS 2018*, Hong Kong, 128–133.

[4] Wobbrock, J. O., Kane, S. K., Gajos, K. Z., Harada, S. and Froehlich, J. 2011. Ability-Based Design: Concept, Principles and Examples. *ACM Transactions on Accessible Computing*. Volume and article number not verified.

[5] Mao, L., Lee, J. H., Faroqi Shah, Y. and Valencia, S. 2025. Design Probes for AI-Driven AAC: Addressing Complex Communication Needs in Aphasia. In *Proceedings of DIS '25*, Funchal, Madeira.

[6] Biega, A. J., Potash, P., Daumé III, H., Diaz, F. and Finck, M. 2020. Operationalizing the Legal Principle of Data Minimization for Personalization. In *SIGIR '20*, 399–408.

[7] Narayanan, A. and Shmatikov, V. 2008. Robust De-anonymization of Large Sparse Datasets. In *IEEE Symposium on Security and Privacy*, 111–125.
