---
title: "Minimisation Strategies That Look Best Personalise Least: A Metric Artefact in Performance-Based Data Minimisation"
author: "Moses Nderemani, Pervasive Interaction Research Group, Tampere University"
date: "Draft, 7 October 2026 — prepared for SDLCAI 2026, Marsio, Aalto University, 13 October"
geometry: margin=2.2cm
fontsize: 10pt
linestretch: 1.08
colorlinks: true
---

**ABSTRACT**

Article 5(1)(c) of the GDPR requires that personal data be limited to what is necessary. Biega et al. operationalised this for personalisation as performance-based data minimisation and compared strategies for choosing which of a user's items a system retains, reporting that selecting the most-watched items performs best. We replicate that ranking on MovieLens 1M and then add a second axis the original study measured separately: how easily the retained data identifies the user. On standard Recall@20, retaining the most popular items dominates every other strategy at every profile size, and does so while identifying far fewer users. The apparent result is that minimisation and re-identification risk are not in tension.

The result does not survive a control. Scored only on long-tail targets, the most-popular strategy retrieves almost nothing: Recall@20 of 0.0000 at profile sizes of 8 and 13 items, against 0.0221 for a random sample of the same size. Across 45 strategy and profile-size combinations the two metrics are negatively rank-correlated, short of conventional significance (Spearman rho = -0.284, p = 0.058). The strategy that looks best under the standard metric is the one that discards the individual and reverts to a popularity ranking. On the corrected metric the trade-off returns in a harsher form: the only strategy whose long-tail performance improves with profile size is recency, which identifies 99.7% of users uniquely by 34 items.

We also test a different kind of holding. Instead of retaining item identifiers, the system retains a structured attribute description derived from the same items, with no titles. This form is the only one that reaches comparable long-tail utility at low identification risk: 0.0237 against 0.0243 for random items, while identifying 0.8% of users rather than 3.2%. We report the result as a measurement problem for data minimisation research rather than as a solution.

**CCS CONCEPTS** • Information systems → Recommender systems; • Security and privacy → Privacy protections; • Human-centered computing → Empirical studies in HCI.

**KEYWORDS** data minimisation, GDPR, recommender systems, re-identification, popularity bias, offline evaluation.

---

## 1 Introduction

Personalised systems accumulate interaction histories, most of it observed rather than volunteered. The GDPR requires that such data be adequate, relevant and limited to what is necessary for the stated purpose. Biega et al. [2] noted that this principle has no settled computational meaning for systems where data collection improves service quality but is not required to deliver it, and proposed performance-based data minimisation: retain the smallest per-user profile that still meets a target quality. They compared seven strategies for choosing what to retain and found the average quality cost modest, the per-user cost uneven, and the most-watched strategy best for neighbourhood models.

That study measured recommendation quality and profile identifiability, but reported them separately. The question this paper asks is what happens when they are treated as two axes of a single decision. A system choosing what to keep is choosing a point on a plane: how well it can still serve the user, and how easily the retained data points back to that user.

Narayanan and Shmatikov [5] established that film ratings identify people. With 8 ratings, of which two may be wrong, plus dates with a 14-day error, 99% of Netflix Prize records can be uniquely identified; 84% can be identified from 6 of 8 films outside the top 500. The qualification matters here. Obscure items identify; popular items do not. A minimisation strategy that prefers popular items should therefore sit in a favourable position on both axes at once.

It does, on the standard metric, and the position is an artefact. This paper reports that artefact, the control that exposes it, and what remains after it is removed.

Our contributions are:

1. A joint measurement of utility and re-identification across minimisation strategies and profile sizes, rather than separate measurement of each.
2. A demonstration that the strategy ranked best by standard offline evaluation retrieves essentially no long-tail items, and that the two metrics are negatively rank-correlated across conditions.
3. A first measurement of a minimisation strategy that changes the form of the retained data rather than selecting a subset of it.

## 2 Related work

