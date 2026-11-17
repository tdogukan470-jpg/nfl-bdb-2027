# Speed Travels: What 10 Hz Combine Tracking Tells Us About the NFL Pass Rush

**Track:** Open. The attached public notebook rebuilds every number and figure from the raw competition files; code, figures and results are mirrored at github.com/tdogukan470-jpg/nfl-bdb-2027.

**Bottom line for a front office.** (1) The 40's top speed is the one Combine movement number that reaches the field: it repeats almost perfectly and shows up in game speed, while drill first-step numbers repeat poorly and track game speed weakly. (2) Faster interior linemen cross the line of scrimmage sooner: about {GETOFF_MS} ms per +0.5 yd/s of top speed, a link that holds when whole players are resampled {GETOFF_HOLD} (Fig. 4). (3) They also generate more pressure ({PCT1:p10_p90.rate10}% to {PCT1:p10_p90.rate90}% from the 10th to 90th speed percentile), but that gain is borderline once whole players are resampled ({F2:pooled_boot.OR_lo} to {F2:pooled_boot.OR_hi}) and has not held out of class, so use it as a tiebreaker, not a rule. (4) For edge rushers, offensive linemen and receivers the 40 shows no consistent effect beyond size and draft slot.

## 1. The question

Which Combine movement traits carry over to regular-season NFL performance, and which do not?

Published studies find weak links between Combine tests and season production: sprint times mattered only for running backs in one [1], the tests explained about 3% of first-year performance in another [2], and correlations were scattered in others [3, 4]. Season totals mix talent with opportunity. We use per-snap outcomes from game tracking, movement rebuilt from the 10 Hz trace, one position group at a time, with size and draft slot held fixed.

## 2. What the Combine data measures

From each 10 Hz 40-yard trace we rebuilt start of motion, peak speed over 30 yd, speed at 10 yd, the 10 to 30 yd split and an acceleration time constant (Fig. 1). The stopwatch 40 is almost entirely top-end speed: across {N:n40} prospects, tracking peak speed and stopwatch time correlate at r = {F2:forty_vs_vpk_r}. A sensor audit and data-hygiene checks are in Appendix A1.

![Fig. 1: Rebuilt 40-yard dash from 10 Hz tracking]({IMG}fig1_forty.png)
*Figure 1. Left: mean speed curve of each player's fastest tracked 40 by position group (band = 1 SD). Right: tracking top speed against the stopwatch 40 time, one dot per prospect.*

**Reliability (Fig. 2).** Across repeat attempts, peak speed ({REL:40 yd: peak speed}) and the 10 to 30 yd split ({REL:40 yd: 10-30 yd split time}) are nearly perfectly repeatable; the acceleration constant is {REL:40 yd: acceleration time constant}. In the pass-rush drill, speed at 1.0 s is {REL:Pass-rush drill: speed at 1.0 s}, at 0.5 s {REL:Pass-rush drill: speed at 0.5 s}, first-step acceleration {REL:Pass-rush drill: first-step acceleration}.

![Fig. 2: Reliability of Combine metrics (40 vs drill)]({IMG}fig2_reliability.png)
*Figure 2. Test-retest reliability from repeat attempts ({N:reliability_n.forty} players with two 40s, {N:reliability_n.prd} with two drill reps). Top speed repeats; first-step metrics do not.*

## 3. Drill first-step numbers travel weakly (Fig. 3)

For {N:translate.n_game} linemen with both drill traces and game tracking, the 40's top speed tracks game speed one second after the snap within each group (interior r = {F2:translate.within_interior.r_vpk_s10.0}, edge r = {F2:translate.within_edge.r_vpk_s10.0}; pooled {F2:translate.r_vpk_s10.0}, inflated by the interior-edge gap). The drill's speed one second in tracks it weakly: r = {F2:translate.r_drill_s10.0} (CI {F2:translate.r_drill_s10.1} to {F2:translate.r_drill_s10.2}), or {F2:translate.r_drill_s10_trim.0} ({F2:translate.r_drill_s10_trim.1} to {F2:translate.r_drill_s10_trim.2}) without one outlier trace, against {F2:translate.r_vpk_s10.0} for the 40 on the same pooled basis. The drill's peak speed does better (r = {F2:translate.r_drill_speak.0}, repeatability {REL:Pass-rush drill: peak speed}), but that is top speed again. Trust top speed, not single-attempt first-step numbers.

