# How this came about

The process, in order, including the two findings that were reversed. This is
here because the reversals are the most useful part of the record and they are
invisible in the poster.

---

## 0. Why I am doing this at all

My PhD direction is accessibility, and the problem I keep returning to is
**forced disclosure**: to be served well by a system you have to let it know
you. For most people that is a bad trade they can decline — use the thing
logged out, accept worse suggestions, move on. For someone who depends on an
assistive system it is not a trade at all. It is a condition of access. You
cannot opt out of your own communication aid.

That is the asymmetry the field has not costed: **the people who most need
personalisation have the least room to refuse disclosure.** And their needs
move — day to day, room to room, hour to hour — so the disclosure is never
finished. It is a standing demand, renewed every session, and the profile it
builds outlives the person it described.

An earlier PhD application of mine came back asking me to specify what the AI
was actually *doing*. That was a fair hit. "AI-assisted accessibility" names a
hope, not a mechanism. This whole prototype is my answer to that question, and
the answer only counts if it is a number rather than an argument. §6 is the
answer; everything before it is how I got there, including the parts where I
was wrong.

---

## 1. The origin: a recommender that kept being wrong about me

I had been building a movie recommender for some months. It started the
obvious way: train it on my own taste. Rate things, learn the pattern, get
suggestions back.

It kept being wrong, and not randomly wrong. It was wrong in a specific
direction — it kept recommending the person I used to be. So I kept adding
categories to pin the taste down more precisely. More genres, more facets,
finer buckets. Every addition helped a little and the underlying problem never
moved, which is usually the sign that the problem is not the one you are
solving.

The thing I was actually running into is that a preference is not a property
of a person. A mug that is green can be beautiful *because* it is green, and a
shirt in exactly that green can be hideous, to the same person, on the same
day. If I liked a genre while I was seeing someone and we broke up, does the
preference carry over? Sometimes. There is no rule in the profile that knows
which.

And preferences expire silently. Nothing in a profile has a timestamp that
says "this stopped being true in 2021." The system keeps serving a model of
someone who has left.

So I reframed the question. Not *what does this person like* but **what does
this moment call for**. A recommender built on that question does not need a
complete model of me. It needs to know what is going on right now. The design
I wanted was: anchor on one film I actually chose recently, then offer
something near it, something far from it, and something random. The near one
respects the mood, the far one gives the taste somewhere to move, the random
one is how you find out you were wrong about yourself.

The analogy I kept using: you cannot take a bath in a cup of tea. The
container determines what the thing can be. A profile is a cup; a moment is
not.

## 2. The turn that made it a research question

The interesting consequence is not better recommendations. It is that *if the
moment carries the specificity, the profile does not have to.* Which means it
is an empirical question how much of the profile you can drop.

That question already has a literature. Biega et al. (SIGIR 2020)
operationalised GDPR Article 5(1)(c) — data minimisation — as a measurement:
hold quality fixed, see how little data you can get away with. They found
performance-based minimisation is feasible, and that selecting *which* items
to keep matters more than how many.

My question sat one step to the side of theirs. They varied how *much*. I
wanted to vary the **form**: the same budget spent on raw item IDs, on the
most popular items, on the most recent ones, or translated into a structured
description with no titles in it at all. And I wanted a cost on the other
axis, because minimisation is a privacy argument and privacy arguments need a
privacy measurement. So: how re-identifiable is each form?

That is the disclosure curve. Utility on one axis, re-identifiability on the
other, swept across input forms at matched budgets.

## 3. What I expected, and the first reversal

I expected translation to win — describe yourself in attributes instead of
titles, keep the utility, lose the fingerprint. That is the satisfying answer
and it is the one I was hoping for.

What actually won was **popularity disclosure**. Disclose your most-watched
items and you get the best Recall@20 at every budget, *and* you are the
hardest to re-identify (37% identified at rank 1, against 98% for random
items). It beat the trade-off in both directions at once.

That should have been the poster. Beating a trade-off in both directions at
once is also exactly the shape of a result that is wrong, so the gate for that
stage was: re-score every condition on **long-tail items only** — items below
the 80th popularity percentile, the ones a person could not plausibly have
found without personalisation.

Popularity disclosure scored **0.0000**. Not low. Zero, at k=8 and at k=13.
Disclosing random items scored 0.0221 on the same targets.

It had not beaten the trade-off. It had stopped personalising. Telling a
system your most popular items tells it almost nothing it did not already know
from the population, so it returns the population default — and the population
default is excellent on a metric dominated by popular items and worthless on
everything else. The strategy was winning the measurement by declining to do
the task.

This is the finding. It is not a minimisation strategy, it is a **measurement
warning**: the metric used to certify data minimisation can be passed by not
personalising, and in this setting it ranks strategies roughly opposite to the
metric that reflects personalisation.

## 4. The second reversal, which was my own fault

If selecting better is not the way out, the way out has to be getting
specificity from somewhere other than the person. That is the accessibility
motivation: context, environment, time, room — cues the system can observe
without anyone disclosing anything.

The first run said exactly that. Group context (occupation-level popularity on
ML-1M) looked like it beat individual disclosure. Very satisfying, directly
useful for the design argument, and **unfair**: the context condition was
restricted to tail items and the disclosure condition was not. I was comparing
one condition's hard score against another condition's easy score.

Restricting both (`fair_ml1m.py`):

```
global popularity  (no disclosure)   0.0408
group context      (no disclosure)   0.0476
1 disclosed item                     0.0581
8 items                              0.0954
55 items                             0.1775
full history                         0.2319
```

Context adds about 17% over knowing nothing. **One** disclosed item beats it.
Frappe, with real situational context instead of demographics standing in for
it, agrees in direction.