**Performance-based data minimisation.** Biega et al. [2] define global minimisation (meet a target mean quality) and per-user minimisation (meet a target for every user), and compare random, most recent, most and least favourite, most watched, most characteristic and highest variance selection over n in {1, 3, 7, 15, 100} on MovieLens 20M. They find SVD more robust to minimisation than user-user kNN, most watched best for kNN, and that preserving average performance conceals substantial per-user loss. They also note, in discussing potential negative impacts, that minimisation may require more data from users who are poorly served by the majority model. Wen et al. [6] study a related setting in which users restrict a system to their most recent N days of data.

**Re-identification from preference data.** Narayanan and Shmatikov [5] show that sparse high-dimensional preference records are rarely anonymous, and that identification requires only a small number of ratings, particularly outside the popularity head. Biega et al. [2] report an identifiability statistic for minimised profiles and find it varies little across strategies, from 2.02 at n = 3 to 1.55 at n = 100.

**Offline evaluation and popularity bias.** The limitations of accuracy metrics on skewed catalogues are long established, and recent methodological work argues that widespread flaws in offline evaluation make reported comparisons unreliable [3]. Said et al. [4] argue that the field treats logged behaviour as stable ground truth and calls for evaluation that acknowledges preference volatility and modelling limits. The result we report is an instance of this problem appearing inside a privacy argument, where its consequences are not only a mis-ranked algorithm but a mistaken conclusion about what a system may safely discard.

**Positioning.** We do not claim the question is new. Biega et al. asked it and compared more strategies than we do. What has not been done is to measure both axes jointly, to subject the resulting ranking to a popularity control, or to compare a retained description against retained identifiers.

## 3 Method

**Data.** MovieLens 1M: 1,000,209 ratings from 6,040 users over 3,706 films. Ratings of 4 or above are treated as positives; lower ratings are discarded rather than treated as negatives, since a low rating indicates a watched and disliked item, which is distinct from an unseen one. Iterative filtering to a minimum of 20 positives per user and per item, five passes, leaves 553,277 interactions, 5,148 users and 2,380 films.

**Split.** Users are split, not interactions. This is necessary rather than conventional: if a test user's interactions appear in the training matrix, the model has already absorbed them, and truncating that user's profile at prediction time measures nothing. 2,000 users are held out as minimisation candidates and the model is trained on the remaining 3,148. Each candidate's positives are split into a pool (80%) and a target set (20%), with targets drawn at random rather than by recency, because MovieLens timestamps record when a user rated a film and not when they watched it [7]. Only candidates with a pool of at least 55 items are retained, so that the same users contribute at every profile size; a moving cohort produces a non-monotonic curve that is an artefact of composition. The final cohort is 1,012 users.

**Model.** EASE [1] with regularisation 250. EASE is a linear item-item model with a closed-form solution, so the user profile enters at prediction time and a profile-size sweep requires no retraining. Scoring is identical across all conditions; only the input differs. The entire pool is excluded from the candidate set at every profile size, so the ranking task does not change as the profile is truncated.

**Conditions.** Profile size k in {1, 2, 3, 5, 8, 13, 21, 34, 55}, plus full history and a popularity baseline that retains nothing. Selection strategies: random, most recent, most popular. Two further conditions retain a structured attribute description built from the same k items: a 29-dimensional vector of genre weights, release-era bands and popularity tier, with no item identifiers. To predict, the description is expanded into its 20 best-matching catalogue items, which are scored by the same model. A shuffled control assigns each user another user's description.

**Metrics.** Recall@20 and NDCG@20. Long-tail Recall@20 restricts targets to items below the 80th percentile of training popularity (1,904 of 2,380 films). Re-identification is the rank of the true user when an adversary matches the retained data against all full profiles under cosine similarity, with each adversary operating in the representation the system actually holds. We report the proportion of users identified at rank 1.

**Reproducibility.** Three seeds (42, 7, 2024); confidence intervals are 2,000-sample bootstraps over users. Code and results accompany this submission.

## 4 Results

### 4.1 Selection strategies on the standard metric

Table 1 reports the standard metric. The popularity baseline reaches Recall@20 of 0.2008 and full history 0.3552.

**Table 1. Standard Recall@20 [95% CI] and proportion of users identified at rank 1.**