![Fig. 3: Does Combine speed translate to in-game speed?]({IMG}fig3_translation.png)
*Figure 3. Combine measures against in-game speed one second after the snap: the 40's top speed (left) carries over, the pass-rush drill's speed 1.0 s in (right) tracks it more weakly, and its r depends on one outlier. Dot size: game rushes.*

## 4. Method

From 2023 to 2025 regular-season tracking we computed, per snap, get-off (seconds from the snap until the rusher crosses the line of scrimmage) and pressure for pass rushers, pressure allowed for offensive linemen, and separation at pass-forward for WR/TE adjusted for route and coverage. The Combine feature is mean top speed across a player's 40 attempts, in units of +0.5 yd/s, about {STOPWATCH} s on the stopwatch at a lineman's speed. Models are GEE with standard errors clustered by player [8], controlling for weight, arm length, log draft slot, draft class, down and distance. Speed and weight correlate at {F2:interior_corr_weight_speed} among interior linemen, so size is always in the model. Because a few heavy-usage players can make clustered intervals too narrow, every headline estimate is also re-checked by resampling whole players.

## 5. Where speed shows up first: the get-off

For {N:n.int_players} interior linemen and {N:n.int_snaps} dropback rushes, each +0.5 yd/s of Combine top speed shortens get-off by {GETOFF_MS} ms ({GETOFF_SD} SD; whole-player bootstrap {GETOFF_MS_BOOT} ms), about {GETOFF_SHARE}% of the spread in average get-off between interior players (SD {GETOFF_BSD} s among the {N:getoff_loco.n_players_100} with 100+ rushes). The sign is the same in all three draft classes, though each class alone is imprecise (Fig. 4). This is the most direct Combine-to-game link in the data: speed measured in February shows up in the first second of an NFL rush.

![Fig. 4: Faster interior linemen cross the line sooner]({IMG}fig4_getoff.png)
*Figure 4. Left: each interior lineman's raw mean get-off against his Combine top speed (players with 50+ rushes; unadjusted, so lighter players' speed advantage is mixed in; circled: the illustrative pair below). Right: the adjusted effect in milliseconds, pooled and by class, with clustered-SE (blue) and whole-player bootstrap (orange) intervals.*

{PAIR_SENTENCE}

Get-off then feeds pressure: in a formal mediation analysis [5], **{PCT0:mediation.interior.player_get_off.prop.est}% ({PCT0:mediation.interior.player_get_off.prop.lo}% to {PCT0:mediation.interior.player_get_off.prop.hi}%) of the speed-pressure link runs through get-off** (Appendix A4).

## 6. Pressure: a real but borderline gain

Each +0.5 yd/s raises the odds of pressure by {ORPCT:table1.int_pressure}% (odds ratio, OR, {OR:table1.int_pressure}; clustered 95% CI {LO:table1.int_pressure} to {HI:table1.int_pressure}{BOOTCI}). An OR of 1.0 means no effect. From the 10th to the 90th percentile of speed ({F1:p10_p90.v10} to {F1:p10_p90.v90} yd/s) the adjusted pressure rate moves from {PCT1:p10_p90.rate10}% to {PCT1:p10_p90.rate90}% (Fig. 5). In scouting terms: for two interior prospects of the same size and draft range, {STOPWATCH} s on the 40 is worth about {PRESS100} pressures per 100 rushes.

