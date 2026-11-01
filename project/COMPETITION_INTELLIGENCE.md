# COMPETITION_INTELLIGENCE (2026-11-01)

Sources inspected: competition Overview/Evaluation/Data/Rules pages; host (Tom Bliss) forum answers (threads 746425, 746678, 750418); 12 public notebooks pulled with the Kaggle CLI and read (markdown + code).

## Host clarifications (VERIFIED FACT, forum)
- Preseason/postseason outcomes may be used; theme text says regular season. We use REG only and report the all-games fit as a robustness row.
- blitz TRUE + NA pressure fields = no pressure. player_get_off NA = never crossed the LOS (rare). Dropbacks = plays with pass_result != "".
- Captions, figure labels and an in-writeup appendix do not count toward the 2,000 words.

## Data quirks found by the field (VERIFIED by our own run where marked)
- Files hold preseason (16.5% of player_play rows, VERIFIED v13) and playoff (4.2%, VERIFIED) games; games.season_type has REG/PRE/POST.
- player_get_off is populated on run plays: the dropback filter removed 24% of rows with a get-off (VERIFIED v13 log: 33,577 -> 25,384).
- Combine `dis` column is close to the squared step (D. Afshar; not used by us). Ball frames carry nfl_id in receiver drills (we filter entity_type == PLAYER).
- 2025 Combine export at full precision vs 1/60-yd grid in 2023-24 (Yumeko, agileteam; not independently verified by us -> cited, handled with draft-class fixed effects).

## Strongest public competitors (by votes, 2026-11-01)
- dariushafshar "Combine Tracking Audit" (44 votes): reliability + noise-floor audit; finds DL 10-yd split vs get-off r=0.67 raw, 0.35 weight-adjusted; "no detectable gain from the Combine beyond draft position" for rookie playing time. Different outcome (snap share) from ours (per-snap pressure).
- agileteam "Bend Before Sacks" (8 votes): rookie DL, bend speed, hoop drill, LightGBM xP + POE, beta shrinkage, class-centred Combine features, REG filter. Closest in method to ours; player-level partial Spearman rather than snap-level GEE.
- mathurinache "Who Owns the Get-Off": decomposes get-off into snap timing, depth, first movement; REG only; deletes per-play tables for licence reasons.
- olsols4 "Indy or Tape": Combine-prior vs game-evidence exchange rate; WR focus.
- nathanjacob OL pass protection; yumekohata DB drills EDA (2024 data trap); haydonnazar WR braking.
Writeups themselves are private until judging; only notebooks were readable.

## Our differentiators (HYPOTHESIS about judge perception)
Snap-level GEE with player clustering; sensor audit; IPW + Heckman selection correction over all 510 prospects; out-of-fold context model; Beta-Binomial shrinkage; formal IKT mediation; BH-FDR over all tests; decision matrix in scouting units; literature contrast.
