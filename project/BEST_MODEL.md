# BEST_MODEL
Notebook version 16 (doukanturan/nfl-bdb27-speed-travels). Rollback points: v12 outputs in nfl_k/nb_out12 (old pipeline), v14 outputs in nb_out14 (same numbers as v16 with old figure labels).
Spec: logistic GEE on regular-season dropback rushes, clustered by player; controls weight z, arm length z, log draft slot z, draft-class fixed effects, down>=3, yards to go (capped 15). Exposure: mean Combine top speed per +0.5 yd/s.
Context model: ridge logistic (C=0.1) chosen by out-of-fold log loss over regularized LightGBM and the league rate; GroupKFold(5) by rusher.
Seeds: fixed (0, 1, 5, 11 for the respective bootstraps/permutations); results deterministic across v14-v16.
