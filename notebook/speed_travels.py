# %% [markdown]
# # Speed Travels: What 10 Hz Combine Tracking Tells Us About the NFL Pass Rush
#
# **NFL Big Data Bowl 2027 submission notebook.** This notebook rebuilds every number and figure in the writeup from the raw competition files.
#
# **Question.** Which movement traits measured by Combine player tracking carry over to regular-season NFL performance, and where do they not?
#
# **Short answer.**
# 1. The 10 Hz data shows that a prospect's 40-yard time is almost entirely *top-end speed*; the start phase is much noisier and carries no extra signal.
# 2. For **interior defensive linemen**, Combine top speed predicts pass-rush pressure in games, on top of draft slot, weight and arm length (odds ratio 1.22 per +0.5 yd/s, 95% CI 1.12 to 1.33). It is stable across seasons, teams, opponents, and outcome definitions.
# 3. For **edge rushers, offensive linemen and receivers** we find no speed signal. The boundary matters as much as the finding.
# 4. Drill "first-step" numbers from the Combine pass-rush drill do not translate to in-game first-step speed, and are only about 0.4 to 0.6 reliable on their own.
#
# 5. **Added checks (Part 5).** The result survives sensor cleaning, selection-bias correction (IPW and a Heckman-type control function over all 510 prospects), and a cross-validated LightGBM expected-pressure model (Pressure Over Expected). Formal mediation (Imai-Keele-Tingley) puts about 18% of the interior effect through get-off; on the edge, path efficiency suppresses the speed effect. All tests carry Benjamini-Hochberg q-values.
#
# **Layout.** Part 1 builds Combine movement features. Part 2 builds in-game features (cached after the first run). Part 3 is the statistics. Part 4 is the figures. Part 5 (placed before Part 4 in the file) holds the sensor audit, selection, xP/POE, mediation, FDR and decision-matrix numbers.

# %%
import os, json, time, warnings
import numpy as np, pandas as pd
import statsmodels.api as sm, statsmodels.formula.api as smf
from scipy.optimize import least_squares
from scipy.stats import spearmanr, pearsonr
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
warnings.filterwarnings("ignore")

IN = os.environ.get("NFL_IN", "/kaggle/input/competitions/nfl-big-data-bowl-2027/nfl-big-data-bowl-2027")
WORK = os.environ.get("NFL_WORK", "/kaggle/working")
FIG = os.path.join(WORK, "figs"); os.makedirs(FIG, exist_ok=True)
FAST = os.environ.get("NFL_FAST", "0") == "1"      # smaller bootstraps for quick local tests
T0 = time.time()
def log(*a): print(f"[{time.time()-T0:6.0f}s]", *a, flush=True)
z = lambda s: (s - s.mean()) / s.std()

# %% [markdown]
# ## Part 1. Combine movement features
# Each Combine event is a short 10 Hz trace of one player. For the 40-yard dash we find the start of motion (first 0.25 yd of travel), then compute top speed over the first 30 yards, speed at 10 yards, the 10 to 30 yard split, and a fitted acceleration time constant. We also keep each player's fastest attempt as a speed-time curve.

# %%
ct = pd.read_csv(f"{IN}/combine_tracking.csv", low_memory=False)
ct = ct[ct.entity_type == "PLAYER"].copy(); ct["t"] = pd.to_datetime(ct.time)
cr = pd.read_csv(f"{IN}/combine_results.csv"); pl = pd.read_csv(f"{IN}/players.csv")
log("combine tracking rows", len(ct), "players", ct.nfl_id.nunique())

def pos_model(t, v, tau, t0):
    zz = np.clip(t - t0, 0, None); return v * (zz - tau * (1 - np.exp(-zz / tau)))

GRID = np.arange(0, 5.6, 0.1)
rows, curves = [], {}
for (pid, eid), g in ct[ct.drill_name == "FORTY_YARD_DASH"].groupby(["nfl_id", "event_id"], sort=False):
    g = g.sort_values("t"); ts = (g.t - g.t.iloc[0]).dt.total_seconds().values; s = g.s.values; d = g.x.values - g.x.values[0]
    if len(g) < 40 or d[-1] < 35: continue
    k = np.argmax(d >= 0.25); t = ts - ts[k]; x = d - d[k]
    keep = t >= -0.3; t_, x_, s_ = t[keep], x[keep], s[keep]
    if x_.max() < 30: continue
    last = np.argmax(x_ >= 30); tt, xx, ss = t_[:last + 1], x_[:last + 1], s_[:last + 1]
    def tat(yd):
        i = np.argmax(xx >= yd); return np.interp(yd, [xx[i - 1], xx[i]], [tt[i - 1], tt[i]]) if i > 0 else tt[0]
    sol = least_squares(lambda p: pos_model(tt, *p) - xx, [10.5, 1.3, tt[0]], bounds=([6, 0.3, tt[0] - 1.0], [14, 4, tt[0] + 1.5]))
    vpk = ss.max(); v10 = float(np.interp(10, xx, ss))
    rows.append(dict(nfl_id=pid, event_id=eid, vpk=vpk, v10=v10, v10_frac=v10 / vpk, split10_30=tat(30) - tat(10), tau=sol.x[1], t30=tat(30)))
    curves[(pid, eid)] = np.interp(GRID, t, s, left=np.nan)
att40 = pd.DataFrame(rows)
log("40-yd attempts", len(att40), "players", att40.nfl_id.nunique())

# player level: mean over attempts
c40 = att40.groupby("nfl_id").agg(vpk=("vpk", "mean"), v10=("v10", "mean"), v10_frac=("v10_frac", "mean"), s1030=("split10_30", "mean"), n40=("vpk", "size")).reset_index()
c40 = c40.merge(cr, on="nfl_id").merge(pl[["nfl_id", "nfl_position", "draft_overall_pick", "draft_round"]], on="nfl_id")
c40["pos"] = c40.combine_position
c40["burst"] = smf.ols("v10 ~ vpk + C(pos)", c40).fit().resid     # start-phase speed after removing top speed
best = att40.sort_values("t30").groupby("nfl_id").head(1)
CUR = pd.DataFrame({r.nfl_id: curves[(r.nfl_id, r.event_id)] for r in best.itertuples()}).T; CUR.columns = GRID
CUR = CUR.join(c40.set_index("nfl_id")[["combine_position", "forty"]])

# pass-rush drill (defensive linemen): speed 0.5 s and 1.0 s after start, peak speed, first-step acceleration
rows = []
for (pid, eid), g in ct[ct.drill_name == "PASS_RUSH_DRILL"].groupby(["nfl_id", "event_id"], sort=False):
    g = g.sort_values("t"); ts = (g.t - g.t.iloc[0]).dt.total_seconds().values; s = g.s.values; a = g.a.values
    gx, gy = g.x.values, g.y.values; dist = np.hypot(gx - gx[0], gy - gy[0])
    if len(g) < 25 or dist.max() < 5.0 or np.any(np.diff(ts) <= 0): continue
    on = int(np.argmax(dist >= 0.25)); tt = ts - ts[on]          # same physical start rule as the 40 (0.25 yd of travel)
    vx, vy = np.gradient(gx, ts), np.gradient(gy, ts); angv = np.abs(np.gradient(np.unwrap(np.arctan2(vy, vx)), ts))
    win = (tt >= 0.8) & (tt <= 3.0); speak = float(s[on:].max())
    smin_turn = float(s[win & (angv >= np.percentile(angv[win], 75))].min()) if win.sum() >= 5 else np.nan
    plen = float(np.sum(np.hypot(np.diff(gx[on:]), np.diff(gy[on:])))); net = float(dist[-1] - dist[on])
    rows.append(dict(nfl_id=pid, event_id=eid, s05=np.interp(0.5, tt, s), s10=np.interp(1.0, tt, s), speak=speak, a_first=a[on:on + 6].mean() if len(a) > on + 6 else np.nan,
                     smin_turn=smin_turn, bend_retention=smin_turn / max(speak, 1e-3) if np.isfinite(smin_turn) else np.nan, path_eff=net / max(plen, 1e-3)))
prd = pd.DataFrame(rows); log("pass-rush drill attempts", len(prd), "players", prd.nfl_id.nunique())
c40.to_parquet(f"{WORK}/c40.parquet"); log("c40", c40.shape, " | forty vs tracking top speed r =", round(c40.dropna(subset=['forty']).pipe(lambda m: m.vpk.corr(m.forty)), 3))

# %% [markdown]
# ## Part 2. In-game features
# Game tracking contains only the Combine prospects (about 500 players across 2023 to 2025), so there is no opponent information. We therefore build, for every snap a prospect played:
# * the **speed profile after the snap** (speed at 0.5, 1.0, 1.5, 2.0, 3.0 s, top speed before the pass is thrown), and
# * the play-level outcomes from `player_play` (pressure, get-off time, sack, pressure allowed, separation, route).
#
# This is the slow part (about 5 minutes); results are cached in the working directory.

# %%
def snap_profile(year):
    d = pd.read_csv(f"{IN}/game_tracking_{year}.csv", usecols=["game_id", "play_id", "nfl_id", "time", "x", "y", "s", "o", "dir", "event"], dtype={"x": "float32", "y": "float32", "s": "float32", "o": "float32", "dir": "float32"})
    d = d.sort_values(["game_id", "play_id", "nfl_id", "time"], kind="stable").reset_index(drop=True)
    keys = ["game_id", "play_id", "nfl_id"]; g = d.groupby(keys, sort=False)
    d["fr"] = g.cumcount().astype("int32")
    snap = d.loc[d.event == "ball_snap"].groupby(keys, sort=False)["fr"].min().rename("snap_fr")
    pf = d.loc[d.event == "pass_forward"].groupby(keys, sort=False)["fr"].min().rename("pf_fr")
    d = d.join(snap, on=keys).join(pf, on=keys); d = d[d.snap_fr.notna()].copy()
    d["rel"] = (d.fr - d.snap_fr).astype("int32"); d["pf_rel"] = d.pf_fr - d.snap_fr
    at0 = d[d.rel == 0].set_index(keys)[["x", "y"]].rename(columns={"x": "x0", "y": "y0"})
    w = d[(d.rel >= 0) & (d.rel <= 40)].join(at0, on=keys)
    w["disp"] = np.hypot(w.x - w.x0, w.y - w.y0).astype("float32"); da = np.abs(w.o - w.dir) % 360.0; w["slip"] = np.minimum(da, 360.0 - da).astype("float32")
    out = w.groupby(keys, sort=False).agg(smax4=("s", "max"))
    for k in (5, 10, 15, 20, 30):
        sk = w[w.rel == k].set_index(keys); out[f"s_{k}"] = sk["s"]
        if k in (10, 20): out[f"disp_{k}"] = sk["disp"]; out[f"slip_{k}"] = sk["slip"]; out[f"adx_{k}"] = (sk["x"] - sk["x0"]).abs(); out[f"ady_{k}"] = (sk["y"] - sk["y0"]).abs()
    out["path_20"] = w[(w.rel >= 1) & (w.rel <= 20)].groupby(keys, sort=False)["s"].sum() * 0.1; out["path_eff_20"] = (out["disp_20"] / np.maximum(out["path_20"], 0.1)).clip(0, 1)
    pre = d[(d.rel >= 0) & (d.rel <= np.minimum(d.pf_rel.fillna(40), 40))]
    out["x0"] = at0["x0"]; out["y0"] = at0["y0"]
    out["smax_pre"] = pre.groupby(keys, sort=False)["s"].max(); out["pf_rel"] = d.groupby(keys, sort=False)["pf_rel"].first()
    out = out.reset_index(); out["season"] = year; log("snap profile", year, out.shape); return out

_c = f"{WORK}/snap_profile.parquet"
if os.path.exists(_c) and os.path.exists(f"{WORK}/player_play_slim.parquet") and "adx_20" in pd.read_parquet(_c).columns:
    sp = pd.read_parquet(_c); pp = pd.read_parquet(f"{WORK}/player_play_slim.parquet"); log("loaded cached in-game tables")
