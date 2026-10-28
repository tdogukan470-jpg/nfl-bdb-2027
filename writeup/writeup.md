# Speed Travels: What 10 Hz Combine Tracking Tells Us About the NFL Pass Rush

**Subtitle:** Combine top speed predicts interior DL pressure (OR 1.22 per +0.5 yd/s) and survives sensor cleaning, selection correction and a context model. Edge, OL, WR/TE and drill first-step numbers do not.

**Track:** Open. **Code:** public notebook attached; it rebuilds every number and figure from the raw competition files.

## 1. The question

Teams read Combine tracking as a proxy for how a player will move on Sundays. We ask which Combine movement traits carry over to game performance, and where they do not. A scouting number that is wrong for half the positions is dangerous, so the boundaries matter as much as the finding.

## 2. What the Combine data measures, and whether we can trust it

We rebuilt each 40-yard dash from the 10 Hz trace: start of motion, peak speed over 30 yd, speed at 10 yd, the 10 to 30 yd split, and an acceleration time constant (Fig. 1). The stopwatch 40 is almost entirely top-end speed: across 418 prospects, tracking peak speed and stopwatch time correlate at r = -0.98.

**Reliability (Fig. 2).** Using repeat attempts, peak speed (0.99) and the 10 to 30 yd split (0.99) are nearly perfectly repeatable; the acceleration constant is 0.36. In the pass-rush drill, speed at 1.0 s is 0.54, at 0.5 s 0.40 and first-step acceleration 0.36. A mostly-noise trait cannot predict anything.

**Sensor audit.** Quantization artifacts would show as instantaneous acceleration above 3.5 g, which no lineman produces. We checked all 793 forty-yard attempts (2023 to 2025). In the 40-yard window, no attempt in any class contains a frame above 3.5 g (median peak 0.5 g), so our feature is not contaminated. We then rebuilt top speed with a Savitzky-Golay derivative filter and a 2.5 g acceleration limiter: correlation with the raw feature is 0.999, and the interior result is unchanged (OR 1.23 and 1.22). Dropping the entire 2024 class gives OR 1.25.

## 3. Method

From in-game tracking and play data for 2023 to 2025 we computed pressure per pass rush (interior DL, edge), pressure allowed per block (OL) and separation at pass-forward for WR/TE adjusted for route and coverage. The Combine feature is mean top speed across a player's 40 attempts, in units of +0.5 yd/s. Models are logistic GEE with standard errors clustered by player, controlling for weight, arm length, log draft slot, down and distance. Speed and weight correlate at -0.84 among interior linemen, so size is always in the model.

## 4. Result: interior defensive linemen

For 88 interior DL and 14,868 rushes, each +0.5 yd/s raises the odds of pressure by 22% (OR 1.22, 95% CI 1.12 to 1.33). Moving from the 10th to the 90th percentile of speed (9.1 to 10.7 yd/s) moves the adjusted pressure rate from 5.2% to 9.3%, a ratio of 1.8 (CI 1.2 to 2.5; Fig. 4).

**Table 1. Effect of +0.5 yd/s Combine top speed**

| Group | Outcome | Players / snaps | Effect (95% CI) | p |
|---|---|---|---|---|
| Interior DL | Pressure per rush | 88 / 14,868 | OR 1.22 [1.12, 1.33] | <0.001 |
| Edge | Pressure per rush | 121 / 19,322 | OR 1.05 [0.96, 1.14] | 0.30 |
| OL | Pressure allowed | 94 / 48,404 | OR 1.03 [0.93, 1.14] | 0.58 |
| WR / TE | Separation (yd) | 123 / 35,252 | +0.008 [-0.052, +0.067] | 0.80 |
| WR / TE, deep | Separation (yd) | 122 / 13,020 | +0.016 [-0.060, +0.092] | 0.68 |

**Stress tests (Fig. 5).** Team fixed effects give OR 1.30, opposing-offense effects 1.24, formation and alignment 1.21. Outcome variants: quick pressure 1.26, late 1.19, hurry 1.23, sack 1.33. Each season alone: 1.20, 1.21, 1.24. Dropping any single player: 1.19 to 1.25. A permutation test gives p < 0.001.

