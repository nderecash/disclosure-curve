---
title: "Designing for Context Instead of Disclosure: What Two Datasets Say"
subtitle: "A design guide, with a correction to an earlier claim"
author: "Moses Nderemani, Pervasive Interaction Research Group, Tampere University"
date: "8 October 2026"
geometry: margin=2.3cm
fontsize: 10pt
linestretch: 1.1
colorlinks: true
---

## The correction first

The earlier run compared context against disclosure unfairly. Context conditions were restricted to obscure items, so all twenty slots went to obscure items. Disclosure conditions were not restricted, so most of their slots went to popular items. On that comparison context scored 0.0476 and eight disclosed items scored 0.0223, and the conclusion was that context beats any amount of personal disclosure.

Run fairly, with every condition restricted the same way, one disclosed item scores 0.0581 against context at 0.0476. Disclosure wins from the first item, and keeps winning all the way up.

The second dataset found this independently, which is why it was worth adding.

## What was tested

Two datasets, same protocol. People are split so that test users never appear in training. Each test user's items are split into a pool they could disclose and a hidden target set. The system is given a varying amount, and three things are measured: how well it predicts, how well it predicts obscure items specifically, and how easily whatever it holds points back to the person.

**MovieLens 1M.** 1,012 users after filtering. Context is the user's occupation, which is a property of the person rather than the situation. A weak proxy, used because it is the only grouping available that is not derived from the behaviour being predicted.

**Frappe.** Mobile app usage logs, 957 users and 4,082 apps, built for context-aware recommendation. Context here is a property of the situation: time of day, weekday, weekend, home or work, weather. 252 users and 403 apps survive filtering, giving a cohort of 87 users and 235 user-context cells. Small, and that limits the strength of any single number from it.

A third dataset, InCarMusic, was downloaded and rejected: 4,012 ratings across 139 tracks cannot support a profile-size sweep.

![Three findings. (a) With every condition scored the same way, personal disclosure beats context from the first item. (b) Identification rises steeply: two apps identify 62% of people, eight identify 94%. (c) The choice of context variable changes the result more than the presence of context.](guide.png)

## Finding 1: context beats a generic default, by a little

| Dataset | Popularity default | Context | Gain |
|---|---|---|---|
| MovieLens 1M (occupation) | 0.0408 | 0.0476 | +17% |
| Frappe (time of day) | 0.0200 | 0.0272 | +36% |

Shuffled-label controls scored below the popularity default in both cases, so the grouping carries real information rather than the gain coming from the grouping procedure itself.

Both gains are real and both are small in absolute terms.

## Finding 2: context does not substitute for disclosure

MovieLens, every condition restricted to obscure items:

| What the system holds | Long-tail Recall@20 |
|---|---|
| Nothing, popularity default | 0.0408 |
| Group context only | 0.0476 |
| 1 disclosed item | 0.0581 |
| 8 disclosed items | 0.0954 |
| 55 disclosed items | 0.1775 |
| Full history | 0.2319 |

Frappe agrees. Context scores 0.0272 and a single disclosed app scores 0.0294.

Context substitutes for the generic default, not for the person. What it replaces is the thing a system shows when it knows nothing.

## Finding 3: identification is immediate, and that is where context earns its place

| Items disclosed | MovieLens, % identified | Frappe, % identified |
|---|---|---|
| 1 | 3.2% | 17.2% |
| 2 | 23.6% | 62.1% |
| 8 | 90.3% | 94.3% |
| 13 | 98.0% | 97.7% |

Context membership costs 3% or less in both datasets.

Apps identify faster than films. Two apps identify 62% of people. This replicates the established result that sparse preference records are rarely anonymous, measured here without timestamps.

## Finding 4: which context variable matters more than whether you have context

Frappe, gain over the popularity default on obscure items:

| Context variable | Gain | Cells |
|---|---|---|
| Weather | +65% | 151 |
| Time of day | +36% | 235 |
| Weekday | +15% | 237 |
| Weekend or not | +11% | 117 |
| Home or work | -2% | 97 |

Home or work is the variable that looks most obviously relevant to an interface, and it gave nothing. It is also 79% unknown in the data, which is the likely reason and is itself the lesson: a context signal that is usually missing is worse than no context signal, because the system falls back to a default while appearing to adapt.

## What this means for building something

**Use context to replace the default, not the profile.** When a system knows nothing about someone, it shows a generic list. Context-derived content is a strictly better version of that generic list, at near-zero identification cost. That is the whole of its value, and it is worth having.

**Spend disclosure sparingly and deliberately.** The first item a person gives is worth more than all the context. It also costs little identification risk on its own. The steep part of the identification curve arrives between two and eight items. A system that asks for a handful of personal items has already identified most of its users.

**Reserve capacity for the uncommon.** The single largest effect in all of this was refusing to fill a list with popular items. A ranked list spends most of its slots on things everyone wants, which are the things the person already has access to. In an AAC board this is the core vocabulary, which is permanently available anyway, so slots spent on it are wasted twice.

**Choose the context variable empirically.** The spread from -2% to +65% is larger than the difference between having context and not having it. Pick candidate variables, measure them, discard the ones that do not pay.

**Treat a missing context value as missing, not as a category.** The home or work variable failed largely because "unknown" dominated it. A system should know when it does not know where it is, and fall back visibly rather than silently.

## Limits

The Frappe cohort is 87 users and 235 cells. Single numbers from it should not be leaned on; the value is that it agrees with MovieLens on direction.

MovieLens occupation is a personal attribute, not an environmental one. It stands in for a shared setting and does not establish anything about rooms.

Both datasets measure retrieval of items the person later used. Neither measures whether anyone was better served, which is what a user study measures and what these cannot.

Identification is measured as rank-matching within a closed set of about 1,000 people. It indicates linkage risk inside the dataset. It is not a privacy guarantee and the figure would change against a larger population.

The obscure-item threshold is the 80th percentile of training popularity in both datasets. It was not swept.

Frappe's licence permits research use and forbids redistribution of the data. The identification measure here is linkage within an already anonymised dataset, not an attempt to identify real people.

## Sources

Baltrunas, L., Church, K., Karatzoglou, A. and Oliver, N. 2015. Frappe: Understanding the Usage and Perception of Mobile App Recommendations In-The-Wild. arXiv:1505.03014.

Harper, F. M. and Konstan, J. A. 2015. The MovieLens Datasets: History and Context. *ACM TiiS* 5, 4.

Biega, A. J., Potash, P., Daumé III, H., Diaz, F. and Finck, M. 2020. Operationalizing the Legal Principle of Data Minimization for Personalization. *SIGIR '20*, 399–408.

Narayanan, A. and Shmatikov, V. 2008. Robust De-anonymization of Large Sparse Datasets. *IEEE Symposium on Security and Privacy*, 111–125.

Steck, H. 2019. Embarrassingly Shallow Autoencoders for Sparse Data. *WWW '19*.