else:
    sp = pd.concat([snap_profile(y) for y in (2023, 2024, 2025)], ignore_index=True)
    pp = pd.read_csv(f"{IN}/player_play.csv", low_memory=False).drop(columns=["play_description"])
    sp.to_parquet(f"{WORK}/snap_profile.parquet"); pp.to_parquet(f"{WORK}/player_play_slim.parquet")
def season_of(g):
    y = g // 1000000; m = (g // 10000) % 100; return np.where(m >= 8, y, y - 1)
pp["season"] = season_of(pp.game_id)
log("player_play", pp.shape, "| prospects with in-game rows:", pp.nfl_id.nunique())

# %% [markdown]
# ## Part 3. Statistics
# **Unit.** Speed is expressed per **+0.5 yd/s of Combine top speed** (about 0.2 s off a 40 time at this range). Controls are always: combine weight, arm length, log draft slot (undrafted = 260), down, and yards to go. Odds ratios come from logistic GEE models clustered by player (a prospect appears in hundreds of snaps).

# %%
cov = c40[["nfl_id", "vpk", "v10", "combine_weight", "draft_overall_pick", "arm_length", "forty", "ten_yd_split", "burst"]]
def prep(d):
    d = d.merge(cov, on="nfl_id")
    d["vs"] = (d.vpk - 10.0) / 0.5; d["wz"] = z(d.combine_weight)
    d["pickz"] = z(np.log(d.draft_overall_pick.fillna(260))); d["az"] = z(d.arm_length.fillna(d.arm_length.mean()))
    d["down3"] = (d.down >= 3).astype(int); d["ytg"] = d.yards_to_go.clip(upper=15); return d
G = lambda f, dd, fam=None: smf.gee(f, groups="nfl_id", data=dd, family=fam or sm.families.Binomial()).fit()
def orci(g, k="vs"):
    b, se = g.params[k], g.bse[k]
    return dict(b=float(b), se=float(se), OR=float(np.exp(b)), lo=float(np.exp(b - 1.96 * se)), hi=float(np.exp(b + 1.96 * se)), p=float(g.pvalues[k]))
res = {}; B_BOOT = 60 if FAST else 300

rush = pp[pp.player_get_off.notna() & pp.lined_up_position.isin(["EDGE", "INTERIOR_LINE"])].copy()
rush["pres"] = rush.time_to_pressure.notna().astype(int); rush["quick"] = (rush.time_to_pressure <= 2.5).astype(int); rush["late"] = (rush.time_to_pressure > 2.5).astype(int)
rush["hurry"] = rush.time_to_qb_hurry.notna().astype(int); rush["sk"] = (rush.sack == 1).astype(int)
rush = prep(rush); IL = rush[rush.lined_up_position == "INTERIOR_LINE"].copy(); ED = rush[rush.lined_up_position == "EDGE"].copy()
res["n"] = dict(int_snaps=len(IL), int_players=int(IL.nfl_id.nunique()), edge_snaps=len(ED), edge_players=int(ED.nfl_id.nunique()), int_rate=float(IL.pres.mean()), edge_rate=float(ED.pres.mean()))
Pint = IL.groupby("nfl_id").first(); res["speed_sd_int"] = float(Pint.vpk.std()); res["speed_p10_p50_p90"] = [float(x) for x in np.percentile(Pint.vpk, [10, 50, 90])]
res["interior_corr_weight_speed"] = float(Pint.vpk.corr(Pint.combine_weight)); res["interior_corr_speed_logpick"] = float(Pint.vpk.corr(np.log(Pint.draft_overall_pick.fillna(260))))
b = "wz + pickz + az + down3 + ytg"
print(res["n"])

# %% [markdown]
# ### 3.1 Where does Combine speed matter? (Table 1)

# %%
T = {}
T["int_pressure"] = orci(G(f"pres ~ vs + {b}", IL)); T["edge_pressure"] = orci(G(f"pres ~ vs + {b}", ED))
ol = pp[pp.pressure_allowed.notna() & pp.lined_up_position.isin(["T", "G", "C"])].copy(); ol["pa"] = (ol.pressure_allowed.astype(str) == "True").astype(int); ol = prep(ol)
T["ol_pressure_allowed"] = orci(G(f"pa ~ vs + {b}", ol)); T["ol_n"] = dict(snaps=len(ol), players=int(ol.nfl_id.nunique()))
rt = pp[pp.route_ran.notna() & pp.lined_up_position.isin(["WR", "SLOT_WR", "TE"])].dropna(subset=["separation_at_pass_forward", "cushion", "team_coverage_man_zone"]).copy()
rt["man"] = (rt.team_coverage_man_zone == "MAN_COVERAGE").astype(int); rt = prep(rt)
fs = "separation_at_pass_forward ~ vs + wz + pickz + az + man + cushion + C(route_ran)"
def lin(g): return dict(b=float(g.params["vs"]), se=float(g.bse["vs"]), lo=float(g.params["vs"] - 1.96 * g.bse["vs"]), hi=float(g.params["vs"] + 1.96 * g.bse["vs"]), p=float(g.pvalues["vs"]))
T["wr_sep_all"] = lin(G(fs, rt, sm.families.Gaussian())); dp = rt[rt.route_ran.isin(["GO", "POST", "CORNER"])]; T["wr_sep_deep"] = lin(G(fs, dp, sm.families.Gaussian()))
T["wr_n"] = dict(snaps=len(rt), players=int(rt.nfl_id.nunique()), deep_snaps=len(dp), deep_players=int(dp.nfl_id.nunique()))
res["table1"] = T
tab = pd.DataFrame([
    ["Interior DL", "Pressure per rush", f"{res['n']['int_players']} / {res['n']['int_snaps']:,}", f"OR {T['int_pressure']['OR']:.2f} [{T['int_pressure']['lo']:.2f}, {T['int_pressure']['hi']:.2f}]", f"{T['int_pressure']['p']:.1e}"],
    ["Edge", "Pressure per rush", f"{res['n']['edge_players']} / {res['n']['edge_snaps']:,}", f"OR {T['edge_pressure']['OR']:.2f} [{T['edge_pressure']['lo']:.2f}, {T['edge_pressure']['hi']:.2f}]", f"{T['edge_pressure']['p']:.2f}"],
    ["OL (T, G, C)", "Pressure allowed per pass block", f"{T['ol_n']['players']} / {T['ol_n']['snaps']:,}", f"OR {T['ol_pressure_allowed']['OR']:.2f} [{T['ol_pressure_allowed']['lo']:.2f}, {T['ol_pressure_allowed']['hi']:.2f}]", f"{T['ol_pressure_allowed']['p']:.2f}"],
    ["WR / TE", "Separation at pass forward (yd), route and coverage adjusted", f"{T['wr_n']['players']} / {T['wr_n']['snaps']:,}", f"{T['wr_sep_all']['b']:+.3f} yd [{T['wr_sep_all']['lo']:+.3f}, {T['wr_sep_all']['hi']:+.3f}]", f"{T['wr_sep_all']['p']:.2f}"],
    ["WR / TE, deep routes", "Separation at pass forward (yd)", f"{T['wr_n']['deep_players']} / {T['wr_n']['deep_snaps']:,}", f"{T['wr_sep_deep']['b']:+.3f} yd [{T['wr_sep_deep']['lo']:+.3f}, {T['wr_sep_deep']['hi']:+.3f}]", f"{T['wr_sep_deep']['p']:.2f}"]],
    columns=["Group", "Outcome", "Players / snaps", "Effect of +0.5 yd/s top speed (95% CI)", "p"])
print(tab.to_string(index=False)); tab.to_csv(f"{WORK}/table1.csv", index=False)

# %% [markdown]
# ### 3.2 Stress tests for the interior DL result

# %%
Rb = {}
Rb["Baseline (all controls)"] = orci(G(f"pres ~ vs + {b}", IL))
Rb["+ defensive team fixed effects"] = orci(G(f"pres ~ vs + {b} + C(team_abbr)", IL))
Rb["+ opposing offense fixed effects"] = orci(G(f"pres ~ vs + {b} + C(possession_team)", IL))
Rb["+ formation and receiver alignment"] = orci(G(f"pres ~ vs + {b} + C(offense_formation) + C(receiver_alignment)", IL.dropna(subset=["offense_formation", "receiver_alignment"])))
Rb["Quick pressure only (<= 2.5 s)"] = orci(G(f"quick ~ vs + {b}", IL)); Rb["Late pressure only (> 2.5 s)"] = orci(G(f"late ~ vs + {b}", IL))
Rb["QB hurry"] = orci(G(f"hurry ~ vs + {b}", IL)); Rb["Sack"] = orci(G(f"sk ~ vs + {b}", IL))
IL["fz"] = -(IL.forty - 4.8) / 0.2          # stopwatch 40, per 0.2 s faster
Rb["Stopwatch 40 instead (per 0.2 s faster)"] = orci(G(f"pres ~ fz + {b}", IL.dropna(subset=["fz"])), "fz")
for s_, dd in IL.groupby("season"): Rb[f"Season {int(s_)} only"] = orci(G(f"pres ~ vs + {b}", dd))
loo = [G(f"pres ~ vs + {b}", IL[IL.nfl_id != i]).params["vs"] for i in (IL.nfl_id.unique()[:15] if FAST else IL.nfl_id.unique())]
res["loo_OR_range"] = [float(np.exp(min(loo))), float(np.exp(max(loo)))]; res["robust"] = Rb
P = IL.groupby("nfl_id").agg(pres=("pres", "mean"), n=("pres", "size"), vs=("vs", "first"), wz=("wz", "first"), pickz=("pickz", "first"), az=("az", "first")).reset_index()
b0 = smf.wls("pres ~ vs + wz + pickz + az", P, weights=P.n).fit().params["vs"]; rng = np.random.default_rng(1); bs = []
for _ in range(300 if FAST else 2000):
    Q = P.copy(); Q["vs"] = rng.permutation(Q.vs.values); bs.append(smf.wls("pres ~ vs + wz + pickz + az", Q, weights=Q.n).fit().params["vs"])
res["perm_p"] = float((np.sum(np.abs(bs) >= abs(b0)) + 1) / (len(bs) + 1))
for k, v in Rb.items(): print(f"{k:44s} OR {v['OR']:.2f} [{v['lo']:.2f}, {v['hi']:.2f}]  p={v['p']:.4f}")
print("drop-one-player OR range", np.round(res["loo_OR_range"], 3), "| permutation p =", res["perm_p"])

# %% [markdown]
# ### 3.3 What part of the 40 matters? Start vs top-end speed

# %%
IL["bz"] = z(IL.burst); IL["tz"] = -z(IL.ten_yd_split.fillna(IL.ten_yd_split.mean()))
g = G(f"pres ~ vs + bz + {b}", IL); res["decomp"] = dict(top=orci(g, "vs"), burst=orci(g, "bz"))
g = G(f"pres ~ fz + tz + {b}", IL.dropna(subset=["fz"])); res["decomp_stopwatch"] = dict(forty=orci(g, "fz"), ten=orci(g, "tz"))
print("tracking top speed OR", round(res["decomp"]["top"]["OR"], 3), "| start-phase burst OR", round(res["decomp"]["burst"]["OR"], 3), "p =", round(res["decomp"]["burst"]["p"], 2))
print("stopwatch 40 OR", round(res["decomp_stopwatch"]["forty"]["OR"], 3), "| stopwatch 10-yd split OR", round(res["decomp_stopwatch"]["ten"]["OR"], 3), "p =", round(res["decomp_stopwatch"]["ten"]["p"], 2))

# %% [markdown]
# ### 3.4 Dose response and the size of the effect