**Top speed, not burst.** Splitting the signal, top speed carries the effect (OR 1.22) and burst carries none (OR 1.03, p = 0.47); the stopwatch 10-yard split adds nothing once the 40 is in (p = 0.92). Interior rushers who reach and hold high speed win more often than those who merely start quickly, which runs against the usual emphasis on the first 10 yards.

## 5. Selection bias: we only see players who reached the field

Of 510 prospects, 97% appear in game tracking but only 133 (26%) rush the passer and 68 (13%) rush 100+ times. We modeled the probability of being observed for all 510 from measurables, draft slot, position and class (cross-fitted, AUC 0.97 and 0.99), then weighted by the inverse probability. A Heckman-type control function adds the probit inverse Mills ratio, with draft class (length of the observation window) as the excluded variable. Results: IPW OR 1.21 (CI 1.10 to 1.32) and 1.21 (1.10 to 1.34); control function OR 1.22 and 1.22, with Mills ratio coefficients far from significant (p = 0.25 and 0.78). Selection is largely explained by position and draft slot, so correcting for it moves nothing.

## 6. Context model: Pressure Over Expected

We built a LightGBM expected-pressure (xP) model on 34,190 rushes using down, distance, quarter, clock, score differential, defensive win probability, expected points, formation, receiver alignment, line-up group, distance to the sideline and distance to the nearest tracked opposing lineman (a double-team proxy, known on 67% of snaps). Five-fold cross-validation is grouped by rusher, so a player never trains the model that scores him. Out of fold, AUC is 0.64, log-loss improves 2.9% over the league rate and the worst decile miscalibration is 2.5 points. Two features we wanted were not usable: time to throw is not populated on defender rows (results are identical with and without it) and quarterback tracking is missing.

Pressure Over Expected (POE) is pressure minus xP. Entering xP as an offset, interior speed still gives OR 1.20 (1.09 to 1.31). In percentage points, +0.5 yd/s adds 1.03 POE per 100 rushes (0.55 to 1.50). Edge: OR 1.01 (0.93 to 1.10).

**Hierarchical shrinkage.** Raw player POE is noisy; its SD across interior players is 11.7 points. We fit a Beta-Binomial model in which each player's latent pressure probability has a prior mean equal to his context-expected rate, shifted by speed and size. Shrinking cuts the SD of player POE to 1.3 points, and Combine speed in the prior mean is significant (OR 1.20, CI 1.05 to 1.36, likelihood-ratio p = 0.009). Speed explains 9% of the variance in raw interior POE beyond weight, draft slot and arm length. Edge: OR 0.99 (0.88 to 1.16). Shrunk interior leaders are Fiske (+2.8 points), Byron Murphy (+2.2), Dexter (+1.8), Adebawore (+1.6) and Sweat (+1.1). Fig. 6 maps every interior lineman with 100+ rushes by weight and speed against what draft slot and size predict; it is an illustration, not a recommendation list, because single player-seasons are noisy.

## 7. How speed becomes pressure: formal mediation

We estimated Imai-Keele-Tingley causal mediation (1,000 quasi-Bayesian draws, cluster-robust covariances), on the risk-difference scale per +0.5 yd/s (Fig. 3 shows the first-second speed link).

**Interior.** Speed shortens get-off time, and get-off drives pressure. The average causal mediation effect (ACME) is +0.22 points per 100 rushes (95% CI 0.05 to 0.39, p = 0.007) against a total effect of +1.17 (0.57 to 1.71), so **18% (5% to 42%) runs through get-off**. Speed at 1 s, path directness, depth and width carry no detectable indirect effect.

**Edge: suppression.** Faster edge rushers do run faster in-game: ACME through speed at 1 s is +0.57 points (0.16 to 0.97). But they take less direct paths, and path efficiency carries an ACME of -0.76 (-1.26 to -0.28) while the direct effect is +1.16 (0.30 to 2.07). The total effect is +0.39 (-0.65 to +1.46). Speed helps; the route taken spends it. This is inconsistent mediation, which is why the total looks null. Sequential ignorability is an assumption: both variables are measured in the same snap, so read these as the indirect effects that would hold if no unmeasured factor drives get-off and pressure together.

