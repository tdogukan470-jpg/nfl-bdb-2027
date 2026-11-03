# FAILED_EXPERIMENTS
- v12 LightGBM expected-pressure model on all plays (AUC 0.64) -> on dropbacks only AUC 0.57, log-loss gain -0.03% (v13). Cause: it learned run vs pass. Replaced (v14).
- Heckman control function with draft-class fixed effects in the outcome model would void the exclusion restriction (class is the excluded variable) -> control-function rows use the no-class control set.
- Gallery-only figures (v12) risked the "embedded visuals" PASS/FAIL gate -> inline embedding added (v16 writeup).
- Edge "Wide-9 rescues fast-but-inefficient rushers" hypothesis: not supported (wide -1.2, tight -1.7 POE; interaction p 0.54). Reported as negative.
- Process failures (2026-10/11): claimed figure embedding could not be automated without trying URL embedding; reported "done" before competitor/forum/literature scans; presented the v12 xP model as a context control without checking it on dropbacks only; mixed word-count methods; hand-wrote some constants while claiming none were hand-written; Table 2 middle row mislabelled for two days. All corrected; see RESEARCH_LOG 2026-11-03.