# %%
def dose(dd, grid, B=B_BOOT, seed=0):
    dd = dd.reset_index(drop=True); ids = dd.nfl_id.unique(); pidx = dd.nfl_id.map({i: k for k, i in enumerate(ids)}).values
    rng = np.random.default_rng(seed); out = np.zeros((B, len(grid))); Xs = []
    for v in grid: X = dd.copy(); X["vs"] = (v - 10.0) / 0.5; Xs.append(X)
    for k in range(B):
        w = np.bincount(rng.integers(0, len(ids), len(ids)), minlength=len(ids))[pidx]
        gg = smf.glm(f"pres ~ vs + {b}", dd, family=sm.families.Binomial(), freq_weights=w).fit()
        for j, X in enumerate(Xs): out[k, j] = np.average(gg.predict(X), weights=w)
    gg = smf.glm(f"pres ~ vs + {b}", dd, family=sm.families.Binomial()).fit()
    return [float(gg.predict(X).mean()) for X in Xs], np.percentile(out, 2.5, axis=0).tolist(), np.percentile(out, 97.5, axis=0).tolist()
dose_out = {}
for lab, dd in [("INT", IL), ("EDGE", ED)]:
    Pp = dd.groupby("nfl_id").first(); grid = np.linspace(np.percentile(Pp.vpk, 5), np.percentile(Pp.vpk, 95), 13)
    m, lo, hi = dose(dd, grid); dose_out[lab] = dict(grid=grid.tolist(), mid=m, lo=lo, hi=hi, speeds=Pp.vpk.tolist())
res["dose"] = dose_out
q10, q90 = np.percentile(Pint.vpk, [10, 90]); ids = IL.nfl_id.unique(); pidx = IL.nfl_id.map({i: k for k, i in enumerate(ids)}).values; rng = np.random.default_rng(5); rr = []
X1 = IL.copy(); X1["vs"] = (q90 - 10.0) / 0.5; X0 = IL.copy(); X0["vs"] = (q10 - 10.0) / 0.5
for _ in range(100 if FAST else 300):
    w = np.bincount(rng.integers(0, len(ids), len(ids)), minlength=len(ids))[pidx]
    gg = smf.glm(f"pres ~ vs + {b}", IL, family=sm.families.Binomial(), freq_weights=w).fit(); rr.append((gg.predict(X1) * w).sum() / (gg.predict(X0) * w).sum())
gg = smf.glm(f"pres ~ vs + {b}", IL, family=sm.families.Binomial()).fit()
res["p10_p90"] = dict(v10=float(q10), v90=float(q90), rate10=float(gg.predict(X0).mean()), rate90=float(gg.predict(X1).mean()), ratio=float(gg.predict(X1).mean() / gg.predict(X0).mean()), ratio_lo=float(np.percentile(rr, 2.5)), ratio_hi=float(np.percentile(rr, 97.5)))
fm = c40.dropna(subset=["forty"]); res["forty_poly"] = np.polyfit(fm.vpk, fm.forty, 2).tolist(); res["forty_vs_vpk_r"] = float(fm.vpk.corr(fm.forty))
print(res["p10_p90"])

# %% [markdown]
# ### 3.5 Does Combine speed show up in game movement, and does the drill's first step?

# %%
rs = rush.merge(sp[["game_id", "play_id", "nfl_id", "s_10", "s_20", "smax_pre"]], on=["game_id", "play_id", "nfl_id"], how="left")
pg = rs.groupby("nfl_id").agg(n=("s_10", "count"), s_10=("s_10", "mean"), s_20=("s_20", "mean"), smax_pre=("smax_pre", "mean"), vpk=("vpk", "first"), ipos=("lined_up_position", lambda x: (x == "INTERIOR_LINE").mean())).reset_index()
pg = pg[pg.n >= 50].merge(prd.groupby("nfl_id")[["s05", "s10", "speak", "a_first"]].mean().add_prefix("d_").reset_index(), on="nfl_id", how="left")
def bootr(x, y, B=2000):
    r0 = pearsonr(x, y)[0]; rng = np.random.default_rng(3); n = len(x); rs_ = []
    for _ in range(300 if FAST else B): i = rng.integers(0, n, n); rs_.append(pearsonr(x[i], y[i])[0])
    return [float(r0), float(np.percentile(rs_, 2.5)), float(np.percentile(rs_, 97.5))]
dd_ = pg.dropna(subset=["d_s10"])
res["translate"] = dict(n_game=len(pg), r_vpk_s10=bootr(pg.vpk.values, pg.s_10.values), r_vpk_smax=bootr(pg.vpk.values, pg.smax_pre.values), n_drill=len(dd_),
                        r_drill_s10=bootr(dd_.d_s10.values, dd_.s_10.values), r_drill_s05=bootr(dd_.d_s05.values, dd_.s_10.values), r_drill_speak=bootr(dd_.d_speak.values, dd_.s_10.values))
for nm, msk in (("interior", pg.ipos > 0.5), ("edge", pg.ipos <= 0.5)):
    q = pg[msk]; res["translate"][f"within_{nm}"] = dict(n=len(q), r_vpk_s10=bootr(q.vpk.values, q.s_10.values) if len(q) > 10 else None)
print(json.dumps(res["translate"], indent=1))

# reliability: first two attempts of each player
def rel_pairs(df, cols):
    f = df.sort_values(["nfl_id", "event_id"]); A = f.groupby("nfl_id").nth(0).set_index("nfl_id"); B2 = f.groupby("nfl_id").nth(1).set_index("nfl_id"); ix = A.index.intersection(B2.index)
    return {c: float(A.loc[ix, c].corr(B2.loc[ix, c])) for c in cols}, len(ix)
r40, n40 = rel_pairs(att40, ["vpk", "split10_30", "v10", "v10_frac", "tau"]); rpr, npr = rel_pairs(prd, ["speak", "s10", "s05", "a_first"])
res["reliability"] = {"40 yd: peak speed": r40["vpk"], "40 yd: 10-30 yd split time": r40["split10_30"], "40 yd: speed at 10 yd": r40["v10"], "40 yd: share of top speed reached by 10 yd": r40["v10_frac"], "40 yd: acceleration time constant": r40["tau"],
                      "Pass-rush drill: peak speed": rpr["speak"], "Pass-rush drill: speed at 1.0 s": rpr["s10"], "Pass-rush drill: speed at 0.5 s": rpr["s05"], "Pass-rush drill: first-step acceleration": rpr["a_first"]}
res["reliability_n"] = dict(forty=n40, prd=npr); print(json.dumps(res["reliability"], indent=1))

# %% [markdown]
# ### 3.6 Out-of-time check and the scouting list
# Models are fit on the 2023 and 2024 seasons only, then predict each interior lineman's pressure rate in the 2025 season (including playoffs).

# %%
from sklearn.metrics import log_loss
tr = IL[IL.season <= 2024].copy(); te = IL[IL.season == 2025].copy().reset_index(drop=True)
for c in ["wz", "pickz", "az"]:
    mu, sd = tr[c].mean(), tr[c].std(); tr[c] = (tr[c] - mu) / sd; te[c] = (te[c] - mu) / sd
sets = {"context": ["down3", "ytg"], "draft+size": ["down3", "ytg", "pickz", "wz", "az"], "draft+size+speed": ["down3", "ytg", "pickz", "wz", "az", "vs"]}
pred = {n: LogisticRegression(C=1e6, max_iter=1000).fit(tr[c], tr.pres).predict_proba(te[c])[:, 1] for n, c in sets.items()}
Pt = te.assign(**pred).groupby("nfl_id").agg(y=("pres", "mean"), n=("pres", "size"), **{n: (n, "mean") for n in sets}).reset_index(); Pt = Pt[Pt.n >= 75]
fw = dict(train_snaps=len(tr), train_players=int(tr.nfl_id.nunique()), test_snaps=len(te), test_players=int(te.nfl_id.nunique()), eval_players=len(Pt))
for n in sets: fw["ll_" + n] = float(log_loss(te.pres, pred[n])); fw["rho_" + n] = float(spearmanr(Pt.y, Pt[n])[0]); fw["r_" + n] = float(pearsonr(Pt.y, Pt[n])[0])
ids = te.nfl_id.unique(); rng = np.random.default_rng(11); dll, drho = [], []; grp = {i: np.where(te.nfl_id.values == i)[0] for i in ids}
for _ in range(300 if FAST else 1000):
    ix_ = np.concatenate([grp[i] for i in rng.choice(ids, len(ids))])
    dll.append(log_loss(te.pres.values[ix_], pred["draft+size"][ix_]) - log_loss(te.pres.values[ix_], pred["draft+size+speed"][ix_]))
    tmp = pd.DataFrame({"id": te.nfl_id.values[ix_], "y": te.pres.values[ix_], "a": pred["draft+size"][ix_], "b": pred["draft+size+speed"][ix_]}).groupby("id").agg(y=("y", "mean"), a=("a", "mean"), b=("b", "mean"), n=("y", "size")); tmp = tmp[tmp.n >= 75]
    if len(tmp) > 8: drho.append(spearmanr(tmp.y, tmp.b)[0] - spearmanr(tmp.y, tmp.a)[0])
fw.update(dll_mean=float(np.mean(dll)), dll_ci=[float(np.percentile(dll, 2.5)), float(np.percentile(dll, 97.5))], dll_pos_share=float(np.mean(np.array(dll) > 0)), drho_ci=[float(np.percentile(drho, 2.5)), float(np.percentile(drho, 97.5))], drho_pos_share=float(np.mean(np.array(drho) > 0)))
res["forward"] = fw; print(json.dumps(fw, indent=1))

# scouting map: observed pressure minus what draft slot + size + arm length predict (no speed)
m0 = LogisticRegression(C=1e6, max_iter=1000).fit(IL[["down3", "ytg", "pickz", "wz", "az"]], IL.pres); IL["exp0"] = m0.predict_proba(IL[["down3", "ytg", "pickz", "wz", "az"]])[:, 1]
S = IL.groupby("nfl_id").agg(n=("pres", "size"), obs=("pres", "mean"), exp0=("exp0", "mean"), vpk=("vpk", "first"), w=("combine_weight", "first"), pick=("draft_overall_pick", "first")).reset_index().merge(pl[["nfl_id", "display_name", "draft_year", "draft_round"]], on="nfl_id")
S["diff"] = (S.obs - S.exp0) * 100; S = S[S.n >= 100].sort_values("diff", ascending=False); res["scout_n"] = len(S); res["scout_corr_diff_speed"] = float(S["diff"].corr(S.vpk))
print("top over-performers vs draft-and-size expectation:"); print(S.head(8)[["display_name", "draft_year", "pick", "w", "vpk", "n", "obs", "exp0", "diff"]].round(3).to_string(index=False))
print("\nbiggest under-performers:"); print(S.tail(5)[["display_name", "draft_year", "pick", "w", "vpk", "n", "obs", "exp0", "diff"]].round(3).to_string(index=False))
# %% [markdown]
# ### 3.8 How does speed become pressure? Mediation, and the edge question
# Post-snap speed is partly an outcome (a rusher who is winning keeps running), so we treat these as descriptive. Path a: does Combine speed predict the in-game variable (in SDs, per +0.5 yd/s)? Path b: does that variable predict pressure? The last column shows how much the speed coefficient shrinks when the variable is added.

# %%
sp_ = sp.copy(); mech = {}; geom = {}
for nm, DD in (("interior", IL), ("edge", ED)):
    q = DD.merge(sp_, on=["game_id", "play_id", "nfl_id"], how="left"); geom[nm] = dict(path_eff_20=float(q.path_eff_20.mean()), slip_10=float(q.slip_10.mean()), disp_10=float(q.disp_10.mean()), disp_20=float(q.disp_20.mean()))