**Table 1. Effect of +0.5 yd/s Combine top speed.** *Interior = lined up inside on the snap; {IL_NONDL} of the {N:n.int_players} are linebackers or defensive backs ({IL_NONDL_PCT}% of rushes). Roster DT, NT or DE only: OR {ORB:robust.Roster DT, NT or DE only}, {N:robust.Roster DT, NT or DE only.players} players. Interior row with whole players resampled: {F2:pooled_boot.OR_lo} to {F2:pooled_boot.OR_hi}. Edge: one class alone (2024) gives OR {F2:within_class.edge_2024.OR}, player bootstrap {F2:within_class.edge_2024.boot_ci.0} to {F2:within_class.edge_2024.boot_ci.1}.*

| Group | Outcome | Players / snaps | Effect (95% CI) | p |
|---|---|---|---|---|
| Interior DL | Pressure per rush | {N:n.int_players} / {N:n.int_snaps} | OR {ORB:table1.int_pressure} | {P:table1.int_pressure.p} |
| Edge | Pressure per rush | {N:n.edge_players} / {N:n.edge_snaps} | OR {ORB:table1.edge_pressure} | {P:table1.edge_pressure.p} |
| OL | Pressure allowed | {N:table1.ol_n.players} / {N:table1.ol_n.snaps} | OR {ORB:table1.ol_pressure_allowed} | {P:table1.ol_pressure_allowed.p} |
| WR / TE | Separation (yd) | {N:table1.wr_n.players} / {N:table1.wr_n.snaps} | {LINB:table1.wr_sep_all} | {P:table1.wr_sep_all.p} |
| WR / TE, deep | Separation (yd) | {N:table1.wr_n.deep_players} / {N:table1.wr_n.deep_snaps} | {LINB:table1.wr_sep_deep} | {P:table1.wr_sep_deep.p} |

![Fig. 5: Pressure rate vs Combine top speed (interior DL vs edge)]({IMG}fig5_dose.png)
*Figure 5. Adjusted pressure rate against Combine top speed with cluster-bootstrap bands. Interior linemen rise across the speed range; the edge slope is weak and its interval includes zero.*

**Stress tests (Fig. 6).** Across {N_RB} alternative specifications the odds ratio runs from {RB_MIN} to {RB_MAX}. {WEAK_ROWS} Dropping any single player gives {F2:loo_OR_range.0} to {F2:loo_OR_range.1}; a permutation test gives p {PERM}. Single seasons share draft classes, so they are not independent checks.

Correcting for who reached the field, for game context and for sensor noise leaves the estimate between {CORR_RANGE} (Appendix A1 to A3).

![Fig. 6: Robustness checks with clustered and player-bootstrap intervals]({IMG}fig6_robust.png)
*Figure 6. The interior pressure effect under the baseline and key alternatives (all {N_RB} in the notebook): fixed effects, outcome definitions, seasons, sensor cleaning, selection correction and the context model, with clustered-SE intervals; the orange bar resamples whole players. 1.0 is no effect.*

**Top speed, not burst.** Top speed carries the effect (OR {OR:decomp.top}) and burst carries none (OR {OR:decomp.burst}, p = {P2:decomp.burst.p}); the stopwatch 10-yard split adds nothing once the 40 is in (p = {P2:decomp_stopwatch.ten.p}).

## 7. Does it hold for a new class?

A scout needs the finding to hold for the next draft, so we hide one whole draft class at a time, fit on the other two and score the hidden class. **In plain terms: for a class the model had not seen, knowing speed did not measurably improve predictions of either pressure or per-snap get-off.** Pressure: {LOCO_SENTENCE} Get-off: {GETOFF_LOCO_SENTENCE} A season split (fit through 2024, predict 2025) is mildly positive but its interval also includes zero (Appendix A6).

![Fig. 7: Interior pressure effect by draft class]({IMG}fig7_byclass.png)
*Figure 7. Interior pressure effect fit separately by draft class. Blue: clustered-SE intervals; orange: whole-player bootstrap. Every class leans positive; none is precise once whole players are resampled (2023 is the tightest).*

## 8. How a team uses this

**Table 2. Exploratory draft-cycle and deployment matrix (small cells; cut-offs scanned, see note). POE is percentage points of pressure per 100 rushes above context expectation.**

