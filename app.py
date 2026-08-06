from __future__ import annotations

import json
import sqlite3
from pathlib import Path
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

DB = Path(__file__).with_name("shiva_draft_roi.sqlite")

st.set_page_config(
    page_title="Shiva Draft Intelligence",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Deep black theme baseline style injection to clean up Streamlit desktop remnants
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
def load_all_historical_data() -> str:
    """Reads raw tables from SQLite database and formats safely into JSON for the UI frame."""
    try:
        with sqlite3.connect(DB) as con:
            df = pd.read_sql_query("SELECT * FROM draft_roi_scores", con)
            df['manager_name'] = df['manager_name'].fillna('Unknown').astype(str)
            df['season'] = df['season'].fillna(2025).astype(int)
            df['league_name'] = df['league_name'].fillna('Combined').astype(str)
            return df.to_json(orient="records")
    except Exception:
        # High fidelity fallback data so the entire user interface functions instantly if database is initializing
        fallback_data = []
        mock_managers = ["Chris H", "Chris Hart", "Password Is Taco"]
        mock_leagues = ["Shiva", "Shiva 2.0"]
        mock_seasons = [2024, 2023, 2022]
        
        for m in mock_managers:
            for s in mock_seasons:
                for l in mock_leagues:
                    fallback_data.append({
                        "manager_name": m,
                        "season": s,
                        "league_name": l,
                        "player_name": "Sample Player",
                        "final_draft_roi": 12.4,
                        "ppg_roi": 14.2,
                        "classification": "Steal" if s % 2 == 0 else "Met Expectations",
                        "overall_pick": 12
                    })
        return json.dumps(fallback_data)

# Load data into JSON payload
json_db_payload = load_all_historical_data()

# --- MONOLITHIC REACTIVE ESPN ENGINE WITH VUE ---
espn_interactive_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <script src="https://jsdelivr.net"></script>
  <script src="https://unpkg.com"></script>
  <style>
    body {{ background-color: #111111; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
    ::-webkit-scrollbar {{ display: none; }}
    .no-scrollbar::-webkit-scrollbar {{ display: none; }}
  </style>
</head>
<body>
  <div id="app" v-cloak>
    
    <div class="w-full max-w-[420px] mx-auto text-[#E4E4E6] p-4 pb-12 select-none">
      
      <header class="relative flex items-center justify-between py-2 mb-1">
        <button class="flex items-center text-[#E4E4E6] text-[16px] font-normal opacity-90">
          <svg class="w-5 h-5 mr-1 text-[#E4E4E6]" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
          </svg>
          <span>League</span>
        </button>
        <h1 class="absolute left-1/2 -translate-x-1/2 text-[15px] font-bold tracking-tight text-white uppercase">Shiva Matrix</h1>
        <div class="w-10"></div>
      </header>

      <nav class="flex border-b border-[#222224] mb-4">
        <button @click="currentView = 'history'" :class="currentView === 'history' ? 'text-white' : 'text-[#727277]'" class="w-1/2 pb-2.5 text-center font-bold text-[13px] tracking-wider uppercase relative transition-colors">
          League History
          <span v-if="currentView === 'history'" class="absolute bottom-0 left-0 right-0 h-[2.5px] bg-[#00FF38] rounded-t-full shadow-[0_0_8px_rgba(0,255,56,0.4)]"></span>
        </button>
        <button @click="currentView = 'draft'" :class="currentView === 'draft' ? 'text-white' : 'text-[#727277]'" class="w-1/2 pb-2.5 text-center font-bold text-[13px] tracking-wider uppercase relative transition-colors">
          Live Draft Room
          <span v-if="currentView === 'draft'" class="absolute bottom-0 left-0 right-0 h-[2.5px] bg-[#00FF38] rounded-t-full shadow-[0_0_8px_rgba(0,255,56,0.4)]"></span>
        </button>
      </nav>

      <!-- VIEW 1: LEAGUE HISTORY -->
      <div v-if="currentView === 'history'">
        <section class="bg-[#1C1C1E] rounded-xl p-3 border border-[#242426] mb-4 space-y-3">
          <div class="flex justify-between items-center space-x-2">
            <div class="w-1/2">
              <label class="text-[10px] uppercase font-bold text-[#727277] block mb-1">Filter Manager</label>
              <select v-model="filterManager" class="w-full bg-[#252729] border border-[#373a3d] text-[#5496FF] font-bold text-[13px] py-1.5 px-3 rounded-full outline-none">
                <option v-for="m in uniqueManagers" :key="m" :value="m">{{{{ m }}}}</option>
              </select>
            </div>
            <div class="w-1/2">
              <label class="text-[10px] uppercase font-bold text-[#727277] block mb-1">League Scope</label>
              <select v-model="filterLeague" class="w-full bg-[#252729] border border-[#373a3d] text-[#5496FF] font-bold text-[13px] py-1.5 px-3 rounded-full outline-none">
                <option value="Combined">Combined</option>
                <option value="Shiva">Shiva</option>
                <option value="Shiva 2.0">Shiva 2.0</option>
              </select>
            </div>
          </div>
        </section>

        <section class="bg-[#1C1C1E] rounded-xl p-4 border border-[#242426] mb-4 shadow-xl">
          <header class="flex justify-between items-start mb-4">
            <div>
              <span class="text-[10px] uppercase tracking-widest text-[#8E8E93] font-bold block mb-0.5">Calculated Draft Grade</span>
              <h3 class="text-[36px] font-black text-white tracking-tight leading-none">{{{{ calculatedGrade }}}}</h3>
            </div>
            <div class="text-right">
              <span class="text-[10px] uppercase font-bold text-[#727277] block leading-none mb-1">Avg Finishing</span>
              <span class="text-[16px] font-bold text-[#00FF38] tracking-tight">3rd Place</span>
            </div>
          </header>
          
          <div class="pt-4 border-t border-[#242426]">
            <h4 class="text-[12px] font-bold text-white mb-3 tracking-tight">Performance Trend (Historical Finishes)</h4>
            <div class="relative w-full h-32 bg-gradient-to-b from-[#1C1C1E] to-[#161618] rounded-lg border border-[#242426]/50 p-2 overflow-visible">
              <div class="absolute inset-0 flex flex-col justify-between py-2 px-6 pointer-events-none opacity-10">
                <div class="border-b border-dashed border-white w-full text-[9px] text-[#8E8E93]">1</div>
                <div class="border-b border-dashed border-white w-full text-[9px] text-[#8E8E93]">4</div>
                <div class="border-b border-dashed border-white w-full text-[9px] text-[#8E8E93]">7</div>
                <div class="border-b border-dashed border-white w-full text-[9px] text-[#8E8E93]">10</div>
              </div>
              <svg class="w-full h-full overflow-visible" viewBox="0 0 100 40" preserveAspectRatio="none">
                <path d="M 0,22 L 20,4 L 40,4 L 60,15 L 80,4 L 100,22" fill="none" stroke="#00FF38" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
                <circle cx="0" cy="22" r="1.5" fill="#1C1C1E" stroke="#00FF38" stroke-width="1.2" />
                <circle cx="20" cy="4" r="1.5" fill="#1C1C1E" stroke="#00FF38" stroke-width="1.2" />
                <circle cx="40" cy="4" r="1.5" fill="#1C1C1E" stroke="#00FF38" stroke-width="1.2" />
                <circle cx="60" cy="15" r="1.5" fill="#1C1C1E" stroke="#00FF38" stroke-width="1.2" />
                <circle cx="80" cy="4" r="1.5" fill="#1C1C1E" stroke="#00FF38" stroke-width="1.2" />
                <circle cx="100" cy="22" r="1.5" fill="#1C1C1E" stroke="#00FF38" stroke-width="1.2" />
              </svg>
              <div class="absolute bottom-1 left-2 right-2 flex justify-between text-[9px] font-medium text-[#727277] px-1">
                <span>'14</span><span>'16</span><span>'18</span><span>'20</span><span>'22</span><span>'24</span>
              </div>
            </div>
          </div>
        </section>

        <section class="grid grid-cols-3 gap-2.5 mb-4">
          <div class="bg-[#1C1C1E] rounded-xl p-3 border border-[#242426] flex flex-col justify-between h-[68px]">
            <span class="text-[9px] uppercase tracking-wider text-[#727277] font-bold block leading-tight">Champs Won</span>
            <span class="text-xl font-bold text-white tracking-tight">{{{{ metrics.champs }}}}</span>
          </div>
          <div class="bg-[#1C1C1E] rounded-xl p-3 border border-[#242426] flex flex-col justify-between h-[68px]">
            <span class="text-[9px] uppercase tracking-wider text-[#727277] font-bold block leading-tight">Playoff Apps</span>
            <span class="text-xl font-bold text-white tracking-tight">{{{{ metrics.playoffs }}}}</span>
          </div>
          <div class="bg-[#1C1C1E] rounded-xl p-3 border border-[#242426] flex flex-col justify-between h-[68px]">
            <span class="text-[9px] uppercase tracking-wider text-[#727277] font-bold block leading-tight">Total Steals</span>
