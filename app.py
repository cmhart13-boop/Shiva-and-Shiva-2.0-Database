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


try:
    roi = load_data()
    managers = sorted(roi["manager_name"].dropna().unique().tolist())
    scopes = ["Combined", "Shiva", "Shiva 2.0"]
    seasons = ["Career"] + [str(x) for x in sorted(roi["season"].unique(), reverse=True)]
except Exception:
    roi = pd.DataFrame()
    managers = ["Chris H"]
    scopes = ["Combined"]
    seasons = ["Career"]


def default_idx() -> int:
    for candidate in ("Chris H", "Chris Hart"):
        if candidate in managers:
            return managers.index(candidate)
    return 0


def filt(manager: str, scope: str, season: str) -> pd.DataFrame:
    if roi.empty:
        return roi
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
    if roi.empty:
        return pd.DataFrame()
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
        )
    )
    return board


# --- BASIC USER INTERFACE RENDER CONTROLS ---
st.markdown('<div class="mobile-filter-shell">', unsafe_allow_html=True)
st.markdown('<div class="mobile-filter-title">Dashboard Controls</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    sel_manager = st.selectbox("Manager", managers, index=default_idx())
with col2:
    sel_scope = st.selectbox("League Scope", scopes, index=0)
with col3:
    sel_season = st.selectbox("Season Year", seasons, index=0)

st.markdown('</div>', unsafe_allow_html=True)

# Filter data dynamically based on selections
filtered_df = filt(sel_manager, sel_scope, sel_season)

if not filtered_df.empty:
    st.write(f"Displaying performance data for {sel_manager}")
    st.dataframe(filtered_df)
else:
    st.warning("No performance entries found matching the active dashboard filters.")
