# Speed Travels: What 10 Hz Combine Tracking Tells Us About the NFL Pass Rush

Entry for the Kaggle **NFL Big Data Bowl 2027** (Open track) by Doğukan Turan.

- Kaggle writeup: https://www.kaggle.com/competitions/nfl-big-data-bowl-2027/writeups/speed-travels-nfl-pass-rush
- Kaggle notebook (rebuilds every number and figure from the competition files): https://www.kaggle.com/code/doukanturan/nfl-bdb27-speed-travels

## Summary

At 10 Hz the 40-yard dash is a top-speed test (tracking peak speed vs stopwatch time: r = -0.98). For **interior defensive linemen** (75 players, 9,378 regular-season dropback rushes) each +0.5 yd/s of Combine top speed raises the odds of generating pressure by 22% (OR 1.22, 95% CI 1.12 to 1.34), with weight, arm length, draft slot, draft class, down and distance held fixed. From the 10th to the 90th percentile of speed the adjusted pressure rate moves from 6.3% to 11.4%. The effect survives sensor cleaning (Savitzky-Golay and a 2.5 g limiter), inverse-probability weighting and a Heckman-type control function for selection into the NFL, and a cross-validated expected-pressure context model (POE OR 1.22); a Beta-Binomial shrinkage check is supportive (likelihood-ratio p = 0.003) but its player bootstrap interval (0.93 to 1.34) includes 1. Of 21 robustness checks, only team fixed effects, sacks and the 2024 season alone have intervals touching 1.0. **Out of class, the effect does not hold:** The stricter test fails. Holding out each draft class, adding speed does not improve held-out prediction (log-loss gain -0.48 x 10^-3, 95% CI -1.26 to +0.40; player Spearman 0.32 without speed, 0.25 with). Per class the estimate exceeds 1 (2023 1.27, 2024 1.11, 2025 1.24; interaction p = 0.38), but only 2023 is precise; without 2023, OR 1.09 [0.75, 1.57]. The data cannot separate a common effect from a 2023-only one. Imai-Keele-Tingley mediation puts 20% (9% to 43%) of the effect through a faster get-off. **Edge rushers, offensive linemen and WR/TE show no detectable speed effect**; on the edge, speed reaches the field but is spent on less direct paths. Drill "first-step" numbers have test-retest reliability of 0.36 to 0.54 and do not travel to games.

## Headline table

| Group | Outcome | Players / snaps | Effect of +0.5 yd/s top speed (95% CI) | p |
|---|---|---|---|---|
| Interior DL | Pressure per rush | 75 / 9,378 | OR 1.22 [1.12, 1.34] | <0.001 |
| Edge | Pressure per rush | 95 / 10,448 | OR 1.07 [0.96, 1.19] | 0.20 |
| OL (T, G, C) | Pressure allowed per block | 72 / 38,854 | OR 1.02 [0.92, 1.14] | 0.67 |
| WR / TE | Separation at pass forward (yd) | 102 / 29,670 | -0.011 [-0.071, +0.049] | 0.72 |
| WR / TE, deep | Separation at pass forward (yd) | 100 / 10,978 | -0.008 [-0.089, +0.073] | 0.85 |

113 tests in total (15 headline, 76 mechanism, 22 robustness); 61 have Benjamini-Hochberg q < 0.05.

## Data hygiene

