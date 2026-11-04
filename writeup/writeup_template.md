# Speed Travels: What 10 Hz Combine Tracking Tells Us About the NFL Pass Rush

**Track:** Open. The attached public notebook rebuilds every number and figure from the raw competition files; code, figures and results are mirrored at github.com/tdogukan470-jpg/nfl-bdb-2027.

## 1. The question

We ask which Combine movement traits carry over to regular-season NFL performance and where they do not; for a scout the boundaries matter as much as the finding.

Published studies report weak or modest links between Combine tests and season-level production: one study of quarterbacks, running backs and receivers found a link only for running backs' sprint times [1], another that the tests explained about 3% of first-year performance [2], and others found scattered position-specific correlations [3, 4]. Part of that is measurement: season totals mix talent with opportunity and most studies pool positions. We use per-snap outcomes from game tracking, movement rebuilt from the 10 Hz trace, one position group at a time, with size and draft slot held fixed.

## 2. What the Combine data measures, and whether we can trust it

From each 10 Hz 40-yard trace we rebuilt start of motion, peak speed over 30 yd, speed at 10 yd, the 10 to 30 yd split and an acceleration time constant (Fig. 1). The stopwatch 40 is almost entirely top-end speed: across {N:n40} prospects, tracking peak speed and stopwatch time correlate at r = {F2:forty_vs_vpk_r}.

![Fig. 1: Rebuilt 40-yard dash from 10 Hz tracking]({IMG}fig1_forty.png)
*Figure 1. Left: mean speed curve of each player's fastest tracked 40 by position group (band = 1 SD). Right: tracking top speed against the stopwatch 40 time, one dot per prospect.*

**Reliability (Fig. 2).** Across repeat attempts, peak speed ({REL:40 yd: peak speed}) and the 10 to 30 yd split ({REL:40 yd: 10-30 yd split time}) are nearly perfectly repeatable; the acceleration constant is {REL:40 yd: acceleration time constant}. In the pass-rush drill, speed at 1.0 s is {REL:Pass-rush drill: speed at 1.0 s}, at 0.5 s {REL:Pass-rush drill: speed at 0.5 s}, first-step acceleration {REL:Pass-rush drill: first-step acceleration}.

![Fig. 2: Reliability of Combine metrics (40 vs drill)]({IMG}fig2_reliability.png)
*Figure 2. Test-retest reliability from repeat attempts ({N:reliability_n.forty} players with two 40s, {N:reliability_n.prd} with two drill reps). Top speed repeats; first-step metrics do not.*

**Sensor audit.** Quantization artifacts would appear as implausible accelerations above 3.5 g. Across all {N:audit.n_attempts} forty-yard attempts (2023 to 2025) no frame in the 40-yard window exceeds 3.5 g (median peak {MEDG} g). Rebuilding top speed with a Savitzky-Golay derivative filter [9] or a 2.5 g limiter leaves the feature (r = {F3:audit.r_raw_sg}) and the interior result (OR {OR:robust.Sensor-cleaned: Savitzky-Golay filter} and {OR:robust.Sensor-cleaned: 2.5 g limiter}) unchanged. Public notebooks report that the 2025 export is stored at full precision while 2023-24 sit on a 1/60-yd grid [11]; we did not verify this ourselves, so every model carries draft-class fixed effects; dropping the 2024 class gives OR {OR:robust.Drop the 2024 Combine class}.

**Data hygiene.** The game files also hold preseason and playoff games ({PCT_NONREG}% of player-play rows); every number below uses regular-season dropbacks only. Including every game gives OR {OR:robust.All games incl. preseason and playoffs}.

## 3. Drill numbers do not travel (Fig. 3)

For {N:translate.n_game} linemen with both drill traces and game tracking, the 40's top speed correlates r = {F2:translate.r_vpk_s10.0} with game speed one second after the snap; within interior linemen r = {F2:translate.within_interior.r_vpk_s10.0} and within edge r = {F2:translate.within_edge.r_vpk_s10.0}. The drill's first-step speed correlates r = {F2:translate.r_drill_s10.0} (CI {F2:translate.r_drill_s10.1} to {F2:translate.r_drill_s10.2}). Trust the 40's speed trace; single-attempt drill first-step numbers are too noisy to use alone.

![Fig. 3: Does Combine speed translate to in-game speed?]({IMG}fig3_translation.png)
*Figure 3. Combine measures against in-game speed one second after the snap: the 40's top speed (left) carries over, the pass-rush drill's first step (right) does not.*

## 4. Method

