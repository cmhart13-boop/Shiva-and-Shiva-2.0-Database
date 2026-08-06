from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import requests
import streamlit as st

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "shiva_draft_roi.sqlite"
CURRENT_RANKINGS = APP_DIR / "current_rankings.csv"

LEAGUE_IDS = {
    "Shiva": 1465338,
    "Shiva 2.0": 1506903,
}
CURRENT_SEASON = 2026

st.set_page_config(
    page_title="Shiva 2026 Draft Coach",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
:root{
  --bg:#111113;--top:#080809;--card:#1c1c1e;--card2:#252528;--line:#2c2c30;
  --muted:#7d7e84;--white:#f7f7f8;--green:#28f33d;--blue:#5a98ff;
  --red:#ff535d;--gold:#ffb52b;
}
html,body,[class*="css"]{
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
}
.stApp{background:var(--bg);color:var(--white);}
.block-container{max-width:430px;padding:0 14px 54px!important;}
#MainMenu,footer,header{visibility:hidden;}

.top-shell{
  position:sticky;top:0;z-index:999;margin:0 -14px 14px;
  background:var(--top);border-bottom:1px solid #222225;
}
.top-row{position:relative;display:flex;align-items:center;justify-content:space-between;padding:13px 14px 7px;}
.back{color:#d8d8da;font-size:15px;font-weight:600;}
.title{
  position:absolute;left:50%;transform:translateX(-50%);
  color:#fff;font-size:15px;font-weight:900;text-transform:uppercase;white-space:nowrap;
}
.tabs{display:flex;border-bottom:1px solid #232326;padding:0 14px;}
.tab{
  flex:1;text-align:center;color:#707176;font-size:11px;font-weight:900;
  letter-spacing:.06em;text-transform:uppercase;padding:10px 0 9px;
}
.tab.active{color:#fff;border-bottom:3px solid var(--green);}

.section-label{
  color:#77787d;font-size:10px;font-weight:900;letter-spacing:.1em;
  text-transform:uppercase;margin:17px 0 8px;
}
.card{
  background:var(--card);border:1px solid #252528;border-radius:14px;
  padding:14px;margin-bottom:11px;box-shadow:0 10px 24px rgba(0,0,0,.16);
}
.card-title{color:#fff;font-size:15px;font-weight:900;}
.card-sub{color:var(--muted);font-size:11px;margin-top:3px;}
.callout{
  border-left:4px solid var(--green);padding-left:11px;margin:8px 0;
}
.callout.blue{border-left-color:var(--blue);}
.callout.red{border-left-color:var(--red);}
.callout.gold{border-left-color:var(--gold);}
.callout-title{color:#fff;font-size:13px;font-weight:900;}
.callout-text{color:#a6a7ac;font-size:11px;line-height:1.4;margin-top:3px;}

.hero-row{display:flex;align-items:flex-end;justify-content:space-between;gap:12px;}
.hero-grade{color:var(--green);font-size:56px;line-height:.9;font-weight:1000;}
.hero-rank{color:#fff;font-size:14px;font-weight:900;text-align:right;}
.hero-note{color:var(--muted);font-size:10px;text-align:right;margin-top:3px;}

.triple-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:9px;margin-bottom:11px;}
.stat-box{
  background:var(--card);border:1px solid #252528;border-radius:13px;
  min-height:76px;padding:11px;display:flex;flex-direction:column;justify-content:space-between;
}
.stat-label{
  color:#73747a;font-size:9px;line-height:1.2;font-weight:900;
  letter-spacing:.06em;text-transform:uppercase;
}
.stat-value{color:#fff;font-size:18px;font-weight:1000;line-height:1.05;}
.stat-value.green{color:var(--green);}
.stat-value.blue{color:var(--blue);}
.stat-value.red{color:var(--red);}

.list-row{
  display:grid;grid-template-columns:34px 1fr auto;gap:10px;align-items:center;
  padding:11px 0;border-top:1px solid #29292c;
}
.list-row:first-child{border-top:0;}
.rank-circle{
  width:30px;height:30px;border-radius:50%;background:var(--card2);
  display:flex;align-items:center;justify-content:center;color:#fff;font-size:12px;font-weight:1000;
}
.row-title{color:#fff;font-size:14px;font-weight:900;}
.row-sub{color:#7f8085;font-size:10px;line-height:1.35;margin-top:2px;}
.row-tag{font-size:11px;font-weight:1000;text-transform:uppercase;color:var(--green);}
.row-tag.blue{color:var(--blue);}
.row-tag.red{color:var(--red);}
.row-tag.gold{color:var(--gold);}

.pos-badge{
  display:inline-flex;align-items:center;justify-content:center;width:34px;height:23px;
  border-radius:6px;font-size:10px;font-weight:1000;color:#111;
}
.pos-RB{background:#56d78d}.pos-WR{background:#6bb8ff}.pos-QB{background:#ff6b70}.pos-TE{background:#c78cff}

[data-baseweb="select"]>div{
  background:var(--card)!important;border:1px solid #313134!important;
  border-radius:999px!important;min-height:44px;
}
[data-baseweb="select"] span,[data-baseweb="select"] input{
  color:var(--blue)!important;font-weight:900!important;
}
.stSelectbox label p,.stRadio label p,.stNumberInput label p,.stFileUploader label p{
  color:#dedee1!important;font-weight:800!important;
}
div[role="radiogroup"]{
  background:var(--card);border:1px solid #303033;border-radius:12px;padding:6px 8px;
}
[data-testid="stDataFrame"]{
  background:var(--card)!important;border:1px solid #29292c!important;
  border-radius:13px!important;overflow:hidden;
}
.stButton button,.stDownloadButton button{
  color:var(--blue)!important;background:transparent!important;
  border:2px solid var(--blue)!important;border-radius:999px!important;
  font-weight:900!important;width:100%;
}
h1,h2,h3,h4,p,label,.stMarkdown{color:var(--white)!important;}
@media(min-width:900px){.block-container{max-width:430px;}}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="top-shell">
  <div class="top-row">
    <div class="back">‹ League</div>
    <div class="title">2026 Draft Coach</div>
    <div style="width:48px"></div>
  </div>
  <div class="tabs">
    <div class="tab">League</div>
    <div class="tab active">Draft Intelligence</div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def load_data():
    with sqlite3.connect(DB_PATH) as con:
        roi = pd.read_sql_query(
            "SELECT * FROM draft_roi_scores ORDER BY league_name,season,overall_pick",
            con,
        )
    return roi


roi = load_data()
latest_season = int(roi["season"].max())

current_franchises = (
    roi[roi["season"].eq(latest_season)]
    [["league_name","team_id","team_name","manager_name","owner_id"]]
    .drop_duplicates(["league_name","team_id"])
    .sort_values(["league_name","team_id"])
)

player_seasons = (
    roi[
        ["season","player_id","position","position_finish_total",
         "fantasy_points_ppr","ppg","games_played"]
    ]
    .drop_duplicates(["season","player_id","position"])
)

benchmarks = (
    player_seasons.groupby(["position","position_finish_total"],as_index=False)
    .agg(expected_points=("fantasy_points_ppr","mean"),expected_ppg=("ppg","mean"))
    .rename(columns={"position_finish_total":"position_draft_rank"})
)

base = roi.merge(
    benchmarks,
    on=["position","position_draft_rank"],
    how="left",
)


def finish_buffer(rank: int) -> int:
    if rank <= 5: return 2
    if rank <= 12: return 4
    if rank <= 24: return 6
    return 9


def round_weight(round_number: int) -> float:
    return {
        1:1.00,2:.92,3:.84,4:.74,5:.64,6:.55,7:.46,8:.38,
        9:.29,10:.22,11:.17,12:.13,13:.10,14:.08,15:.06,16:.05,
    }.get(int(round_number),.05)


def grade_pick(row: pd.Series) -> pd.Series:
    expected = int(row["position_draft_rank"])
    actual = int(row["position_finish_total"])
    buffer = finish_buffer(expected)
    gap = actual - expected

    points_ratio = (
        float(row["fantasy_points_ppr"]) / float(row["expected_points"])
        if pd.notna(row["expected_points"]) and row["expected_points"] > 0
        else np.nan
    )
    ppg_ratio = (
        float(row["ppg"]) / float(row["expected_ppg"])
        if pd.notna(row["expected_ppg"]) and row["expected_ppg"] > 0
        else np.nan
    )

    finish_pass = gap <= buffer
    production_pass = (
        (pd.notna(points_ratio) and points_ratio >= .85)
        or (pd.notna(ppg_ratio) and ppg_ratio >= .90)
    )
    injury = (
        not finish_pass and pd.notna(ppg_ratio) and ppg_ratio >= .95
        and int(row["games_played"]) <= 13
    )
    steal = (
        actual <= max(1,expected-buffer)
        and (
            (pd.notna(points_ratio) and points_ratio >= 1.05)
            or (pd.notna(ppg_ratio) and ppg_ratio >= 1.05)
        )
    )

    result = (
        "Steal" if steal
        else "Hit" if finish_pass and production_pass
        else "Injury-Protected" if injury
        else "Bust"
    )

    finish_score = max(0,min(100,100-max(0,gap-buffer)*6.5))
    point_score = max(0,min(110,points_ratio*100)) if pd.notna(points_ratio) else 45
    ppg_score = max(0,min(110,ppg_ratio*100)) if pd.notna(ppg_ratio) else 45
    score = .55*finish_score + .30*point_score + .15*ppg_score

    if result == "Injury-Protected":
        score = min(max(score,58),69)

    return pd.Series({
        "Result":result,
        "Pick Score":max(0,min(100,score)),
        "Round Weight":round_weight(row["round"]),
    })


graded = base.join(base.apply(grade_pick,axis=1))


def letter_grade(score: float) -> str:
    if pd.isna(score): return "—"
    if score >= 90: return "A"
    if score >= 85: return "A-"
    if score >= 80: return "B+"
    if score >= 75: return "B"
    if score >= 70: return "B-"
    if score >= 65: return "C+"
    if score >= 60: return "C"
    if score >= 55: return "C-"
    if score >= 50: return "D"
    return "F"


def weighted_score(rows: pd.DataFrame) -> float:
    if rows.empty:
        return np.nan
    return float(np.average(rows["Pick Score"],weights=rows["Round Weight"]))


def current_managers(scope: str) -> list[str]:
    if scope == "Combined":
        return sorted(current_franchises["manager_name"].unique().tolist())
    return sorted(
        current_franchises[current_franchises["league_name"].eq(scope)]
        ["manager_name"].unique().tolist()
    )


def franchise_rows(manager: str,scope: str) -> pd.DataFrame:
    current = current_franchises[current_franchises["manager_name"].eq(manager)]
    if scope != "Combined":
        current = current[current["league_name"].eq(scope)]
    keys = set(zip(current["league_name"],current["team_id"]))
    if not keys:
        return graded.iloc[0:0].copy()
    mask = graded.apply(
        lambda row:(row["league_name"],row["team_id"]) in keys,
        axis=1,
    )
    return graded[mask].copy()


def franchise_name(manager: str,scope: str) -> str:
    current = current_franchises[current_franchises["manager_name"].eq(manager)]
    if scope != "Combined":
        current = current[current["league_name"].eq(scope)]
    names = current["team_name"].dropna().unique().tolist()
    return " / ".join(names) if names else manager


def round_summary(rows: pd.DataFrame) -> pd.DataFrame:
    output = []
    for rnd,group in rows.groupby("round"):
        score = float(group["Pick Score"].mean())
        output.append({
            "Round":int(rnd),
            "Score":score,
            "Grade":letter_grade(score),
            "Picks":len(group),
        })
    return pd.DataFrame(output).sort_values("Round")


def position_summary(rows: pd.DataFrame) -> pd.DataFrame:
    output = []
    for pos,group in rows.groupby("position"):
        score = float(group["Pick Score"].mean())
        output.append({
            "Position":pos,
            "Score":score,
            "Grade":letter_grade(score),
            "Picks":len(group),
        })
    return pd.DataFrame(output).sort_values("Score",ascending=False)


def historical_rules(rows: pd.DataFrame) -> dict[str,Any]:
    rounds = round_summary(rows)
    positions = position_summary(rows)

    early = rows[rows["round"] <= 3]
    middle = rows[rows["round"].between(4,8)]

    best_position = positions.iloc[0]["Position"] if not positions.empty else "—"
    worst_position = positions.iloc[-1]["Position"] if not positions.empty else "—"

    meaningful_rounds = rounds[rounds["Round"] <= 8]
    best_round = (
        int(meaningful_rounds.sort_values("Score",ascending=False).iloc[0]["Round"])
        if not meaningful_rounds.empty else None
    )
    worst_round = (
        int(meaningful_rounds.sort_values("Score").iloc[0]["Round"])
        if not meaningful_rounds.empty else None
    )

    early_pos = early["position"].value_counts()
    early_identity = early_pos.index[0] if not early_pos.empty else "—"

    rb_early_share = early["position"].eq("RB").mean()*100 if not early.empty else 0
    wr_early_share = early["position"].eq("WR").mean()*100 if not early.empty else 0

    middle_pos = middle.groupby("position")["Pick Score"].mean().sort_values(ascending=False)
    middle_strength = middle_pos.index[0] if not middle_pos.empty else "—"

    return {
        "best_position":best_position,
        "worst_position":worst_position,
        "best_round":best_round,
        "worst_round":worst_round,
        "early_identity":early_identity,
        "rb_early_share":rb_early_share,
        "wr_early_share":wr_early_share,
        "middle_strength":middle_strength,
    }


def personalized_rules(rows: pd.DataFrame) -> tuple[list[str],list[str],list[str]]:
    r = historical_rules(rows)

    rules = []
    rules.append(
        f"Lean into {r['best_position']} when similarly ranked players are available; "
        f"it has been your strongest drafted position."
    )
    if r["best_round"] is not None:
        rules.append(
            f"Protect Round {r['best_round']}: it has historically been one of your best value rounds."
        )
    if r["worst_round"] is not None:
        rules.append(
            f"Slow down in Round {r['worst_round']}; your history says this is where forced picks have hurt most."
        )
    rules.append(
        f"Your early-round identity has been {r['early_identity']}-heavy. "
        f"Only continue that approach when the remaining tier supports it."
    )
    rules.append(
        f"In Rounds 4–8, your strongest historical position has been {r['middle_strength']}."
    )

    do_more = [
        f"Use {r['best_position']} as a tiebreaker when two players are closely ranked.",
        f"Build around the approach that produced your strongest first-eight-round results.",
        "Prioritize players with proven weekly scoring, not just optimistic season projections.",
    ]

    do_less = [
        f"Do not force {r['worst_position']} at cost simply because your roster has an empty slot.",
        f"Avoid repeating the decision pattern that made Round {r['worst_round']} your weakest premium round."
        if r["worst_round"] is not None
        else "Avoid forcing positional need over player value.",
        "Do not let late-round hits disguise mistakes made with premium draft capital.",
    ]

    return rules,do_more,do_less


def snake_schedule(slot: int,teams: int=10,rounds: int=16) -> list[dict[str,int]]:
    output = []
    for rnd in range(1,rounds+1):
        overall = (
            (rnd-1)*teams+slot
            if rnd%2==1
            else rnd*teams-slot+1
        )
        output.append({"Round":rnd,"Overall":overall})
    return output


def opening_builds(rows: pd.DataFrame) -> list[str]:
    early = rows[rows["round"] <= 3].sort_values(["season","round"])
    if early.empty:
        return ["Best player available","Balanced start","Value-based start"]

    builds = []
    for _,group in early.groupby("season"):
        sequence = "/".join(group.sort_values("round")["position"].head(3).tolist())
        if sequence:
            builds.append(sequence)

    if not builds:
        return ["Best player available","Balanced start","Value-based start"]

    counts = pd.Series(builds).value_counts()
    return counts.index[:3].tolist()


def load_rankings(uploaded) -> pd.DataFrame:
    source = uploaded if uploaded is not None else CURRENT_RANKINGS if CURRENT_RANKINGS.exists() else None
    if source is None:
        return pd.DataFrame()

    rankings = pd.read_csv(source)
    required = {
        "player_name","position","adp","projected_points","projected_ppg"
    }
    missing = required-set(rankings.columns)
    if missing:
        st.error("Missing ranking columns: "+", ".join(sorted(missing)))
        return pd.DataFrame()

    for optional,default in {
        "team":"","tier":np.nan,"injury_status":"",
        "prior_top12":False,"prior_top20":False,
        "weekly_15_plus":np.nan,"espn_player_id":np.nan,
    }.items():
        if optional not in rankings.columns:
            rankings[optional] = default

    for col in ["adp","projected_points","projected_ppg","weekly_15_plus","espn_player_id"]:
        rankings[col] = pd.to_numeric(rankings[col],errors="coerce")

    return rankings.dropna(subset=["player_name","position","adp"])


def player_fit(rankings: pd.DataFrame,rows: pd.DataFrame,current_pick: int) -> pd.DataFrame:
    if rankings.empty:
        return rankings

    profile = historical_rules(rows)
    result = rankings.copy()

    result["ADP Value"] = current_pick-result["adp"]
    result["Projection Rank"] = result["projected_points"].rank(pct=True)*100
    result["PPG Rank"] = result["projected_ppg"].rank(pct=True)*100

    fit_bonus = []
    fit_reason = []

    for _,player in result.iterrows():
        bonus = 0.0
        reasons = []

        if player["position"] == profile["best_position"]:
            bonus += 12
            reasons.append("matches your strongest drafted position")

        if player["position"] == profile["middle_strength"]:
            bonus += 7
            reasons.append("fits your strongest middle-round profile")

        if pd.notna(player["weekly_15_plus"]) and player["weekly_15_plus"] >= 7:
            bonus += 9
            reasons.append("strong weekly usability")

        if bool(player["prior_top12"]):
            bonus += 8
            reasons.append("already proven at an elite level")
        elif bool(player["prior_top20"]):
            bonus += 4
            reasons.append("has delivered a strong positional finish")

        if str(player["injury_status"]).strip():
            bonus -= 8
            reasons.append("current injury risk")

        fit_bonus.append(bonus)
        fit_reason.append(", ".join(reasons) if reasons else "neutral historical fit")

    result["Historical Fit"] = fit_bonus
    result["Why"] = fit_reason
    result["Recommendation Score"] = (
        .45*result["Projection Rank"]
        + .25*result["PPG Rank"]
        + 1.4*result["ADP Value"].clip(-20,20)
        + result["Historical Fit"]
    )

    def label(row):
        if row["Recommendation Score"] >= result["Recommendation Score"].quantile(.80):
            return "Strong Fit"
        if row["Recommendation Score"] >= result["Recommendation Score"].quantile(.50):
            return "Acceptable"
        if row["Recommendation Score"] >= result["Recommendation Score"].quantile(.25):
            return "Risky"
        return "Avoid at ADP"

    result["Fit"] = result.apply(label,axis=1)
    return result.sort_values(
        ["Recommendation Score","projected_points"],
        ascending=False,
    )


def fetch_live_draft(league_name: str) -> tuple[pd.DataFrame,str]:
    league_id = LEAGUE_IDS[league_name]
    url = (
        f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/"
        f"seasons/{CURRENT_SEASON}/segments/0/leagues/{league_id}"
        f"?view=mDraftDetail&view=mTeam&view=mStatus"
    )

    cookies = {}
    try:
        if st.secrets.get("ESPN_SWID",""):
            cookies["SWID"] = st.secrets["ESPN_SWID"]
        if st.secrets.get("ESPN_S2",""):
            cookies["espn_s2"] = st.secrets["ESPN_S2"]
    except Exception:
        pass

    try:
        response = requests.get(
            url,
            headers={"User-Agent":"Mozilla/5.0","Accept":"application/json"},
            cookies=cookies,
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        picks = ((data.get("draftDetail") or {}).get("picks") or [])
        return pd.DataFrame(picks),"Connected"
    except Exception as exc:
        return pd.DataFrame(),f"Feed unavailable: {exc}"


page = st.radio(
    "Section",
    ["2026 Draft Coach","Player Fit","Draft Slot Plan","Live Draft","History"],
    horizontal=True,
    label_visibility="collapsed",
)

scope = st.selectbox("League",["Shiva","Shiva 2.0","Combined"])
managers = current_managers(scope)
manager = st.selectbox("Current Manager",managers)
rows = franchise_rows(manager,scope)
team_name = franchise_name(manager,scope)

if page == "2026 Draft Coach":
    rules,do_more,do_less = personalized_rules(rows)
    builds = opening_builds(rows)
    score = weighted_score(rows)

    st.markdown('<div class="section-label">Your 2026 Draft Plan</div>',unsafe_allow_html=True)

    st.markdown(
        f"""
<div class="card">
  <div class="card-title">{team_name}</div>
  <div class="card-sub">{manager} · Personalized from your complete historical draft record</div>
</div>
""",
        unsafe_allow_html=True,
    )

    profile = historical_rules(rows)

    st.markdown(
        f"""
<div class="triple-grid">
  <div class="stat-box">
    <div class="stat-label">Historical Draft Grade</div>
    <div class="stat-value green">{letter_grade(score)}</div>
  </div>
  <div class="stat-box">
    <div class="stat-label">Strongest Position</div>
    <div class="stat-value blue">{profile['best_position']}</div>
  </div>
  <div class="stat-box">
    <div class="stat-label">Weakest Premium Round</div>
    <div class="stat-value red">{f"R{profile['worst_round']}" if profile['worst_round'] else "—"}</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-label">Your Five Draft Rules</div>',unsafe_allow_html=True)
    st.markdown('<div class="card">',unsafe_allow_html=True)
    for i,rule in enumerate(rules,1):
        st.markdown(
            f"""
<div class="list-row">
  <div class="rank-circle">{i}</div>
  <div>
    <div class="row-title">{rule}</div>
  </div>
  <div class="row-tag">2026</div>
</div>
""",
            unsafe_allow_html=True,
        )
    st.markdown('</div>',unsafe_allow_html=True)

    st.markdown('<div class="section-label">Do More</div>',unsafe_allow_html=True)
    st.markdown('<div class="card">',unsafe_allow_html=True)
    for text in do_more:
        st.markdown(
            f'<div class="callout"><div class="callout-title">{text}</div></div>',
            unsafe_allow_html=True,
        )
    st.markdown('</div>',unsafe_allow_html=True)

    st.markdown('<div class="section-label">Do Less</div>',unsafe_allow_html=True)
    st.markdown('<div class="card">',unsafe_allow_html=True)
    for text in do_less:
        st.markdown(
            f'<div class="callout red"><div class="callout-title">{text}</div></div>',
            unsafe_allow_html=True,
        )
    st.markdown('</div>',unsafe_allow_html=True)

    st.markdown('<div class="section-label">Best Opening Builds From Your History</div>',unsafe_allow_html=True)
    st.markdown('<div class="card">',unsafe_allow_html=True)
    for i,build in enumerate(builds,1):
        st.markdown(
            f"""
<div class="list-row">
  <div class="rank-circle">{i}</div>
  <div>
    <div class="row-title">{build}</div>
    <div class="row-sub">Most successful historical first-three-round construction pattern</div>
  </div>
  <div class="row-tag blue">BUILD</div>
</div>
""",
            unsafe_allow_html=True,
        )
    st.markdown('</div>',unsafe_allow_html=True)

elif page == "Player Fit":
    st.markdown('<div class="section-label">2026 Player Fit</div>',unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Upload verified 2026 rankings",
        type=["csv"],
        help=(
            "Required: player_name, position, adp, projected_points, projected_ppg. "
            "Recommended: prior_top12, prior_top20, weekly_15_plus, injury_status."
        ),
    )
    rankings = load_rankings(uploaded)

    current_pick = st.number_input("Your Current Overall Pick",1,200,9,1)

    if rankings.empty:
        st.warning(
            "Upload current verified 2026 rankings to activate player fits. "
            "The app will not guess current ADP, projections, or injuries."
        )
    else:
        fits = player_fit(rankings,rows,int(current_pick))

        filter_choice = st.radio(
            "Show",
            ["Strong Fit","Acceptable","Risky","Avoid at ADP"],
            horizontal=True,
        )
        selected = fits[fits["Fit"].eq(filter_choice)].head(12)

        st.markdown('<div class="card">',unsafe_allow_html=True)
        for _,player in selected.iterrows():
            tag_class = {
                "Strong Fit":"",
                "Acceptable":" blue",
                "Risky":" gold",
                "Avoid at ADP":" red",
            }[player["Fit"]]
            st.markdown(
                f"""
<div class="list-row">
  <div><span class="pos-badge pos-{player['position']}">{player['position']}</span></div>
  <div>
    <div class="row-title">{player['player_name']}</div>
    <div class="row-sub">ADP {float(player['adp']):.1f} · {float(player['projected_points']):.1f} projected points · {player['Why']}</div>
  </div>
  <div class="row-tag{tag_class}">{player['Fit']}</div>
</div>
""",
                unsafe_allow_html=True,
            )
        st.markdown('</div>',unsafe_allow_html=True)

elif page == "Draft Slot Plan":
    st.markdown('<div class="section-label">Draft Slot Game Plan</div>',unsafe_allow_html=True)

    slot = st.number_input("Your Draft Slot",1,10,9,1)
    schedule = snake_schedule(int(slot),10,16)
    builds = opening_builds(rows)

    st.markdown(
        f"""
<div class="card">
  <div class="card-title">Pick {int(slot)} · 10-Team Snake</div>
  <div class="card-sub">Your picks: {", ".join(str(x['Overall']) for x in schedule[:8])}</div>
</div>
""",
        unsafe_allow_html=True,
    )

    plan = [
        ("Rounds 1–2","Build the foundation","Take the highest-tier RB/WR value. Do not force a position if the tier is gone."),
        ("Round 3","Complete the core","Leave the first three rounds with a build that matches one of your strongest historical constructions."),
        ("Rounds 4–6","Weekly starters","Prioritize proven weekly roles and the position where your middle-round history is strongest."),
        ("Rounds 7–9","Upside with a path","Target players who can become weekly starters, not low-ceiling bench insulation."),
        ("Rounds 10+","Swing for impact","Late misses are cheap. Chase breakout paths, contingent value, and spike-week ability."),
    ]

    st.markdown('<div class="card">',unsafe_allow_html=True)
    for phase,goal,avoid in plan:
        st.markdown(
            f"""
<div class="callout blue">
  <div class="callout-title">{phase}: {goal}</div>
  <div class="callout-text">{avoid}</div>
</div>
""",
            unsafe_allow_html=True,
        )
    st.markdown('</div>',unsafe_allow_html=True)

    st.markdown('<div class="section-label">Recommended Opening Builds</div>',unsafe_allow_html=True)
    st.markdown('<div class="card">',unsafe_allow_html=True)
    for i,build in enumerate(builds,1):
        st.markdown(
            f"""
<div class="list-row">
  <div class="rank-circle">{i}</div>
  <div><div class="row-title">{build}</div></div>
  <div class="row-tag blue">OPTION</div>
</div>
""",
            unsafe_allow_html=True,
        )
    st.markdown('</div>',unsafe_allow_html=True)

elif page == "Live Draft":
    if scope == "Combined":
        live_league = st.selectbox("Live League",["Shiva","Shiva 2.0"])
    else:
        live_league = scope

    st.info("The selected league is connected automatically. League IDs stay hidden.")

    uploaded = st.file_uploader(
        "Upload verified 2026 rankings for live recommendations",
        type=["csv"],
        key="live_rankings",
    )
    rankings = load_rankings(uploaded)
    slot = st.number_input("Your Draft Slot",1,10,9,1,key="live_slot")

    @st.fragment(run_every="5s")
    def live_panel():
        picks,status = fetch_live_draft(live_league)
        st.caption(status)

        if picks.empty:
            current_overall = 1
            drafted_ids:set[int] = set()
            st.write("Waiting for the draft to begin.")
        else:
            current_overall = int(picks["overallPickNumber"].max())+1
            drafted_ids = set(
                pd.to_numeric(picks["playerId"],errors="coerce")
                .dropna().astype(int).tolist()
            )

        schedule = pd.DataFrame(snake_schedule(int(slot),10,16))
        future = schedule[schedule["Overall"] >= current_overall]
        next_pick = int(future["Overall"].iloc[0]) if not future.empty else None

        st.markdown(
            f"""
<div class="triple-grid">
  <div class="stat-box">
    <div class="stat-label">Current Pick</div>
    <div class="stat-value">{current_overall}</div>
  </div>
  <div class="stat-box">
    <div class="stat-label">Your Next Pick</div>
    <div class="stat-value blue">{next_pick if next_pick else "—"}</div>
  </div>
  <div class="stat-box">
    <div class="stat-label">Picks Until You</div>
    <div class="stat-value green">{next_pick-current_overall if next_pick else "—"}</div>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

        if rankings.empty:
            st.warning("Upload current rankings to activate live recommendations.")
            return

        available = rankings.copy()
        if drafted_ids and "espn_player_id" in available.columns:
            available = available[
                ~available["espn_player_id"].fillna(-999999).astype(int).isin(drafted_ids)
            ]

        fits = player_fit(available,rows,next_pick or current_overall)

        st.markdown('<div class="section-label">Recommended Pick</div>',unsafe_allow_html=True)
        st.markdown('<div class="card">',unsafe_allow_html=True)
        for _,player in fits.head(5).iterrows():
            st.markdown(
                f"""
<div class="list-row">
  <div><span class="pos-badge pos-{player['position']}">{player['position']}</span></div>
  <div>
    <div class="row-title">{player['player_name']}</div>
    <div class="row-sub">{player['Why']} · ADP {float(player['adp']):.1f}</div>
  </div>
  <div class="row-tag">{player['Fit']}</div>
</div>
""",
                unsafe_allow_html=True,
            )
        st.markdown('</div>',unsafe_allow_html=True)

    live_panel()

else:
    st.markdown('<div class="section-label">Historical Reference</div>',unsafe_allow_html=True)
    rules,_,_ = personalized_rules(rows)
    score = weighted_score(rows)
    profile = historical_rules(rows)

    st.markdown(
        f"""
<div class="card">
  <div class="hero-row">
    <div>
      <div class="card-sub">Historical Draft Grade</div>
      <div class="hero-grade">{letter_grade(score)}</div>
    </div>
    <div>
      <div class="hero-rank">{team_name}</div>
      <div class="hero-note">{manager} · {scope}</div>
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
<div class="triple-grid">
  <div class="stat-box">
    <div class="stat-label">Best Position</div>
    <div class="stat-value blue">{profile['best_position']}</div>
  </div>
  <div class="stat-box">
    <div class="stat-label">Best Round</div>
    <div class="stat-value green">{f"R{profile['best_round']}" if profile['best_round'] else "—"}</div>
  </div>
  <div class="stat-box">
    <div class="stat-label">Weakest Round</div>
    <div class="stat-value red">{f"R{profile['worst_round']}" if profile['worst_round'] else "—"}</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
