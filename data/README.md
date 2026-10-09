# Datasets

**No dataset files are committed to this repository.**

Frappe's licence states: *"The user may not redistribute the data without
separate permission"* and *"The user may not try to deanonymise the data."*
MovieLens likewise asks that redistribution be by link rather than by copy.
So this directory ships empty and `download_data.sh` fetches both.

After running `bash download_data.sh` from the repository root, this directory
should contain:

```
data/
  ml-1m/
    ratings.dat        1,000,209 ratings, 6,040 users, 3,706 films
    users.dat          age / gender / occupation / zip
    movies.dat         title + genre string
  frappe/
    Mobile_Frappe/frappe/
      frappe.csv       96,203 app-usage events with situational context
      meta.csv         app metadata
```

## MovieLens 1M

F. Maxwell Harper and Joseph A. Konstan. 2015. The MovieLens Datasets:
History and Context. *ACM TiiS* 5, 4, Article 19.
<https://grouplens.org/datasets/movielens/1m/>

Used in `experiment.py`, `robust.py`, `gate_tail.py`, `pareto*.py`,
`context_test.py`, `context_control.py`, `fair_ml1m.py`.

## Frappe

Linas Baltrunas, Karen Church, Alexandros Karatzoglou, Nuria Oliver. 2015.
Frappe: Understanding the Usage and Perception of Mobile App Recommendations
In-The-Wild. arXiv:1505.03014.
<https://www.baltrunas.info/context-aware>

Used in `frappe_exp.py`. Frappe carries real situational context recorded at
use time — daytime, weekday, is-weekend, weather, country, city, cost — which
is why it is the second dataset: ML-1M has no context, only demographics
standing in for it.

## Re-identification experiments and this data

The identification numbers reported here are **linkage within a closed set**:
given a holding of k items, rank all cohort profiles by cosine and ask whether
the true one comes first. That is not an attack on a real person and not a
privacy guarantee. It is an upper bound on how distinctive a short disclosure
is inside a known population, and it is reported only to put a cost on the
x-axis of the disclosure curve. Nothing here attempts to deanonymise any
Frappe or MovieLens user, and the scripts do not join either dataset to any
external source.
