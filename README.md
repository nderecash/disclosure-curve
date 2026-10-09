# Minimum Viable Disclosure

**What a short disclosure buys you, and why the strategy that looks best
personalises least.**

Poster, SDLCAI 2026 seminar (Tampere University) · Moses Nderemani, PIRG

---

## The one-paragraph version

Performance-based data minimisation asks how little personal data a
recommender needs before quality drops (Biega et al., SIGIR 2020). Running
that sweep across input *forms* rather than just input *size*, one strategy
appears to beat the trade-off: disclose your **most popular** items and you
get the highest Recall@20 at every budget while staying the hardest to
re-identify. That result is an artefact. Re-scored on long-tail targets —
items below the 80th popularity percentile, i.e. the ones a person could not
have found without personalisation — the same strategy scores **0.0000**,
against 0.0221 for disclosing random items. It won the standard metric by
abandoning personalisation and returning the population default. The
headline finding is therefore not a minimisation strategy but a **measurement
warning**: in this setting the metric used to certify minimisation ranks
strategies in roughly the opposite order from the metric that reflects
personalisation, and the certification can be passed by not personalising.

## What held up, and what did not

| Claim | Verdict |
|---|---|
| Popularity disclosure tops standard Recall@20 at every budget | **holds** (0.2294 at k=13 vs 0.1957 random) |
| …and is hardest to re-identify | **holds** (37.1% identified at rank 1 vs 98.0% random) |
| …therefore it is a good minimisation strategy | **fails** — tail Recall@20 = 0.0000 at k=8 and k=13 |
| Standard and tail metrics disagree in rank | **weak**: Spearman ρ = −0.284, p = 0.058, n = 45 — reported as suggestive, not significant |
| Context can substitute for individual disclosure | **fails** — see the correction below |

### The correction I had to make

An early run suggested group context (occupation-level popularity) beat
individual disclosure, which would have been the comfortable conclusion: get
specificity from the situation, not the person. That comparison was unfair —
the context condition was restricted to tail items and the disclosure
condition was not. `fair_ml1m.py` restricts both. Fairly compared, on ML-1M
tail Recall@20:

```
global popularity  (no disclosure)   0.0408
group context      (no disclosure)   0.0476     context adds ~+17% over popularity
1 disclosed item                     0.0581     one item already beats context
8 items                              0.0954
55 items                             0.1775
full history                         0.2319
```

Frappe, with *real* situational context rather than demographics standing in
for it, agrees: context popularity 0.0272 tail Recall@10 vs 0.0294 for a
single disclosed app. **Context raises the floor; it does not replace the
person.** The design consequence is the opposite of the comfortable one: aim
for the smallest honest disclosure, not for no disclosure.

## The two datasets

**MovieLens 1M** — no context, demographics standing in for it. 553,277
positives after iterative ≥20 filtering (5 passes), 5,148 users, 2,380 films.
Users split, not interactions, so test users are absent from the training
matrix (strong generalisation). Fixed cohort of 1,012–1,053 users with pool
≥ 55 so the population cannot move between budgets. EASE (Steck, WWW 2019,
λ=250), whose profile enters at inference — so a profile-size sweep needs no
retraining. 3 seeds (42, 7, 2024), bootstrap CIs over users (2,000 resamples).

**Frappe** — real situational context recorded at use time. Evaluated per
(user, context) cell, Recall@10, cohort of 87 users / 235 cells. Small, and
quoted as a direction check rather than an independent confirmation.

## Reproducing

```bash
git clone https://github.com/nderecash/disclosure-curve
cd disclosure-curve
pip install -r requirements.txt
bash download_data.sh          # datasets are not committed; see data/README.md

python src/experiment.py       # main sweep        -> results/sweep.csv, meta.json
python src/robust.py           # 3 seeds + CIs    -> results/sweep_allseeds.csv, summary.csv
python src/gate_tail.py        # THE GATE         -> results/tail.csv
python src/pareto.py           # frontier, standard metric
python src/pareto_tail.py      # frontier, tail metric + Spearman
python src/context_test.py     # group context, 3 gates -> results/context_test.csv
python src/context_control.py  # shuffled-group control
python src/fair_ml1m.py        # the fair comparison -> results/fair_ml1m.csv
python src/frappe_exp.py       # second dataset      -> results/frappe.csv
python src/figs.py             # paper figures
python src/poster_figs.py      # poster figures
```