| k | Random | Most recent | Most popular |
|---|---|---|---|
| 1 | 0.1015 [0.0985, 0.1045] / 3.2% | 0.0756 [0.0729, 0.0780] / 4.5% | 0.1599 [0.1558, 0.1639] / 0.7% |
| 5 | 0.1498 [0.1462, 0.1534] / 72.9% | 0.1066 [0.1037, 0.1095] / 75.2% | 0.2035 [0.1990, 0.2081] / 6.2% |
| 8 | 0.1672 [0.1637, 0.1708] / 90.3% | 0.1217 [0.1188, 0.1247] / 90.3% | 0.2133 [0.2087, 0.2181] / 19.9% |
| 13 | 0.1957 [0.1921, 0.1993] / 98.0% | 0.1404 [0.1370, 0.1437] / 96.3% | 0.2294 [0.2248, 0.2342] / 37.1% |
| 55 | 0.2877 [0.2834, 0.2921] / 100.0% | 0.2423 [0.2383, 0.2462] / 99.9% | 0.3056 [0.3008, 0.3104] / 88.1% |

Three observations. First, re-identification is immediate: 8 random items identify 90.3% of users at rank 1, consistent with Narayanan and Shmatikov's finding for 8 Netflix ratings with dates [5], obtained here without dates.

Second, recency is worse than random at every size, reproducing Biega et al.'s observation for kNN [2]. Their explanation applies to our protocol as well: the targets are sampled at random, so a recency-selected profile is mismatched to them. This result is therefore protocol-dependent and should not be read as evidence that production systems truncate profiles wrongly.

Third, most popular dominates random at every profile size on both axes simultaneously: higher recall and fewer users identified, with the gap in identification reaching 70.3 percentage points at k = 8. The whole Pareto frontier consists of most-popular points. Read at this stage, the finding is that minimisation and re-identification risk are not in tension, and that the existing best-performing strategy is also the safest.

### 4.2 The control

Figure 1 shows what happens when the same conditions are scored only on long-tail targets.

![The same conditions under two metrics. (a) Standard Recall@20: retaining the most popular items dominates. (b) Recall@20 restricted to long-tail targets: the same strategy collapses to near zero. Labels mark profile sizes 1, 13 and 55.](figures/fig1_inversion.png)

Most popular retrieves a long-tail Recall@20 of 0.0004 at k = 1, 0.0000 at k = 8 and k = 13, and 0.0066 at k = 55. Random holds steady at approximately 0.022 and matches full history (0.0212). Recency is the strongest condition on this metric and the only one that improves with profile size, from 0.0216 at k = 1 to 0.0393 at k = 34.

The direct comparison is unambiguous: at k = 13, most popular retrieves 0.0000 and random retrieves 0.0221. Across all 45 strategy and profile-size combinations the rank correlation between the two metrics is negative, though it falls short of conventional significance (Spearman rho = -0.284, p = 0.058, Figure 2). We therefore make the weaker claim the evidence supports: standard Recall@20 provides no positive evidence about long-tail performance, and the point estimate of the association runs the wrong way.

![Standard Recall@20 against long-tail Recall@20 for all 45 strategy and profile-size combinations.](figures/fig2_metric_disagreement.png)

The mechanism is not subtle. Retaining a user's most-watched items leaves the model with a profile that is close to the population average, so its output approximates a popularity ranking. Against targets drawn from the user's own history, which also skew popular, that scores well. The strategy achieves its apparent minimisation by discarding the individual.

On the corrected metric the trade-off returns, and in a harsher form than before. The only condition whose long-tail performance improves with profile size, recency, identifies 75.2% of users at k = 5 and 99.7% at k = 34. What makes an item useful for distinguishing one person from another is the same property that makes it identify them, which is what Narayanan and Shmatikov's "outside the top 500" qualification already implied.

### 4.3 Retaining a description instead of identifiers

The attribute conditions never reach the popularity baseline on the standard metric: the best is 0.1623 at k = 55 against a floor of 0.2008. They do carry individual signal, exceeding the shuffled control by 0.0679 at k = 13 (0.1514 against 0.0835), so the deficit is not an absence of personalisation but a weak representation of it.

On long-tail targets the comparison changes. At k = 1 the attribute description reaches 0.0237 against 0.0243 for random items, which is 97.5% of the utility, while identifying 0.8% of users rather than 3.2%. At k = 13 it reaches 0.0171 at 20.4% identification, against 0.0221 at 98.0% for random. Expressed as long-tail recall per unit of identification risk, the attribute description at k = 1 is four times more efficient than random item retention (3.06 against 0.77).