- Regular-season games only (`games.season_type == "REG"`); the files also hold preseason and playoff games (21% of player-play rows).
- Dropbacks only: rushes are kept when the play has a recorded `pass_result` (the host's definition of a dropback). `player_get_off` is also populated on run plays, where pressure cannot occur.
- Ball frames (`entity_type == "BALL"`) removed from the Combine file; the Combine `dis` column is not used.
- Draft-class fixed effects in every model: public notebooks report that the 2025 Combine export is stored at full precision while 2023-24 positions sit on a 1/60-yd grid (not verified by us).
- Per-play intermediate tables are cached outside the published notebook output; only aggregates, figures and `results.json` are saved.

## Figures

| | |
|---|---|
| ![Fig 1](figures/fig1_forty.png) Fig. 1: Rebuilt 40-yard dash from 10 Hz tracking | ![Fig 2](figures/fig2_reliability.png) Fig. 2: Reliability of Combine metrics (40 vs drill) |
| ![Fig 3](figures/fig3_translation.png) Fig. 3: Does Combine speed translate to in-game speed? | ![Fig 4](figures/fig4_dose.png) Fig. 4: Pressure rate vs Combine top speed (interior DL vs edge) |
| ![Fig 5](figures/fig5_robust.png) Fig. 5: Robustness checks (sensor, selection, xP, seasons) | ![Fig 6](figures/fig6_scouting.png) Fig. 6: Scouting view, interior DL vs expectation |
| ![Fig 7](figures/fig7_forward.png) Fig. 7: Out-of-time check (fit through 2024, test 2025) | |

## Methods in the notebook

1. **Combine features from raw 10 Hz traces**: start of motion, peak speed over 30 yd, speed at 10 yd, 10 to 30 yd split, acceleration time constant; test-retest reliability from repeat attempts.
2. **Sensor audit**: all 793 forty-yard attempts (2023 to 2025) scanned for frames above 3.5 g; none found in the 40-yard window. Features rebuilt with a Savitzky-Golay derivative filter and a 2.5 g slew limiter as a check.
3. **Outcomes from game tracking**: pressure per pass rush (interior DL, edge), pressure allowed per block (OL), route- and coverage-adjusted separation at pass-forward (WR/TE).
4. **Main model**: logistic GEE on snaps with standard errors clustered by player; controls for weight, arm length, log draft slot, draft class, down and distance. Cluster bootstrap, permutation test, leave-one-player-out, team and opponent fixed effects, alternative outcome definitions, per-season fits, all-games-included fit.
5. **Selection**: cross-fitted logistic selection model over all 510 prospects, inverse-probability-weighted GEE, Heckman-type control function with draft class as the excluded variable.
6. **Context model**: expected pressure (xP) chosen out of fold (GroupKFold by rusher) between a regularized LightGBM and a ridge logistic regression; Pressure Over Expected; GEE with logit(xP) offset; Beta-Binomial empirical-Bayes shrinkage of player POE.
7. **Mediation**: Imai-Keele-Tingley quasi-Bayesian mediation (1,000 draws, cluster-robust covariances) on the risk-difference scale; mediators are get-off, speed at 1 s, path efficiency, depth and width over the first 2 s.
8. **Multiple testing**: Benjamini-Hochberg FDR over all tests, by family.
9. **Out-of-time check**: fit through 2024, test on 2025.
10. **Decision matrix**: 10 to 30 yd split cuts, weight bands, and edge path-efficiency cells with POE and bootstrap intervals.

## Repository layout

```
notebook/   speed-travels.ipynb (the Kaggle notebook), speed_travels.py (same code as a script), kernel-metadata.json
writeup/    writeup.md (the submitted text), writeup_template.md and fill_writeup.py (every result number is filled from results.json; method constants such as the 3.5 g threshold are written in the template)
figures/    fig1 to fig7, 16:9 at 3200x1800
results/    results.json (every result number quoted in the writeup), table1.csv
```

## Reproducing

The competition data is only available inside Kaggle. Attach the `nfl-big-data-bowl-2027` competition dataset and run `notebook/speed-travels.ipynb` on a CPU kernel (no internet needed, about 20 minutes); it writes `results.json`, `table1.csv` and the seven figures. Or push it with the Kaggle CLI:

```
kaggle kernels push -p notebook
python3 writeup/fill_writeup.py results/results.json writeup/writeup_template.md writeup/writeup.md
```

Python packages used: pandas, numpy, pyarrow, scipy, statsmodels, scikit-learn, lightgbm, matplotlib.

## License

Code: MIT. Competition data belongs to the NFL and Kaggle and is not included here.