From 2023 to 2025 regular-season tracking we computed pressure per pass rush (interior DL, edge), pressure allowed per block (OL) and separation at pass-forward for WR/TE adjusted for route and coverage. The Combine feature is mean top speed across a player's 40 attempts, in units of +0.5 yd/s, about {STOPWATCH} s on the stopwatch at a lineman's speed. Models are GEE with standard errors clustered by player [8] (logistic for pressure, linear for separation), controlling for weight, arm length, log draft slot and draft class, plus down and distance for rushers and route, coverage and cushion for receivers. Speed and weight correlate at {F2:interior_corr_weight_speed} among interior linemen, so size is always in the model.

## 5. Result: interior defensive linemen

For {N:n.int_players} interior DL and {N:n.int_snaps} rushes, each +0.5 yd/s raises the odds of pressure by {ORPCT:table1.int_pressure}% (OR {OR:table1.int_pressure}, 95% CI {LO:table1.int_pressure} to {HI:table1.int_pressure}{BOOTCI}). From the 10th to the 90th percentile of speed ({F1:p10_p90.v10} to {F1:p10_p90.v90} yd/s) the adjusted pressure rate moves from {PCT1:p10_p90.rate10}% to {PCT1:p10_p90.rate90}%, a ratio of {F1:p10_p90.ratio} (CI {F1:p10_p90.ratio_lo} to {F1:p10_p90.ratio_hi}; Fig. 4). In scouting terms: between two interior prospects of the same weight, arm length and draft range, {STOPWATCH} s on the 40 is worth about {PRESS100} pressures per 100 rushes.

**Table 1. Effect of +0.5 yd/s Combine top speed**

| Group | Outcome | Players / snaps | Effect (95% CI) | p |
|---|---|---|---|---|
| Interior DL | Pressure per rush | {N:n.int_players} / {N:n.int_snaps} | OR {ORB:table1.int_pressure} | {P:table1.int_pressure.p} |
| Edge | Pressure per rush | {N:n.edge_players} / {N:n.edge_snaps} | OR {ORB:table1.edge_pressure} | {P:table1.edge_pressure.p} |
| OL | Pressure allowed | {N:table1.ol_n.players} / {N:table1.ol_n.snaps} | OR {ORB:table1.ol_pressure_allowed} | {P:table1.ol_pressure_allowed.p} |
| WR / TE | Separation (yd) | {N:table1.wr_n.players} / {N:table1.wr_n.snaps} | {LINB:table1.wr_sep_all} | {P:table1.wr_sep_all.p} |
| WR / TE, deep | Separation (yd) | {N:table1.wr_n.deep_players} / {N:table1.wr_n.deep_snaps} | {LINB:table1.wr_sep_deep} | {P:table1.wr_sep_deep.p} |

![Fig. 4: Pressure rate vs Combine top speed (interior DL vs edge)]({IMG}fig4_dose.png)
*Figure 4. Adjusted pressure rate against Combine top speed with cluster-bootstrap bands. Interior linemen rise across the speed range; the edge slope is not distinguishable from zero.*

**Stress tests (Fig. 5).** Across {N_RB} alternative specifications the odds ratio runs from {RB_MIN} to {RB_MAX}. {WEAK_ROWS} Dropping any single player gives {F2:loo_OR_range.0} to {F2:loo_OR_range.1}; a permutation test gives p {PERM}. Single seasons are not independent checks, since the same draft classes recur across seasons (Section 9).

![Fig. 5: Robustness checks (sensor, selection, xP, seasons)]({IMG}fig5_robust.png)
*Figure 5. The interior effect under every specification: fixed effects, outcome definitions, seasons, sensor cleaning, selection correction and the context model. 1.0 is no effect.*

**Top speed, not burst.** Splitting the signal, top speed carries the effect (OR {OR:decomp.top}) and burst carries none (OR {OR:decomp.burst}, p = {P2:decomp.burst.p}); the stopwatch 10-yard split adds nothing once the 40 is in (p = {P2:decomp_stopwatch.ten.p}).

## 6. Selection bias: we only see players who reached the field

Of {N:selection.universe} prospects, {PCT0:selection.share_any_snap}% appear in game tracking but only {N:selection.S_rush.n_selected} ({PCT0:selection.share_rush}%) rush the passer and {N:selection.S_100.n_selected} ({PCT0:selection.share_100}%) rush 100+ times. We modeled each prospect's chance of being observed from measurables, draft slot, position and class (cross-fitted, AUC {F2:selection.S_rush.auc} and {F2:selection.S_100.auc}) and weighted by its inverse; a Heckman-type control function [7] adds the probit inverse Mills ratio, with draft class as the excluded variable. IPW OR {OR:robust.IPW selection weights (any rush snap)} (CI {LO:robust.IPW selection weights (any rush snap)} to {HI:robust.IPW selection weights (any rush snap)}) and {OR:robust.IPW selection weights (100+ rush snaps)} ({LO:robust.IPW selection weights (100+ rush snaps)} to {HI:robust.IPW selection weights (100+ rush snaps)}); control function OR {OR:robust.Heckman-type control function (any rush snap)} and {OR:robust.Heckman-type control function (100+ rush snaps)} (Mills ratio p = {P2:selection.S_rush.imr_coef_p} and {P2:selection.S_100.imr_coef_p}).