The attribute conditions occupy the low-identification end of the long-tail Pareto frontier together with random selection at k = 1; the remainder of the frontier is recency. We report this as a direction rather than a result: the attribute space is hand-constructed, 29 dimensions of genre, era and popularity tier, and a richer description would plausibly behave differently.

## 5 Discussion

The practical finding for data minimisation research is a measurement warning. A minimisation strategy is evaluated by how little quality it costs, and the standard measure of quality rewards strategies that abandon personalisation. Any study that selects a minimisation strategy on accuracy alone risks recommending the strategy that keeps the least informative data, and then reporting its low identifiability as a privacy benefit. Both halves of that conclusion would be artefacts of the same bias.

The finding also narrows a hope. If the most useful items were the least identifying, minimisation and privacy would align and systems could keep more while exposing less. Our corrected results indicate the opposite: within this evaluation the informative signal and the identifying signal are the same signal. The route that remains open is not better selection of what to keep but a change in what kind of thing is kept, which is what section 4.3 begins to test.

For agent memory systems the relevance is direct. Compressing an interaction history into a short natural-language profile is now routine practice, motivated by context budgets. Whether that compression also permits collecting less, rather than merely carrying less, is an open question of the same shape as the one measured here, and the metric warning transfers with it.

## 6 Limitations

The cohort requires a pool of at least 55 items and therefore over-represents heavy users, who are more identifiable than average; the re-identification figures should be read as an upper bound. MovieLens timestamps record rating time rather than viewing time [7], so no temporal claim is made and the recency condition should be understood as simulating a truncated profile rather than a viewing history. Re-identification by rank matching against a 1,012-user database is a proxy for linkage risk and is not a formal privacy guarantee; it is not k-anonymity and should not be described as anonymity. The 80th-percentile tail threshold is a choice, and we have not swept it. The attribute representation is hand-built; a negative result for this representation is not a negative result for retained descriptions in general. One dataset, one model family, three seeds.

## 7 Conclusion

Retaining a user's most popular items appears, under standard offline evaluation, to deliver more utility and less re-identification risk than any alternative at every profile size. Restricted to long-tail targets, the same strategy retrieves almost nothing, and the two metrics are negatively rank-correlated across conditions. The condition that best retrieves non-obvious items, recency, identifies nearly every user uniquely. Retaining an attribute description rather than item identifiers is the only form tested that reaches comparable long-tail utility at low identification risk.

## References

[1] Steck, H. 2019. Embarrassingly Shallow Autoencoders for Sparse Data. In *The World Wide Web Conference (WWW '19)*.

[2] Biega, A. J., Potash, P., Daumé III, H., Diaz, F., and Finck, M. 2020. Operationalizing the Legal Principle of Data Minimization for Personalization. In *Proceedings of the 43rd International ACM SIGIR Conference on Research and Development in Information Retrieval (SIGIR '20)*, 399–408.

[3] Hidasi, B. and Czapp, Á. T. 2023. Widespread Flaws in Offline Evaluation of Recommender Systems. In *Proceedings of the 17th ACM Conference on Recommender Systems (RecSys '23)*.

[4] Said, A., Pera, M. S., and Ekstrand, M. D. 2025. We're Still Doing It (All) Wrong: Recommender Systems, Fifteen Years Later. *BEYOND Workshop, RecSys 2025*. arXiv:2509.09414.

[5] Narayanan, A. and Shmatikov, V. 2008. Robust De-anonymization of Large Sparse Datasets. In *2008 IEEE Symposium on Security and Privacy*, 111–125.

[6] Wen, H., Yang, L., Sobolev, M., and Estrin, D. 2018. Exploring Recommendations Under User-Controlled Data Filtering. In *Proceedings of the 12th ACM Conference on Recommender Systems (RecSys '18)*, 72–76.

[7] Fan, Y.-c., Ji, Y., Zhang, J., and Sun, A. 2024. Our Model Achieves Excellent Performance on MovieLens: What Does it Mean? *ACM Transactions on Information Systems*. arXiv:2307.09985.