## 8. Drill numbers do not travel (Fig. 3)

For 80 linemen with both drill traces and game tracking, the 40's top speed correlates r = 0.77 with game speed one second after the snap, but within interior linemen only r = 0.45 and within edge r = 0.24. The drill's first-step speed correlates r = 0.17 (CI -0.11 to 0.46). Trust the 40's speed trace; treat single-attempt drill first-step numbers as too noisy to use alone.

## 9. Out-of-time check and multiple testing

We fit through 2024 and test 2025 (Fig. 7). For 32 interior linemen with 75+ snaps, adding speed lifts the player-level Spearman correlation from 0.59 to 0.62. The interval includes zero, so forward evidence is directional, not conclusive.

We ran 112 tests: 15 group-level hypotheses, 76 mechanism paths and 21 robustness re-tests. With Benjamini-Hochberg correction, 66 have q < 0.05. Every interior headline test (Table 1, top speed, POE, stopwatch 40) has q < 0.001 except the Beta-Binomial test (q = 0.017); none of the edge, OL or WR headline tests has q below 0.4. Two robustness rows are weaker: sacks (q = 0.06) and quick pressure (q = 0.049).

## 10. Draft and deployment decision matrix

**Table 2. What to do with the numbers.** POE is percentage points of pressure per 100 rushes above context expectation.

| Prospect profile | Evidence | Action |
|---|---|---|
| Interior, 10 to 30 yd split <= 2.05 s (22 players) | POE +1.5 [-0.0, +3.5] vs -0.2 for the rest; gap +1.7 [0.2, 3.6] | Draft up. Starts as rotational pass rusher |
| Interior, split 2.05 to 2.21 s | Near zero (+0.4 [-0.6, 1.3] for all <= 2.21 s) | Rely on tape and size |
| Interior, split > 2.21 s (29 players) | POE -0.7 [-1.7, +0.0] | Run-down role unless tape shows win-quick |
| Interior under 297 lb (3-tech types) | Fast-minus-slow POE +2.7 (<=263 lb) and +1.7 (264 to 297 lb); CIs include 0 | Speed is the best Combine filter here |
| Interior 302+ lb (nose types) | Fast-minus-slow +0.2 [-2.0, 2.2] | Ignore the split |
| Fast edge with direct game paths (18 players) | POE +0.9 [-1.2, +1.9] | Rush from tight and wide alike; coach arc discipline |
| Fast edge, indirect paths (22 players) | POE -0.5 [-1.9, +0.3]; wide -1.0, tight -0.8 | Wide-9 does not rescue them. Use stunts and games that shorten the path |
| Any edge, OL, WR/TE | No speed effect | Do not pay for speed alone |

Edge cells use the drill's path efficiency, which does not predict pressure on its own (interaction p = 0.59), so judge path directness on game tape. We cannot see line-up depth or stunts; the wide/tight split uses distance to the nearest tracked blocker and is exploratory. Weight bands are a proxy for 3-tech versus nose.

## 11. Limitations

- Observational: speed correlates with draft slot, weight and conditioning, so we make no causal claim beyond the mediation assumptions above.
- 88 interior and 121 edge players. Intervals reflect that, and the decision-matrix cells are small; treat them as direction, not rules.
- The sensor audit covers the 40-yard window only.
- No quarterback tracking, time to throw or line-up depth, so double-team and alignment are proxies.
- Edge and OL nulls mean no detectable linear speed effect, not zero.

## 12. Takeaway

At 10 Hz the 40 is a top-speed test. For interior linemen, that top speed shows up as about 1.8x the pressure rate between slow and fast prospects of the same size and draft slot, survives sensor cleaning, selection correction and a context model, and runs 18% through a faster first move. On the edge, speed is real but the path spends it. Teams should use the trace to find interior rushers who are fast for their weight and read edge rushers off the tape.

*Reproduce: public notebook "NFL BDB27 Speed Travels".*
