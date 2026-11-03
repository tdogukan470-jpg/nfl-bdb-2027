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