## 7. Context model: Pressure Over Expected

We built an expected-pressure (xP) model on {N:xp.n} dropback rushes from down, distance, clock, score, win probability, field position, formation and the distance to the nearest tracked opposing lineman (a double-team proxy, known on {PCT0:xp.opp_ol_known_share}% of snaps). A regularized LightGBM [10] and a ridge logistic regression compete out of fold, with folds grouped by rusher so no player trains the model that scores him. {XP_SENTENCE}

Pressure Over Expected (POE) is pressure minus xP. With xP as an offset, interior speed gives OR {OR:poe.interior.or_offset} ({LO:poe.interior.or_offset} to {HI:poe.interior.or_offset}): +0.5 yd/s adds {F1:poe.interior.poe_pp_per_unit.b} points of POE per 100 rushes ({F1:poe.interior.poe_pp_per_unit.lo} to {F1:poe.interior.poe_pp_per_unit.hi}). Edge: OR {OR:poe.edge.or_offset} ({LO:poe.edge.or_offset} to {HI:poe.edge.or_offset}).

**Hierarchical shrinkage.** Raw player POE is noisy; its SD across interior players is {F1:eb.interior.sd_raw_poe_pp} points. We fit a Beta-Binomial model in which each player's latent pressure probability has a prior mean equal to his context-expected rate, shifted by speed, weight, arm length and draft slot. Shrinking cuts the SD of player POE to {F1:eb.interior.sd_shrunk_poe_pp} points. Combine speed in the prior mean carries OR {F2:eb.interior.OR}; the likelihood-ratio test gives p = {P3:eb.interior.lr_p}, but a player bootstrap interval ({F2:eb.interior.OR_lo} to {F2:eb.interior.OR_hi}) includes 1, so we count this check as supportive, not decisive. Edge: OR {F2:eb.edge.OR} ({F2:eb.edge.OR_lo} to {F2:eb.edge.OR_hi}). Shrunk leaders: {EBTOP}.

![Fig. 6: Scouting view, interior DL vs expectation]({IMG}fig6_scouting.png)
*Figure 6. Scouting view: each interior lineman with 100+ rushes placed by Combine weight and top speed, coloured by pressures per 100 rushes above or below what draft slot and size predict. An illustration of the method, not a recommendation list: single player-seasons are noisy.*

## 8. How speed becomes pressure: formal mediation

Imai-Keele-Tingley mediation [5] (1,000 quasi-Bayesian draws, cluster-robust), risk-difference scale per +0.5 yd/s.

**Interior.** Speed shortens get-off time, and get-off drives pressure: the average causal mediation effect (ACME) is {PP:mediation.interior.player_get_off.acme} points per 100 rushes (p = {P3:mediation.interior.player_get_off.acme.p}) against a total effect of {PP:mediation.interior.player_get_off.tot}, so **{PCT0:mediation.interior.player_get_off.prop.est}% ({PCT0:mediation.interior.player_get_off.prop.lo}% to {PCT0:mediation.interior.player_get_off.prop.hi}%) runs through get-off**. Speed at 1 s, path directness, depth and width show no detectable indirect effect.

**Edge: suppression.** Faster edge rushers do run faster in-game (ACME through speed at 1 s {PP:mediation.edge.s_10.acme}), but they take less direct paths: path efficiency carries an ACME of {PP:mediation.edge.path_eff_20.acme} against a direct effect of {PP:mediation.edge.path_eff_20.ade}, total {PP:mediation.edge.path_eff_20.tot}. Speed helps, the route spends it, and the edge total looks null. Mediator and outcome come from the same snap, so these hold only if no unmeasured factor drives both.

## 9. Out-of-sample checks and multiple testing

We fit through 2024 and test 2025 (Fig. 7). For {N:forward.eval_players} interior linemen with 75+ snaps, adding speed lifts the player-level Spearman correlation from {F2:forward.rho_draft+size} to {F2:forward.rho_draft+size+speed}; the log-loss gain is positive in {PCT0:forward.dll_pos_share}% of bootstrap resamples but its interval includes zero. {LOCO_SENTENCE}

![Fig. 7: Out-of-time check (fit through 2024, test 2025)]({IMG}fig7_forward.png)
*Figure 7. Models fit on 2023 and 2024 predict 2025 interior pressure rates. Adding Combine speed to draft slot and size moves the ranking in the right direction.*

We ran {N:fdr.n_tests} tests: {N:fdr.by_family.H} group-level hypotheses, {N:fdr.by_family.M} mechanism paths and {N:fdr.by_family.R} robustness re-tests. With Benjamini-Hochberg correction [6], {N:fdr.n_q05_all} have q < 0.05. {FDR_HEADLINE}

