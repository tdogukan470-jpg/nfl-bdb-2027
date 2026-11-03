"""Fill writeup_template.md from results.json so every number in the writeup is machine-copied, not hand-typed.
Usage: python3 fill_writeup.py results.json template.md out.md
"""
import json, re, sys, math
import numpy as np
from pathlib import Path

res = json.load(open(sys.argv[1]))
tpl = Path(sys.argv[2]).read_text()
IMG = "https://raw.githubusercontent.com/tdogukan470-jpg/nfl-bdb-2027/main/figures/"
N40_CONST = 418   # prospects with both a stopwatch 40 and a tracked 40 (printed by the notebook: "forty vs tracking top speed r")

def get(path):
    # dot path; keys may themselves contain dots (e.g. "Quick pressure only (<= 2.5 s)"), so try the longest matching join first
    cur = res; parts = path.split(".")
    while parts:
        if isinstance(cur, list): cur = cur[int(parts.pop(0))]; continue
        for k in range(len(parts), 0, -1):
            key = ".".join(parts[:k])
            if key in cur: cur = cur[key]; parts = parts[k:]; break
        else: raise KeyError(path)
    return cur

def fmt_p(p, nd=2):
    if p < 0.001: return "<0.001"
    if nd == 2 and p < 0.01: return f"{p:.3f}"
    return f"{p:.{nd}f}"

def signed(x, nd):
    return f"{x:+.{nd}f}"

def pp(d):   # mediation-style dict with est/lo/hi
    return f"{signed(d['est'], 2)} [{d['lo']:.2f}, {d['hi']:.2f}]"

def poe(v, lo, hi, nd=1):
    return f"{signed(v, nd)} [{lo:+.{nd}f}, {hi:+.{nd}f}]"

def handler(kind, path):
    if kind == "OR": return f"{get(path)['OR']:.2f}"
    if kind == "LO": return f"{get(path)['lo']:.2f}"
    if kind == "HI": return f"{get(path)['hi']:.2f}"
    if kind == "ORB": v = get(path); return f"{v['OR']:.2f} [{v['lo']:.2f}, {v['hi']:.2f}]"
    if kind == "ORPCT": return f"{round((get(path)['OR'] - 1) * 100):d}"
    if kind == "LINB": v = get(path); return f"{signed(v['b'], 3)} [{signed(v['lo'], 3)}, {signed(v['hi'], 3)}]"
    if kind == "P": return fmt_p(get(path), 2)
    if kind == "P2": return fmt_p(get(path), 2)
    if kind == "P3": return fmt_p(get(path), 3)
    if kind == "F1": return f"{get(path):.1f}"
    if kind == "F2": return f"{get(path):.2f}"
    if kind == "F3": return f"{get(path):.3f}"
    if kind == "N": return f"{int(round(get(path))):,}"
    if kind == "PCT0": return f"{round(get(path) * 100):d}"
    if kind == "PCT1": return f"{get(path) * 100:.1f}"
    if kind == "REL": return f"{res['reliability'][path]:.2f}"
    if kind == "PP": return pp(get(path))
    raise KeyError(kind)

# ---- derived tokens -------------------------------------------------------------------------------------------
tok = {}
tok["IMG"] = IMG
tok["N40"] = str(N40_CONST)
shares = res.get("season_filter", {}).get("shares_of_player_play_rows", {})
tok["PCT_NONREG"] = f"{round((1 - shares.get('REG', 1.0)) * 100):d}" if shares else "NA"
a, b, c = res["forty_poly"]; vmed = res["speed_p10_p50_p90"][1]
tok["STOPWATCH"] = f"{abs(2 * a * vmed + b) * 0.5:.1f}"
ppu = res["poe"]["interior"]["poe_pp_per_unit"]["b"]
tok["PRESS100"] = f"{ppu:.1f}"
_rb = {k: v for k, v in res["robust"].items() if k != "Baseline (all controls)"}
tok["N_RB"] = str(len(_rb)); tok["RB_MIN"] = f"{min(v['OR'] for v in _rb.values()):.2f}"; tok["RB_MAX"] = f"{max(v['OR'] for v in _rb.values()):.2f}"
tok["PRESS_SEASON"] = str(int(round(ppu * 5)))
# robustness rows whose interval includes 1.0
weak_rows = [k for k, v in res["robust"].items() if v["lo"] <= 1.0]
if weak_rows:
    names = {"+ defensive team fixed effects": "team fixed effects", "Season 2024 only": "the 2024 season alone", "Sack": "sacks", "Quick pressure only (<= 2.5 s)": "quick pressure", "Season 2023 only": "the 2023 season alone", "Season 2025 only": "the 2025 season alone"}
    lst = [names.get(k, k.lower()) for k in weak_rows]
    tok["WEAK_ROWS_LC"] = "only " + (", ".join(lst[:-1]) + " and " + lst[-1] if len(lst) > 1 else lst[0]) + " have intervals touching 1.0."
    tok["WEAK_ROWS"] = "Only " + (", ".join(lst[:-1]) + " and " + lst[-1] if len(lst) > 1 else lst[0]) + " have intervals touching 1.0."