| Prospect profile | Evidence | Action |
|---|---|---|
| Interior, 10 to 30 yd split <= {CUT_G} s ({N_G} players) | POE {POE_G} vs {POE_REST} for the rest; gap {GAP_G} | Flag for a closer pass-rush look |
| Interior, split {CUT_G} to {CUT_R} s ({N_MID} players) | {MID_TEXT} | Rely on tape and size |
| Interior, split > {CUT_R} s ({N_R} players) | POE {POE_R} | Lower pass-rush priority; let tape decide |
| Interior up to {W2} lb (the lightest band includes linebackers and DBs aligned inside) | Fast-minus-slow POE {GAP_LIGHT_CI} (<= {W1} lb) and {GAP_MID_CI} ({W1P} to {W2} lb) | {LIGHT_ACTION} |
| Interior {W2P}+ lb (nose types) | Fast-minus-slow {GAP_HEAVY} | No gap; use other traits |
| Edge, any speed x drill-path profile ({N_FE}/{N_FI}/{N_SE}/{N_SI} players) | Fast: POE {POE_FE} and {POE_FI}; slow: {POE_SE} and {POE_SI} | Leans toward fast, but cells are small; judge on tape |
| OL, WR/TE | No detectable speed effect | Do not pay for speed alone |

Edge cells use the drill's path efficiency, which does not predict pressure on its own (main effect p = {P2:matrix.edge_main_pez.p}; speed x path interaction p = {P2:matrix.edge_interaction.p}), so judge path directness on tape. Weight bands proxy 3-tech versus nose. {CUTSCAN}

**In practice.** (1) Read speed off the 40's top speed (tracking or stopwatch), not the drill's first step. (2) Among interior prospects of similar weight and draft range, expect the faster one to cross the line about {GETOFF_MS} ms sooner per 0.5 yd/s; treat any pressure edge as a tiebreaker. (3) *Proposed, not tested here:* get-off is logged on every rush, so a rookie's early-season get-off is a quick check on whether his Combine speed is reaching the field, long before his pressure rate settles.

## 9. Limitations

- Observational data: no causal claim beyond the mediation assumptions in Appendix A4.
- {N:n.int_players} interior and {N:n.edge_players} edge players; decision-matrix cells are small.
- No single draft class pins down the pressure effect once whole players are resampled.
- The rush sample is defined by a recorded get-off, so rushes where a lineman never crossed the line are not in it; we could not test whether speed predicts that.
- No quarterback tracking, time to throw or line-up depth, so double-team and alignment are proxies.
- Edge and OL nulls mean no detectable linear speed effect, not zero.

## 10. Takeaway

At 10 Hz the 40 is a top-speed test, and its clearest game footprint is a quicker interior get-off. The pressure gain that follows (about {F1:p10_p90.ratio}x from slow to fast, whole-player bootstrap {RATIO_BOOT}) is not yet proven out of class, so it should guide where scouts look, not replace the tape.

## Appendix A: robustness details

**A1. Sensor audit and data hygiene.** No frame in any of the {N:audit.n_attempts} forty-yard attempts (2023 to 2025) exceeds 3.5 g (median peak {MEDG} g), so quantization spikes do not drive the feature; rebuilding top speed with a Savitzky-Golay filter [9] or a 2.5 g limiter leaves it (r = {F3:audit.r_raw_sg}) and the interior result (OR {OR:robust.Sensor-cleaned: Savitzky-Golay filter} and {OR:robust.Sensor-cleaned: 2.5 g limiter}) unchanged. Public notebooks report [11] (not verified by us) that 2023-24 positions sit on a 1/60-yd grid while 2025 is full precision, so every model carries draft-class fixed effects; the 2025 and 2023 classes give similar point estimates ({F2:within_class.2025.OR} and {F2:within_class.2023.OR}; Section 7).

We drop preseason and playoff games ({PCT_NONREG}% of player-play rows) and keep regular-season dropbacks; including every game gives OR {OR:robust.All games incl. preseason and playoffs}.