## 10. How a team uses this

**Table 2. Draft-cycle and deployment decision matrix. POE is percentage points of pressure per 100 rushes above context expectation.**

| Prospect profile | Evidence | Action |
|---|---|---|
| Interior, 10 to 30 yd split <= {CUT_G} s ({N_G} players) | POE {POE_G} vs {POE_REST} for the rest; gap {GAP_G} | Flag for a closer pass-rush look |
| Interior, split {CUT_G} to {CUT_R} s ({N_MID} players) | {MID_TEXT} | Rely on tape and size |
| Interior, split > {CUT_R} s ({N_R} players) | POE {POE_R} | Lower pass-rush priority; let tape decide |
| Interior under {W2P} lb (3-tech types) | Fast-minus-slow POE {GAP_LIGHT_CI} (<= {W1} lb) and {GAP_MID_CI} ({W1P} to {W2} lb) | {LIGHT_ACTION} |
| Interior {W2P}+ lb (nose types) | Fast-minus-slow {GAP_HEAVY} | No gap; use other traits |
| Fast edge, efficient drill path ({N_FE} players) | POE {POE_FE} | No clear gain from speed; judge on tape |
| Fast edge, inefficient drill path ({N_FI} players) | POE {POE_FI}; wide {POE_FI_W}, tight {POE_FI_T} (exploratory) | Wider alignment did not offset it; path-shortening stunts are an untested option |
| Any edge, OL, WR/TE | No detectable speed effect | Do not pay for speed alone |

Edge cells use the drill's path efficiency, which does not predict pressure on its own (interaction p = {P2:matrix.edge_interaction.p}), so judge path directness on tape. Weight bands proxy 3-tech versus nose.

**Week to week (proposed, not tested here).** Refitting xP on the season to date and shrinking each rusher's POE toward his Combine-based prior would separate a hot month from a trait.

## 11. Limitations

- Observational data: no causal claim beyond the mediation assumptions above.
- {N:n.int_players} interior and {N:n.edge_players} edge players; the decision-matrix cells are small. Treat them as direction, not rules.
- {LIM_CLASS}
- The sensor audit covers the 40-yard window only; no quarterback tracking, time to throw or line-up depth, so double-team and alignment are proxies.
- Edge and OL nulls mean no detectable linear speed effect, not zero.

## 12. Takeaway

At 10 Hz the 40 is a top-speed test. In 2023-25 data, interior linemen who are fast for their size and draft slot generate about {F1:p10_p90.ratio}x the pressure rate of slow ones, about {PCT0:mediation.interior.player_get_off.prop.est}% of it through a faster first move. {TAKE_CLASS} On the edge, speed is real but the path spends it; read edge rushers off the tape.

## Appendix: references

1. Kuzmits FE, Adams AJ. The NFL combine: does it predict performance in the National Football League? J Strength Cond Res. 2008;22(6):1721-1727. doi:10.1519/JSC.0b013e318185f09d
2. Cook J, Ryan GA, Snarr RL, Rossi S. The relationship between the NFL Scouting Combine and game performance over a 5-year period. J Strength Cond Res. 2020;34(9):2492-2499.
3. LaPlaca DA, McCullick BA. National Football League Scouting Combine tests correlated to National Football League player performance. J Strength Cond Res. 2020;34(5):1317-1329. doi:10.1519/JSC.0000000000003479
4. Vincent LM, Blissmer BJ, Hatfield DL. National Scouting Combine scores as performance predictors in the National Football League. J Strength Cond Res. 2019;33(1):104-111. doi:10.1519/JSC.0000000000002937
5. Imai K, Keele L, Tingley D. A general approach to causal mediation analysis. Psychol Methods. 2010;15(4):309-334.
6. Benjamini Y, Hochberg Y. Controlling the false discovery rate: a practical and powerful approach to multiple testing. J R Stat Soc B. 1995;57(1):289-300.
7. Heckman JJ. Sample selection bias as a specification error. Econometrica. 1979;47(1):153-161.
8. Liang KY, Zeger SL. Longitudinal data analysis using generalized linear models. Biometrika. 1986;73(1):13-22.
9. Savitzky A, Golay MJE. Smoothing and differentiation of data by simplified least squares procedures. Anal Chem. 1964;36(8):1627-1639.
10. Ke G, et al. LightGBM: a highly efficient gradient boosting decision tree. Advances in Neural Information Processing Systems 30. 2017.
11. Data notes on preseason games, ball frames and the 2025 export come from the competition data page and public BDB 2027 notebooks by D. Afshar ("Combine Tracking Audit") and Yumeko ("DB Drills Decoded"), Kaggle, October 2026.

References 1-4 are cited from their abstracts and library records, not full texts.
