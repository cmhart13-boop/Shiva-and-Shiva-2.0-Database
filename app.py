from __future__ import annotations

import math
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

DB = Path(__file__).with_name("shiva_draft_roi.sqlite")

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
  --bg:#0b0d0f; --card:#1d1f21; --card2:#252729; --line:#373a3d;
  --muted:#a1a5aa; --white:#f7f8fa; --green:#35f23e;
  --blue:#5b96ff; --red:#ff4e59; --gold:#ffb52b;
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

.control-shell,.grade-card,.summary-card{
  background:var(--card);border:1px solid var(--line);border-radius:18px;
  box-shadow:0 8px 24px rgba(0,0,0,.28);
}
.control-shell{padding:14px 14px 4px;margin-bottom:14px;}
.control-title,.eyebrow{
  color:var(--muted);font-size:.76rem;font-weight:1000;letter-spacing:.08em;text-transform:uppercase;
}
.control-title{color:#fff;margin-bottom:3px;}
.control-sub{color:var(--muted);font-size:.76rem;margin-bottom:8px;}

.grade-card{padding:18px;margin:8px 0 16px;}
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
.stSelectbox label p,.stRadio label p{color:#e8e8e8!important;font-weight:900!important;}
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

st.markdown(
    '<div class="shiva-banner">SHIVA LEAGUE DRAFT INTELLIGENCE</div>',
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    with sqlite3.connect(DB) as con:
        return pd.read_sql_query(
            """
            SELECT *
            FROM draft_roi_scores
            ORDER BY league_name, season, overall_pick
            """,
            con,
        )


raw = load_data()

# One player-season outcome can appear in both leagues. Deduplicate before
# calculating historical positional benchmarks.
player_seasons = (
    raw[
        [
            "season",
            "player_id",
            "player_name",
            "position",
            "position_finish_total",
            "position_finish_ppg",
            "fantasy_points_ppr",
            "ppg",
            "games_played",
        ]
    ]
    .drop_duplicates(["season", "player_id", "position"])
    .copy()
)

# Historical benchmark: what the RB5, WR7, QB3, etc. actually scored on
# average across the completed seasons in the database.
finish_benchmarks = (
    player_seasons.groupby(["position", "position_finish_total"], as_index=False)
    .agg(
        Historical_Avg_Points=("fantasy_points_ppr", "mean"),
        Historical_Avg_PPG=("ppg", "mean"),
        Benchmark_Seasons=("season", "nunique"),
    )
    .rename(columns={"position_finish_total": "Expected_Position_Rank"})
)

df = raw.merge(
    finish_benchmarks,
    left_on=["position", "position_draft_rank"],
    right_on=["position", "Expected_Position_Rank"],
    how="left",
)

managers = sorted(df["manager_name"].dropna().unique().tolist())
scopes = ["Combined", "Shiva", "Shiva 2.0"]
seasons = ["Career"] + [str(x) for x in sorted(df["season"].unique(), reverse=True)]


def default_idx() -> int:
    for candidate in ("Chris H", "Chris Hart"):
        if candidate in managers:
            return managers.index(candidate)
    return 0


def rank_buffer(expected_rank: int) -> int:
    if expected_rank <= 5:
        return 3
    if expected_rank <= 12:
        return 5
    if expected_rank <= 24:
        return 8
    return 12


def round_weight(round_number: int) -> float:
    # Premium picks matter much more. Rounds 1-3 dominate the grade;
    # Rounds 10-16 have very little power to hurt or help a manager.
    weights = {
        1: 1.00, 2: 0.90, 3: 0.80, 4: 0.70,
        5: 0.60, 6: 0.52, 7: 0.44, 8: 0.36,
        9: 0.28, 10: 0.22, 11: 0.17, 12: 0.13,
        13: 0.10, 14: 0.08, 15: 0.06, 16: 0.05,
    }
    return weights.get(int(round_number), 0.05)


def classify_pick(row: pd.Series) -> pd.Series:
    expected = int(row["position_draft_rank"])
    actual = int(row["position_finish_total"])
    buffer = rank_buffer(expected)

    rank_gap = actual - expected
    rank_hit = rank_gap <= buffer

    avg_points = row["Historical_Avg_Points"]
    avg_ppg = row["Historical_Avg_PPG"]

    points_ratio = (
        float(row["fantasy_points_ppr"]) / float(avg_points)
        if pd.notna(avg_points) and avg_points > 0
        else np.nan
    )
    ppg_ratio = (
        float(row["ppg"]) / float(avg_ppg)
        if pd.notna(avg_ppg) and avg_ppg > 0
        else np.nan
    )

    # Plain-language result:
    # HIT = close enough to draft expectation OR at least 90% of the historical
    # production normally delivered by that drafted positional rank.
    # STEAL = substantially beat expected finish or historical production.
    # BUST = missed both rank and production expectations.
    if actual <= max(1, expected - buffer) or (
        pd.notna(points_ratio) and points_ratio >= 1.20
    ):
        result = "Steal"
    elif rank_hit or (
        pd.notna(points_ratio)
        and pd.notna(ppg_ratio)
        and max(points_ratio, ppg_ratio) >= 0.90
    ):
        result = "Hit"
    else:
        result = "Bust"

    # Easy-to-explain pick score from 0-100.
    # 50% where he finished vs where drafted.
    # 30% total points vs historical expectation.
    # 20% PPG vs historical expectation, protecting injury-shortened elite play.
    rank_component = max(0.0, min(100.0, 100 - max(0, rank_gap - buffer) * 4))
    points_component = (
        max(0.0, min(120.0, points_ratio * 100))
        if pd.notna(points_ratio)
        else 50.0
    )
    ppg_component = (
        max(0.0, min(120.0, ppg_ratio * 100))
        if pd.notna(ppg_ratio)
        else 50.0
    )

    pick_score = (
        0.50 * rank_component
        + 0.30 * points_component
        + 0.20 * ppg_component
    )

    return pd.Series(
        {
            "Rank Buffer": buffer,
            "Finish Difference": rank_gap,
            "Expected Points": avg_points,
            "Expected PPG": avg_ppg,
            "Points vs Expected %": points_ratio * 100 if pd.notna(points_ratio) else np.nan,
            "PPG vs Expected %": ppg_ratio * 100 if pd.notna(ppg_ratio) else np.nan,
            "Result": result,
            "Pick Score": max(0.0, min(100.0, pick_score)),
            "Round Weight": round_weight(int(row["round"])),
        }
    )


graded = df.join(df.apply(classify_pick, axis=1))


def filt(manager: str, scope: str, season: str) -> pd.DataFrame:
    x = graded[graded["manager_name"].eq(manager)].copy()
    if scope != "Combined":
        x = x[x["league_name"].eq(scope)]
    if season != "Career":
        x = x[x["season"].eq(int(season))]
    return x


def letter_grade(score: float) -> str:
    if pd.isna(score):
        return "—"
    if score >= 93: return "A"
    if score >= 88: return "A-"
    if score >= 83: return "B+"
    if score >= 78: return "B"
    if score >= 73: return "B-"
    if score >= 68: return "C+"
    if score >= 63: return "C"
    if score >= 58: return "C-"
    if score >= 53: return "D"
    return "F"


def weighted_manager_score(x: pd.DataFrame) -> float:
    if x.empty:
        return np.nan
    weights = x["Round Weight"]
    return float(np.average(x["Pick Score"], weights=weights))


def manager_board(scope: str, season: str) -> pd.DataFrame:
    pool = graded.copy()
    if scope != "Combined":
        pool = pool[pool["league_name"].eq(scope)]
    if season != "Career":
        pool = pool[pool["season"].eq(int(season))]

    rows = []
    for manager_name, x in pool.groupby("manager_name"):
        score = weighted_manager_score(x)
        rows.append(
            {
                "Manager": manager_name,
                "Draft Score": score,
                "Draft Grade": letter_grade(score),
                "Hit Rate": x["Result"].isin(["Hit", "Steal"]).mean() * 100,
                "Steal Rate": x["Result"].eq("Steal").mean() * 100,
                "Bust Rate": x["Result"].eq("Bust").mean() * 100,
                "Picks": len(x),
            }
        )

    board = pd.DataFrame(rows).sort_values(
        ["Draft Score", "Hit Rate"],
        ascending=False,
    ).reset_index(drop=True)
    board.insert(0, "League Rank", board.index + 1)
    return board


def round_summary(x: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for round_number, group in x.groupby("round"):
        score = float(group["Pick Score"].mean())
        rows.append(
            {
                "Round": int(round_number),
                "Grade": letter_grade(score),
                "Pick Score": score,
                "Hit Rate": group["Result"].isin(["Hit", "Steal"]).mean() * 100,
                "Steal Rate": group["Result"].eq("Steal").mean() * 100,
                "Bust Rate": group["Result"].eq("Bust").mean() * 100,
                "Picks": len(group),
            }
        )
    return pd.DataFrame(rows).sort_values("Round")


def position_summary(x: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for position, group in x.groupby("position"):
        score = float(group["Pick Score"].mean())
        rows.append(
            {
                "Position": position,
                "Grade": letter_grade(score),
                "Pick Score": score,
                "Hit Rate": group["Result"].isin(["Hit", "Steal"]).mean() * 100,
                "Steal Rate": group["Result"].eq("Steal").mean() * 100,
                "Bust Rate": group["Result"].eq("Bust").mean() * 100,
                "Picks": len(group),
            }
        )
    return pd.DataFrame(rows).sort_values("Pick Score", ascending=False)


def best_meaningful_round(x: pd.DataFrame) -> str:
    # Rounds 1-8 only. A Round 16 hit is fun, but it should not be presented
    # as the manager's most important drafting strength.
    early_middle = round_summary(x[x["round"] <= 8])
    if early_middle.empty:
        return "—"
    row = early_middle.loc[early_middle["Pick Score"].idxmax()]
    return f"Round {int(row['Round'])} ({row['Grade']})"


def worst_meaningful_round(x: pd.DataFrame) -> str:
    early_middle = round_summary(x[x["round"] <= 8])
    if early_middle.empty:
        return "—"
    row = early_middle.loc[early_middle["Pick Score"].idxmin()]
    return f"Round {int(row['Round'])} ({row['Grade']})"


def show_table(table: pd.DataFrame, score_column: str | None = None) -> None:
    if table.empty:
        st.info("No data for this selection.")
        return

    formats = {}
    for col in table.columns:
        if col in {"Pick Score", "Draft Score"}:
            formats[col] = "{:.1f}"
        elif col.endswith("Rate"):
            formats[col] = "{:.1f}%"
        elif col in {"Expected Points", "PPR Points", "Expected PPG", "PPG"}:
            formats[col] = "{:.1f}"
        elif col.endswith("%"):
            formats[col] = "{:.0f}%"

    styler = table.style.format(formats)
    if score_column and score_column in table.columns:
        styler = styler.background_gradient(
            subset=[score_column],
            cmap="RdYlGn",
            vmin=45,
            vmax=95,
        )

    st.dataframe(styler, use_container_width=True, hide_index=True)


st.markdown(
    '<div class="control-shell"><div class="control-title">League History Controls</div><div class="control-sub">Choose any manager, league, season, or report.</div></div>',
    unsafe_allow_html=True,
)

c1, c2, c3 = st.columns([1.5, 1, 1])
manager = c1.selectbox("👤 Manager", managers, index=default_idx())
scope = c2.selectbox("🏈 League", scopes)
season = c3.selectbox("📅 Season", seasons)

page_choice = st.radio(
    "Report",
    [
        "📈 Manager Report Card",
        "⚔️ Head-to-Head",
        "🏅 League Leaderboard",
        "🔥 Draft Heatmap",
        "🧾 All Picks",
        "📘 How Grades Work",
    ],
    horizontal=True,
)
page = page_choice.split(" ", 1)[1]


if page == "Manager Report Card":
    x = filt(manager, scope, season)
    board = manager_board(scope, season)
    manager_row = board[board["Manager"].eq(manager)]

    score = weighted_manager_score(x)
    grade = letter_grade(score)
    rank = (
        int(manager_row["League Rank"].iloc[0])
        if not manager_row.empty
        else None
    )

    hit_rate = x["Result"].isin(["Hit", "Steal"]).mean() * 100 if not x.empty else np.nan
    steal_rate = x["Result"].eq("Steal").mean() * 100 if not x.empty else np.nan
    bust_rate = x["Result"].eq("Bust").mean() * 100 if not x.empty else np.nan

    st.markdown(
        f'<div class="summary-card"><div class="summary-title">{manager}</div><div class="summary-sub">{scope} · {season}</div></div>',
        unsafe_allow_html=True,
    )

    left, right = st.columns([1, 2.25])
    with left:
        st.markdown(
            f"""
<div class="grade-card">
  <div class="eyebrow">Overall Draft Grade</div>
  <div class="grade-value">{grade}</div>
  <div class="grade-sub">Draft Score {score:.1f}/100 · League Rank #{rank if rank else "—"}</div>
</div>
""",
            unsafe_allow_html=True,
        )

    with right:
        a, b, c = st.columns(3)
        a.metric("Hit Rate", "—" if pd.isna(hit_rate) else f"{hit_rate:.1f}%")
        b.metric("Steal Rate", "—" if pd.isna(steal_rate) else f"{steal_rate:.1f}%")
        c.metric("Bust Rate", "—" if pd.isna(bust_rate) else f"{bust_rate:.1f}%")

        d, e, f = st.columns(3)
        d.metric("Best Round (1-8)", best_meaningful_round(x))
        e.metric("Worst Round (1-8)", worst_meaningful_round(x))
        best_pos = position_summary(x)
        f.metric(
            "Best Position",
            "—" if best_pos.empty else f"{best_pos.iloc[0]['Position']} ({best_pos.iloc[0]['Grade']})",
        )

    st.markdown("### Round-by-Round Report Card")
    rounds = round_summary(x)
    show_table(
        rounds[
            ["Round", "Grade", "Hit Rate", "Steal Rate", "Bust Rate", "Picks"]
        ],
    )

    st.markdown("### Position Report Card")
    positions = position_summary(x)
    show_table(
        positions[
            ["Position", "Grade", "Hit Rate", "Steal Rate", "Bust Rate", "Picks"]
        ],
    )

    st.markdown("### Pick-by-Pick Explanation")
    picks = x[
        [
            "season",
            "league_name",
            "round",
            "player_name",
            "position",
            "position_draft_rank",
            "position_finish_total",
            "fantasy_points_ppr",
            "Expected Points",
            "ppg",
            "Expected PPG",
            "Result",
        ]
    ].rename(
        columns={
            "season": "Season",
            "league_name": "League",
            "round": "Round",
            "player_name": "Player",
            "position": "Pos",
            "position_draft_rank": "Drafted As",
            "position_finish_total": "Finished As",
            "fantasy_points_ppr": "PPR Points",
            "Expected Points": "Historical Avg Points",
            "ppg": "PPG",
            "Expected PPG": "Historical Avg PPG",
        }
    )

    picks["Drafted As"] = picks["Pos"] + picks["Drafted As"].astype(int).astype(str)
    picks["Finished As"] = picks["Pos"] + picks["Finished As"].astype(int).astype(str)

    show_table(picks)


elif page == "Head-to-Head":
    st.title("Manager Head-to-Head")
    a, b, c, d = st.columns(4)
    manager_a = a.selectbox("Manager A", managers, index=default_idx())
    manager_b = b.selectbox("Manager B", managers, index=1 if len(managers) > 1 else 0)
    compare_scope = c.selectbox("League Scope", scopes)
    compare_season = d.selectbox("Season", seasons)

    xa = filt(manager_a, compare_scope, compare_season)
    xb = filt(manager_b, compare_scope, compare_season)
    board = manager_board(compare_scope, compare_season)

    def manager_line(name: str, x: pd.DataFrame) -> dict:
        row = board[board["Manager"].eq(name)].iloc[0]
        return {
            "Draft Grade": row["Draft Grade"],
            "League Rank": f"#{int(row['League Rank'])}",
            "Hit Rate": f"{row['Hit Rate']:.1f}%",
            "Steal Rate": f"{row['Steal Rate']:.1f}%",
            "Bust Rate": f"{row['Bust Rate']:.1f}%",
            "Best Round 1-8": best_meaningful_round(x),
            "Worst Round 1-8": worst_meaningful_round(x),
        }

    la = manager_line(manager_a, xa)
    lb = manager_line(manager_b, xb)
    comparison = pd.DataFrame(
        [[metric, la[metric], lb[metric]] for metric in la],
        columns=["Metric", manager_a, manager_b],
    )
    st.dataframe(comparison, use_container_width=True, hide_index=True)


elif page == "League Leaderboard":
    st.title("League Draft Leaderboard")
    a, b = st.columns(2)
    board_scope = a.selectbox("League Scope", scopes)
    board_season = b.selectbox("Season", seasons)

    board = manager_board(board_scope, board_season)
    show_table(
        board[
            [
                "League Rank",
                "Manager",
                "Draft Grade",
                "Hit Rate",
                "Steal Rate",
                "Bust Rate",
                "Picks",
            ]
        ]
    )


elif page == "Draft Heatmap":
    st.title("Draft Heatmap")
    x = filt(manager, scope, "Career")
    if x.empty:
        st.info("No data available.")
    else:
        pivot = (
            x.pivot_table(
                index="season",
                columns="round",
                values="Pick Score",
                aggfunc="mean",
            )
            .sort_index()
            .reindex(columns=list(range(1, 17)))
        )
        fig = px.imshow(
            pivot,
            aspect="auto",
            color_continuous_scale="RdYlGn",
            zmin=45,
            zmax=95,
            labels={"x": "Round", "y": "Season", "color": "Pick Score"},
        )
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#1d1f21",
            plot_bgcolor="#1d1f21",
            title="Pick Grades by Season and Round",
        )
        st.plotly_chart(fig, use_container_width=True)


elif page == "All Picks":
    st.title("All Draft Picks")
    x = filt(manager, scope, season)
    picks = x[
        [
            "season",
            "league_name",
            "round",
            "player_name",
            "position",
            "position_draft_rank",
            "position_finish_total",
            "fantasy_points_ppr",
            "Expected Points",
            "ppg",
            "Expected PPG",
            "Result",
            "Pick Score",
        ]
    ].rename(
        columns={
            "season": "Season",
            "league_name": "League",
            "round": "Round",
            "player_name": "Player",
            "position": "Pos",
            "position_draft_rank": "Drafted As",
            "position_finish_total": "Finished As",
            "fantasy_points_ppr": "PPR Points",
            "Expected Points": "Historical Avg Points",
            "ppg": "PPG",
            "Expected PPG": "Historical Avg PPG",
        }
    )
    picks["Drafted As"] = picks["Pos"] + picks["Drafted As"].astype(int).astype(str)
    picks["Finished As"] = picks["Pos"] + picks["Finished As"].astype(int).astype(str)

    show_table(picks, "Pick Score")


else:
    st.title("How the Draft Grades Work")
    st.markdown(
        """
### Every pick is judged using three things people understand

1. **Where the player was drafted at his position**  
   Example: RB5, WR7, QB3.

2. **Where the player actually finished at his position**  
   Example: drafted RB5 and finished RB7.

3. **How many points he scored compared with the historical average for that drafted position**  
   Example: the app calculates what the average RB5 scored across the completed seasons, then compares the player's points and PPG with that benchmark.

### Hit, Steal, and Bust

- **Steal:** The player substantially beat his drafted positional rank or produced at least 20% more than the historical expectation.
- **Hit:** The player finished within a reasonable positional range or produced at least 90% of the historical expected points or PPG.
- **Bust:** The player missed both the positional-finish expectation and the production expectation.

### The positional-finish buffers

- Drafted 1–5 at the position: within 3 spots is a Hit.
- Drafted 6–12: within 5 spots is a Hit.
- Drafted 13–24: within 8 spots is a Hit.
- Drafted 25+: within 12 spots is a Hit.

### Why early rounds matter more

The overall Draft Grade is weighted heavily toward premium draft capital:

- Round 1 = 100% weight
- Round 2 = 90%
- Round 3 = 80%
- Round 4 = 70%
- Round 5 = 60%
- Round 6 = 52%
- Round 8 = 36%
- Round 10 = 22%
- Round 12 = 13%
- Round 16 = 5%

A Round 2 bust matters far more than a Round 12 miss. Late-round picks cannot dominate the overall grade.

### What the Draft Score means

- 93–100 = A
- 88–92 = A-
- 83–87 = B+
- 78–82 = B
- 73–77 = B-
- 68–72 = C+
- 63–67 = C
- 58–62 = C-
- 53–57 = D
- Below 53 = F

The report shows plain fantasy-football results. The raw calculation stays underneath.
"""
    )
