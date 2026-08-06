from __future__ import annotations

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
  --bg:#0b0d0f;
  --black:#000000;
  --card:#1d1f21;
  --card2:#252729;
  --line:#373a3d;
  --muted:#a1a5aa;
  --white:#f7f8fa;
  --green:#35f23e;
  --blue:#5b96ff;
  --red:#ff4e59;
  --gold:#ffb52b;
}

html,body,[class*="css"]{
  font-family:"Arial Narrow","Roboto Condensed","Helvetica Neue",Arial,sans-serif;
}

.stApp{
  background:linear-gradient(180deg,#000 0,#000 118px,var(--bg) 118px,var(--bg) 100%);
  color:var(--white);
}

.block-container{
  max-width:1180px;
  padding-top:0;
  padding-bottom:4rem;
}

#MainMenu,footer,header{visibility:hidden;}

.shiva-splash{
  position:fixed;
  inset:0;
  z-index:999999;
  background:#0828bd;
  display:flex;
  align-items:center;
  justify-content:center;
  animation:splashFade .55s ease 1.8s forwards;
}

.shiva-logo-svg{
  width:150px;
  height:176px;
  display:block;
}

@keyframes splashFade{
  0%{opacity:1;visibility:visible;}
  99%{opacity:0;visibility:visible;}
  100%{opacity:0;visibility:hidden;pointer-events:none;}
}

.shiva-banner{
  position:sticky;
  top:0;
  z-index:999;
  margin:0 -1rem 12px;
  padding:18px 18px 13px;
  background:#000;
  border-bottom:1px solid #242629;
  color:#fff;
  font-size:clamp(1.05rem,4vw,1.65rem);
  font-weight:1000;
  letter-spacing:.015em;
  line-height:1.05;
  text-transform:uppercase;
}

.shiva-banner span{color:#fff;}

.shiva-banner:after{
  content:"";
  display:block;
  height:4px;
  width:100%;
  margin-top:10px;
  background:var(--green);
}

.mobile-filter-shell{
  background:var(--card);
  border:1px solid var(--line);
  border-radius:18px;
  padding:14px 14px 4px;
  margin:0 0 14px;
  box-shadow:0 8px 24px rgba(0,0,0,.28);
}

.mobile-filter-title{
  font-size:.82rem;
  font-weight:1000;
  letter-spacing:.08em;
  text-transform:uppercase;
  color:#fff;
  margin-bottom:4px;
}

.mobile-filter-sub{
  font-size:.76rem;
  color:var(--muted);
  margin-bottom:8px;
}

h1,h2,h3,h4,p,label,.stMarkdown{color:var(--white)!important;}
h1,h2,h3{font-weight:1000!important;letter-spacing:-.02em;}
hr{border-color:#313438;}

[data-baseweb="select"]>div{
  background:var(--card2)!important;
  border:1px solid #474b4f!important;
  border-radius:999px!important;
  min-height:47px;
}

[data-baseweb="select"] span,
[data-baseweb="select"] input{
  color:var(--blue)!important;
  font-weight:900!important;
}

.stSelectbox label p,.stRadio label p{
  color:#e8e8e8!important;
  font-weight:900!important;
}

div[role="radiogroup"]{
  background:var(--card);
  border:1px solid #303337;
  border-radius:15px;
  padding:8px 10px;
}

div[data-testid="stMetric"]{
  background:var(--card);
  border:1px solid var(--line);
  border-radius:14px;
  padding:14px 15px;
  min-width:0;
  overflow:visible;
  box-shadow:0 9px 24px rgba(0,0,0,.24);
}

div[data-testid="stMetricLabel"]{
  color:var(--muted);
  font-size:.72rem;
  font-weight:900;
  letter-spacing:.055em;
  text-transform:uppercase;
}

div[data-testid="stMetricValue"]{
  color:var(--green);
  font-size:clamp(1.35rem,3vw,2rem)!important;
  font-weight:1000;
  white-space:nowrap!important;
  overflow:visible!important;
  text-overflow:clip!important;
  min-width:max-content;
  line-height:1.05;
}

[data-testid="stDataFrame"],
[data-testid="stPlotlyChart"]{
  background:var(--card)!important;
  border:1px solid #34373a!important;
  border-radius:14px!important;
  overflow:hidden;
}

.stDownloadButton button,.stButton button{
  color:var(--blue)!important;
  background:transparent!important;
  border:2px solid var(--blue)!important;
  border-radius:999px!important;
  font-weight:1000!important;
  width:100%;
}

.grade-card{
  background:var(--card);
  border:1px solid var(--line);
  border-radius:18px;
  padding:18px;
  margin:8px 0 16px;
  box-shadow:0 10px 26px rgba(0,0,0,.25);
}

.grade-label{
  color:var(--muted);
  font-size:.78rem;
  font-weight:900;
  letter-spacing:.08em;
  text-transform:uppercase;
}

.grade-value{
  color:var(--green);
  font-size:3.4rem;
  line-height:1;
  font-weight:1000;
  margin-top:6px;
}

.grade-sub{
  color:#fff;
  font-weight:800;
  margin-top:8px;
}

.profile-strip{
  background:var(--card);
  border:1px solid var(--line);
  border-radius:16px;
  padding:14px 16px;
  margin:8px 0 14px;
}

.profile-title{
  color:#fff;
  font-size:1.2rem;
  font-weight:1000;
}

.profile-sub{
  color:var(--muted);
  font-size:.85rem;
  margin-top:2px;
}

@media(max-width:900px){
  section[data-testid="stSidebar"]{display:none!important;}
  .block-container{
    padding-left:.65rem!important;
    padding-right:.65rem!important;
  }
  .shiva-banner{
    margin-left:-.65rem!important;
    margin-right:-.65rem!important;
  }
  div[data-testid="stMetric"]{padding:11px 9px!important;}
  div[data-testid="stMetricValue"]{
    font-size:1.05rem!important;
    white-space:nowrap!important;
  }
  .grade-value{font-size:2.8rem;}
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="shiva-splash" aria-label="Shiva Draft Intelligence loading">
  <svg class="shiva-logo-svg" viewBox="0 0 220 250" role="img" aria-label="Shiva S logo">
    <path d="M28 24 H192 L180 166 Q174 203 110 230 Q46 203 40 166 Z"
          fill="none" stroke="#C8FF00" stroke-width="15" stroke-linejoin="round"/>
    <text x="110" y="154" text-anchor="middle"
          font-family="Arial Black, Arial, sans-serif" font-size="128"
          font-style="italic" font-weight="900" fill="#C8FF00">S</text>
  </svg>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="shiva-banner">SHIVA LEAGUE <span>DRAFT INTELLIGENCE MATRIX</span></div>',
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


roi = load_data()
managers = sorted(roi["manager_name"].dropna().unique().tolist())
scopes = ["Combined", "Shiva", "Shiva 2.0"]
seasons = ["Career"] + [str(x) for x in sorted(roi["season"].unique(), reverse=True)]


def default_idx() -> int:
    for candidate in ("Chris H", "Chris Hart"):
        if candidate in managers:
            return managers.index(candidate)
    return 0


def filt(manager: str, scope: str, season: str) -> pd.DataFrame:
    x = roi[roi["manager_name"].eq(manager)].copy()
    if scope != "Combined":
        x = x[x["league_name"].eq(scope)]
    if season != "Career":
        x = x[x["season"].eq(int(season))]
    return x


def grade_from_percentile(percentile: float) -> str:
    if percentile >= 97:
        return "A+"
    if percentile >= 92:
        return "A"
    if percentile >= 87:
        return "A-"
    if percentile >= 82:
        return "B+"
    if percentile >= 75:
        return "B"
    if percentile >= 68:
        return "B-"
    if percentile >= 60:
        return "C+"
    if percentile >= 50:
        return "C"
    if percentile >= 40:
        return "C-"
    if percentile >= 30:
        return "D+"
    if percentile >= 20:
        return "D"
    return "F"


def manager_board(scope: str, season: str) -> pd.DataFrame:
    x = roi.copy()
    if scope != "Combined":
        x = x[x["league_name"].eq(scope)]
    if season != "Career":
        x = x[x["season"].eq(int(season))]
    if x.empty:
        return pd.DataFrame()

    board = (
        x.groupby("manager_name", as_index=False)
        .agg(
            Picks=("player_name", "count"),
            Draft_Value=("final_draft_roi", "mean"),
            PPG_Value=("ppg_roi", "mean"),
            Steals=("classification", lambda s: int(s.eq("Steal").sum())),
            Met=("classification", lambda s: int(s.eq("Met Expectations").sum())),
            Busts=("classification", lambda s: int(s.eq("Bust").sum())),
        )
    )
    board["Hit Rate"] = (board["Steals"] + board["Met"]) / board["Picks"] * 100
    board = board.sort_values(
        ["Draft_Value", "PPG_Value"],
        ascending=False,
    ).reset_index(drop=True)
    board.insert(0, "League Rank", board.index + 1)
    board["Percentile"] = board["Draft_Value"].rank(pct=True, method="average") * 100
    board["Draft Grade"] = board["Percentile"].apply(grade_from_percentile)
    return board


def summary(x: pd.DataFrame, manager: str, scope: str, season: str) -> dict:
    if x.empty:
        return {
            "picks": 0,
            "draft_value": np.nan,
            "ppg_value": np.nan,
            "steals": 0,
            "met": 0,
            "busts": 0,
            "hit_rate": np.nan,
            "grade": "—",
            "rank": "—",
        }

    board = manager_board(scope, season)
    row = board[board["manager_name"].eq(manager)]
    league_rank = int(row["League Rank"].iloc[0]) if not row.empty else None
    grade = row["Draft Grade"].iloc[0] if not row.empty else "—"

    steals = int(x["classification"].eq("Steal").sum())
    met = int(x["classification"].eq("Met Expectations").sum())
    busts = int(x["classification"].eq("Bust").sum())
    hit_rate = (steals + met) / len(x) * 100

    return {
        "picks": len(x),
        "draft_value": x["final_draft_roi"].mean(),
        "ppg_value": x["ppg_roi"].mean(),
        "steals": steals,
        "met": met,
        "busts": busts,
        "hit_rate": hit_rate,
        "grade": grade,
        "rank": f"#{league_rank}" if league_rank else "—",
    }


def round_table(x: pd.DataFrame) -> pd.DataFrame:
    if x.empty:
        return pd.DataFrame()
    return (
        x.groupby("round", as_index=False)
        .agg(
            Picks=("player_name", "count"),
            Draft_Value=("final_draft_roi", "mean"),
            PPG_Value=("ppg_roi", "mean"),
            Steal_Pct=("classification", lambda s: s.eq("Steal").mean() * 100),
            Hit_Pct=("classification", lambda s: s.isin(["Steal", "Met Expectations"]).mean() * 100),
            Bust_Pct=("classification", lambda s: s.eq("Bust").mean() * 100),
        )
        .rename(
            columns={
                "round": "Round",
                "Draft_Value": "Average Draft Value",
                "PPG_Value": "PPG-Adjusted Value",
                "Steal_Pct": "Steal %",
                "Hit_Pct": "Hit Rate",
                "Bust_Pct": "Bust %",
            }
        )
    )


def position_table(x: pd.DataFrame) -> pd.DataFrame:
    if x.empty:
        return pd.DataFrame()
    return (
        x.groupby("position", as_index=False)
        .agg(
            Picks=("player_name", "count"),
            Draft_Value=("final_draft_roi", "mean"),
            PPG_Value=("ppg_roi", "mean"),
            Steal_Pct=("classification", lambda s: s.eq("Steal").mean() * 100),
            Hit_Pct=("classification", lambda s: s.isin(["Steal", "Met Expectations"]).mean() * 100),
            Bust_Pct=("classification", lambda s: s.eq("Bust").mean() * 100),
        )
        .rename(
            columns={
                "position": "Position",
                "Draft_Value": "Average Draft Value",
                "PPG_Value": "PPG-Adjusted Value",
                "Steal_Pct": "Steal %",
                "Hit_Pct": "Hit Rate",
                "Bust_Pct": "Bust %",
            }
        )
        .sort_values("Average Draft Value", ascending=False)
    )


def best_draft(x: pd.DataFrame) -> str:
    if x.empty:
        return "—"
    seasons_df = (
        x.groupby(["league_name", "season"], as_index=False)
        .agg(Draft_Value=("final_draft_roi", "mean"))
        .sort_values("Draft_Value", ascending=False)
    )
    row = seasons_df.iloc[0]
    return f"{row['league_name']} {int(row['season'])}"


def best_round(x: pd.DataFrame) -> str:
    table = round_table(x)
    if table.empty:
        return "—"
    return f"Round {int(table.loc[table['Average Draft Value'].idxmax(), 'Round'])}"


def worst_round(x: pd.DataFrame) -> str:
    table = round_table(x)
    if table.empty:
        return "—"
    return f"Round {int(table.loc[table['Average Draft Value'].idxmin(), 'Round'])}"


def best_position(x: pd.DataFrame) -> str:
    table = position_table(x)
    if table.empty:
        return "—"
    return str(table.iloc[0]["Position"])


def pick_label(row: pd.Series) -> str:
    return f"{row['player_name']} — {row['league_name']} {int(row['season'])}, Round {int(row['round'])}"


def show_table(df: pd.DataFrame, value_column: str | None = None) -> None:
    if df.empty:
        st.info("No data for this selection.")
        return

    fmt = {}
    for column in df.columns:
        if "Value" in column:
            fmt[column] = "{:.2f}"
        elif column.endswith("%") or column == "Hit Rate":
            fmt[column] = "{:.1f}%"

    styler = df.style.format(fmt)
    if value_column and value_column in df.columns:
        styler = styler.background_gradient(
            subset=[value_column],
            cmap="RdYlGn",
        )
    st.dataframe(styler, use_container_width=True, hide_index=True)


def style_fig(fig, title: str):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#1d1f21",
        plot_bgcolor="#1d1f21",
        font=dict(color="#f6f7f8"),
        title=title,
        margin=dict(l=18, r=18, t=48, b=18),
    )
    fig.update_xaxes(gridcolor="#34373a", zerolinecolor="#34373a")
    fig.update_yaxes(gridcolor="#34373a", zerolinecolor="#34373a")
    return fig


st.markdown(
    '<div class="mobile-filter-shell"><div class="mobile-filter-title">League History Controls</div><div class="mobile-filter-sub">Tap any field to change the manager, league, season, or report.</div></div>',
    unsafe_allow_html=True,
)

fc1, fc2, fc3 = st.columns([1.45, 1, 1])
manager = fc1.selectbox("👤 Manager", managers, index=default_idx(), key="main_manager")
scope = fc2.selectbox("🏈 League", scopes, key="main_scope")
season = fc3.selectbox("📅 Season", seasons, key="main_season")

page_choice = st.radio(
    "Report",
    [
        "📈 Manager Report Card",
        "⚔️ Head-to-Head",
        "🏅 League Leaderboard",
        "🔥 Draft Heatmap",
        "🧾 All Picks",
        "📘 Methodology",
    ],
    horizontal=True,
    key="main_page",
)
page = page_choice.split(" ", 1)[1]


if page == "Manager Report Card":
    x = filt(manager, scope, season)
    s = summary(x, manager, scope, season)

    st.markdown(
        f'<div class="profile-strip"><div class="profile-title">{manager}</div><div class="profile-sub">{scope} · {season}</div></div>',
        unsafe_allow_html=True,
    )

    left, right = st.columns([1, 2.2])
    with left:
        st.markdown(
            f"""
<div class="grade-card">
  <div class="grade-label">Overall Draft Grade</div>
  <div class="grade-value">{s['grade']}</div>
  <div class="grade-sub">League Rank {s['rank']}</div>
</div>
""",
            unsafe_allow_html=True,
        )

    with right:
        a, b, c = st.columns(3)
        a.metric("Hit Rate", "—" if pd.isna(s["hit_rate"]) else f"{s['hit_rate']:.1f}%")
        b.metric("Steals", s["steals"])
        c.metric("Busts", s["busts"])

        d, e, f = st.columns(3)
        d.metric("Best Round", best_round(x))
        e.metric("Best Position", best_position(x))
        f.metric("Best Draft", best_draft(x))

    if not x.empty:
        best_pick_row = x.loc[x["final_draft_roi"].idxmax()]
        worst_pick_row = x.loc[x["final_draft_roi"].idxmin()]
        g, h = st.columns(2)
        g.metric("Best Pick Ever", pick_label(best_pick_row))
        h.metric("Worst Pick Ever", pick_label(worst_pick_row))

    st.markdown("### Round-by-Round Performance")
    rounds = round_table(x)
    show_table(rounds, "Average Draft Value")

    if not rounds.empty:
        fig = px.bar(
            rounds,
            x="Round",
            y="Average Draft Value",
            color="Average Draft Value",
            color_continuous_scale="RdYlGn",
        )
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(style_fig(fig, "Average Draft Value by Round"), use_container_width=True)

    st.markdown("### Position Performance")
    show_table(position_table(x), "Average Draft Value")

    steals_col, busts_col = st.columns(2)
    pick_columns = [
        "league_name",
        "season",
        "round",
        "player_name",
        "position",
        "position_draft_rank",
        "position_finish_total",
        "position_finish_ppg",
        "ppg",
        "games_played",
        "final_draft_roi",
    ]
    rename = {
        "league_name": "League",
        "season": "Season",
        "round": "Round",
        "player_name": "Player",
        "position": "Pos",
        "position_draft_rank": "Drafted Pos",
        "position_finish_total": "Total Finish",
        "position_finish_ppg": "PPG Finish",
        "ppg": "PPG",
        "games_played": "Games",
        "final_draft_roi": "Draft Value",
    }

    with steals_col:
        st.markdown("### Top 10 Steals")
        show_table(
            x.nlargest(10, "final_draft_roi")[pick_columns].rename(columns=rename),
            "Draft Value",
        )

    with busts_col:
        st.markdown("### Top 10 Busts")
        show_table(
            x.nsmallest(10, "final_draft_roi")[pick_columns].rename(columns=rename),
            "Draft Value",
        )


elif page == "Head-to-Head":
    st.title("Manager Head-to-Head")
    a, b, c, d = st.columns(4)
    manager_a = a.selectbox("Manager A", managers, index=default_idx())
    manager_b = b.selectbox("Manager B", managers, index=1 if len(managers) > 1 else 0)
    compare_scope = c.selectbox("League Scope", scopes)
    compare_season = d.selectbox("Season", seasons)

    xa = filt(manager_a, compare_scope, compare_season)
    xb = filt(manager_b, compare_scope, compare_season)
    sa = summary(xa, manager_a, compare_scope, compare_season)
    sb = summary(xb, manager_b, compare_scope, compare_season)

    comparison = pd.DataFrame(
        [
            ["Draft Grade", sa["grade"], sb["grade"]],
            ["League Rank", sa["rank"], sb["rank"]],
            ["Hit Rate", sa["hit_rate"], sb["hit_rate"]],
            ["Steals", sa["steals"], sb["steals"]],
            ["Busts", sa["busts"], sb["busts"]],
            ["Best Round", best_round(xa), best_round(xb)],
            ["Best Position", best_position(xa), best_position(xb)],
            ["Best Draft", best_draft(xa), best_draft(xb)],
        ],
        columns=["Metric", manager_a, manager_b],
    )
    st.dataframe(comparison, use_container_width=True, hide_index=True)

    pa = position_table(xa)[["Position", "Average Draft Value"]].rename(
        columns={"Average Draft Value": manager_a}
    )
    pb = position_table(xb)[["Position", "Average Draft Value"]].rename(
        columns={"Average Draft Value": manager_b}
    )
    pc = pa.merge(pb, on="Position", how="outer").fillna(0)

    if not pc.empty:
        fig = px.bar(
            pc.melt(id_vars="Position", var_name="Manager", value_name="Average Draft Value"),
            x="Position",
            y="Average Draft Value",
            color="Manager",
            barmode="group",
        )
        st.plotly_chart(style_fig(fig, "Position Drafting Comparison"), use_container_width=True)


elif page == "League Leaderboard":
    st.title("League Draft Efficiency Leaderboard")
    a, b = st.columns(2)
    board_scope = a.selectbox("League Scope", scopes)
    board_season = b.selectbox("Season", seasons)

    board = manager_board(board_scope, board_season)
    if board.empty:
        st.info("No data for this selection.")
    else:
        display = board[
            [
                "League Rank",
                "manager_name",
                "Draft Grade",
                "Hit Rate",
                "Steals",
                "Busts",
                "Picks",
            ]
        ].rename(columns={"manager_name": "Manager"})
        show_table(display)


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
                values="final_draft_roi",
                aggfunc="mean",
            )
            .sort_index()
            .reindex(columns=list(range(1, 17)))
        )
        fig = px.imshow(
            pivot,
            aspect="auto",
            color_continuous_scale="RdYlGn",
            labels={"x": "Round", "y": "Season", "color": "Draft Value"},
        )
        st.plotly_chart(style_fig(fig, "Draft Value Heatmap"), use_container_width=True)
        st.dataframe(
            pivot.style.background_gradient(cmap="RdYlGn", axis=None),
            use_container_width=True,
        )


elif page == "All Picks":
    st.title("Complete Pick-Level Draft Value")
    x = filt(manager, scope, season)
    display = x[
        [
            "league_name",
            "season",
            "round",
            "overall_pick",
            "team_name",
            "player_name",
            "position",
            "position_draft_rank",
            "position_finish_total",
            "position_finish_ppg",
            "fantasy_points_ppr",
            "ppg",
            "games_played",
            "final_draft_roi",
            "classification",
        ]
    ].rename(
        columns={
            "league_name": "League",
            "season": "Season",
            "round": "Round",
            "overall_pick": "Overall",
            "team_name": "Team",
            "player_name": "Player",
            "position": "Pos",
            "position_draft_rank": "Drafted Pos Rank",
            "position_finish_total": "Total Finish",
            "position_finish_ppg": "PPG Finish",
            "fantasy_points_ppr": "PPR Points",
            "ppg": "PPG",
            "games_played": "Games",
            "final_draft_roi": "Draft Value",
            "classification": "Result",
        }
    )
    show_table(display, "Draft Value")
    st.download_button(
        "Download filtered CSV",
        display.to_csv(index=False).encode("utf-8"),
        file_name=f"{manager}_{scope}_{season}_draft_value.csv".replace(" ", "_"),
        mime="text/csv",
    )


else:
    st.title("Methodology")
    st.markdown(
        """
### What “Draft Value” Means

The database still calculates a mathematical value internally, but the app translates it into fantasy-football language.

- **Draft Grade:** Your average Draft Value converted into a percentile grade against the other managers in the selected league and season.
- **League Rank:** Your position among all managers for the selected league and season.
- **Hit Rate:** Picks classified as either a Steal or Met Expectations.
- **Steals:** Picks that materially outperformed their positional draft cost.
- **Busts:** Picks that materially underperformed their positional draft cost.
- **Best Round:** The round where your picks generated the highest average Draft Value.
- **Best Position:** The position where your picks generated the highest average Draft Value.
- **Best Draft:** Your highest-rated league-season draft.
- **Best/Worst Pick:** Your highest and lowest individual Draft Value selections.

### Underlying Formula

1. Position Draft Rank = order drafted within position for each league-season.
2. Season finishes = total-point positional rank and PPG positional rank.
3. Near-Hit Buffers:
   - Drafted 1–5: ±2
   - Drafted 6–15: ±4
   - Drafted 16–30: ±7
   - Drafted 31+: ±12
4. Draft Capital Weight = `1 / square_root(round drafted)`.
5. Final Draft Value = 70% total-points value + 30% PPG-adjusted value.
6. After Round 8, finishes outside the positional Top 50 are capped at -0.1 for each value component.

Positive Draft Value means the pick beat expectations. Zero means expectations were met. Negative means the pick underperformed expectations.
"""
    )