def mech_table(D, tag):
    D = D.merge(sp_, on=["game_id", "play_id", "nfl_id"], how="left"); out = {}
    for m in ["player_get_off", "s_10", "s_20", "smax_pre", "disp_10", "disp_20", "path_eff_20", "slip_10"]:
        d = D.dropna(subset=[m]).copy(); d["mz"] = z(d[m])
        a = smf.ols(f"mz ~ vs + {b}", d).fit(cov_type="cluster", cov_kwds={"groups": d["nfl_id"]})
        g1 = G(f"pres ~ vs + {b}", d); g2 = G(f"pres ~ vs + mz + {b}", d)
        out[m] = dict(a=float(a.params["vs"]), a_p=float(a.pvalues["vs"]), b=float(g2.params["mz"]), b_p=float(g2.pvalues["mz"]), vs_before=float(g1.params["vs"]), vs_after=float(g2.params["vs"]), vs_after_p=float(g2.pvalues["vs"]))
    mech[tag] = out
mech_table(IL, "interior"); mech_table(ED, "edge")
print("geometry (first 2 s after snap):", json.dumps(geom))
for tag in ("interior", "edge"):
    print(tag)
    for m, r in mech[tag].items(): print(f"  {m:15s} a={r['a']:+.3f} (p={r['a_p']:.3f})  b={r['b']:+.3f}  speed coef {r['vs_before']:.3f} -> {r['vs_after']:.3f}")
# edge: length and hands, alone and interacting with speed
E2 = ED.merge(c40[["nfl_id", "wing_span", "hand_size"]], on="nfl_id", how="left")
E2["wingz"] = z(E2.wing_span.fillna(E2.wing_span.mean())); E2["handz"] = z(E2.hand_size.fillna(E2.hand_size.mean()))
g_arm = G(f"pres ~ vs*az + wz + pickz + down3 + ytg", E2); g_wing = G(f"pres ~ vs*wingz + wz + pickz + az + down3 + ytg", E2)
mech["edge_length"] = dict(speed_x_arm=orci(g_arm, "vs:az"), speed_x_wing=orci(g_wing, "vs:wingz"), arm_main=orci(G(f"pres ~ vs + {b}", E2), "az"), n_players=int(E2.nfl_id.nunique()))
print("edge speed x arm length:", mech["edge_length"]["speed_x_arm"]); print("edge speed x wingspan:", mech["edge_length"]["speed_x_wing"])
pdl = prd.groupby("nfl_id")[["bend_retention", "smin_turn", "path_eff", "speak"]].mean().reset_index(); Ed = ED.merge(pdl, on="nfl_id").dropna(subset=["bend_retention"]).copy()
if Ed.nfl_id.nunique() >= 15:
    for c_ in ("bend_retention", "path_eff", "smin_turn"):
        Ed["mz_"] = z(Ed[c_]); mech[f"edge_drill_{c_}"] = dict(orci(G(f"pres ~ vs + mz_ + {b}", Ed), "mz_"), n_players=int(Ed.nfl_id.nunique()))
res["mech"] = mech; res["mech_geom"] = geom

# %% [markdown]
# ## Part 5. Closing the gaps
# Five additions, each answering a specific objection a reviewer could raise:
# 1. **Sensor audit.** Are the 2024 Combine traces contaminated by quantization spikes, and does the result survive cleaning?
# 2. **Selection bias.** Only players who reached the field are observed. Inverse-probability-of-selection weights and a Heckman-type control function over all 510 prospects.
# 3. **Expected pressure (xP).** A cross-validated LightGBM on game context, then Pressure Over Expected (POE) and Beta-Binomial (empirical Bayes) player effects.
# 4. **Formal causal mediation** (Imai-Keele-Tingley quasi-Bayesian simulation), and **Benjamini-Hochberg** q-values across every test.
# 5. **A decision matrix** whose thresholds come from the data.
#
# Every block is wrapped so that a failure in one cannot erase the others; errors land in `results.json["_errors"]`.

# %%
from scipy.signal import savgol_filter, medfilt
from scipy.special import expit, logit, betaln, gammaln
from scipy.stats import norm, chi2
from scipy.optimize import minimize
from sklearn.model_selection import StratifiedKFold, cross_val_predict, GroupKFold
from sklearn.metrics import roc_auc_score
GY = 9.80665 * 1.0936133                      # 1 g in yd/s^2 (tracking is in yards)
ERR = res.setdefault("_errors", {}); KEYS = ["game_id", "play_id", "nfl_id"]
IL5 = IL.copy().reset_index(drop=True); ED5 = ED.copy().reset_index(drop=True)
GEOMC = [c for c in ["s_10", "s_20", "disp_20", "path_eff_20", "adx_10", "ady_10", "adx_20", "ady_20", "x0", "y0"] if c in sp.columns]
IL5 = IL5.merge(sp[KEYS + GEOMC], on=KEYS, how="left"); ED5 = ED5.merge(sp[KEYS + GEOMC], on=KEYS, how="left")
dy_map = c40.set_index("nfl_id").draft_year
IL5["dy"] = IL5.nfl_id.map(dy_map); ED5["dy"] = ED5.nfl_id.map(dy_map)
def fail(tag, e): ERR[tag] = repr(e)[:400]; log("ERROR", tag, repr(e)[:300])
def sim_p(x): x = np.asarray(x); return float(min(1.0, 2 * min((x > 0).mean(), (x < 0).mean()) + 1.0 / len(x)))

# %% [markdown]
# ### 5.1 Sensor audit of the Combine 10 Hz traces
# Instantaneous acceleration above 3.5 g is not humanly possible for a linemen sprinting from a standing start, so any frame above it is a measurement artifact. We count those frames by Combine class, rebuild top speed after (a) a Savitzky-Golay position-derivative filter (5 frames, quadratic) and (b) a 2.5 g acceleration limiter (3-frame median, then forward-backward slew limit), and refit the main model.

# %%
def slew(s, dt, amax):
    f = s.copy(); bk = s.copy(); lim = amax * dt
    for i in range(1, len(f)): f[i] = min(max(f[i], f[i - 1] - lim), f[i - 1] + lim)
    for i in range(len(bk) - 2, -1, -1): bk[i] = min(max(bk[i], bk[i + 1] - lim), bk[i + 1] + lim)
    return 0.5 * (f + bk)
try:
    arows = []
    for (pid, eid), g in ct[ct.drill_name == "FORTY_YARD_DASH"].groupby(["nfl_id", "event_id"], sort=False):
        g = g.sort_values("t"); ts = (g.t - g.t.iloc[0]).dt.total_seconds().values
        if len(g) < 40 or np.any(np.diff(ts) <= 0): continue
        s = g.s.values.astype(float); a = g.a.values.astype(float); gx = g.x.values.astype(float); gyv = g.y.values.astype(float); d = gx - gx[0]
        if d[-1] < 35: continue
        k = np.argmax(d >= 0.25); t = ts - ts[k]; x = d - d[k]; idx = np.where(t >= -0.3)[0]
        if x[idx].max() < 30: continue
        sl = idx[:np.argmax(x[idx] >= 30) + 1]; dt = float(np.median(np.diff(ts)))
        fd = np.r_[0.0, np.diff(s) / np.diff(ts)]
        s_sg = np.hypot(savgol_filter(gx, 5, 2, deriv=1, delta=dt), savgol_filter(gyv, 5, 2, deriv=1, delta=dt))
        s_lp = slew(medfilt(s, 3), dt, 2.5 * GY); fd_lp = np.r_[0.0, np.diff(s_lp) / np.diff(ts)]
        arows.append(dict(nfl_id=pid, event_id=eid, year=int(g.draft_year.iloc[0]), vpk=float(s[sl].max()), vpk_sg=float(s_sg[sl].max()), vpk_lp=float(s_lp[sl].max()),
                          any_rep=bool((np.abs(a[sl]) > 3.5 * GY).any()), frac_rep=float((np.abs(a[sl]) > 3.5 * GY).mean()),
                          any_fd=bool((np.abs(fd[sl]) > 3.5 * GY).any()), frac_fd=float((np.abs(fd[sl]) > 3.5 * GY).mean()),
                          any_lp=bool((np.abs(fd_lp[sl]) > 3.5 * GY).any()), amax_rep=float(np.abs(a[sl]).max() / GY)))
    AUD = pd.DataFrame(arows)
    ay = AUD.groupby("year").agg(attempts=("vpk", "size"), players=("nfl_id", "nunique"), pct_attempts_spike=("any_rep", "mean"), pct_frames_spike=("frac_rep", "mean"), pct_attempts_spike_fd=("any_fd", "mean"),
                                 pct_attempts_spike_after=("any_lp", "mean"), median_peak_g=("amax_rep", "median"), vpk_raw=("vpk", "mean"), vpk_sg=("vpk_sg", "mean"), vpk_lp=("vpk_lp", "mean")).reset_index()
    print(ay.round(3).to_string(index=False))
    pm = AUD.groupby("nfl_id")[["vpk", "vpk_sg", "vpk_lp"]].mean().rename(columns={"vpk": "vpk_raw5", "vpk_sg": "vpk_sg5", "vpk_lp": "vpk_lp5"}).reset_index()
    res["audit"] = dict(by_year=ay.to_dict("records"), n_attempts=len(AUD), r_raw_sg=float(AUD.vpk.corr(AUD.vpk_sg)), r_raw_lp=float(AUD.vpk.corr(AUD.vpk_lp)),
                        mean_shift_sg=float((AUD.vpk_sg - AUD.vpk).mean()), mean_shift_lp=float((AUD.vpk_lp - AUD.vpk).mean()))
    for IX in (IL5, ED5):
        pass
    IL5 = IL5.merge(pm, on="nfl_id", how="left"); ED5 = ED5.merge(pm, on="nfl_id", how="left")
    for alt in ("sg5", "lp5"):
        IL5[f"vs_{alt}"] = (IL5[f"vpk_{alt}"] - 10.0) / 0.5; ED5[f"vs_{alt}"] = (ED5[f"vpk_{alt}"] - 10.0) / 0.5
    Rb["Sensor-cleaned: Savitzky-Golay filter"] = orci(G(f"pres ~ vs_sg5 + {b}", IL5.dropna(subset=["vs_sg5"])), "vs_sg5")
    Rb["Sensor-cleaned: 2.5 g limiter"] = orci(G(f"pres ~ vs_lp5 + {b}", IL5.dropna(subset=["vs_lp5"])), "vs_lp5")
    Rb["Drop the 2024 Combine class"] = orci(G(f"pres ~ vs + {b}", IL5[IL5.dy != 2024]))
    res["audit"]["edge_sg"] = orci(G(f"pres ~ vs_sg5 + {b}", ED5.dropna(subset=["vs_sg5"])), "vs_sg5")
    res["audit"]["or_2024_only"] = orci(G(f"pres ~ vs + {b}", IL5[IL5.dy == 2024])) if IL5[IL5.dy == 2024].nfl_id.nunique() >= 10 else None
    res["audit"]["n_players_2024_int"] = int(IL5[IL5.dy == 2024].nfl_id.nunique())
    print({k: round(v["OR"], 3) for k, v in Rb.items() if k.startswith("Sensor") or k.startswith("Drop the 2024")})
except Exception as e: fail("5.1_audit", e)

# %% [markdown]
# ### 5.2 Selection bias: who gets observed?
# Our estimation sample is the set of prospects who actually rushed the passer in the NFL. Players who never got on the field, or got on it briefly, are invisible. We model the probability of being observed for **all 510 prospects** from Combine measurables, draft slot, position and draft class (cross-fitted, 5 folds), then (a) reweight the interior sample by the inverse of that probability and (b) add the inverse Mills ratio from a probit selection equation, using draft class (length of the observation window) as the excluded variable.

