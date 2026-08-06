from __future__ import annotations

import math
import sqlite3
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import plotly.express as px
import requests
import streamlit as st

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "shiva_draft_roi.sqlite"
LOCAL_RANKINGS = APP_DIR / "current_rankings.csv"

st.set_page_config(
    page_title="Shiva Draft Intelligence",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
:root{
  --bg:#0b0d0f;--card:#1d1f21;--card2:#252729;--line:#373a3d;
  --muted:#a1a5aa;--white:#f7f8fa;--green:#35f23e;
  --blue:#5b96ff;--red:#ff4e59;--gold:#ffb52b;
}
.stApp{background:linear-gradient(180deg,#000 0,#000 116px,var(--bg) 116px);color:var(--white);}
.block-container{max-width:1180px;padding-top:0;padding-bottom:4rem;}
#MainMenu,footer,header{visibility:hidden;}
html,body,[class*="css"]{font-family:"Arial Narrow","Roboto Condensed","Helvetica Neue",Arial,sans-serif;}
.shiva-banner{
  position:sticky;top:0;z-index:999;margin:0 -1rem 12px;padding:18px 18px 13px;
  background:#000;border-bottom:1px solid #242629;color:#fff;
  font-size:clamp(1.05rem,4vw,1.65rem);font-weight:1000;text-transform:uppercase;
}
.shiva-banner:after{content:"";display:block;height:4px;width:100%;margin-top:10px;background:var(--green);}
.control-shell,.grade-card,.summary-card,.war-card{
  background:var(--card);border:1px solid var(--line);border-radius:18px;
  box-shadow:0 8px 24px rgba(0,0,0,.28);
}
.control-shell{padding:14px 14px 4px;margin-bottom:14px;}
.control-title,.eyebrow{
  color:var(--muted);font-size:.76rem;font-weight:1000;letter-spacing:.08em;text-transform:uppercase;
}
.control-title{color:#fff;margin-bottom:3px;}
.control-sub{color:var(--muted);font-size:.76rem;margin-bottom:8px;}
.grade-card,.war-card{padding:18px;margin:8px 0 16px;}
.grade-value{color:var(--green);font-size:3.35rem;line-height:1;font-weight:1000;margin-top:6px;}
.grade-sub{color:#fff;font-weight:900;margin-top:8px;}
.summary-card{padding:14px 16px;margin:8px 0 14px;}
.summary-title{color:#fff;font-size:1.15rem;font-weight:1000;}
.summary-sub{color:var(--muted);font-size:.84rem;margin-top:3px;}
h1,h2,h3,h4,p,label,.stMarkdown{color:var(--white)!important;}
h1,h2,h3{font-weight:1000!important;letter-spacing:-.02em;}
[data-baseweb="select"]>div{
  background:var(--card2)!important;border:1px solid #474b4f!important;
  border-radius:999px!important;min-height:47px;
}
[data-baseweb="select"] span,[data-baseweb="select"] input{color:var(--blue)!important;font-weight:900!important;}
.stSelectbox label p,.stRadio label p,.stNumberInput label p,.stFileUploader label p{
  color:#e8e8e8!important;font-weight:900!important;
}
div[role="radiogroup"]{background:var(--card);border:1px solid #303337;border-radius:15px;padding:8px 10px;}
div[data-testid="stMetric"]{
  background:var(--card);border:1px solid var(--line);border-radius:14px;
  padding:14px 15px;overflow:visible;box-shadow:0 9px 24px rgba(0,0,0,.24);
}
div[data-testid="stMetricLabel"]{
  color:var(--muted);font-size:.72rem;font-weight:900;letter-spacing:.055em;text-transform:uppercase;
}
div[data-testid="stMetricValue"]{
  color:var(--green);font-size:clamp(1.25rem,3vw,1.9rem)!important;font-weight:1000;
  white-space:nowrap!important;overflow:visible!important;text-overflow:clip!important;
}
[data-testid="stDataFrame"],[data-testid="stPlotlyChart"]{
  background:var(--card)!important;border:1px solid #34373a!important;border-radius:14px!important;overflow:hidden;
}
.stButton button,.stDownloadButton button{
  color:var(--blue)!important;background:transparent!important;border:2px solid var(--blue)!important;
  border-radius:999px!important;font-weight:1000!important;width:100%;
}
@media(max-width:900px){
  section[data-testid="stSidebar"]{display:none!important;}
  .block-container{padding-left:.65rem!important;padding-right:.65rem!important;}
  .shiva-banner{margin-left:-.65rem!important;margin-right:-.65rem!important;}
  div[data-testid="stMetric"]{padding:11px 9px!important;}
  div[data-testid="stMetricValue"]{font-size:1rem!important;}
  .grade-value{font-size:2.7rem;}
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown('<div class="shiva-banner">SHIVA LEAGUE DRAFT INTELLIGENCE</div>', unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def load_history() -> pd.DataFrame:
    with sqlite3.connect(DB_PATH) as con:
        return pd.read_sql_query(
            """
            SELECT *
            FROM draft_roi_scores
            ORDER BY league_name, season, overall_pick
            """,
            con,
        )


history = load_history()

# Deduplicate player-season outcomes before calculating historical benchmarks.
player_seasons = (
    history[
        [
            "season","player_id","player_name","position",
            "position_finish_total","position_finish_ppg",
            "fantasy_points_ppr","ppg","games_played",
        ]
    ]
    .drop_duplicates(["season","player_id","position"])
    .copy()
)

finish_benchmarks = (
    player_seasons.groupby(["position","position_finish_total"], as_index=False)
    .agg(
        Expected_Points=("fantasy_points_ppr","mean"),
        Expected_PPG=("ppg","mean"),
        Benchmark_Seasons=("season","nunique"),
    )
    .rename(columns={"position_finish_total":"position_draft_rank"})
)

graded_base = history.merge(
    finish_benchmarks,
    on=["position","position_draft_rank"],
    how="left",
)

managers = sorted(graded_base["manager_name"].dropna().unique().tolist())
scopes = ["Combined","Shiva","Shiva 2.0"]
seasons = ["Career"] + [str(x) for x in sorted(graded_base["season"].unique(), reverse=True)]


def default_manager_index() -> int:
    for name in ("Chris H","Chris Hart"):
        if name in managers:
            return managers.index(name)
    return 0


# ---------------- STRICTER HISTORICAL GRADING ----------------

def finish_buffer(expected_rank: int) -> int:
    if expected_rank <= 5:
        return 2
    if expected_rank <= 12:
        return 4
    if expected_rank <= 24:
        return 6
    return 9


def round_weight(round_number: int) -> float:
    weights = {
        1:1.00,2:0.92,3:0.84,4:0.74,5:0.64,6:0.55,7:0.46,8:0.38,
        9:0.29,10:0.22,11:0.17,12:0.13,13:0.10,14:0.08,15:0.06,16:0.05,
    }
    return weights.get(int(round_number),0.05)


def grade_pick(row: pd.Series) -> pd.Series:
    expected = int(row["position_draft_rank"])
    actual = int(row["position_finish_total"])
    buffer = finish_buffer(expected)
    gap = actual - expected

    expected_points = float(row["Expected_Points"]) if pd.notna(row["Expected_Points"]) else np.nan
    expected_ppg = float(row["Expected_PPG"]) if pd.notna(row["Expected_PPG"]) else np.nan

    points_ratio = (
        float(row["fantasy_points_ppr"]) / expected_points
        if pd.notna(expected_points) and expected_points > 0 else np.nan
    )
    ppg_ratio = (
        float(row["ppg"]) / expected_ppg
        if pd.notna(expected_ppg) and expected_ppg > 0 else np.nan
    )

    finish_pass = gap <= buffer
    production_pass = (
        (pd.notna(points_ratio) and points_ratio >= 0.85)
        or (pd.notna(ppg_ratio) and ppg_ratio >= 0.90)
    )
    injury_protection = (
        not finish_pass
        and pd.notna(ppg_ratio)
        and ppg_ratio >= 0.95
        and int(row["games_played"]) <= 13
    )
    clear_steal = (
        actual <= max(1, expected - buffer)
        and (
            (pd.notna(points_ratio) and points_ratio >= 1.05)
            or (pd.notna(ppg_ratio) and ppg_ratio >= 1.05)
        )
    )

    if clear_steal:
        result = "Steal"
    elif finish_pass and production_pass:
        result = "Hit"
    elif injury_protection:
        result = "Injury-Protected"
    else:
        result = "Bust"

    # Strict, explainable score:
    # 55% finish vs draft cost, 30% total production, 15% PPG.
    finish_score = max(0.0, min(100.0, 100 - max(0, gap - buffer) * 6.5))
    points_score = max(0.0, min(110.0, points_ratio * 100)) if pd.notna(points_ratio) else 45.0
    ppg_score = max(0.0, min(110.0, ppg_ratio * 100)) if pd.notna(ppg_ratio) else 45.0
    pick_score = 0.55 * finish_score + 0.30 * points_score + 0.15 * ppg_score

    # Injury protection prevents an F, but does not award a strong grade.
    if result == "Injury-Protected":
        pick_score = min(max(pick_score, 58.0), 69.0)

    return pd.Series(
        {
            "Finish Buffer":buffer,
            "Expected Points":expected_points,
            "Expected PPG":expected_ppg,
            "Points vs Expected %":points_ratio * 100 if pd.notna(points_ratio) else np.nan,
            "PPG vs Expected %":ppg_ratio * 100 if pd.notna(ppg_ratio) else np.nan,
            "Result":result,
            "Pick Score":max(0.0,min(100.0,pick_score)),
            "Round Weight":round_weight(int(row["round"])),
        }
    )


graded = graded_base.join(graded_base.apply(grade_pick, axis=1))


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
    return float(np.average(rows["Pick Score"], weights=rows["Round Weight"]))


def filter_history(manager: str, scope: str, season: str) -> pd.DataFrame:
    rows = graded[graded["manager_name"].eq(manager)].copy()
    if scope != "Combined":
        rows = rows[rows["league_name"].eq(scope)]
    if season != "Career":
        rows = rows[rows["season"].eq(int(season))]
    return rows


def manager_board(scope: str, season: str) -> pd.DataFrame:
    pool = graded.copy()
    if scope != "Combined":
        pool = pool[pool["league_name"].eq(scope)]
    if season != "Career":
        pool = pool[pool["season"].eq(int(season))]

    rows = []
    for manager_name, group in pool.groupby("manager_name"):
        score = weighted_score(group)
        rows.append(
            {
                "Manager":manager_name,
                "Draft Score":score,
                "Draft Grade":letter_grade(score),
                "Hit Rate":group["Result"].isin(["Hit","Steal"]).mean() * 100,
                "Steal Rate":group["Result"].eq("Steal").mean() * 100,
                "Injury-Protected":group["Result"].eq("Injury-Protected").mean() * 100,
                "Bust Rate":group["Result"].eq("Bust").mean() * 100,
                "Picks":len(group),
            }
        )
    board = pd.DataFrame(rows).sort_values(
        ["Draft Score","Hit Rate"], ascending=False
    ).reset_index(drop=True)
    board.insert(0,"League Rank",board.index + 1)
    return board


def round_summary(rows: pd.DataFrame) -> pd.DataFrame:
    output = []
    for rnd, group in rows.groupby("round"):
        score = float(group["Pick Score"].mean())
        output.append(
            {
                "Round":int(rnd),
                "Grade":letter_grade(score),
                "Hit Rate":group["Result"].isin(["Hit","Steal"]).mean() * 100,
                "Steal Rate":group["Result"].eq("Steal").mean() * 100,
                "Bust Rate":group["Result"].eq("Bust").mean() * 100,
                "Picks":len(group),
                "_score":score,
            }
        )
    return pd.DataFrame(output).sort_values("Round")


def position_summary(rows: pd.DataFrame) -> pd.DataFrame:
    output = []
    for position, group in rows.groupby("position"):
        score = float(group["Pick Score"].mean())
        output.append(
            {
                "Position":position,
                "Grade":letter_grade(score),
                "Hit Rate":group["Result"].isin(["Hit","Steal"]).mean() * 100,
                "Steal Rate":group["Result"].eq("Steal").mean() * 100,
                "Bust Rate":group["Result"].eq("Bust").mean() * 100,
                "Picks":len(group),
                "_score":score,
            }
        )
    return pd.DataFrame(output).sort_values("_score",ascending=False)


def show_table(table: pd.DataFrame) -> None:
    if table.empty:
        st.info("No data for this selection.")
        return
    formats = {
        column:"{:.1f}%"
        for column in table.columns
        if column.endswith("Rate") or column == "Injury-Protected"
    }
    formats.update({
        column:"{:.1f}"
        for column in table.columns
        if column in {"PPR Points","Historical Avg Points","PPG","Historical Avg PPG","Draft Score"}
    })
    st.dataframe(table.style.format(formats), use_container_width=True, hide_index=True)


# ---------------- DRAFT WAR ROOM ----------------

def snake_picks(draft_slot: int, team_count: int, rounds: int) -> list[dict[str,int]]:
    picks = []
    for rnd in range(1, rounds + 1):
        if rnd % 2 == 1:
            overall = (rnd - 1) * team_count + draft_slot
        else:
            overall = rnd * team_count - draft_slot + 1
        picks.append({"Round":rnd,"Overall Pick":overall})
    return picks


def load_rankings(uploaded_file: Any) -> pd.DataFrame:
    if uploaded_file is not None:
        rankings = pd.read_csv(uploaded_file)
    elif LOCAL_RANKINGS.exists():
        rankings = pd.read_csv(LOCAL_RANKINGS)
    else:
        return pd.DataFrame()

    required = {"player_name","position","adp","projected_points","projected_ppg"}
    missing = required - set(rankings.columns)
    if missing:
        st.error("Rankings file is missing: " + ", ".join(sorted(missing)))
        return pd.DataFrame()

    for optional, default in {
        "espn_player_id":np.nan,
        "team":"",
        "tier":np.nan,
        "injury_status":"",
    }.items():
        if optional not in rankings.columns:
            rankings[optional] = default

    rankings["adp"] = pd.to_numeric(rankings["adp"],errors="coerce")
    rankings["projected_points"] = pd.to_numeric(rankings["projected_points"],errors="coerce")
    rankings["projected_ppg"] = pd.to_numeric(rankings["projected_ppg"],errors="coerce")
    rankings["espn_player_id"] = pd.to_numeric(rankings["espn_player_id"],errors="coerce")
    return rankings.dropna(subset=["player_name","position","adp"])


def espn_headers() -> dict[str,str]:
    return {
        "User-Agent":"Mozilla/5.0",
        "Accept":"application/json",
    }


def fetch_espn_draft(
    league_id: int,
    season_id: int,
    swid: str = "",
    espn_s2: str = "",
) -> tuple[pd.DataFrame,str]:
    url = (
        f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/"
        f"seasons/{season_id}/segments/0/leagues/{league_id}"
        f"?view=mDraftDetail&view=mTeam&view=mStatus"
    )
    cookies = {}
    if swid:
        cookies["SWID"] = swid
    if espn_s2:
        cookies["espn_s2"] = espn_s2

    try:
        response = requests.get(
            url,
            headers=espn_headers(),
            cookies=cookies,
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
    except Exception as exc:
        return pd.DataFrame(), f"ESPN feed error: {exc}"

    picks = ((data.get("draftDetail") or {}).get("picks") or [])
    rows = []
    for pick in picks:
        rows.append(
            {
                "overall_pick":pick.get("overallPickNumber"),
                "round":pick.get("roundId"),
                "round_pick":pick.get("roundPickNumber"),
                "team_id":pick.get("teamId"),
                "espn_player_id":pick.get("playerId"),
            }
        )
    return pd.DataFrame(rows), "Connected"


def recommendation_board(
    rankings: pd.DataFrame,
    drafted_ids: set[int],
    drafted_names: set[str],
    current_overall_pick: int,
    roster_positions: list[str],
    strategy: str,
) -> pd.DataFrame:
    available = rankings.copy()

    if drafted_ids and "espn_player_id" in available:
        available = available[
            ~available["espn_player_id"].fillna(-999999).astype(int).isin(drafted_ids)
        ]
    if drafted_names:
        available = available[
            ~available["player_name"].str.lower().isin({name.lower() for name in drafted_names})
        ]

    if available.empty:
        return available

    # Better projections and players falling past ADP rate higher.
    available["Projection Score"] = available["projected_points"].rank(pct=True) * 100
    available["PPG Score"] = available["projected_ppg"].rank(pct=True) * 100
    available["ADP Value"] = current_overall_pick - available["adp"]

    position_counts = pd.Series(roster_positions).value_counts().to_dict()
    need_bonus = []
    for pos in available["position"]:
        bonus = 0.0
        if pos == "RB" and position_counts.get("RB",0) < 2:
            bonus += 12
        if pos == "WR" and position_counts.get("WR",0) < 2:
            bonus += 12
        if pos == "TE" and position_counts.get("TE",0) < 1:
            bonus += 5
        if pos == "QB" and position_counts.get("QB",0) < 1:
            bonus += 5

        if strategy == "RB Heavy" and pos == "RB":
            bonus += 10
        elif strategy == "WR Heavy" and pos == "WR":
            bonus += 10
        elif strategy == "Best Player Available":
            bonus += 0
        need_bonus.append(bonus)

    available["Roster Fit"] = need_bonus
    available["Recommendation Score"] = (
        0.46 * available["Projection Score"]
        + 0.24 * available["PPG Score"]
        + 1.4 * available["ADP Value"].clip(-20,20)
        + available["Roster Fit"]
    )

    return available.sort_values(
        ["Recommendation Score","projected_points"],
        ascending=False,
    )


st.markdown(
    '<div class="control-shell"><div class="control-title">League Controls</div><div class="control-sub">Choose a report or open the Draft War Room.</div></div>',
    unsafe_allow_html=True,
)

page = st.radio(
    "View",
    [
        "📈 Historical Report Card",
        "⚔️ Head-to-Head",
        "🏅 League Leaderboard",
        "🎯 Draft Projector",
        "🔴 Live Draft War Room",
        "📘 How Grades Work",
    ],
    horizontal=True,
)
page = page.split(" ",1)[1]


if page == "Historical Report Card":
    c1,c2,c3 = st.columns([1.5,1,1])
    manager = c1.selectbox("Manager",managers,index=default_manager_index())
    scope = c2.selectbox("League",scopes)
    season = c3.selectbox("Season",seasons)

    rows = filter_history(manager,scope,season)
    board = manager_board(scope,season)
    board_row = board[board["Manager"].eq(manager)]
    score = weighted_score(rows)
    rank = int(board_row["League Rank"].iloc[0]) if not board_row.empty else None

    st.markdown(
        f"""
<div class="grade-card">
  <div class="eyebrow">Overall Draft Grade</div>
  <div class="grade-value">{letter_grade(score)}</div>
  <div class="grade-sub">Draft Score {score:.1f}/100 · League Rank #{rank if rank else "—"}</div>
</div>
""",
        unsafe_allow_html=True,
    )

    a,b,c = st.columns(3)
    a.metric("Hit Rate",f"{rows['Result'].isin(['Hit','Steal']).mean()*100:.1f}%" if not rows.empty else "—")
    b.metric("Steal Rate",f"{rows['Result'].eq('Steal').mean()*100:.1f}%" if not rows.empty else "—")
    c.metric("Bust Rate",f"{rows['Result'].eq('Bust').mean()*100:.1f}%" if not rows.empty else "—")

    st.subheader("Round-by-Round Report Card")
    rounds = round_summary(rows)
    show_table(rounds[["Round","Grade","Hit Rate","Steal Rate","Bust Rate","Picks"]])

    st.subheader("Position Report Card")
    positions = position_summary(rows)
    show_table(positions[["Position","Grade","Hit Rate","Steal Rate","Bust Rate","Picks"]])

    st.subheader("Pick-by-Pick Explanation")
    picks = rows[
        [
            "season","league_name","round","player_name","position",
            "position_draft_rank","position_finish_total",
            "fantasy_points_ppr","Expected Points","ppg","Expected PPG","Result",
        ]
    ].rename(
        columns={
            "season":"Season","league_name":"League","round":"Round",
            "player_name":"Player","position":"Pos",
            "position_draft_rank":"Drafted As","position_finish_total":"Finished As",
            "fantasy_points_ppr":"PPR Points","Expected Points":"Historical Avg Points",
            "ppg":"PPG","Expected PPG":"Historical Avg PPG",
        }
    )
    picks["Drafted As"] = picks["Pos"] + picks["Drafted As"].astype(int).astype(str)
    picks["Finished As"] = picks["Pos"] + picks["Finished As"].astype(int).astype(str)
    show_table(picks)


elif page == "Head-to-Head":
    a,b,c,d = st.columns(4)
    manager_a = a.selectbox("Manager A",managers,index=default_manager_index())
    manager_b = b.selectbox("Manager B",managers,index=1 if len(managers)>1 else 0)
    scope = c.selectbox("League",scopes)
    season = d.selectbox("Season",seasons)

    board = manager_board(scope,season)
    display = board[board["Manager"].isin([manager_a,manager_b])][
        ["League Rank","Manager","Draft Grade","Hit Rate","Steal Rate","Injury-Protected","Bust Rate","Picks"]
    ]
    show_table(display)


elif page == "League Leaderboard":
    a,b = st.columns(2)
    scope = a.selectbox("League",scopes)
    season = b.selectbox("Season",seasons)
    show_table(
        manager_board(scope,season)[
            ["League Rank","Manager","Draft Grade","Hit Rate","Steal Rate","Injury-Protected","Bust Rate","Picks"]
        ]
    )


elif page == "Draft Projector":
    st.title("Draft Projector")
    a,b,c,d = st.columns(4)
    teams = a.number_input("Teams",min_value=8,max_value=16,value=10,step=1)
    slot = b.number_input("Your Draft Slot",min_value=1,max_value=int(teams),value=min(9,int(teams)),step=1)
    rounds = c.number_input("Rounds",min_value=8,max_value=20,value=16,step=1)
    strategy = d.selectbox("Strategy",["RB Heavy","Balanced","WR Heavy","Best Player Available"])

    uploaded = st.file_uploader(
        "Upload current verified rankings/projections CSV",
        type=["csv"],
        help="Required columns: player_name, position, adp, projected_points, projected_ppg. Optional: espn_player_id, team, tier, injury_status.",
    )
    rankings = load_rankings(uploaded)

    schedule = pd.DataFrame(snake_picks(int(slot),int(teams),int(rounds)))
    st.subheader("Your Snake-Draft Pick Schedule")
    st.dataframe(schedule,use_container_width=True,hide_index=True)

    if rankings.empty:
        st.warning(
            "No current rankings file is loaded, so the app will not invent player recommendations. "
            "Upload a verified 2026 rankings/projections CSV to activate targets."
        )
    else:
        st.subheader("Round-by-Round Target Windows")
        target_rows = []
        for _,pick in schedule.iterrows():
            overall = int(pick["Overall Pick"])
            window = rankings[
                rankings["adp"].between(max(1,overall-8),overall+12)
            ].sort_values(["adp","projected_points"],ascending=[True,False]).head(8)
            target_rows.append(
                {
                    "Round":int(pick["Round"]),
                    "Your Pick":overall,
                    "Realistic Targets":", ".join(window["player_name"].tolist()),
                }
            )
        st.dataframe(pd.DataFrame(target_rows),use_container_width=True,hide_index=True)


elif page == "Live Draft War Room":
    st.title("Live ESPN Draft War Room")
    st.caption("The feed polls ESPN. Current recommendations require your verified rankings CSV.")

    a,b,c,d = st.columns(4)
    league_id = a.number_input("ESPN League ID",min_value=1,value=1465338,step=1)
    season_id = b.number_input("Season",min_value=2026,value=2026,step=1)
    teams = c.number_input("Teams",min_value=8,max_value=16,value=10,step=1)
    slot = d.number_input("Your Draft Slot",min_value=1,max_value=int(teams),value=min(9,int(teams)),step=1)

    strategy = st.selectbox("Draft Strategy",["RB Heavy","Balanced","WR Heavy","Best Player Available"])
    uploaded = st.file_uploader("Upload verified current rankings/projections CSV",type=["csv"],key="live_rankings")
    rankings = load_rankings(uploaded)

    swid = ""
    espn_s2 = ""
    try:
        swid = st.secrets.get("ESPN_SWID","")
        espn_s2 = st.secrets.get("ESPN_S2","")
    except Exception:
        pass

    @st.fragment(run_every="5s")
    def live_board() -> None:
        picks,status = fetch_espn_draft(int(league_id),int(season_id),swid,espn_s2)
        st.write(f"Feed status: **{status}**")

        if picks.empty:
            st.info("No completed draft picks are currently visible.")
            drafted_ids:set[int] = set()
            current_overall = 1
        else:
            picks = picks.sort_values("overall_pick")
            drafted_ids = set(
                picks["espn_player_id"].dropna().astype(int).tolist()
            )
            current_overall = int(picks["overall_pick"].max()) + 1
            st.dataframe(picks.tail(20),use_container_width=True,hide_index=True)

        schedule = pd.DataFrame(snake_picks(int(slot),int(teams),16))
        future = schedule[schedule["Overall Pick"] >= current_overall]
        next_user_pick = int(future["Overall Pick"].iloc[0]) if not future.empty else None
        picks_until = next_user_pick - current_overall if next_user_pick is not None else None

        m1,m2,m3 = st.columns(3)
        m1.metric("Current Overall Pick",current_overall)
        m2.metric("Your Next Pick",next_user_pick if next_user_pick is not None else "Draft Complete")
        m3.metric("Picks Until Your Turn",picks_until if picks_until is not None else "—")

        if rankings.empty:
            st.warning("Upload current rankings to activate recommendations.")
            return

        roster_positions:list[str] = []
        recommendation = recommendation_board(
            rankings=rankings,
            drafted_ids=drafted_ids,
            drafted_names=set(),
            current_overall_pick=next_user_pick or current_overall,
            roster_positions=roster_positions,
            strategy=strategy,
        )

        if recommendation.empty:
            st.info("No available players remain in the rankings file.")
            return

        display = recommendation.head(15)[
            [
                "player_name","position","team","adp","projected_points",
                "projected_ppg","tier","injury_status","ADP Value",
                "Roster Fit","Recommendation Score",
            ]
        ].rename(
            columns={
                "player_name":"Player","position":"Pos","team":"Team","adp":"ADP",
                "projected_points":"Projected Points","projected_ppg":"Projected PPG",
                "tier":"Tier","injury_status":"Injury Status",
            }
        )
        st.subheader("Best Available Recommendations")
        st.dataframe(display.style.format({
            "ADP":"{:.1f}","Projected Points":"{:.1f}","Projected PPG":"{:.1f}",
            "ADP Value":"{:.1f}","Recommendation Score":"{:.1f}",
        }),use_container_width=True,hide_index=True)

    live_board()


else:
    st.title("How Grades Work")
    st.markdown(
        """
### Stricter draft grading

Every pick is judged by:

1. Where he was drafted at his position.
2. Where he finished at his position.
3. His total PPR points compared with the historical average for that drafted positional rank.
4. His PPG compared with the same historical expectation.

### Results

- **Steal:** Clearly beat the expected finish and delivered strong production.
- **Hit:** Passed both the finish test and production test.
- **Injury-Protected:** Missed the total finish test, but delivered at least 95% of expected PPG in 13 or fewer games. This prevents an automatic bust, but does not award a high grade.
- **Bust:** Failed the required finish/production standard.

### Finish buffers

- Drafted 1–5: within 2 spots.
- Drafted 6–12: within 4 spots.
- Drafted 13–24: within 6 spots.
- Drafted 25+: within 9 spots.

### Overall grade weighting

Rounds 1–3 count the most. Rounds 9–16 carry sharply reduced weight. A late-round miss cannot outweigh an early-round bust.

### Draft War Room data rule

The War Room never invents current rankings. It requires a verified current rankings/projections CSV. The live ESPN feed removes drafted players when matching ESPN player IDs are present.
"""
    )
