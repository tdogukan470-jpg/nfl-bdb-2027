# DECISION_HISTORY
- 2026-11-01: Main analysis restricted to regular-season dropbacks (host allows pre/post, theme says regular season; strongest competitors filter REG). All-games fit kept as a robustness row.
- 2026-11-01: Draft-class fixed effects added to every model after public audits reported a 2025 export change; dropped automatically in single-class subsets.
- 2026-11-01: Context model chosen out of fold among GBM, logistic and league rate instead of a fixed LightGBM.
- 2026-11-01: Figures embedded inline from the public GitHub mirror; gallery kept as a Kaggle-hosted copy.
- 2026-11-01: Figure headlines softened to match the evidence (three robustness intervals touch 1.0; edge slope not distinguishable from zero).
- 2026-11-01: References moved to an in-writeup appendix (excluded from the word count by the host).
- 2026-11-03: Drill-translation section moved before Method so figures appear in order 1-7 (live page verified). Writeup body now loaded into Kaggle from the GitHub raw file, so the published text and writeup/writeup.md are byte-identical.
- 2026-11-03: E17 leave-one-class-out failed (speed does not improve held-out-class prediction; 2024+2025 classes alone give OR 1.00). Writeup, README, takeaway, limitations and Table 2 actions rewritten to say the interior effect leans on the 2023 class and is a hypothesis for new classes. Headline subtitle changed accordingly.
- 2026-11-03: Kaggle bridge hardened: write_json retries on PermissionError; jobs claimed atomically (inbox -> claimed) so a second bridge instance cannot run a job twice. Takes effect after restart.

## 2026-11-17 D: NO-GO on a 2026-season out-of-time test with nflverse data
- Trigger: host confirmed public external data is allowed (discussion 759641, "submission should focus on the data from the 2027 Big Data Bowl"); a competitor pre-registered a 2026 out-of-time test (759351).
- Feasibility checked WITHOUT looking at any speed-outcome relation: nflverse 2026 data reachable, through week 10. Per-rusher pressure is not public; only QB hits/sacks per defensive snap (a noisy proxy that also counts run snaps).
- 2026 draft class DT with a public 40 time and >=100 defensive snaps through week 10: 4 players (5 at >=50). 2023-25 classes: 6/8/7.
- Decision: NO-GO. A new-class test on 4-8 players with a proxy outcome cannot falsify or support an OR of about 1.2; a null would be uninformative and still have to be reported. Revisit only if a per-rusher pressure source becomes public.
- Host also said pre-registration hash posts are not needed and are not judged (759621); no action.