# %%
try:
    U = pl.drop(columns=["draft_year"]).merge(cr, on="nfl_id", how="left"); U["logpick"] = np.log(U.draft_overall_pick.fillna(260))
    U["n_rush"] = U.nfl_id.map(rush.groupby("nfl_id").size()).fillna(0); U["S_any_snap"] = U.nfl_id.isin(pp.nfl_id.unique()).astype(int)
    U["S_rush"] = (U.n_rush >= 1).astype(int); U["S_100"] = (U.n_rush >= 100).astype(int)
    drills = ["forty", "ten_yd_split", "vertical", "broad_jump", "three_cone", "short_shuttle", "bench_reps"]
    feats = ["logpick", "combine_height", "combine_weight", "arm_length", "hand_size", "wing_span"] + drills
    posm = U.combine_position.fillna("NA"); X = U[feats].copy()
    for c in drills: X[c + "_miss"] = X[c].isna().astype(int)
    for c in feats: X[c] = X[c].fillna(X[c].groupby(posm).transform("median")).fillna(X[c].median())
    X = pd.concat([X, pd.get_dummies(posm, prefix="pos", dtype=int)], axis=1); X["draft_class"] = U.draft_year.astype(float)
    Xs = ((X - X.mean()) / X.std().replace(0, 1)).fillna(0.0)
    sel = {"universe": int(len(U)), "share_any_snap": float(U.S_any_snap.mean()), "share_rush": float(U.S_rush.mean()), "share_100": float(U.S_100.mean())}
    IL5 = IL5.merge(U[["nfl_id", "n_rush"]], on="nfl_id", how="left"); ED5 = ED5.merge(U[["nfl_id", "n_rush"]], on="nfl_id", how="left")
    def selfit(col):
        y = U[col].values; out = {}
        if min(y.sum(), len(y) - y.sum()) < 8: return None
        lr = LogisticRegression(C=0.5, max_iter=3000)
        ph = cross_val_predict(lr, Xs, y, cv=StratifiedKFold(5, shuffle=True, random_state=0), method="predict_proba")[:, 1]
        lr.fit(Xs, y); xb = lr.decision_function(Xs)
        try:
            pr = sm.Probit(y, sm.add_constant(Xs.drop(columns=[c for c in Xs.columns if Xs[c].std() == 0]))).fit(disp=0, maxiter=300, method="bfgs")
            xbp = pr.fittedvalues.values if hasattr(pr.fittedvalues, "values") else np.asarray(pr.fittedvalues); how = "probit"
        except Exception: xbp = xb / 1.702; how = "logit/1.702"
        return dict(auc=float(roc_auc_score(y, ph)), p=np.clip(ph, 0.02, 0.98), imr=norm.pdf(xbp) / np.clip(norm.cdf(xbp), 1e-3, None), how=how)
    for col, lab in (("S_rush", "any rush snap"), ("S_100", "100+ rush snaps")):
        sf = selfit(col)
        if sf is None: sel[col] = "too few unselected players to model"; continue
        U[f"p_{col}"] = sf["p"]; U[f"imr_{col}"] = sf["imr"]; s = U[col].values; w = np.where(s == 1, s.mean() / sf["p"], np.nan)
        lo_, hi_ = np.nanpercentile(w, [1, 99]); U[f"w_{col}"] = np.clip(w, lo_, hi_)
        sel[col] = dict(auc=sf["auc"], mills=sf["how"], n_selected=int(s.sum()), w_min=float(np.nanmin(U[f"w_{col}"])), w_max=float(np.nanmax(U[f"w_{col}"])))
        D5 = IL5.merge(U[["nfl_id", f"w_{col}", f"imr_{col}"]], on="nfl_id", how="left"); D5 = D5[D5[f"w_{col}"].notna()].reset_index(drop=True)
        if col == "S_100": D5 = D5[D5.n_rush >= 100].reset_index(drop=True)
        if D5.nfl_id.nunique() < 15: continue
        gw = smf.gee(f"pres ~ vs + {b}", groups="nfl_id", data=D5, family=sm.families.Binomial(), weights=D5[f"w_{col}"].values).fit()
        Rb[f"IPW selection weights ({lab})"] = orci(gw)
        gh = G(f"pres ~ vs + {b} + imr_{col}", D5); Rb[f"Heckman-type control function ({lab})"] = orci(gh)
        gu = G(f"pres ~ vs + {b}", D5); sel[col]["unweighted_same_sample"] = orci(gu); sel[col]["n_players_int"] = int(D5.nfl_id.nunique()); sel[col]["imr_coef_p"] = float(gh.pvalues[f"imr_{col}"])
    res["selection"] = sel; print(json.dumps(sel, indent=1, default=float))
except Exception as e: fail("5.2_selection", e)

# %% [markdown]
# ### 5.3 Context model: LightGBM expected pressure (xP), POE and empirical-Bayes player effects
# The xP model sees **only game context and alignment, never the player's identity or Combine numbers**. Features: down, distance, quarter, clock, score differential (defense minus offense), time to throw (`dropback_duration`, play level), defensive win probability, expected points, formation and receiver alignment, line-up group, distance to the sideline, and the distance to the nearest tracked offensive lineman at the snap (double-team proxy; defined only when that blocker is a tracked prospect, otherwise missing). Out-of-fold predictions use **5-fold cross-validation grouped by rusher**, so a player's own snaps never train the model that scores him.

# %%
try:
    import lightgbm as lgb
    games = pd.read_csv(f"{IN}/games.csv")[["game_id", "home_team_abbr"]]
    R = rush.merge(games, on="game_id", how="left").merge(sp[KEYS + ["x0", "y0"]], on=KEYS, how="left")
    hs, vs_ = R.pre_snap_home_score, R.pre_snap_visitor_score; home = R.team_abbr == R.home_team_abbr
    R["score_diff"] = np.where(home, hs - vs_, vs_ - hs); R["wp_def"] = np.where(home, R.pre_snap_home_team_win_probability, R.pre_snap_visitor_team_win_probability)
    R["clock"] = R.game_clock.astype(str).str.split(":").apply(lambda p: int(p[0]) * 60 + int(p[1]) if len(p) == 2 else np.nan)
    R["dbd"] = R.groupby(["game_id", "play_id"]).dropback_duration.transform("max"); R["ysl"] = np.minimum(R.y0, 53.3 - R.y0)
    sx = sp[KEYS + ["x0", "y0"]].merge(pp[KEYS + ["lined_up_position", "team_abbr"]], on=KEYS, how="inner")
    olp = sx[sx.lined_up_position.isin(["T", "G", "C"])][["game_id", "play_id", "team_abbr", "x0", "y0"]].rename(columns={"team_abbr": "ol_team", "x0": "ox", "y0": "oy"})
    mm_ = R[KEYS + ["team_abbr", "x0", "y0"]].merge(olp, on=["game_id", "play_id"]); mm_ = mm_[mm_.ol_team != mm_.team_abbr]
    mm_["d"] = np.hypot(mm_.x0 - mm_.ox, mm_.y0 - mm_.oy); mm_["n2"] = (mm_.d <= 2.0).astype(int)
    nn_ = mm_.groupby(KEYS).agg(ol_d1=("d", "min"), ol_n2=("n2", "sum")).reset_index(); R = R.merge(nn_, on=KEYS, how="left")
    print("rush snaps", len(R), "| with a tracked opposing OL at snap:", round(R.ol_d1.notna().mean(), 3))
    cats = ["offense_formation", "receiver_alignment", "lined_up_position"]
    for c in cats: R[c] = R[c].astype("category")
    num = ["down", "yards_to_go", "quarter", "clock", "score_diff", "wp_def", "expected_points", "yardline_number", "ysl", "ol_d1", "ol_n2"]
    FULL = num + ["dbd"] + cats; NODB = num + cats
    prm = dict(n_estimators=350, learning_rate=0.03, num_leaves=15, min_child_samples=120, subsample=0.8, subsample_freq=1, colsample_bytree=0.8, reg_lambda=5.0, objective="binary", verbose=-1, random_state=0, n_jobs=-1)
    def oof(cols, grp):
        p = np.zeros(len(R))
        for a_, b_ in GroupKFold(5).split(R, R.pres, grp):
            m = lgb.LGBMClassifier(**prm).fit(R.iloc[a_][cols], R.pres.iloc[a_]); p[b_] = m.predict_proba(R.iloc[b_][cols])[:, 1]
        return p
    R["xp"] = oof(FULL, R.nfl_id); R["xp_nodb"] = oof(NODB, R.nfl_id); xp_game = oof(FULL, R.game_id)
    base = R.pres.mean(); ll0 = log_loss(R.pres, np.full(len(R), base))
    mf = lgb.LGBMClassifier(**prm).fit(R[FULL], R.pres); imp = dict(sorted(zip(FULL, mf.booster_.feature_importance("gain") / mf.booster_.feature_importance("gain").sum()), key=lambda kv: -kv[1]))
    dec = pd.qcut(R.xp, 10, duplicates="drop"); cal = R.groupby(dec).agg(pred=("xp", "mean"), obs=("pres", "mean"))
    res["xp"] = dict(n=len(R), base_rate=float(base), auc_player_cv=float(roc_auc_score(R.pres, R.xp)), auc_game_cv=float(roc_auc_score(R.pres, xp_game)), auc_no_dropback=float(roc_auc_score(R.pres, R.xp_nodb)),
                     logloss_null=float(ll0), logloss_model=float(log_loss(R.pres, R.xp)), logloss_gain_pct=float(100 * (ll0 - log_loss(R.pres, R.xp)) / ll0), calib_max_gap=float((cal.pred - cal.obs).abs().max()),
                     opp_ol_known_share=float(R.ol_d1.notna().mean()), importance={k: float(v) for k, v in list(imp.items())[:8]})
    print(json.dumps(res["xp"], indent=1, default=float))
    XP = R[KEYS + ["xp", "xp_nodb", "ol_d1", "ol_n2", "dbd"]]
    for nm in ("IL5", "ED5"):
        D = globals()[nm].merge(XP, on=KEYS, how="left").reset_index(drop=True); D["poe"] = D.pres - D.xp; D["lxp"] = logit(D.xp.clip(1e-4, 1 - 1e-4)); D["lxp_nd"] = logit(D.xp_nodb.clip(1e-4, 1 - 1e-4)); globals()[nm] = D
    poe = {}
    for nm, D in (("interior", IL5), ("edge", ED5)):
        go = smf.gee("pres ~ vs + wz + pickz + az", groups="nfl_id", data=D, family=sm.families.Binomial(), offset=D.lxp.values).fit()
        go_nd = smf.gee("pres ~ vs + wz + pickz + az", groups="nfl_id", data=D, family=sm.families.Binomial(), offset=D.lxp_nd.values).fit()
        gl = G("poe ~ vs + wz + pickz + az", D, sm.families.Gaussian()); gl0 = G("poe ~ vs", D, sm.families.Gaussian())
        poe[nm] = dict(or_offset=orci(go), or_offset_no_dropback=orci(go_nd), poe_pp_per_unit=dict(b=float(gl.params["vs"] * 100), lo=float((gl.params["vs"] - 1.96 * gl.bse["vs"]) * 100), hi=float((gl.params["vs"] + 1.96 * gl.bse["vs"]) * 100), p=float(gl.pvalues["vs"])),
                       poe_pp_no_controls=dict(b=float(gl0.params["vs"] * 100), p=float(gl0.pvalues["vs"])))
    res["poe"] = poe; Rb["LightGBM context-adjusted (xP offset)"] = poe["interior"]["or_offset"]; Rb["xP offset without time-to-throw"] = poe["interior"]["or_offset_no_dropback"]
    print(json.dumps(poe, indent=1, default=float))
except Exception as e: fail("5.3_xp", e)

# %%
# Beta-Binomial empirical Bayes: each player's latent pressure probability ~ Beta with mean = context-expected rate (xP), shifted by speed and size in the prior mean.
def bb_nll(th, P, fix_delta):
    kap = np.exp(th[0]); delta = 0.0 if fix_delta else th[1]
    lm = logit(P.mu.clip(1e-4, 1 - 1e-4)) + th[5] + delta * P.vs + th[2] * P.wz + th[3] * P.pickz + th[4] * P.az
    mu = expit(lm); a_ = mu * kap; b_ = (1 - mu) * kap
    return -(gammaln(P.n + 1) - gammaln(P.k + 1) - gammaln(P.n - P.k + 1) + betaln(P.k + a_, P.n - P.k + b_) - betaln(a_, b_)).sum()
