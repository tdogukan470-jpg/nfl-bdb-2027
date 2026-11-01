# Speed Travels: What 10 Hz Combine Tracking Tells Us About the NFL Pass Rush

**Track:** Open. The attached public notebook rebuilds every number and figure from the raw competition files; code, figures and results are mirrored at github.com/tdogukan470-jpg/nfl-bdb-2027.

## 1. The question

Teams read Combine tracking as a proxy for how a player will move on Sundays. We ask which movement traits carry over to regular-season performance, and where they do not; a scouting number that is wrong for half the positions is dangerous, so the boundaries matter as much as the finding.

Two decades of Combine studies found little: the tests explain a few percent of season-level production, with sprint speed for running backs the usual exception [1-4]. That null is partly measurement: season totals mix talent with opportunity, a stopwatch gives one number per drill, and most studies pool positions. We use per-snap outcomes from game tracking, movement rebuilt from the 10 Hz trace, one position group at a time, with size and draft slot held fixed.

## 2. What the Combine data measures, and whether we can trust it

From each 10 Hz 40-yard trace we rebuilt start of motion, peak speed over 30 yd, speed at 10 yd, the 10 to 30 yd split and an acceleration time constant (Fig. 1). The stopwatch 40 is almost entirely top-end speed: across 418 prospects, tracking peak speed and stopwatch time correlate at r = -0.98.