else:
    tok["WEAK_ROWS"] = "Every interval excludes 1.0."; tok["WEAK_ROWS_LC"] = "every interval excludes 1.0."
xp = res["xp"]
if xp.get("model", "gbm") == "league rate":
    cl = xp["candidate_logloss"]
    tok["XP_SENTENCE"] = (f"Neither beats the league rate out of fold (log loss {cl['gbm']:.4f} and {cl['logit']:.4f} against {xp['logloss_null']:.4f}): on true dropbacks, pre-snap context says almost nothing about which rusher gets home, so xP is the league rate and the POE checks collapse to the baseline model. "
                          "That null is itself a finding: an expected-pressure model fit on all plays mostly learns run versus pass.")
else:
    mname = {"gbm": "gradient-boosted model", "logit": "logistic regression"}[xp["model"]]
    g = xp['logloss_gain_pct']; gtxt = f"log loss improves {g:.1f}% over the league rate" if g >= 0.05 else "log loss only matches the league rate"
    tok["XP_SENTENCE"] = (f"The {mname} wins. Out of fold, AUC is {xp['auc_player_cv']:.2f}, {gtxt} and the worst decile miscalibration is {xp['calib_max_gap'] * 100:.1f} points: "
                          "on true dropbacks, pre-snap context predicts which rusher gets home only weakly, so POE stays close to the raw rate.")
tok["PERM"] = "< 0.001" if res["perm_p"] < 0.001 else f"= {res['perm_p']:.3f}"
top = res["eb"]["interior"]["top"][:5]
def short(n):
    parts = n.split(); return n if len(parts) == 1 else (parts[0] + " " + parts[-1] if parts[0] in ("Byron",) else parts[-1])
top = top[:3]; tok["EBTOP"] = ", ".join(f"{t['display_name']} ({t['poe_shrunk'] * 100:+.1f})" for t in top[:-1]) + f" and {top[-1]['display_name']} ({top[-1]['poe_shrunk'] * 100:+.1f}) points"

# FDR headline sentence
tab = {t["test"]: t for t in res["fdr"]["table"]}
int_head = [k for k in tab if k in ("Table 1: int_pressure", "Decomposition: top speed", "Stopwatch 40", "POE (xP offset), interior", "POE linear, interior")]
bb = tab.get("Beta-Binomial speed effect, interior")
null_head = [k for k in tab if k in ("Table 1: edge_pressure", "Table 1: ol_pressure_allowed", "Table 1: wr_sep_all", "Table 1: wr_sep_deep", "POE (xP offset), edge", "POE linear, edge", "Beta-Binomial speed effect, edge")]
qmax_int = max(tab[k]["q_all"] for k in int_head); qmin_null = min(tab[k]["q_all"] for k in null_head)
def qfmt(q): return "< 0.001" if q < 0.001 else f"= {q:.3f}" if q < 0.01 else f"= {q:.2f}"
def qceil(q): return f"{math.ceil(q * 1000) / 1000:.3f}" if q < 0.01 else f"{math.ceil(q * 100) / 100:.2f}"
def qfloor(q):  # a round number below q, for "none has q below X"
    for x in (0.5, 0.4, 0.3, 0.2, 0.1, 0.05):
        if q >= x: return f"{x:g}"
    return f"{q:.2f}"
s = f"Every interior headline test (Table 1, top speed, stopwatch 40, POE) has q at or below {qceil(qmax_int)}"
if bb is not None:
    s += f" except the Beta-Binomial likelihood-ratio test (q {qfmt(bb['q_all'])}"
    s += "; its player bootstrap interval includes 1)" if res["eb"]["interior"]["OR_lo"] <= 1 else ")"