def bb_fit(P, fix_delta=False, x0=None):
    x0 = np.array([np.log(300.0), 0, 0, 0, 0, 0.0]) if x0 is None else x0
    f = lambda th: bb_nll(th, P, fix_delta)
    r = minimize(f, x0, method="L-BFGS-B", bounds=[(np.log(5), np.log(1e5))] + [(-3, 3)] * 5); return r
try:
    eb = {}
    for nm, D in (("interior", IL5), ("edge", ED5)):
        P = D.groupby("nfl_id").agg(k=("pres", "sum"), n=("pres", "size"), mu=("xp", "mean"), vs=("vs", "first"), wz=("wz", "first"), pickz=("pickz", "first"), az=("az", "first"), vpk=("vpk", "first"), w=("combine_weight", "first")).reset_index()
        P = P.merge(pl[["nfl_id", "display_name"]], on="nfl_id", how="left")
        rf = bb_fit(P); r0 = bb_fit(P, True, rf.x); LR = max(0.0, 2 * (r0.fun - rf.fun)); kap = float(np.exp(rf.x[0])); delta = float(rf.x[1])
        rng = np.random.default_rng(21); bd = []
        for _ in range(40 if FAST else 250):
            Q = P.iloc[rng.integers(0, len(P), len(P))].reset_index(drop=True)
            try: bd.append(bb_fit(Q, False, rf.x).x[1])
            except Exception: pass
        th = rf.x; lm = logit(P.mu.clip(1e-4, 1 - 1e-4)) + th[5] + th[1] * P.vs + th[2] * P.wz + th[3] * P.pickz + th[4] * P.az; mus = expit(lm)
        P["post"] = (P.k + mus * kap) / (P.n + kap); P["poe_raw"] = P.k / P.n - P.mu; P["poe_shrunk"] = P.post - P.mu
        wl = lambda f_: smf.wls(f_, P, weights=P.n).fit()
        r2_full = wl("poe_raw ~ vs + wz + pickz + az").rsquared; r2_ctrl = wl("poe_raw ~ wz + pickz + az").rsquared; r2_speed = wl("poe_raw ~ vs").rsquared     # raw POE: the shrunk one already contains speed in its prior mean
        eb[nm] = dict(players=len(P), kappa=kap, icc=float(1 / (kap + 1)), delta_logit_per_unit=delta, OR=float(np.exp(delta)), OR_lo=float(np.exp(np.percentile(bd, 2.5))), OR_hi=float(np.exp(np.percentile(bd, 97.5))), lr=float(LR), lr_p=float(chi2.sf(LR, 1)),
                      r2_speed_alone=float(r2_speed), r2_controls=float(r2_ctrl), r2_full=float(r2_full), partial_r2_speed=float((r2_full - r2_ctrl) / max(1e-9, 1 - r2_ctrl)), sd_raw_poe_pp=float(P.poe_raw.std() * 100), sd_shrunk_poe_pp=float(P.poe_shrunk.std() * 100),
                      top=P[P.n >= 100].nlargest(5, "poe_shrunk")[["display_name", "n", "vpk", "poe_shrunk"]].to_dict("records"), bottom=P[P.n >= 100].nsmallest(3, "poe_shrunk")[["display_name", "n", "vpk", "poe_shrunk"]].to_dict("records"))
        if nm == "interior": PEBI = P.copy()
        print(nm, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in eb[nm].items() if k not in ("top", "bottom")})
    res["eb"] = eb
except Exception as e: fail("5.3_eb", e)

# %% [markdown]
# ### 5.4 Formal causal mediation (Imai-Keele-Tingley)
# Treatment: +0.5 yd/s of Combine top speed, from the sample mean. Mediator model: linear, cluster-robust covariance. Outcome model: logit on pressure with the mediator, same controls. We draw 1,000 parameter sets from the (cluster-robust) sampling distributions, simulate the potential mediator under each treatment level, and compute the average causal mediation effect (ACME), average direct effect (ADE) and total effect on the risk-difference scale (percentage points of pressure per rush). **Sequential ignorability is an assumption, not something the data can prove**: the mediator and outcome are both measured in the same snap, and anything that makes a rusher both quick off the ball and likely to get home (a bad block, a tipped call) confounds the mediator-outcome link. We report these as the indirect effect that would hold if that assumption were true.

# %%
def ikt(D, m, B=1000, seed=0):
    d = D.dropna(subset=[m]).copy().reset_index(drop=True); d["mz"] = z(d[m])
    fm = smf.ols(f"mz ~ vs + {b}", d).fit(cov_type="cluster", cov_kwds={"groups": d["nfl_id"]})
    fy = smf.glm(f"pres ~ vs + mz + {b}", d, family=sm.families.Binomial()).fit(cov_type="cluster", cov_kwds={"groups": d["nfl_id"]})
    XM, XY = fm.model.exog.copy(), fy.model.exog.copy(); iM = fm.model.exog_names.index("vs"); iv, im = fy.model.exog_names.index("vs"), fy.model.exog_names.index("mz")
    t0 = float(d.vs.mean()) - 0.5; t1 = t0 + 1.0; XM0, XM1 = XM.copy(), XM.copy(); XM0[:, iM] = t0; XM1[:, iM] = t1
    rng = np.random.default_rng(seed); n = len(d); out = {k: [] for k in ("acme", "ade", "tot", "prop")}
    bm_all = rng.multivariate_normal(fm.params.values, fm.cov_params().values, B); gy_all = rng.multivariate_normal(fy.params.values, fy.cov_params().values, B)
    for j in range(B):
        bm, gy_ = bm_all[j], gy_all[j]; s2 = fm.scale * fm.df_resid / rng.chisquare(fm.df_resid); sd = np.sqrt(s2)
        M0 = XM0 @ bm + sd * rng.standard_normal(n); M1 = XM1 @ bm + sd * rng.standard_normal(n)
        rest = XY @ gy_ - XY[:, iv] * gy_[iv] - XY[:, im] * gy_[im]
        Y = lambda t, M: expit(rest + gy_[iv] * t + gy_[im] * M).mean()
        acme = 0.5 * ((Y(t1, M1) - Y(t1, M0)) + (Y(t0, M1) - Y(t0, M0))); ade = 0.5 * ((Y(t1, M1) - Y(t0, M1)) + (Y(t1, M0) - Y(t0, M0))); tot = Y(t1, M1) - Y(t0, M0)
        out["acme"].append(acme * 100); out["ade"].append(ade * 100); out["tot"].append(tot * 100); out["prop"].append(acme / tot if abs(tot) > 1e-6 else np.nan)
    f = lambda v: dict(est=float(np.nanmedian(v)), lo=float(np.nanpercentile(v, 2.5)), hi=float(np.nanpercentile(v, 97.5)), p=sim_p(np.array(v)[np.isfinite(v)]))
    r = {k: f(v) for k, v in out.items()}; r["a_coef_sd_per_unit"] = float(fm.params["vs"]); r["b_coef_logit_per_sd"] = float(fy.params["mz"]); r["n_snaps"] = int(n); r["n_players"] = int(d.nfl_id.nunique())
    return r
try:
    NB = 200 if FAST else 1000; med = {"interior": {}, "edge": {}}
    for nm, D, ms in (("interior", IL5, ["player_get_off", "s_10", "path_eff_20", "adx_20", "ady_20"]), ("edge", ED5, ["path_eff_20", "ady_20", "adx_20", "disp_20", "player_get_off", "s_10"])):
        for m in ms:
            if m in D.columns and D[m].notna().sum() > 500:
                try: med[nm][m] = ikt(D, m, NB)
                except Exception as e: med[nm][m] = {"error": repr(e)[:200]}
    res["mediation"] = med
    for nm in med:
        for m, r in med[nm].items():
            if "acme" in r: print(f"{nm:8s} {m:14s} ACME {r['acme']['est']:+.3f} pp [{r['acme']['lo']:+.3f}, {r['acme']['hi']:+.3f}]  ADE {r['ade']['est']:+.3f} [{r['ade']['lo']:+.3f}, {r['ade']['hi']:+.3f}]  total {r['tot']['est']:+.3f}  prop {r['prop']['est']:.2f}")
except Exception as e: fail("5.4_mediation", e)

# %% [markdown]
# ### 5.5 Multiple testing: Benjamini-Hochberg q-values
# Tests are grouped by what they ask. **H**: distinct group-level hypotheses (Table 1, decomposition, POE, empirical Bayes). **M**: mechanism paths (a, b, direct and indirect effects). **R**: robustness re-tests of one hypothesis (they are not independent, so they are reported for completeness, not as separate discoveries). BH is applied within each family and across all tests.

# %%
def bh(p):
    p = np.asarray(p, float); n = len(p); o = np.argsort(p); r = p[o] * n / np.arange(1, n + 1); r = np.minimum.accumulate(r[::-1])[::-1]; q = np.empty(n); q[o] = np.minimum(r, 1.0); return q
try:
    PV = []
    def addp(lab, p, fam):
        if p is not None and np.isfinite(p): PV.append((lab, float(p), fam))
    for k, v in res["table1"].items():
        if isinstance(v, dict) and "p" in v: addp(f"Table 1: {k}", v["p"], "H")
    addp("Decomposition: top speed", res["decomp"]["top"]["p"], "H"); addp("Decomposition: start-phase burst", res["decomp"]["burst"]["p"], "H")
    addp("Stopwatch 40", res["decomp_stopwatch"]["forty"]["p"], "H"); addp("Stopwatch 10-yd split", res["decomp_stopwatch"]["ten"]["p"], "H")
    for nm in ("interior", "edge"):
        if "poe" in res: addp(f"POE (xP offset), {nm}", res["poe"][nm]["or_offset"]["p"], "H"); addp(f"POE linear, {nm}", res["poe"][nm]["poe_pp_per_unit"]["p"], "H")
        if "eb" in res: addp(f"Beta-Binomial speed effect, {nm}", res["eb"][nm]["lr_p"], "H")
    for tag in ("interior", "edge"):
        for m, r in res["mech"][tag].items():
            addp(f"{tag}: speed -> {m} (path a)", r["a_p"], "M"); addp(f"{tag}: {m} -> pressure (path b)", r["b_p"], "M"); addp(f"{tag}: direct speed effect given {m}", r["vs_after_p"], "M")
    for k, v in res["mech"].items():
        if k.startswith("edge_drill") and "p" in v: addp(f"edge: {k}", v["p"], "M")
    el = res["mech"].get("edge_length", {})
    for k in ("speed_x_arm", "speed_x_wing", "arm_main"):
        if k in el: addp(f"edge: {k}", el[k]["p"], "M")
    for nm in res.get("mediation", {}):
        for m, r in res["mediation"][nm].items():
            if "acme" in r: addp(f"{nm}: ACME via {m}", r["acme"]["p"], "M"); addp(f"{nm}: ADE given {m}", r["ade"]["p"], "M")
    for k, v in Rb.items(): addp(f"Robustness: {k}", v["p"], "R")
    F = pd.DataFrame(PV, columns=["test", "p", "family"]); F["q_family"] = F.groupby("family").p.transform(lambda s: pd.Series(bh(s.values), index=s.index)); F["q_all"] = bh(F.p.values)
    res["fdr"] = dict(n_tests=int(len(F)), by_family={k: int(v) for k, v in F.family.value_counts().items()}, n_q05_all=int((F.q_all < 0.05).sum()), n_q05_family=int((F.q_family < 0.05).sum()), table=F.round(5).to_dict("records"))
    print(F.sort_values("q_all").head(25).round(4).to_string(index=False)); print("tests:", len(F), "| q<0.05 overall:", res["fdr"]["n_q05_all"])
except Exception as e: fail("5.5_fdr", e)