Run from the repository root — the scripts use relative paths. `experiment.py`
takes ~28 s; everything else is faster. Override dataset location with
`ML1M_DIR=/path/to/ml-1m`.

Every script that makes a claim also runs its own control. `gate_tail.py`
re-scores every condition on tail targets. `context_control.py` shuffles group
labels. `experiment.py` includes a shuffled-user control for the translation
condition, and splits held-out items into a selection half and an evaluation
half so that a strategy cannot be chosen and scored on the same targets.

## The story, including the reversals

[`NARRATIVE.md`](NARRATIVE.md) is the process record: why I am working on
forced disclosure in the first place, where the question came from, what I
expected, the two findings that were reversed by their own gates, how this
connects to the wider PhD question of what an AI layer can actually do about
disclosure burden in accessibility, and where it goes next. Read that before
the paper if you want to know why any of this was done.

## Layout

```
NARRATIVE.md  why, how this came about, and the two reversals
src/        experiment + every gate and control
results/    the CSVs behind every number quoted above
figures/    vector figures (SVG for the poster, PDF for the paper)
paper/      paper.{md,pdf}   7pp short paper, Mindtrek format
            guide.{md,pdf}   4pp two-dataset design guide
            design.{md,pdf}  6pp AAC / ability-based-design research design
poster/     poster.html + poster-A0.pdf (841 x 1189 mm, 1 page) + qr.svg
data/       empty; download_data.sh fills it
```

## Honest limits

- **Re-identification here is linkage within a closed set**, not a privacy
  guarantee: rank all cohort profiles by cosine against a k-item holding. It
  bounds how distinctive a short disclosure is in a known population. It is
  not an attack and it does not model an adversary with outside data.
- **ρ = −0.284, p = 0.058** does not clear significance. The load-bearing
  result is the direct comparison (0.0000 vs 0.0221), not the correlation.
- **One model family.** EASE and item-kNN are linear item-item models. A
  sequential or neural recommender may order the strategies differently, and
  nothing here tests that.
- **The tail cut at the 80th percentile is a choice.** It is the usual one,
  but the 0.0000 is a property of popularity disclosure under *that* cut.
- **Frappe's cohort is 87 users.** Direction check only.
- **ML-1M occupation is not situational context.** It stands in for grouping
  because ML-1M has nothing better; Frappe is in the repository precisely
  because it has the real thing.
- **The submitted abstract promised a disclosure budget**; the work delivers a
  measurement warning about how such budgets are certified. The poster says so
  in a figure caption rather than quietly substituting one for the other.

## How this was built

Experiments designed and run with Claude (Anthropic) as the implementation
partner, with a gate after each stage: a hostile-reviewer pass, a control, and
a re-check against the wider literature before proceeding. Two findings were
reversed by those gates — the popularity headline and the context-beats-
disclosure claim — and both reversals are in this repository rather than
edited out of it. Method decisions, framing and the interpretation are the
author's.

## References

- A. J. Biega, P. Potash, H. Daumé III, F. Diaz, M. Finck. 2020.
  *Operationalizing the Legal Principle of Data Minimization for
  Personalization.* SIGIR '20, 399–408.
- H. Steck. 2019. *Embarrassingly Shallow Autoencoders for Sparse Data.*
  WWW '19.
- A. Narayanan, V. Shmatikov. 2008. *Robust De-anonymization of Large Sparse
  Datasets.* IEEE S&P '08.
- L. Baltrunas, K. Church, A. Karatzoglou, N. Oliver. 2015. *Frappe:
  Understanding the Usage and Perception of Mobile App Recommendations
  In-The-Wild.* arXiv:1505.03014.
- B. Hidasi, Á. Czapp. 2023. *The Effect of Third Party Implementations on
  Reproducibility.* RecSys '23.
- F. M. Harper, J. A. Konstan. 2015. *The MovieLens Datasets: History and
  Context.* ACM TiiS 5, 4.
- J. O. Wobbrock, S. K. Kane, K. Z. Gajos, S. Harada, J. Froehlich. 2011.
  *Ability-Based Design.* ACM TACCESS 3, 3.

## Licence

Code: MIT (see `LICENSE`). Paper, poster and figures: CC BY 4.0. Datasets are
not included and remain under their own terms.
