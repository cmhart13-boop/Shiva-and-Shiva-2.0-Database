from __future__ import annotations

import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
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
    page_title="Shiva League",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
:root{
  --bg:#111113;
  --top:#080809;
  --card:#1c1c1e;
  --card2:#242426;
  --line:#2d2d30;
  --muted:#7d7e84;
  --white:#f5f5f7;
  --green:#28f33d;
  --blue:#5898ff;
  --red:#ff515b;
  --gold:#ffb52b;
}
html,body,[class*="css"]{
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
}
.stApp{background:var(--bg);color:var(--white);}
.block-container{max-width:430px;padding:0 14px 52px!important;}
#MainMenu,footer,header{visibility:hidden;}

.espn-top{
  position:sticky;top:0;z-index:999;margin:0 -14px 14px;
  background:var(--top);border-bottom:1px solid #222225;
}
.espn-title-row{
  position:relative;display:flex;align-items:center;justify-content:space-between;
  padding:13px 14px 7px;min-height:34px;
}
.espn-back{color:#d8d8da;font-size:15px;font-weight:600;}
.espn-title{
  position:absolute;left:50%;transform:translateX(-50%);
  color:#fff;font-size:15px;font-weight:900;text-transform:uppercase;white-space:nowrap;
}
.espn-tabs{display:flex;border-bottom:1px solid #232326;padding:0 14px;}
.espn-tab{
  flex:1;text-align:center;color:#6f7076;font-size:11px;font-weight:900;
  letter-spacing:.06em;text-transform:uppercase;padding:10px 0 9px;
}
.espn-tab.active{color:#fff;border-bottom:3px solid var(--green);}

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
.hero-row{display:flex;align-items:flex-end;justify-content:space-between;gap:12px;}
.hero-grade{color:var(--green);font-size:58px;line-height:.9;font-weight:1000;}
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
.stat-value{color:#fff;font-size:19px;font-weight:1000;line-height:1.05;}
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
.row-sub{color:#7f8085;font-size:10px;margin-top:2px;}
.row-grade{font-size:16px;font-weight:1000;color:var(--green);}
.row-grade.red{color:var(--red);}
.row-grade.blue{color:var(--blue);}

.pos-badge{
  display:inline-flex;align-items:center;justify-content:center;width:34px;height:23px;
  border-radius:6px;font-size:10px;font-weight:1000;color:#111;
}
.pos-RB{background:#56d78d}.pos-WR{background:#6bb8ff}.pos-QB{background:#ff6b70}.pos-TE{background:#c78cff}

.result{
  font-size:10px;font-weight:1000;text-align:right;text-transform:uppercase;
}
.result-Steal{color:#70c8ff}.result-Hit{color:var(--green)}
.result-Bust{color:var(--red)}.result-Injury-Protected{color:var(--gold)}

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
<div class="espn-top">
  <div class="espn-title-row">
    <div class="espn-back">‹ League</div>
    <div class="espn-title">Shiva League</div>
    <div style="width:48px"></div>
  </div>
  <div class="espn-tabs">
    <div class="espn-tab">League</div>
    <div class="espn-tab active">League History</div>
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
        full = pd.read_sql_query(
            "SELECT * FROM draft_picks_full WHERE season<=2025 ORDER BY league_name,season,overall_pick",
            con,
        )
    return roi, full


roi, full_draft = load_data()
latest_season = int(roi["season"].max())

# Current franchises only: exactly 10 teams per league from the latest completed season.
current_franchises = (
    roi[roi["season"].eq(latest_season)]
    [["league_name","team_id","team_name","manager_name","owner_id"]]
    .drop_duplicates(["league_name","team_id"])
    .sort_values(["league_name","team_id"])
)

# Historical player benchmarks for each positional finish (RB5, WR7, etc.).
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


def current_managers_for_scope(scope: str) -> list[str]:
    if scope == "Combined":
        return sorted(current_franchises["manager_name"].unique().tolist())
    return sorted(
        current_franchises[current_franchises["league_name"].eq(scope)]
        ["manager_name"].unique().tolist()
    )


def franchise_rows(manager_name: str,scope: str) -> pd.DataFrame:
    current = current_franchises[current_franchises["manager_name"].eq(manager_name)]
    if scope != "Combined":
        current = current[current["league_name"].eq(scope)]

    keys = set(zip(current["league_name"],current["team_id"]))
    if not keys:
        return graded.iloc[0:0].copy()

    mask = graded.apply(
        lambda row:(row["league_name"],row["team_id"]) in keys,
        axis=1,
    )
    # Historical picks stay with the current franchise, even if a previous person managed it.
    return graded[mask].copy()


def franchise_name(manager_name: str,scope: str) -> str:
    current = current_franchises[current_franchises["manager_name"].eq(manager_name)]
    if scope != "Combined":
        current = current[current["league_name"].eq(scope)]
    names = current["team_name"].dropna().unique().tolist()
    return " / ".join(names) if names else manager_name


def round_summary(rows: pd.DataFrame) -> pd.DataFrame:
    output = []
    for rnd,group in rows.groupby("round"):
        score = float(group["Pick Score"].mean())
        best = group.loc[group["Pick Score"].idxmax()]
        worst = group.loc[group["Pick Score"].idxmin()]
        output.append({
            "Round":int(rnd),
            "Grade":letter_grade(score),
            "Score":score,
            "Best Pick":f"{best['player_name']} ({int(best['season'])})",
            "Worst Pick":f"{worst['player_name']} ({int(worst['season'])})",
            "Picks":len(group),
        })
    return pd.DataFrame(output).sort_values("Round")


def position_summary(rows: pd.DataFrame) -> pd.DataFrame:
    output = []
    for pos,group in rows.groupby("position"):
        score = float(group["Pick Score"].mean())
        output.append({
            "Position":pos,
            "Grade":letter_grade(score),
            "Score":score,
            "Picks":len(group),
        })
    return pd.DataFrame(output).sort_values("Score",ascending=False)


def draft_tendencies(rows: pd.DataFrame) -> list[tuple[str,str]]:
    if rows.empty:
        return []

    early = rows[rows["round"] <= 3]
    early_counts = early["position"].value_counts()
    favorite_early = early_counts.index[0] if not early_counts.empty else "—"

    qb_rounds = rows[rows["position"].eq("QB")]["round"]
    avg_qb = f"Round {qb_rounds.mean():.1f}" if not qb_rounds.empty else "Rarely drafts QB"

    rb_share = (early["position"].eq("RB").mean()*100) if not early.empty else 0
    wr_share = (early["position"].eq("WR").mean()*100) if not early.empty else 0

    return [
        ("Early-Round Identity",f"{favorite_early}-first"),
        ("Average First QB",avg_qb),
        ("Rounds 1–3 RB Share",f"{rb_share:.0f}%"),
        ("Rounds 1–3 WR Share",f"{wr_share:.0f}%"),
    ]


def leaderboard(scope: str) -> pd.DataFrame:
    rows = []
    for manager in current_managers_for_scope(scope):
        fr = franchise_rows(manager,scope)
        score = weighted_score(fr)
        pos = position_summary(fr)
        strength = (
            f"{pos.iloc[0]['Position']} ({pos.iloc[0]['Grade']})"
            if not pos.empty else "—"
        )
        rows.append({
            "Manager":manager,
            "Team":franchise_name(manager,scope),
            "Grade":letter_grade(score),
            "Score":score,
            "Best Strength":strength,
        })
    return pd.DataFrame(rows).sort_values("Score",ascending=False).reset_index(drop=True)


def render_ranked_rows(table: pd.DataFrame,best: bool=True):
    if table.empty:
        st.info("No draft history available.")
        return
    ordered = table.sort_values("Score",ascending=not best).head(3)
    for i,(_,row) in enumerate(ordered.iterrows(),1):
        color = "" if best else " red"
        detail = row["Best Pick"] if best else row["Worst Pick"]
        st.markdown(
            f"""
<div class="list-row">
  <div class="rank-circle">{i}</div>
  <div>
    <div class="row-title">Round {int(row['Round'])}</div>
    <div class="row-sub">{detail}</div>
  </div>
  <div class="row-grade{color}">{row['Grade']}</div>
</div>
""",
            unsafe_allow_html=True,
        )


# Main navigation.
page = st.radio(
    "Section",
    ["League History","Draft DNA","League Intelligence","Draft War Room"],
    horizontal=True,
    label_visibility="collapsed",
)

if page == "League History":
    scope = st.selectbox("League",["Shiva","Shiva 2.0","Combined"])
    managers = current_managers_for_scope(scope)
    manager = st.selectbox("Current Manager",managers)

    rows = franchise_rows(manager,scope)
    score = weighted_score(rows)
    board = leaderboard(scope)
    rank = int(board.index[board["Manager"].eq(manager)][0])+1 if manager in board["Manager"].values else 0

    rounds = round_summary(rows)
    positions = position_summary(rows)

    st.markdown('<div class="section-label">Franchise Snapshot</div>',unsafe_allow_html=True)
    st.markdown(
        f"""
<div class="card">
  <div class="card-title">{franchise_name(manager,scope)}</div>
  <div class="card-sub">{manager} · {scope}</div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
<div class="card">
  <div class="hero-row">
    <div>
      <div class="card-sub" style="text-transform:uppercase;font-weight:900;letter-spacing:.08em">Historical Draft Grade</div>
      <div class="hero-grade">{letter_grade(score)}</div>
    </div>
    <div>
      <div class="hero-rank">#{rank} of {len(board)}</div>
      <div class="hero-note">Current franchises only</div>
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    best_round = rounds.sort_values("Score",ascending=False).iloc[0] if not rounds.empty else None
    weak_round = rounds.sort_values("Score").iloc[0] if not rounds.empty else None
    best_pos = positions.iloc[0] if not positions.empty else None

    st.markdown(
        f"""
<div class="triple-grid">
  <div class="stat-box">
    <div class="stat-label">Best Round</div>
    <div class="stat-value green">{f"R{int(best_round['Round'])}" if best_round is not None else "—"}</div>
  </div>
  <div class="stat-box">
    <div class="stat-label">Weakest Round</div>
    <div class="stat-value red">{f"R{int(weak_round['Round'])}" if weak_round is not None else "—"}</div>
  </div>
  <div class="stat-box">
    <div class="stat-label">Best Position</div>
    <div class="stat-value blue">{best_pos['Position'] if best_pos is not None else "—"}</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-label">Best Drafting Rounds</div>',unsafe_allow_html=True)
    st.markdown('<div class="card">',unsafe_allow_html=True)
    render_ranked_rows(rounds,True)
    st.markdown('</div>',unsafe_allow_html=True)

    st.markdown('<div class="section-label">Weakest Drafting Rounds</div>',unsafe_allow_html=True)
    st.markdown('<div class="card">',unsafe_allow_html=True)
    render_ranked_rows(rounds,False)
    st.markdown('</div>',unsafe_allow_html=True)

elif page == "Draft DNA":
    scope = st.selectbox("League",["Shiva","Shiva 2.0","Combined"])
    managers = current_managers_for_scope(scope)
    manager = st.selectbox("Current Manager",managers)
    rows = franchise_rows(manager,scope)

    st.markdown('<div class="section-label">Position Strengths</div>',unsafe_allow_html=True)
    positions = position_summary(rows)
    st.markdown('<div class="card">',unsafe_allow_html=True)
    for _,row in positions.iterrows():
        st.markdown(
            f"""
<div class="list-row">
  <div><span class="pos-badge pos-{row['Position']}">{row['Position']}</span></div>
  <div>
    <div class="row-title">{row['Position']} Drafting</div>
    <div class="row-sub">{int(row['Picks'])} historical picks</div>
  </div>
  <div class="row-grade">{row['Grade']}</div>
</div>
""",
            unsafe_allow_html=True,
        )
    st.markdown('</div>',unsafe_allow_html=True)

    st.markdown('<div class="section-label">Draft Tendencies</div>',unsafe_allow_html=True)
    st.markdown('<div class="card">',unsafe_allow_html=True)
    for label,value in draft_tendencies(rows):
        st.markdown(
            f"""
<div class="list-row">
  <div class="rank-circle">•</div>
  <div><div class="row-title">{label}</div></div>
  <div class="row-grade blue">{value}</div>
</div>
""",
            unsafe_allow_html=True,
        )
    st.markdown('</div>',unsafe_allow_html=True)

    st.markdown('<div class="section-label">Biggest Steals</div>',unsafe_allow_html=True)
    st.markdown('<div class="card">',unsafe_allow_html=True)
    for _,row in rows.sort_values("Pick Score",ascending=False).head(5).iterrows():
        st.markdown(
            f"""
<div class="list-row">
  <div><span class="pos-badge pos-{row['position']}">{row['position']}</span></div>
  <div>
    <div class="row-title">{row['player_name']}</div>
    <div class="row-sub">{int(row['season'])} · Round {int(row['round'])} · Drafted {row['position']}{int(row['position_draft_rank'])} · Finished {row['position']}{int(row['position_finish_total'])}</div>
  </div>
  <div class="result result-{row['Result']}">{row['Result']}</div>
</div>
""",
            unsafe_allow_html=True,
        )
    st.markdown('</div>',unsafe_allow_html=True)

    st.markdown('<div class="section-label">Biggest Busts</div>',unsafe_allow_html=True)
    st.markdown('<div class="card">',unsafe_allow_html=True)
    for _,row in rows.sort_values("Pick Score").head(5).iterrows():
        st.markdown(
            f"""
<div class="list-row">
  <div><span class="pos-badge pos-{row['position']}">{row['position']}</span></div>
  <div>
    <div class="row-title">{row['player_name']}</div>
    <div class="row-sub">{int(row['season'])} · Round {int(row['round'])} · Drafted {row['position']}{int(row['position_draft_rank'])} · Finished {row['position']}{int(row['position_finish_total'])}</div>
  </div>
  <div class="result result-{row['Result']}">{row['Result']}</div>
</div>
""",
            unsafe_allow_html=True,
        )
    st.markdown('</div>',unsafe_allow_html=True)

elif page == "League Intelligence":
    scope = st.selectbox("League",["Shiva","Shiva 2.0","Combined"])
    board = leaderboard(scope)
    st.markdown('<div class="section-label">Drafting Power Rankings</div>',unsafe_allow_html=True)
    st.markdown('<div class="card">',unsafe_allow_html=True)
    for idx,row in board.iterrows():
        st.markdown(
            f"""
<div class="list-row">
  <div class="rank-circle">{idx+1}</div>
  <div>
    <div class="row-title">{row['Manager']}</div>
    <div class="row-sub">{row['Team']} · Best: {row['Best Strength']}</div>
  </div>
  <div class="row-grade">{row['Grade']}</div>
</div>
""",
            unsafe_allow_html=True,
        )
    st.markdown('</div>',unsafe_allow_html=True)

else:
    war_league = st.selectbox("League",["Shiva","Shiva 2.0"])
    tab1,tab2 = st.tabs(["DRAFT PROJECTOR","LIVE DRAFT"])

    with tab1:
        teams = 10
        c1,c2 = st.columns(2)
        slot = c1.number_input("Your Draft Slot",1,10,9,1)
        rounds = c2.number_input("Rounds",8,20,16,1)

        schedule = []
        for rnd in range(1,int(rounds)+1):
            overall = (
                (rnd-1)*teams+int(slot)
                if rnd%2==1
                else rnd*teams-int(slot)+1
            )
            schedule.append({"Round":rnd,"Your Pick":overall})
        st.dataframe(pd.DataFrame(schedule),use_container_width=True,hide_index=True)

        uploaded = st.file_uploader(
            "Upload verified current rankings",
            type=["csv"],
            help="Required columns: player_name, position, adp, projected_points, projected_ppg",
        )
        rankings_path = uploaded if uploaded is not None else CURRENT_RANKINGS if CURRENT_RANKINGS.exists() else None

        if rankings_path is None:
            st.warning("Upload current rankings to activate player recommendations. The app will not guess.")
        else:
            rankings = pd.read_csv(rankings_path)
            required = {"player_name","position","adp","projected_points","projected_ppg"}
            missing = required-set(rankings.columns)
            if missing:
                st.error("Missing columns: "+", ".join(sorted(missing)))
            else:
                st.markdown('<div class="section-label">Round Targets</div>',unsafe_allow_html=True)
                for pick in schedule[:10]:
                    overall = pick["Your Pick"]
                    targets = rankings[
                        rankings["adp"].between(max(1,overall-8),overall+12)
                    ].sort_values(["adp","projected_points"],ascending=[True,False]).head(4)

                    st.markdown(
                        f'<div class="card-title" style="margin:12px 0 5px">Round {pick["Round"]} · Pick {overall}</div>',
                        unsafe_allow_html=True,
                    )
                    st.markdown('<div class="card">',unsafe_allow_html=True)
                    for _,player in targets.iterrows():
                        pos = str(player["position"])
                        st.markdown(
                            f"""
<div class="list-row">
  <div><span class="pos-badge pos-{pos}">{pos}</span></div>
  <div>
    <div class="row-title">{player['player_name']}</div>
    <div class="row-sub">ADP {float(player['adp']):.1f} · {float(player['projected_points']):.1f} projected PPR points</div>
  </div>
  <div class="row-grade blue">{float(player['projected_ppg']):.1f}</div>
</div>
""",
                            unsafe_allow_html=True,
                        )
                    st.markdown('</div>',unsafe_allow_html=True)

    with tab2:
        st.info("The live feed uses the selected league automatically. League IDs are hidden from the app.")

        def fetch_live():
            league_id = LEAGUE_IDS[war_league]
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

        @st.fragment(run_every="5s")
        def live_feed():
            picks,status = fetch_live()
            st.caption(status)
            if picks.empty:
                st.write("Waiting for the draft to begin.")
            else:
                columns = [
                    c for c in
                    ["overallPickNumber","roundId","roundPickNumber","teamId","playerId"]
                    if c in picks.columns
                ]
                st.dataframe(
                    picks[columns].sort_values("overallPickNumber").tail(20),
                    use_container_width=True,
                    hide_index=True,
                )

        live_feed()