# %% [markdown]
# ### 5.6 Draft and deployment decision matrix: the numbers behind it
# **Interior.** For each candidate cut-off on the Combine 10 to 30 yd split (from the 10 Hz trace), we compare the pressure rate of prospects at or below the cut-off with what game context alone predicts (POE, percentage points per 100 rushes), with a player-cluster bootstrap. **Edge.** We cross top speed with Combine pass-rush-drill path efficiency (net distance over distance run) and read POE in each cell. Line-up depth (3-tech, wide-9) is not in the data; the closest proxy is the distance to the nearest tracked blocker, used as an exploratory split.

# %%
def poe_boot(P, masks, B=1000, seed=0):
    rng = np.random.default_rng(seed); N = len(P); kk = P.k.values.astype(float); nn = P.n.values.astype(float); ex = (P.mu.values * nn); out = []
    idx = rng.integers(0, N, (B, N))
    def est(m, I):
        mm = m[I]; num = ((kk[I] - ex[I]) * mm).sum(1); den = (nn[I] * mm).sum(1); return np.where(den > 0, num / np.maximum(den, 1) * 100, np.nan)
    pt = lambda m: float(((kk - ex) * m).sum() / max(1.0, (nn * m).sum()) * 100)
    return idx, est, pt
try:
    mat = {}
    Pl = IL5.groupby("nfl_id").agg(k=("pres", "sum"), n=("pres", "size"), mu=("xp", "mean"), vpk=("vpk", "first"), w=("combine_weight", "first")).reset_index().merge(c40[["nfl_id", "s1030"]], on="nfl_id").dropna(subset=["s1030"]).reset_index(drop=True)
    idx, est, pt = poe_boot(Pl, None, 1000 if not FAST else 200)
    qs = np.percentile(Pl.s1030, [15, 25, 33, 50, 67, 75, 85]); cuts = sorted(set(np.round(qs, 2))); rows = []
    for c in cuts:
        fast = (Pl.s1030.values <= c).astype(float); slow = 1 - fast; ef, es = est(fast, idx), est(slow, idx); dif = ef - es
        rows.append(dict(cut=float(c), n_fast=int(fast.sum()), n_slow=int(slow.sum()), poe_fast=pt(fast), fast_lo=float(np.nanpercentile(ef, 2.5)), fast_hi=float(np.nanpercentile(ef, 97.5)), poe_slow=pt(slow), slow_lo=float(np.nanpercentile(es, 2.5)), slow_hi=float(np.nanpercentile(es, 97.5)),
                         diff=pt(fast) - pt(slow), diff_lo=float(np.nanpercentile(dif, 2.5)), diff_hi=float(np.nanpercentile(dif, 97.5)), vpk_fast=float(Pl.vpk[Pl.s1030 <= c].mean()), w_fast=float(Pl.w[Pl.s1030 <= c].mean())))
    mat["interior_cuts"] = rows; ok = [r for r in rows if r["fast_lo"] > 0]; bad = [r for r in rows if r["slow_hi"] < 0]
    mat["interior_green_cut"] = max(r["cut"] for r in ok) if ok else None; mat["interior_red_cut"] = min(r["cut"] for r in bad) if bad else None
    wq = np.percentile(Pl.w, [33, 67]); bands = {"light (3-tech-type)": Pl.w <= wq[0], "mid": (Pl.w > wq[0]) & (Pl.w <= wq[1]), "heavy (nose-type)": Pl.w > wq[1]}; mat["weight_cut_lb"] = [float(x) for x in wq]; mat["weight_bands"] = {}
    for bn, bm in bands.items():
        S_ = Pl[bm.values].reset_index(drop=True)
        if len(S_) < 12: continue
        c = float(S_.s1030.median()); i2, e2, p2 = poe_boot(S_, None, 1000 if not FAST else 200); fm_ = (S_.s1030.values <= c).astype(float); sm_ = 1 - fm_; d_ = e2(fm_, i2) - e2(sm_, i2)
        mat["weight_bands"][bn] = dict(n=int(len(S_)), median_split=c, poe_fast=p2(fm_), poe_slow=p2(sm_), diff=p2(fm_) - p2(sm_), lo=float(np.nanpercentile(d_, 2.5)), hi=float(np.nanpercentile(d_, 97.5)), w_range=[float(S_.w.min()), float(S_.w.max())])
    print(json.dumps({k: v for k, v in mat.items() if k != "interior_cuts"}, indent=1, default=float)); print(pd.DataFrame(rows).round(2).to_string(index=False))
    # edge: speed x drill path efficiency
    pdl2 = prd.groupby("nfl_id")[["path_eff", "bend_retention"]].mean().reset_index()
    Pe = ED5.groupby("nfl_id").agg(k=("pres", "sum"), n=("pres", "size"), mu=("xp", "mean"), vpk=("vpk", "first")).reset_index().merge(pdl2, on="nfl_id").dropna(subset=["path_eff"]).reset_index(drop=True)
    cv_, cp_ = Pe.vpk.median(), Pe.path_eff.median(); cell = {"fast_efficient": (Pe.vpk >= cv_) & (Pe.path_eff >= cp_), "fast_inefficient": (Pe.vpk >= cv_) & (Pe.path_eff < cp_), "slow_efficient": (Pe.vpk < cv_) & (Pe.path_eff >= cp_), "slow_inefficient": (Pe.vpk < cv_) & (Pe.path_eff < cp_)}
    i3, e3, p3 = poe_boot(Pe, None, 1000 if not FAST else 200); mat["edge_cells"] = {}
    for cn, cm in cell.items():
        m_ = cm.values.astype(float); ee = e3(m_, i3); mat["edge_cells"][cn] = dict(n=int(m_.sum()), poe=p3(m_), lo=float(np.nanpercentile(ee, 2.5)), hi=float(np.nanpercentile(ee, 97.5)))
    mat["edge_cut"] = dict(vpk_median=float(cv_), path_eff_median=float(cp_), n_players=int(len(Pe)))
    Ee = ED5.merge(pdl2, on="nfl_id").dropna(subset=["path_eff"]).copy(); Ee["pez"] = z(Ee.path_eff); gi = G(f"pres ~ vs * pez + {b}", Ee); mat["edge_interaction"] = orci(gi, "vs:pez"); mat["edge_main_pez"] = orci(gi, "pez")
    # exploratory: wide vs tight alignment (distance to nearest tracked blocker), snap level
    Ew = Ee.dropna(subset=["ol_d1"]).copy()
    if Ew.nfl_id.nunique() >= 12 and len(Ew) > 300:
        wc = float(Ew.ol_d1.median()); Ew["wide"] = (Ew.ol_d1 >= wc).astype(int); Ew["fastv"] = (Ew.vpk >= cv_).astype(int); Ew["eff"] = (Ew.path_eff >= cp_).astype(int); mat["edge_wide_cut_yd"] = wc; mat["edge_wide"] = {}
        for fl, fe in ((1, 0), (1, 1), (0, 0), (0, 1)):
            for wd in (0, 1):
                q = Ew[(Ew.fastv == fl) & (Ew.eff == fe) & (Ew.wide == wd)]
                mat["edge_wide"][f"fast{fl}_eff{fe}_wide{wd}"] = dict(snaps=int(len(q)), players=int(q.nfl_id.nunique()), poe_pp=float(q.poe.mean() * 100) if len(q) else None)
    res["matrix"] = mat; print(json.dumps({k: v for k, v in mat.items() if k.startswith("edge")}, indent=1, default=float))
    addp("Edge: speed x drill path efficiency", mat["edge_interaction"]["p"], "M")
except Exception as e: fail("5.6_matrix", e)

# %%
try:
    geom2 = {}
    for nm, D in (("interior", IL5), ("edge", ED5)):
        geom2[nm] = {c: dict(mean=float(D[c].mean()), sd=float(D[c].std())) for c in ["path_eff_20", "adx_20", "ady_20", "disp_20", "s_10", "s_20"] if c in D.columns}
    res["mech_geom"] = {**{k: v for k, v in geom.items()}, "detail": geom2}
except Exception as e: fail("5.7_geom", e)

# %%
json.dump(res, open(f"{WORK}/results.json", "w"), indent=1, default=float); log("results saved")

# %% [markdown]
# ## Part 4. Figures
# Palette: blue for interior linemen, orange for edge rushers, shared y-axes wherever two groups are compared, and direct labels wherever possible.

# %%
import matplotlib; import matplotlib.pyplot as plt, matplotlib.colors as mc
from matplotlib.lines import Line2D
SURF, INK, INK2, MUTED, GRID_, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
BLUE, ORANGE, AQUA, VIOLET, MAGENTA = "#2a78d6", "#eb6834", "#1baf7a", "#6250d6", "#e87ba4"
plt.rcParams.update({"figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF, "axes.edgecolor": AXIS, "axes.labelcolor": INK2, "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK,
                     "axes.grid": True, "grid.color": GRID_, "grid.linewidth": 0.8, "axes.spines.top": False, "axes.spines.right": False, "font.size": 12.5, "axes.titlesize": 15, "axes.titleweight": "bold",
                     "axes.titlelocation": "left", "legend.frameon": False})
def save(fig, name, right=None):
    """16:9 broadcast frame, 3200 x 1800 px: navy lower-third banner, figure number, source line."""
    n = name.split("_")[0].replace("fig", "")
    fig.set_size_inches(16, 9); fig.tight_layout(rect=[0.0, 0.05, 1, 0.915])
    if right: fig.subplots_adjust(right=right)
    fig.add_artist(plt.Rectangle((0, 0.94), 1, 0.06, transform=fig.transFigure, color="#0b2a4a", zorder=0)); fig.add_artist(plt.Rectangle((0, 0.94), 0.006, 0.06, transform=fig.transFigure, color=ORANGE, zorder=1))
    fig.text(0.018, 0.97, f"SPEED TRAVELS  |  FIG. {n}", color="white", fontsize=17, fontweight="bold", va="center")
    fig.text(0.99, 0.97, "NFL BIG DATA BOWL 2027  |  COMBINE 10 Hz TRACKING VS. GAME PASS RUSH", color="#9fc3ee", fontsize=11.5, ha="right", va="center")
    fig.text(0.012, 0.012, "Source: NFL Big Data Bowl 2027 competition data. Models: GEE-logit clustered by rusher unless noted.", fontsize=9.5, color=MUTED)
    fig.savefig(f"{FIG}/{name}", dpi=200, facecolor=SURF); plt.show()
def headline(ax, t, sub=None):
    ax.set_title(t, loc="left", pad=38 if sub else 8)
    if sub: ax.text(0, 1.022, sub, transform=ax.transAxes, fontsize=9.5, color=INK2, va="bottom")

# %% [markdown]
# **Figure 1.** The 40-yard dash, seen at 10 Hz.

# %%
fig, ax = plt.subplots(1, 2, figsize=(11.5, 4.6), gridspec_kw={"width_ratios": [1.25, 1]})
for pos, col in {"DL": BLUE, "OL": ORANGE, "DB": AQUA, "WR": VIOLET, "TE": MAGENTA}.items():
    sub = CUR[CUR.combine_position == pos][GRID]; m, sd = sub.mean(), sub.std()
    ax[0].plot(GRID, m, color=col, lw=2.2); ax[0].fill_between(GRID, m - sd, m + sd, color=col, alpha=0.10, lw=0); ax[0].text(5.62, m.iloc[-1] + (0.25 if pos == "WR" else -0.25 if pos == "DB" else 0), pos, color=col, va="center", fontsize=10, fontweight="bold")
ax[0].set_xlim(0, 5.9); ax[0].set_xlabel("Seconds after start of motion"); ax[0].set_ylabel("Speed (yd/s)")
headline(ax[0], "Positions differ mostly in top speed", "Mean 10 Hz speed curve of each player's fastest 40 (band = 1 SD)")
mm = c40.dropna(subset=["forty", "vpk"]); ax[1].scatter(mm.vpk, mm.forty, s=14, color=BLUE, alpha=0.55, lw=0)
co = np.polyfit(mm.vpk, mm.forty, 1); xs = np.linspace(mm.vpk.min(), mm.vpk.max(), 50); ax[1].plot(xs, np.polyval(co, xs), color=INK, lw=1.4)
ax[1].set_xlabel("Tracking top speed in the 40 (yd/s)"); ax[1].set_ylabel("Stopwatch 40 time (s)"); ax[1].text(0.97, 0.95, f"r = {res['forty_vs_vpk_r']:.2f}", transform=ax[1].transAxes, ha="right", va="top", fontsize=12, fontweight="bold")
headline(ax[1], "The 40 time is mostly top speed", f"{len(mm)} prospects, one dot each"); fig.tight_layout(); save(fig, "fig1_forty.png")