![Fig. 1: Rebuilt 40-yard dash from 10 Hz tracking](https://raw.githubusercontent.com/tdogukan470-jpg/nfl-bdb-2027/main/figures/fig1_forty.png)
*Figure 1. The 40-yard dash rebuilt from 10 Hz tracking: speed-time curves by position group, with the start of motion, speed at 10 yd and the plateau that the stopwatch time measures.*

**Reliability (Fig. 2).** Across repeat attempts, peak speed (0.99) and the 10 to 30 yd split (0.99) are nearly perfectly repeatable; the acceleration constant is 0.36. In the pass-rush drill, speed at 1.0 s is 0.54, at 0.5 s 0.40, first-step acceleration 0.36. A trait that is mostly noise cannot predict anything.

![Fig. 2: Reliability of Combine metrics (40 vs drill)](https://raw.githubusercontent.com/tdogukan470-jpg/nfl-bdb-2027/main/figures/fig2_reliability.png)
*Figure 2. Test-retest reliability from repeat attempts (375 players with two 40s, 106 with two drill reps). Top speed repeats; first-step metrics do not.*

**Sensor audit.** Quantization artifacts would appear as accelerations above 3.5 g, which no lineman produces. Across all 793 forty-yard attempts (2023 to 2025) no frame in the 40-yard window exceeds 3.5 g (median peak about 0.5 g). Rebuilding top speed with a Savitzky-Golay derivative filter [9] or a 2.5 g limiter leaves the feature (r = 0.999) and the interior result (OR 1.23 and 1.22) unchanged. A public audit of the files found the 2025 export stored at full precision while 2023-24 sit on a 1/60-yd grid [11], so every model carries draft-class fixed effects; dropping the 2024 class gives OR 1.27.

**Data hygiene.** The game files also hold preseason and playoff games (21% of player-play rows); every number below uses regular-season dropbacks only. Including every game gives OR 1.23.

## 3. Method

From 2023 to 2025 regular-season tracking we computed pressure per pass rush (interior DL, edge), pressure allowed per block (OL) and separation at pass-forward for WR/TE adjusted for route and coverage. The Combine feature is mean top speed across a player's 40 attempts, in units of +0.5 yd/s, about 0.2 s on the stopwatch at a lineman's speed. Models are logistic GEE with standard errors clustered by player [8], controlling for weight, arm length, log draft slot, draft class, down and distance. Speed and weight correlate at -0.83 among interior linemen, so size is always in the model.

## 4. Result: interior defensive linemen

For 75 interior DL and 9,378 rushes, each +0.5 yd/s raises the odds of pressure by 22% (OR 1.22, 95% CI 1.12 to 1.34). From the 10th to the 90th percentile of speed (9.1 to 10.7 yd/s) the adjusted pressure rate moves from 6.3% to 11.4%, a ratio of 1.8 (CI 1.1 to 2.8; Fig. 4). In scouting terms: between two interior prospects of the same weight, arm length and draft range, 0.2 s on the 40 is worth about 1.4 pressures per 100 rushes, roughly 7 over a 500-rush season.

**Table 1. Effect of +0.5 yd/s Combine top speed**

| Group | Outcome | Players / snaps | Effect (95% CI) | p |
|---|---|---|---|---|
| Interior DL | Pressure per rush | 75 / 9,378 | OR 1.22 [1.12, 1.34] | <0.001 |
| Edge | Pressure per rush | 95 / 10,448 | OR 1.07 [0.96, 1.19] | 0.20 |
| OL | Pressure allowed | 72 / 38,854 | OR 1.02 [0.92, 1.14] | 0.67 |
| WR / TE | Separation (yd) | 102 / 29,670 | -0.011 [-0.071, +0.049] | 0.72 |
| WR / TE, deep | Separation (yd) | 100 / 10,978 | -0.008 [-0.089, +0.073] | 0.85 |

![Fig. 4: Pressure rate vs Combine top speed (interior DL vs edge)](https://raw.githubusercontent.com/tdogukan470-jpg/nfl-bdb-2027/main/figures/fig4_dose.png)
*Figure 4. Adjusted pressure rate against Combine top speed with cluster-bootstrap bands. Interior linemen rise across the speed range; edge rushers are flat.*

**Stress tests (Fig. 5).** Team fixed effects give OR 1.16, opposing-offense effects 1.26, formation and alignment 1.22, without class effects 1.20. Outcome variants: quick pressure 1.30, late 1.18, hurry 1.23, sack 1.27. Each season alone: 1.23, 1.16, 1.28. Dropping any single player: 1.19 to 1.25. A permutation test gives p < 0.001. Point estimates stay above 1.15; only team fixed effects, sacks and the 2024 season alone, the thinnest checks, have intervals touching 1.0.

![Fig. 5: Robustness checks (sensor, selection, xP, seasons)](https://raw.githubusercontent.com/tdogukan470-jpg/nfl-bdb-2027/main/figures/fig5_robust.png)
*Figure 5. The interior effect under every specification we tried: fixed effects, outcome definitions, seasons, sensor cleaning, selection correction and the context model. 1.0 is no effect.*

**Top speed, not burst.** Splitting the signal, top speed carries the effect (OR 1.21) and burst carries none (OR 1.03, p = 0.54); the stopwatch 10-yard split adds nothing once the 40 is in (p = 0.35). Interior rushers who reach and hold high speed win more often than those who merely start quickly, against the usual emphasis on the first 10 yards.

## 5. Selection bias: we only see players who reached the field

Of 510 prospects, 79% appear in game tracking but only 105 (21%) rush the passer and 48 (9%) rush 100+ times. We modeled each prospect's probability of being observed from measurables, draft slot, position and class (cross-fitted, AUC 0.96 and 0.97) and weighted by its inverse; a Heckman-type control function [7] adds the probit inverse Mills ratio, with draft class (the observation window) as the excluded variable. IPW OR 1.17 (CI 1.04 to 1.33) and 1.17 (1.04 to 1.33); control function OR 1.22 and 1.19, with Mills ratio coefficients far from significant (p = 0.16 and 0.63). Selection is mostly position and draft slot; correcting for it moves the estimate little.

## 6. Context model: Pressure Over Expected

We built an expected-pressure (xP) model on 19,826 dropback rushes from down, distance, quarter, clock, score, win probability, expected points, formation, alignment and the distance to the nearest tracked opposing lineman (a double-team proxy, known on 69% of snaps). Two candidates, a regularized LightGBM [10] and a ridge logistic regression, are scored out of fold with folds grouped by rusher, so no player trains the model that scores him. The logistic regression wins and is kept. Out of fold, AUC is 0.58 (grouped by game, 0.58), log loss improves 1.1% over the league rate and the worst decile miscalibration is 0.9 points: on true dropbacks, pre-snap context predicts which rusher gets home only weakly, so POE stays close to the raw rate.

Pressure Over Expected (POE) is pressure minus xP. With xP as an offset, interior speed gives OR 1.22 (1.12 to 1.33): +0.5 yd/s adds 1.4 points of POE per 100 rushes (0.8 to 2.0). Edge: OR 1.05 (0.94 to 1.18).

**Hierarchical shrinkage.** Raw player POE is noisy; its SD across interior players is 13.2 points. We fit a Beta-Binomial model in which each player's latent pressure probability has a prior mean equal to his context-expected rate, shifted by speed and size. Shrinking cuts the SD of player POE to 1.6 points, and Combine speed in the prior mean carries OR 1.20 (bootstrap CI 0.93 to 1.34, likelihood-ratio p = 0.003); speed explains 8% of the variance in raw interior POE beyond weight, draft slot and arm length. Edge: OR 1.04 (0.86 to 1.24). Shrunk leaders: Braden Fiske (+3.2), Byron Murphy (+2.3), Gervon Dexter (+1.9), Adetomiwa Adebawore (+1.7) and C.J. West (+1.2) points.

![Fig. 6: Scouting view, interior DL vs expectation](https://raw.githubusercontent.com/tdogukan470-jpg/nfl-bdb-2027/main/figures/fig6_scouting.png)
*Figure 6. Scouting view: every interior lineman with 100+ rushes, pressure rate against the rate that draft slot and size predict, colored by Combine top speed. Fast-for-weight players sit above the line. An illustration of the method, not a recommendation list: single player-seasons are noisy.*

## 7. How speed becomes pressure: formal mediation

Imai-Keele-Tingley causal mediation [5], 1,000 quasi-Bayesian draws with cluster-robust covariances, on the risk-difference scale per +0.5 yd/s.

**Interior.** Speed shortens get-off time, and get-off drives pressure: the average causal mediation effect (ACME) is +0.29 [0.15, 0.45] points per 100 rushes (p = 0.001) against a total effect of +1.46 [0.81, 2.13], so **20% (9% to 43%) runs through get-off**. Speed at 1 s, path directness, depth and width show no indirect effect.

**Edge: suppression.** Faster edge rushers do run faster in-game (ACME through speed at 1 s +0.69 [0.32, 1.08]), but they take less direct paths: path efficiency carries an ACME of -0.41 [-0.86, -0.13] against a direct effect of +1.22 [0.14, 2.40], total +0.79 [-0.40, 1.98]. Speed helps, the route spends it, and the edge total looks null. Mediator and outcome come from the same snap, so these hold only if no unmeasured factor drives both.

## 8. Drill numbers do not travel (Fig. 3)

For 59 linemen with both drill traces and game tracking, the 40's top speed correlates r = 0.77 with game speed one second after the snap, but within interior linemen only r = 0.39 and within edge r = 0.37. The drill's first-step speed correlates r = 0.13 (CI -0.22 to 0.52). Trust the 40's speed trace; single-attempt drill first-step numbers are too noisy to use alone.

![Fig. 3: Does Combine speed translate to in-game speed?](https://raw.githubusercontent.com/tdogukan470-jpg/nfl-bdb-2027/main/figures/fig3_translation.png)
*Figure 3. Combine measures against in-game speed one second after the snap: the 40's top speed (left) carries over, the pass-rush drill's first step (right) does not.*

## 9. Out-of-time check and multiple testing

We fit through 2024 and test 2025 (Fig. 7). For 22 interior linemen with 75+ snaps, adding speed lifts the player-level Spearman correlation from 0.67 to 0.72; the log-loss gain is positive in 92% of bootstrap resamples but its interval includes zero, so forward evidence is directional, not conclusive.

![Fig. 7: Out-of-time check (fit through 2024, test 2025)](https://raw.githubusercontent.com/tdogukan470-jpg/nfl-bdb-2027/main/figures/fig7_forward.png)
*Figure 7. Models fit on 2023 and 2024 predict 2025 interior pressure rates. Adding Combine speed to draft slot and size moves the ranking in the right direction.*

We ran 113 tests: 15 group-level hypotheses, 76 mechanism paths and 22 robustness re-tests. With Benjamini-Hochberg correction [6], 61 have q < 0.05. Every interior headline test (Table 1, top speed, stopwatch 40, POE) has q at or below 0.002 except the Beta-Binomial test (q = 0.007); no edge, OL or WR headline test has q below 0.2. The robustness rows named above are the ones with q above 0.05.

## 10. How a team uses this

**Table 2. Draft-cycle and deployment decision matrix. POE is percentage points of pressure per 100 rushes above context expectation.**

| Prospect profile | Evidence | Action |
|---|---|---|
| Interior, 10 to 30 yd split <= 2.12 s (37 players) | POE +1.7 [+0.3, +3.2] vs -0.5 for the rest; gap +2.3 [+0.5, +4.1] | Draft up; rotational pass rusher from day one |
| Interior, split 2.12 to 2.20 s | Everyone at or under 2.20 s averages +0.5 [-0.9, +1.5] | Rely on tape and size |
| Interior, split > 2.20 s (23 players) | POE -0.9 [-1.9, +0.1] | Run-down role unless tape shows win-quick |
| Interior under 297 lb (3-tech types) | Fast-minus-slow POE +2.3 [-4.3, +11.9] (<= 263 lb) and +3.1 [+0.6, +5.3] (264 to 294 lb) | Speed is the best Combine filter here |
| Interior 297+ lb (nose types) | Fast-minus-slow +0.5 [-2.4, +2.4] | Ignore the split |
| Fast edge with direct game paths (16 players) | POE +1.5 [-1.8, +3.3] | Rush from any alignment; coach arc discipline |
| Fast edge, indirect paths (18 players) | POE -0.8 [-3.8, +0.5]; wide -1.2, tight -1.7 | Wide-9 does not help; use stunts and games that shorten the path |
| Any edge, OL, WR/TE | No speed effect | Do not pay for speed alone |

Edge cells use the drill's path efficiency, which does not predict pressure on its own (interaction p = 0.54), so judge path directness on tape. The wide/tight split (distance to the nearest tracked blocker) is exploratory; weight bands proxy 3-tech versus nose.

**Week to week.** The same pipeline can be rerun after every game: xP refit on the season to date, each rusher's POE shrunk toward what size, draft slot and Combine speed predict, giving a stabilized leaderboard (Fig. 6) that separates a hot month from a trait. For a coordinator the matrix is a deployment rule: on passing downs rotate the fast-for-weight interior rusher in; for a fast edge with indirect paths, call stunts and games rather than widening his alignment.

## 11. Limitations

- Observational data: no causal claim beyond the mediation assumptions above.
- 75 interior and 95 edge players; the decision-matrix cells are small. Treat them as direction, not rules.
- The sensor audit covers the 40-yard window only; no quarterback tracking, time to throw or line-up depth, so double-team and alignment are proxies.
- Edge and OL nulls mean no detectable linear speed effect, not zero.

## 12. Takeaway

At 10 Hz the 40 is a top-speed test. For interior linemen it means about 1.8x the pressure rate between slow and fast prospects of the same size and draft slot, it survives sensor cleaning, selection correction and a context model, and about 20% of it runs through a faster first move. On the edge, speed is real but the path spends it. Use the trace to find interior rushers who are fast for their weight; read edge rushers off the tape.

## Appendix: references

1. Kuzmits FE, Adams AJ. The NFL Combine: does it predict performance in the National Football League? J Strength Cond Res. 2008;22(6):1721-1727.
2. Cook J, Ryan GA, Snarr RL, Rossi S. The relationship between the NFL Scouting Combine and game performance over a 5-year period. J Strength Cond Res. 2020;34(9):2492-2499.
3. LaPlaca DA, McCullick BA. NFL Scouting Combine tests correlated to NFL player performance. J Strength Cond Res. 2020;34(5):1317-1329.
4. Vincent LM, Blissmer BJ, Hatfield DL. National Scouting Combine scores as performance predictors in the NFL. J Strength Cond Res. 2019;33(1):104-111.
5. Imai K, Keele L, Tingley D. A general approach to causal mediation analysis. Psychol Methods. 2010;15(4):309-334.
6. Benjamini Y, Hochberg Y. Controlling the false discovery rate: a practical and powerful approach to multiple testing. J R Stat Soc B. 1995;57(1):289-300.
7. Heckman JJ. Sample selection bias as a specification error. Econometrica. 1979;47(1):153-161.
8. Liang KY, Zeger SL. Longitudinal data analysis using generalized linear models. Biometrika. 1986;73(1):13-22.
9. Savitzky A, Golay MJE. Smoothing and differentiation of data by simplified least squares procedures. Anal Chem. 1964;36(8):1627-1639.
10. Ke G, et al. LightGBM: a highly efficient gradient boosting decision tree. Advances in Neural Information Processing Systems 30. 2017.
11. Data notes on preseason games, ball frames and the 2025 export come from the competition data page and public BDB 2027 notebooks by D. Afshar ("Combine Tracking Audit") and Yumeko ("DB Drills Decoded"), Kaggle, October 2026.