**A2. Are we only seeing the players good enough to play?** A fast lineman who never earns snaps is invisible here, which could flatter speed. Of {N:selection.universe} prospects, {PCT0:selection.share_any_snap}% appear in game tracking, but only {N:selection.S_rush.n_selected} ({PCT0:selection.share_rush}%) rush the passer and {N:selection.S_100.n_selected} ({PCT0:selection.share_100}%) rush 100+ times. Upweighting rushers whose profile made the field unlikely (stabilized inverse-probability weights; with AUC {F2:selection.S_rush.auc} the weights lean on few players) gives OR {OR:robust.IPW selection weights (any rush snap)} ({LO:robust.IPW selection weights (any rush snap)} to {HI:robust.IPW selection weights (any rush snap)}), the same for 100+ rushes. A Heckman-type control function [7], with draft class as the excluded variable (so that outcome model drops class fixed effects), gives {OR:robust.Heckman-type control function (any rush snap)} and {OR:robust.Heckman-type control function (100+ rush snaps)} (Mills ratio p = {P2:selection.S_rush.imr_coef_p} and {P2:selection.S_100.imr_coef_p}). The estimate shrinks slightly but survives.

**A3. Is it the player or the situation?** Some rushes are easier than others. We predicted each rush's pressure chance (xP) on {N:xp.n} dropback rushes from game situation, formation and the distance to the nearest opposing lineman (a double-team proxy). {XP_SENTENCE}

Pressure Over Expected (POE) is pressure minus xP: what the rusher adds beyond his situation. Adjusting for situation changes nothing: interior OR {OR:poe.interior.or_offset} ({LO:poe.interior.or_offset} to {HI:poe.interior.or_offset}), or {F1:poe.interior.poe_pp_per_unit.b} POE points per 100 rushes per +0.5 yd/s ({F1:poe.interior.poe_pp_per_unit.lo} to {F1:poe.interior.poe_pp_per_unit.hi}). Edge: OR {OR:poe.edge.or_offset} ({LO:poe.edge.or_offset} to {HI:poe.edge.or_offset}).

*Can we rank individual players? No.* A Beta-Binomial model that pulls each player's POE toward what his measurables predict cuts the spread of player POE from {F1:eb.interior.sd_raw_poe_pp} to {F1:eb.interior.sd_shrunk_poe_pp} points; at 500 rushes a player's own record gets {EBW}% weight. Speed in that model carries OR {F2:eb.interior.OR} (likelihood-ratio p = {P3:eb.interior.lr_p}, but player bootstrap {F2:eb.interior.OR_lo} to {F2:eb.interior.OR_hi}): supportive, not decisive.

**A4. Mediation.** Imai-Keele-Tingley mediation [5] (1,000 draws), in pressures per 100 rushes per +0.5 yd/s. Interior: the indirect effect through get-off is {PP:mediation.interior.player_get_off.acme} (p = {P3:mediation.interior.player_get_off.acme.p}) of a total {PP:mediation.interior.player_get_off.tot}; speed at 1 s, path directness, depth and width carry no detectable share. Edge: faster edge rushers run faster in-game (indirect effect through speed at 1 s {PP:mediation.edge.s_10.acme}) but take less direct paths (path efficiency {PP:mediation.edge.path_eff_20.acme}); the total, {PP:mediation.edge.path_eff_20.tot}, includes zero. This assumes no unmeasured factor drives both path and outcome.

**A5. Multiple testing.** Of {N:fdr.n_tests} tests, {N:fdr.n_q05_all} keep q < 0.05 after Benjamini-Hochberg correction [6] (q is the p-value adjusted for the number of tests). {FDR_HEADLINE}

**A6. Season split.** Fit through 2024 and predict 2025: for {N:forward.eval_players} interior linemen with 75+ snaps, adding speed lifts the rank correlation from {F2:forward.rho_draft+size} to {F2:forward.rho_draft+size+speed} (change {F2:forward.drho_ci.0} to {F2:forward.drho_ci.1}); the log-loss gain's interval includes zero. The same draft classes appear on both sides of a season split, which is why Section 7 holds out whole classes instead.

## Appendix B: references

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