# %% [markdown]
# **Figure 2.** How repeatable is each Combine metric?

# %%
rel = res["reliability"]; order = sorted(rel.items(), key=lambda kv: kv[1]); fig, ax = plt.subplots(figsize=(8.6, 4.4))
for i, (k, v) in enumerate(order):
    col = BLUE if k.startswith("40") else ORANGE; ax.hlines(i, 0, v, color=col, lw=2.4, alpha=0.9); ax.plot(v, i, "o", ms=8, color=col, mec=SURF, mew=1.5); ax.text(v + 0.02, i, f"{v:.2f}", va="center", fontsize=9.5, color=INK2)
ax.set_yticks(range(len(order))); ax.set_yticklabels([k for k, _ in order], fontsize=9.5); ax.set_xlim(0, 1.12); ax.set_xlabel("Test-retest correlation between a player's first two attempts"); ax.grid(axis="y", visible=False)
ax.legend(handles=[Line2D([0], [0], color=BLUE, lw=3, label=f"40-yard dash (n={res['reliability_n']['forty']} players)"), Line2D([0], [0], color=ORANGE, lw=3, label=f"Pass-rush drill, DL (n={res['reliability_n']['prd']})")], loc="lower right")
headline(ax, "Top speed is measured almost perfectly; early-phase metrics are mostly noise", "How repeatable is each metric across a prospect's two attempts?"); fig.tight_layout(); save(fig, "fig2_reliability.png")

# %% [markdown]
# **Figure 3.** Which Combine numbers show up in the game?

# %%
tr_ = res["translate"]; fig, ax = plt.subplots(1, 2, figsize=(11.5, 4.6), sharey=True)
ax[0].scatter(pg.vpk, pg.s_10, s=np.clip(pg.n / 6, 14, 90), c=np.where(pg.ipos > 0.5, BLUE, ORANGE), alpha=0.8, lw=0.8, edgecolor=SURF); ax[0].set_xlabel("Combine top speed in the 40 (yd/s)"); ax[0].set_ylabel("In-game speed 1.0 s after the snap (yd/s)")
r, lo, hi = tr_["r_vpk_s10"]; ax[0].text(0.04, 0.95, f"r = {r:.2f}  (95% CI {lo:.2f} to {hi:.2f})\nn = {tr_['n_game']} linemen", transform=ax[0].transAxes, va="top", fontsize=10.5, fontweight="bold")
headline(ax[0], "Top-end speed shows up in the rush", "Combine 40 top speed vs. average speed one second into a pass rush")
ax[1].scatter(dd_.d_s10, dd_.s_10, s=np.clip(dd_.n / 6, 14, 90), c=np.where(dd_.ipos > 0.5, BLUE, ORANGE), alpha=0.8, lw=0.8, edgecolor=SURF); ax[1].set_xlabel("Combine pass-rush drill: speed 1.0 s in (yd/s)")
r, lo, hi = tr_["r_drill_s10"]; ax[1].text(0.04, 0.95, f"r = {r:.2f}  (95% CI {lo:.2f} to {hi:.2f})\nn = {tr_['n_drill']} linemen", transform=ax[1].transAxes, va="top", fontsize=10.5, fontweight="bold")
headline(ax[1], "The drill's first step does not", "Same in-game outcome, measured in the Combine pass-rush drill")
ax[1].legend(handles=[Line2D([0], [0], marker="o", ls="", color=BLUE, label="Interior DL"), Line2D([0], [0], marker="o", ls="", color=ORANGE, label="Edge")], loc="lower right"); fig.tight_layout(); save(fig, "fig3_translation.png")

# %% [markdown]
# **Figure 4.** Interior DL: pressure rate rises with Combine top speed. Edge rushers: it does not.

# %%
dz = res["dose"]; co = res["forty_poly"]; fig, ax = plt.subplots(1, 2, figsize=(11.5, 4.7), sharey=True)
for a, lab, col in [(ax[0], "INT", BLUE), (ax[1], "EDGE", ORANGE)]:
    d = dz[lab]; g_ = np.array(d["grid"]); a.fill_between(g_, np.array(d["lo"]) * 100, np.array(d["hi"]) * 100, color=col, alpha=0.18, lw=0); a.plot(g_, np.array(d["mid"]) * 100, color=col, lw=2.6)
    a.plot(d["speeds"], np.full(len(d["speeds"]), 0.35), "|", color=MUTED, ms=9, alpha=0.7); a.set_xlabel("Combine top speed (yd/s)  [stopwatch 40 equivalent]")
    tk = np.array([9.0, 9.5, 10.0, 10.5, 11.0]); tk = tk[(tk >= g_.min() - 0.01) & (tk <= g_.max() + 0.01)]; a.set_xticks(tk); a.set_xticklabels([f"{t:.1f}\n[{np.polyval(co, t):.2f}s]" for t in tk]); a.set_ylim(0, 16)
ax[0].set_ylabel("Adjusted pressure rate per rush snap (%)"); nn = res["n"]; pq = res["p10_p90"]
headline(ax[0], "Interior DL: faster is better", f"{nn['int_players']} players, {nn['int_snaps']:,} rushes"); headline(ax[1], "Edge rushers: no speed signal", f"{nn['edge_players']} players, {nn['edge_snaps']:,} rushes")
ax[0].annotate(f"{pq['rate10']*100:.1f}%", (pq["v10"], pq["rate10"] * 100), xytext=(-4, -22), textcoords="offset points", color=BLUE, fontweight="bold", ha="center")
ax[0].annotate(f"{pq['rate90']*100:.1f}%", (pq["v90"], pq["rate90"] * 100), xytext=(0, 12), textcoords="offset points", color=BLUE, fontweight="bold", ha="center")
fig.text(0.012, 0.03, "Adjusted for weight, arm length, draft slot, down and distance; band = 95% player-cluster bootstrap CI. Ticks along the bottom: individual players.", fontsize=8.5, color=INK2); fig.tight_layout(); save(fig, "fig4_dose.png")

# %% [markdown]
# **Figure 5.** Stress tests.

# %%
rb = res["robust"]; rows_ = list(rb.items()); nloo = res["loo_OR_range"]; fig, ax = plt.subplots(figsize=(14, 8)); y = np.arange(len(rows_) + 1)[::-1]; XR = max(1.8, max(v["hi"] for v in rb.values()) + 0.12)
for yy, (k, v) in zip(y[:-1], rows_):
    ax.hlines(yy, v["lo"], v["hi"], color=BLUE, lw=2.2); ax.plot(v["OR"], yy, "o", color=BLUE, ms=7.5, mec=SURF, mew=1.4); ax.text(XR + 0.03, yy, f"{v['OR']:.2f}  [{v['lo']:.2f}, {v['hi']:.2f}]", va="center", fontsize=9, color=INK2)
ax.hlines(y[-1], nloo[0], nloo[1], color=BLUE, lw=5, alpha=0.5); ax.text(XR + 0.03, y[-1], f"range {nloo[0]:.2f} to {nloo[1]:.2f}", va="center", fontsize=9, color=INK2)
ax.set_yticks(y); ax.set_yticklabels([k for k, _ in rows_] + ["Drop any single player (all refits)"], fontsize=9.5); ax.axvline(1, color=INK2, lw=1.2, ls="--"); ax.set_xlim(0.9, XR); ax.set_xlabel("Odds ratio of generating pressure per +0.5 yd/s top speed (stopwatch row: per 0.2 s faster)"); ax.grid(axis="y", visible=False)
headline(ax, "The interior DL speed effect survives every stress test", "Odds ratio with 95% CI; 1.0 = no effect"); fig.tight_layout(); save(fig, "fig5_robust.png", right=0.74)

# %% [markdown]
# **Figure 6.** Interior linemen who are fast for their size and produce more than their draft slot and size predict.

# %%
fig, ax = plt.subplots(figsize=(9.4, 6.0)); lim = np.percentile(np.abs(S["diff"]), 95); cmap = mc.LinearSegmentedColormap.from_list("div", ["#e34948", "#f0efec", "#2a78d6"])
sc = ax.scatter(S.w, S.vpk, s=np.clip(S.n / 4, 25, 260), c=S["diff"], cmap=cmap, vmin=-lim, vmax=lim, edgecolor=INK2, linewidth=0.7, alpha=0.95)
cb = fig.colorbar(sc, ax=ax, shrink=0.8, pad=0.02); cb.set_label("Pressures per 100 rushes vs. draft-and-size expectation"); cb.outline.set_visible(False)
for _, r_ in pd.concat([S.nlargest(5, "diff"), S.nsmallest(4, "diff")]).drop_duplicates("nfl_id").iterrows(): ax.annotate(r_.display_name.split(" ")[-1], (r_.w, r_.vpk), xytext=(6, 5), textcoords="offset points", fontsize=8.5, color=INK)
ax.set_xlabel("Combine weight (lb)"); ax.set_ylabel("Combine top speed (yd/s)"); headline(ax, "Fast for their size: who beats expectation?", f"Interior DL with 100+ rush snaps (n={len(S)}); dot size = rushes. Draft slot, weight and arm length already accounted for.")
fig.tight_layout(); save(fig, "fig6_scouting.png")

# %% [markdown]
# **Figure 7.** Out-of-time check: fit on 2023 and 2024, predict 2025.

# %%
fw = res["forward"]; fig, ax = plt.subplots(1, 2, figsize=(11, 4.9), sharex=True, sharey=True); mx = max(Pt.y.max(), Pt["draft+size"].max(), Pt["draft+size+speed"].max()) * 100 + 1
for a, k, ttl in [(ax[0], "draft+size", "Draft slot + size only"), (ax[1], "draft+size+speed", "Adding Combine top speed")]:
    a.plot([0, mx], [0, mx], color=MUTED, lw=1.2, ls="--"); a.scatter(Pt[k] * 100, Pt.y * 100, s=np.clip(Pt.n / 3, 25, 150), color=BLUE, alpha=0.8, edgecolor=SURF, lw=0.8)
    a.set_xlabel("Predicted 2025 pressure rate (%)"); a.set_xlim(0, mx); a.set_ylim(0, mx); a.text(0.04, 0.95, f"Spearman = {fw['rho_' + k]:.2f}", transform=a.transAxes, va="top", fontsize=11, fontweight="bold")
    headline(a, ttl, "Model fit on 2023-24 seasons only" if k == "draft+size" else "Same, plus top speed")
ax[0].set_ylabel("Actual 2025 pressure rate (%)")
fig.text(0.012, 0.03, f"{fw['eval_players']} interior DL with 75+ rushes in 2025. Log-loss improves in {fw['dll_pos_share']*100:.0f}% of player-level bootstrap draws; the 95% interval still includes zero.", fontsize=8.5, color=INK2); fig.tight_layout(); save(fig, "fig7_forward.png")

# %% [markdown]
# ## Limitations
# * Only about 500 prospects (drafted 2023 to 2025) with 1 to 3 seasons of tracking, so effects are estimated from 88 interior and 121 edge rushers.
# * No opponent tracking is available, so blocker quality is controlled only through team and opposing-offense fixed effects.
# * Pressure is a credited outcome in `player_play`; sacks are too rare per player to be a stable target.
# * The out-of-time check (32 players) is directionally positive but cannot, on its own, rule out zero.
# * Speed and weight are strongly correlated among interior linemen (r about -0.8), so the speed coefficient is estimated conditional on weight; it holds across every specification we tried but is not a causal claim.
