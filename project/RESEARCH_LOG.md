# RESEARCH_LOG

## 2026-11-01
- Read competition evaluation rubric; identified PASS/FAIL "embedded visuals" gate -> figures embedded inline via GitHub raw URLs (tested in editor preview before publishing; renders at 3200 px through Kaggle's proxy).
- Pulled and read 12 public notebooks (list in COMPETITION_INTELLIGENCE.md). Found three fixes for our pipeline: REG filter, dropback filter, class fixed effects; plus the data-licence issue (per-play parquet in outputs).
- Literature verified via publisher/library records: Kuzmits & Adams 2008; Cook et al. 2020; LaPlaca & McCullick 2020; Vincent et al. 2019 (all JSCR). Methods refs: IKT 2010, BH 1995, Heckman 1979, Liang-Zeger 1986, Savitzky-Golay 1964, LightGBM 2017.
- Discovered that the v12 LightGBM xP (AUC 0.64) was mostly a run/pass classifier: on true dropbacks AUC fell to 0.57 with negative log-loss gain. Replaced by out-of-fold model selection (regularized GBM vs ridge logistic vs league rate); logistic won (AUC 0.58, +1.1% log loss, 0.9 pp max calibration gap).
