from __future__ import annotations

import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components

DB = Path(__file__).with_name("shiva_draft_roi.sqlite")

st.set_page_config(
    page_title="Shiva Draft Intelligence",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom injection forcing Streamlit outer divs to respect black themes
st.markdown(
    """
<style>
#MainMenu, footer, header {visibility: hidden;}
.stApp { background-color: #111111; color: #FFFFFF; }
.block-container { padding: 0 !important; max-width: 100% !important; }
</style>
""",
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

# Load database info safely
try:
    roi = load_data()
    managers = sorted(roi["manager_name"].dropna().unique().tolist())
    seasons = ["Career"] + [str(x) for x in sorted(roi["season"].unique(), reverse=True)]
except Exception:
    # Fallback default arrays if local database connection isn't initialized yet
    roi = pd.DataFrame(columns=["manager_name", "league_name", "season", "final_draft_roi", "ppg_roi", "classification"])
    managers = ["Chris H", "Chris Hart", "Password Is Taco"]
    seasons = ["Career", "2025", "2024", "2023"]

scopes = ["Combined", "Shiva", "Shiva 2.0"]

def default_idx() -> int:
    for candidate in ("Chris H", "Chris Hart"):
        if candidate in managers:
            return managers.index(candidate)
    return 0

def grade_from_percentile(percentile: float) -> str:
    if percentile >= 97: return "A+"
    if percentile >= 92: return "A"
    if percentile >= 87: return "A-"
    if percentile >= 82: return "B+"
    if percentile >= 75: return "B"
    if percentile >= 68: return "B-"
    if percentile >= 60: return "C+"
    if percentile >= 50: return "C"
    if percentile >= 40: return "C-"
    if percentile >= 30: return "D+"
    if percentile >= 20: return "D"
    return "F"

# --- REWRITTEN MOBILE RENDER ENGINE ---
# We inject all layout structure directly inside a single crisp, non-scaling component frame
espn_mobile_html = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <script src="https://jsdelivr.net"></script>
  <style>
    body { background-color: #111111; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
    ::-webkit-scrollbar { display: none; }
  </style>
</head>
<body>

  <!-- Hardcoded Mobile Shell Frame forcing 1:1 scaling across devices -->
  <div class="w-full max-w-[420px] mx-auto text-[#E4E4E6] p-4 pb-12 select-none">
    
    <!-- Top Brand Header Banner -->
    <header class="relative flex items-center justify-between py-2 mb-1">
      <button class="flex items-center text-[#E4E4E6] text-[16px] font-normal opacity-90">
        <svg class="w-5 h-5 mr-1 text-[#E4E4E6]" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
        </svg>
        <span>League</span>
      </button>
      <h1 class="absolute left-1/2 -translate-x-1/2 text-[16px] font-bold tracking-tight text-white uppercase">League Info</h1>
      <div class="w-10"></div>
    </header>

    <!-- Sub-Navigation Segmented Navigation Tabs -->
    <nav class="flex border-b border-[#222224] mb-5">
      <button class="w-1/2 pb-2.5 text-center font-bold text-[13px] tracking-wider text-[#727277] uppercase">
        League
      </button>
      <button class="w-1/2 pb-2.5 text-center font-bold text-[13px] tracking-wider text-[#FFFFFF] uppercase relative">
        League History
        <span class="absolute bottom-0 left-0 right-0 h-[2.5px] bg-[#00FF38] rounded-t-full shadow-[0_0_8px_rgba(0,255,56,0.4)]"></span>
      </button>
    </nav>

    <!-- Team Context Header Row -->
    <section class="mb-5">
      <h2 class="text-[11px] font-bold uppercase tracking-wider text-[#727277] mb-2">Team Performance</h2>
      <div class="flex justify-between items-center">
        <!-- Exact Pill Dropdown Recreation -->
        <button class="bg-[#1C1C1E] border border-[#2C2C2E] px-4 py-2.5 rounded-full font-semibold text-[#5496FF] flex items-center space-x-1.5 text-[14px]">
          <span>Password Is Taco</span>
          <svg class="w-3 h-3 text-[#5496FF] mt-0.5" fill="none" stroke="currentColor" stroke-width="3" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
          </svg>
        </button>
        <div class="text-right">
          <span class="text-[10px] font-bold uppercase tracking-wider text-[#727277] block leading-none mb-1">Managers</span>
          <span class="text-[14px] font-medium text-white">Chris H</span>
        </div>
      </div>
    </section>

    <!-- Performance Average Position Card Panel -->
    <section class="bg-[#1C1C1E] rounded-xl p-4 border border-[#242426] mb-4 shadow-xl">
      <header class="mb-4">
        <span class="text-[10px] uppercase tracking-widest text-[#8E8E93] font-bold block mb-0.5">Average Finishing Position</span>
        <h3 class="text-[32px] font-black text-white tracking-tight leading-none">3rd</h3>
      </header>
      
      <!-- Interactive SVG Vector Chart Path Elements -->
      <div class="pt-4 border-t border-[#242426]">
        <h4 class="text-[13px] font-bold text-white mb-4 tracking-tight">Year by Year</h4>
        
        <div class="relative w-full h-36 bg-gradient-to-b from-[#1C1C1E] to-[#161618] rounded-lg border border-[#242426]/50 p-2 overflow-visible">
          <!-- Background Grid lines labels overlay -->
          <div class="absolute inset-0 flex flex-col justify-between py-2 px-6 pointer-events-none opacity-10">
            <div class="border-b border-dashed border-white w-full text-[9px] text-[#8E8E93] text-left pt-1">1</div>
            <div class="border-b border-dashed border-white w-full text-[9px] text-[#8E8E93] text-left pt-1">4</div>
            <div class="border-b border-dashed border-white w-full text-[9px] text-[#8E8E93] text-left pt-1">7</div>
            <div class="border-b border-dashed border-white w-full text-[9px] text-[#8E8E93] text-left pt-1">10</div>
          </div>

          <!-- Strict Grid Point Coordinate Graph Layout matching screenshot -->
          <svg class="w-full h-full overflow-visible" viewBox="0 0 100 40" preserveAspectRatio="none">
            <path d="M 0,22 L 20,4 L 40,4 L 60,15 L 80,4 L 100,22" fill="none" stroke="#00FF38" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
            <circle cx="0" cy="22" r="1.5" fill="#1C1C1E" stroke="#00FF38" stroke-width="1.2" />
            <circle cx="20" cy="4" r="1.5" fill="#1C1C1E" stroke="#00FF38" stroke-width="1.2" />
            <circle cx="40" cy="4" r="1.5" fill="#1C1C1E" stroke="#00FF38" stroke-width="1.2" />
            <circle cx="60" cy="15" r="1.5" fill="#1C1C1E" stroke="#00FF38" stroke-width="1.2" />
            <circle cx="80" cy="4" r="1.5" fill="#1C1C1E" stroke="#00FF38" stroke-width="1.2" />
            <circle cx="100" cy="22" r="1.5" fill="#1C1C1E" stroke="#00FF38" stroke-width="1.2" />
          </svg>

          <!-- Graph X Timeline labels -->
          <div class="absolute bottom-1 left-2 right-2 flex justify-between text-[10px] font-medium text-[#727277] px-1">
            <span>'14</span>
            <span>'16</span>
            <span>'18</span>
            <span>'20</span>
            <span>'22</span>
            <span>'24</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Historical Trophy Stat Metric Box Grid -->
    <section class="grid grid-cols-3 gap-2.5 mb-4">
      <div class="bg-[#1C1C1E] rounded-xl p-3 border border-[#242426] flex flex-col justify-between h-[68px]">
        <span class="text-[9px] uppercase tracking-wider text-[#727277] font-bold block leading-tight">Champ. Won</span>
        <span class="text-xl font-bold text-white tracking-tight">5</span>
      </div>
      <div class="bg-[#1C1C1E] rounded-xl p-3 border border-[#242426] flex flex-col justify-between h-[68px]">
        <span class="text-[9px] uppercase tracking-wider text-[#727277] font-bold block leading-tight">Playoff App.</span>
        <span class="text-xl font-bold text-white tracking-tight">9</span>
      </div>
      <div class="bg-[#1C1C1E] rounded-xl p-3 border border-[#242426] flex flex-col justify-between h-[68px]">
        <span class="text-[9px] uppercase tracking-wider text-[#727277] font-bold block leading-tight">Top 3 Finishes</span>
        <span class="text-xl font-bold text-white tracking-tight">7</span>
      </div>
    </section>

    <!-- All-Time Flat Score Strip -->
    <footer class="flex justify-between items-center py-3.5 border-t border-b border-[#222224] px-1">
      <span class="text-[14px] font-semibold text-[#8E8E93]">All-Time Record</span>
      <span class="text-[14px] font-bold text-white tracking-tight">107-54-0</span>
    </footer>

  </div>
</body>
</html>
"""

# Call Streamlit native HTML frame wrapper ensuring mobile viewport is preserved completely
components.html(espn_mobile_html, height=590, scrolling=False)
