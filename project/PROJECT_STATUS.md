# PROJECT_STATUS (updated 2026-11-03)

Competition: Kaggle NFL Big Data Bowl 2027, Open track. Deadline 2027-01-06 23:59 UTC. Judging 2027-01-07 to 01-25. Prizes: 3 finalists ($10k) + 3 runners-up ($5k).
Scoring: Football 30 / Data Science 30 / Writeup 20 / DataViz 20. PASS/FAIL gates: explicit Combine-to-NFL linkage; readable markdown + embedded visuals + attached public notebook. Limits: <= 2,000 words, < 10 figures/tables (host: captions, figure labels and in-writeup appendix do not count).

## Current state (VERIFIED FACT unless noted)
- Writeup "Speed Travels: NFL Pass Rush" is submitted, body from repo commit 040e105 (v17 numbers; 1,951 words by our count). Live page checked 2026-11-03 20:10 TR: "Submitted", new subtitle, "The stricter test fails" paragraph present, 7 inline figures load, gallery holds the 7 v17 figures with titles.
- Notebook version 17 ran to completion; version 18 (adds within-class ORs + class x speed Wald test) pushed 2026-11-03 ~20:08 TR, result pending.
- GitHub mirror: github.com/tdogukan470-jpg/nfl-bdb-2027 (public), commit 040e105.
- Every result number in the writeup is filled from results.json by writeup/fill_writeup.py.
- Kaggle bridge on the PC: two instances running (pids seen alternately in heartbeat), so jobs can run twice. Patched claim logic loads only after restart.

## Best verified result (MEASURED, notebook v16 = v17, regular-season dropbacks, class fixed effects)
- Interior DL: OR 1.22 [1.12, 1.34] per +0.5 yd/s Combine top speed (75 players, 9,378 rushes). p10->p90 pressure rate 6.3% -> 11.4% (ratio 1.8, CI 1.1 to 2.8).
- Edge OR 1.07 [0.96, 1.19]; OL 1.02 [0.92, 1.14]; WR/TE separation null.
- POE offset OR 1.22 [1.12, 1.33]; Beta-Binomial OR 1.20 (bootstrap CI 0.93-1.34, LR p 0.003).
- Mediation: 20% [9%, 43%] of the interior effect through get-off. Edge: path-efficiency suppression (ACME -0.41 [-0.86, -0.13]).
- FDR: 113 tests, 61 with q < 0.05.
- Weak rows (CI touches 1.0): team fixed effects 1.16 [0.96, 1.40], 2024 season alone 1.16 [0.99, 1.36], sacks 1.27 [0.95, 1.70].

- v17 leave-one-class-out: adding speed does NOT improve held-out-class prediction (log-loss gain -0.48e-3 [-1.26e-3, +0.40e-3]); fit on 2024+2025 classes only, interior OR 1.00 [0.72, 1.39]. The pooled effect leans on the 2023 class. Stated in the writeup.

## Known risks
- Central finding depends on one draft class (MEASURED, see above); E18 quantifies how much.
- 75 interior players; decision-matrix cells are small (HYPOTHESIS-level guidance, labelled as such in the writeup).
- Competition rules forbid redistributing data; outputs now hold aggregates only. GitHub repo holds no competition data.
- Inline figures depend on raw.githubusercontent.com availability (ESTIMATE: low risk; gallery copies are hosted on Kaggle as a fallback).