s += f"; no edge, OL or WR headline test has q below {qfloor(qmin_null)}."
weak = [(k.replace('Robustness: ', ''), v['q_all']) for k, v in tab.items() if v['family'] == 'R' and v['q_all'] > 0.05]
if weak:
    names = {"Sack": "sacks", "Quick pressure only (<= 2.5 s)": "quick pressure", "+ defensive team fixed effects": "team fixed effects", "Season 2024 only": "the 2024 season alone", "Season 2023 only": "the 2023 season alone", "Season 2025 only": "the 2025 season alone"}
    if set(k for k, _ in weak) == set(weak_rows): pass
    else: s += " Robustness rows with q above 0.05: " + ", ".join(f"{names.get(k, k.lower())} ({qfmt(q).replace('= ', '')})" for k, q in weak) + "."
tok["FDR_HEADLINE"] = s

# Decision matrix numbers
cuts = res["matrix"]["interior_cuts"]
green = max([c_ for c_ in cuts if c_["diff_lo"] > 0] or [cuts[1]], key=lambda c_: c_["n_fast"])
red_c = [c_ for c_ in cuts if c_["n_slow"] >= 20 and c_["cut"] > green["cut"]]
red = min(red_c, key=lambda c_: c_["poe_slow"]) if red_c else cuts[-3]
tok["CUT_G"] = f"{green['cut']:.2f}"; tok["N_G"] = str(green["n_fast"])
tok["POE_G"] = poe(green["poe_fast"], green["fast_lo"], green["fast_hi"]); tok["POE_REST"] = f"{green['poe_slow']:+.1f}"
tok["GAP_G"] = poe(green["diff"], green["diff_lo"], green["diff_hi"])
tok["CUT_R"] = f"{red['cut']:.2f}"; tok["N_R"] = str(red["n_slow"]); tok["POE_R"] = poe(red["poe_slow"], red["slow_lo"], red["slow_hi"])
tok["POE_MID"] = poe(red["poe_fast"], red["fast_lo"], red["fast_hi"])
band = [x for x in res["matrix"].get("interior_bands", []) if x["lo"] is not None and x["hi"] is not None and abs(x["lo"] - green["cut"]) < 1e-6 and abs(x["hi"] - red["cut"]) < 1e-6]
if band:
    bd = band[0]; tok["N_MID"] = str(bd["n"]); tok["MID_TEXT"] = f"POE {poe(bd['poe'], bd['poe_lo'], bd['poe_hi'])}"
else:
    tok["N_MID"] = None; tok["MID_TEXT"] = f"All {red['n_fast']} players at or under {red['cut']:.2f} s average {tok['POE_MID']}"
tok["LIM_CLASS"] = "Draft classes differ; see Section 9."
tok["TAKE_CLASS"] = ""
lc = res.get("loco")
if lc:
    lo_, hi_ = lc["dll_ci"]
    if lo_ > 0:
        tok["LOCO_SENTENCE"] = (f"Holding out each draft class in turn, so test players never enter training, speed improves held-out log loss (95% interval above zero) and moves the player Spearman correlation from {lc['rho0']:.2f} to {lc['rho1']:.2f}.")
    else:
        # which held-out class leaves a null fit on the others?
        nulls = [(c_, v_["train_or"]) for c_, v_ in lc["by_class"].items() if v_["train_or"]["lo"] <= 1.0]
        others = lambda c_: " and ".join(sorted(k for k in lc["by_class"] if k != c_))
        s_ = (f"The stricter test fails. Holding out each draft class in turn, so test players never enter training, adding speed does not improve held-out prediction "
              f"(log-loss gain {lc['dll'] * 1000:+.2f} x 10^-3, 95% CI {lo_ * 1000:+.2f} to {hi_ * 1000:+.2f}; player Spearman {lc['rho0']:.2f} without speed, {lc['rho1']:.2f} with).")
        if nulls:
            c_, o_ = nulls[0]
            s_ += f" Fit on the {others(c_)} classes alone, the interior OR is {o_['OR']:.2f} [{o_['lo']:.2f}, {o_['hi']:.2f}]: the pooled effect leans on the {c_} class."
            tok["LIM_CLASS"] = f"The interior effect leans on the {c_} draft class and did not transfer to held-out classes; for a new class it is a hypothesis to monitor, not a rule."
            tok["TAKE_CLASS"] = f"That signal leans on the {c_} class and has not yet held up out of class, so it should guide where scouts look, not replace the tape."
        tok["LOCO_SENTENCE"] = s_
