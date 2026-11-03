# RESEARCH_LOG

## 2026-11-01
- Read competition evaluation rubric; identified PASS/FAIL "embedded visuals" gate -> figures embedded inline via GitHub raw URLs (tested in editor preview before publishing; renders at 3200 px through Kaggle's proxy).
- Pulled 12 public notebooks (7 read, 5 not read) (list in COMPETITION_INTELLIGENCE.md). Found three fixes for our pipeline: REG filter, dropback filter, class fixed effects; plus the data-licence issue (per-play parquet in outputs).
- Literature: abstracts and library records only (no full texts) for Kuzmits & Adams 2008; Cook et al. 2020; LaPlaca & McCullick 2020; Vincent et al. 2019 (all JSCR). Methods refs: IKT 2010, BH 1995, Heckman 1979, Liang-Zeger 1986, Savitzky-Golay 1964, LightGBM 2017.
- Discovered that the v12 LightGBM xP (AUC 0.64) was mostly a run/pass classifier: on true dropbacks AUC fell to 0.57 with negative log-loss gain. Replaced by out-of-fold model selection (regularized GBM vs ridge logistic vs league rate); logistic won (AUC 0.58, +1.1% log loss, 0.9 pp max calibration gap).

## 2026-11-03 (corrections after user audit)
- Kuzmits & Adams 2008 issue verified as 22(6):1721-7 (secondary bibliography + publisher URL path 2008/11000); DOI 10.1519/JSC.0b013e318185f09d from the publisher URL. Full titles restored for refs 3-4 with DOIs from library records. Cook 2020 DOI not verified, so omitted.
- Literature sentence rewritten to say only what the abstracts state.
- Figure captions checked against the images: Fig. 1 and Fig. 6 captions were wrong (described content not in the figure) and were rewritten; source/footer lines on all figures claimed "GEE-logit" for figures without models (fixed in notebook source, takes effect on next run).
- Table 2 actions softened to what the intervals support; "best Combine filter" claim removed (no comparison was run); "Wide-9" claim relabelled as exploratory; weekly use labelled "proposed, not tested".
- Beta-Binomial: LR p 0.003 vs player-bootstrap CI 0.93-1.34 now reported together as "supportive, not decisive".
- Unverified 2025-export claim now attributed and marked "not verified by us".
