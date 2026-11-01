# PROJECT_STATUS (updated 2026-11-01)

Competition: Kaggle NFL Big Data Bowl 2027, Open track. Deadline 2027-01-06 23:59 UTC. Judging 2027-01-07 to 01-25. Prizes: 3 finalists ($10k) + 3 runners-up ($5k).
Scoring: Football 30 / Data Science 30 / Writeup 20 / DataViz 20. PASS/FAIL gates: explicit Combine-to-NFL linkage; readable markdown + embedded visuals + attached public notebook. Limits: <= 2,000 words, < 10 figures/tables (host: captions, figure labels and in-writeup appendix do not count).

## Current state (VERIFIED FACT unless noted)
- Writeup "Speed Travels: NFL Pass Rush" is submitted (status "Submitted!") with body v16: 7 figures embedded inline (GitHub raw URLs, rendered by Kaggle's image proxy at 3200 px) + 7 gallery images (v16) + 2 tables = 9 visuals. Body ~1,999 words by a strict count that includes headings and table cells.
- Notebook doukanturan/nfl-bdb27-speed-travels version 16 ran to completion (CPU, ~19 min, no errors in results.json["_errors"]). Outputs: results.json, table1.csv, 7 figures. No per-play competition data in outputs (caches moved to /kaggle/temp).
- GitHub mirror: github.com/tdogukan470-jpg/nfl-bdb-2027 (public), commit "v16".
- Every number in the writeup is filled from results.json by writeup/fill_writeup.py; the template is writeup/writeup_template.md.

## Best verified result (MEASURED, notebook v16, regular-season dropbacks, class fixed effects)
- Interior DL: OR 1.22 [1.12, 1.34] per +0.5 yd/s Combine top speed (75 players, 9,378 rushes). p10->p90 pressure rate 6.3% -> 11.4% (ratio 1.8, CI 1.1 to 2.8).
- Edge OR 1.07 [0.96, 1.19]; OL 1.02 [0.92, 1.14]; WR/TE separation null.
- POE offset OR 1.22 [1.12, 1.33]; Beta-Binomial OR 1.20 (bootstrap CI 0.93-1.34, LR p 0.003).
- Mediation: 20% [9%, 43%] of the interior effect through get-off. Edge: path-efficiency suppression (ACME -0.41 [-0.86, -0.13]).
- FDR: 113 tests, 61 with q < 0.05.
- Weak rows (CI touches 1.0): team fixed effects 1.16 [0.96, 1.40], 2024 season alone 1.16 [0.99, 1.36], sacks 1.27 [0.95, 1.70].

## Known risks
- 75 interior players; decision-matrix cells are small (HYPOTHESIS-level guidance, labelled as such in the writeup).
- Competition rules forbid redistributing data; outputs now hold aggregates only. GitHub repo holds no competition data.
- Inline figures depend on raw.githubusercontent.com availability (ESTIMATE: low risk; gallery copies are hosted on Kaggle as a fallback).