else:
    tok["LOCO_SENTENCE"] = "Forward evidence is directional, not conclusive."
wb = res["matrix"]["weight_bands"]; light = [v for k, v in wb.items() if k.startswith("light")][0]; mid = wb["mid"]; heavy = [v for k, v in wb.items() if k.startswith("heavy")][0]
tok["W1"] = f"{light['w_range'][1]:.0f}"; tok["W1P"] = f"{mid['w_range'][0]:.0f}"; tok["W2"] = f"{mid['w_range'][1]:.0f}"; tok["W2P"] = f"{heavy['w_range'][0]:.0f}"
tok["GAP_LIGHT"] = f"{light['diff']:+.1f}"; tok["GAP_MID"] = f"{mid['diff']:+.1f}"; tok["GAP_HEAVY"] = poe(heavy["diff"], heavy["lo"], heavy["hi"])
tok["GAP_LIGHT_CI"] = poe(light["diff"], light["lo"], light["hi"]); tok["GAP_MID_CI"] = poe(mid["diff"], mid["lo"], mid["hi"])
_sig = [(nm_, b_) for nm_, b_ in (("light", light), ("mid", mid)) if b_["lo"] > 0]
if len(_sig) == 1:
    b_ = _sig[0][1]; tok["LIGHT_ACTION"] = f"Weigh the split here; the {b_['w_range'][0]:.0f} to {b_['w_range'][1]:.0f} lb gap excludes 0"
elif len(_sig) == 2: tok["LIGHT_ACTION"] = "Weigh the split here; both gaps exclude 0"
else: tok["LIGHT_ACTION"] = "Gap is positive but intervals include 0"
tok["MEDG"] = f"{np.median([y['median_peak_g'] for y in res['audit']['by_year']]):.1f}"
ec = res["matrix"]["edge_cells"]; ew = res["matrix"]["edge_wide"]
tok["N_FE"] = str(ec["fast_efficient"]["n"]); tok["POE_FE"] = poe(ec["fast_efficient"]["poe"], ec["fast_efficient"]["lo"], ec["fast_efficient"]["hi"])
tok["N_FI"] = str(ec["fast_inefficient"]["n"]); tok["POE_FI"] = poe(ec["fast_inefficient"]["poe"], ec["fast_inefficient"]["lo"], ec["fast_inefficient"]["hi"])
tok["POE_FI_W"] = f"{ew['fast1_eff0_wide1']['poe_pp']:+.1f}"; tok["POE_FI_T"] = f"{ew['fast1_eff0_wide0']['poe_pp']:+.1f}"

# ---- substitution ---------------------------------------------------------------------------------------------
def sub(m):
    body = m.group(1)
    if body in tok: return tok[body]
    if ":" in body:
        kind, path = body.split(":", 1); return handler(kind, path)
    raise KeyError(body)
if tok.get("N_MID") is None: tpl = tpl.replace(" ({N_MID} players)", "")
out = re.sub(r"\{([A-Z][A-Z0-9_]*(?::[^{}]+)?)\}", sub, tpl)
Path(sys.argv[3]).write_text(out)

# word count of the body: exclude figure captions (italic lines right after an image), image lines, table separator rows and the appendix
body = out.split("## Appendix")[0]
lines = []
prev_img = False
for ln in body.split("\n"):
    if ln.startswith("!["): prev_img = True; continue
    if prev_img and ln.startswith("*") and ln.rstrip().endswith("*"): prev_img = False; continue
    prev_img = False
    if re.match(r"^\*\*Table \d", ln): continue   # table captions do not count (host ruling)
    if re.fullmatch(r"\|?[\s|:-]+\|?", ln.strip() or "x"): continue
    lines.append(ln)
words = [w for w in re.sub(r"[#*|`]", " ", "\n".join(lines)).split() if re.search(r"[A-Za-z0-9]", w)]
tables = re.findall(r"^\*\*Table \d", out, flags=re.M); figs = re.findall(r"^!\[", out, flags=re.M)
if len(words) > 1960: print("WARNING: body word count above 1,960; trim before publishing")
print(f"body words (excl. captions/appendix): {len(words)} | figures: {len(figs)} | tables: {len(tables)} | total visuals: {len(figs) + len(tables)}")