So the comfortable conclusion is false. Context does not replace the person;
it raises the floor. The honest design target is not *no disclosure*, it is
**the smallest honest disclosure** — and the reason that is still worth
chasing is that the curve is steeply concave. The first item buys more than
the next fifty-four. If you have to ask for something, ask for one thing and
stop.

## 5. Where this goes: accessibility and ability-based design

The reason to care is AAC — augmentative and alternative communication. A
picture-based speech app (app2speak is the example I use) groups vocabulary
into categories a user navigates to build an utterance. Core vocabulary is
small: roughly 200 words carry 80% of speech. Fringe vocabulary is enormous,
situational, and the thing people actually get stuck on.

Three things follow from the curve:

- **Context is worth building** even at +17%, because in AAC the floor is
  where the cost lands. Knowing the room, the time and who is present narrows
  the fringe vocabulary without anyone disclosing anything. That is a real
  reduction in navigation depth.
- **But plan to ask for one thing.** Since one disclosed item beats all the
  context available, the design question becomes *which single thing is worth
  asking for, and when* — not how to avoid asking.
- **And translation is the mechanism to study**, because in AAC the user's
  input is already being translated into something else. Measuring and
  moderating the input is what produces a usable output, which makes the human
  contribution legible, auditable and updatable. Ability-based design
  (Wobbrock et al. 2011) says adapt the system to the ability rather than
  requiring the ability — and the thing being adapted here is how much the
  person has to say about themselves before the system is useful.

The forced-intimacy problem is the point: a person who relies on an
assistive system should not have to be more known in order to be served.

## 6. The bigger picture: forced disclosure, and what the AI is doing

The research programme this belongs to is: **reduce how much a person has to
disclose about themselves before a system can serve them, and measure the
reduction.** Not reduce it in principle. Measure it.

The honest state of that question after this work is that there are three
mechanisms by which AI could do something about forced disclosure, and they
are not equally promising:

**Translation.** Turn what the person can express into what the system needs,
without the system needing a profile. This is the one closest to AAC practice,
because an AAC user's input is already being translated — pictures into
utterances. The research move is to treat the translation layer as the thing
being designed, and to measure its utility at a matched disclosure budget
against raw disclosure of the same size. In this prototype the attribute
translation was competitive but did not win, and I do not yet know whether
that is a property of translation or of my particular attribute space. That is
a real open question and it is the one I would want four years for.

**Context substitution.** Read the situation instead of the person — room,
time, who is present, what happened just before. This is the mechanism the
accessibility literature is most optimistic about and the one I most wanted to
confirm. It does not hold at the strength people assume. Measured fairly,
context buys about +17% over knowing nothing at all, and a *single* disclosed
item beats it (§4). Frappe, which has real situational context rather than
demographics standing in for it, agrees. So context is a **floor-raiser, not a
substitute.** That is still worth building in accessibility, because the floor
is exactly where the cost lands — narrowing fringe vocabulary by room and time
reduces navigation depth for someone who pays for every selection in effort.
But it does not get you out of asking.

**Elicitation.** If you must ask, ask the one thing that buys the most. This
is where the curve is actually encouraging: it is steeply concave, so the first
item buys more than the next fifty-four. "Which single thing is worth asking
for, and when" is a well-posed question with a measurable answer, and it is a
much better research target than "how do we avoid asking." The goal is the
**smallest honest disclosure**, not zero.

And one thing AI must not do, which this prototype demonstrates in miniature:
**look like it is personalising while returning the population default.** The
popularity artefact (§3) is exactly that failure — a system scoring well on
the certification metric by declining to do the task. In a recommender that
wastes an evening. In an assistive system it is worse than useless, because
the user cannot tell from inside the interaction that nothing is listening,
and will adapt their own behaviour to a system that is not responding to them.
Any claim that an AI layer has reduced disclosure burden has to be checked
against the possibility that it has simply stopped personalising, and the
standard metric will not catch that. That check is the transferable
contribution here, and it is the part I would carry into the PhD first.

Which is also why the measurement came before the design. There is no shortage
of claims that AI will reduce the disclosure burden in accessibility. What is
missing is a number. The disclosure curve is my attempt at one, and the first
thing it did was kill two of my own claims — which is the strongest argument I
can make that it is measuring something.

## 7. The gates, which are the method

Every stage got the same treatment: run it, then attack it as a hostile
reviewer, then add the control the attack implies, then re-check against the
literature before moving on. Concretely, that caught:

- an **unfair model comparison** — the attribute condition was scored by
  attribute matching while raw conditions were scored by EASE. Fixed by
  expanding descriptions into exemplar items scored by the *same* model.
- **oracle leakage** — a strategy was being selected and evaluated on the same
  held-out items, which produced a score above the full-history ceiling. Fixed
  by splitting targets into a selection half and an evaluation half.
- a **moving cohort** — the population changed between budgets and produced a
  non-monotonic curve. Fixed with a fixed cohort, pool ≥ max budget.
- a **fabricated reference** that I had in a draft and could not verify
  against any index. Replaced with the real one.
- the **popularity artefact** (§3) and the **unfair context comparison** (§4).

Two of those reversed a headline. That is the argument for the gates, and it
is why they are in the repository instead of being tidied away.

## 8. What I would not claim

The limits are in `README.md` and they are load-bearing: ρ = −0.284 at
p = 0.058 is suggestive and not significant, so the direct 0.0000-vs-0.0221
comparison carries the result; re-identification here is linkage inside a
closed set rather than a privacy guarantee; one linear model family; an 87-user
Frappe cohort; and the 80th-percentile tail cut is a conventional choice, not
a derived one.

The submitted abstract promised a disclosure budget. The work produced a
warning about how such budgets are certified. I would rather say that plainly
than present the second as if it had been the plan.
