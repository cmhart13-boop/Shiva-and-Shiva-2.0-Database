from __future__ import annotations
import sqlite3
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

DB = Path(__file__).with_name('shiva_draft_roi.sqlite')
st.set_page_config(page_title='Shiva Draft Intelligence', page_icon='🏆', layout='wide')

st.markdown('''

<style>
:root {--bg:#0b0c0e;--deep:#050607;--panel:#1b1d1f;--line:#3a3d40;--muted:#9da1a6;--white:#f7f7f7;--green:#35f23e;--blue:#5b96ff;--red:#ff4e59;}
html,body,[class*="css"]{font-family:"Arial Narrow","Roboto Condensed","Helvetica Neue",Arial,sans-serif;}
.stApp{background:var(--bg);color:var(--white);} .block-container{max-width:1180px;padding-top:.25rem;padding-bottom:4rem;} #MainMenu,footer,header{visibility:hidden;}
.shiva-splash{position:fixed;inset:0;z-index:999999;background:#0828bd;display:flex;align-items:center;justify-content:center;animation:splashFade .55s ease 2.15s forwards;}
.shiva-shield{position:relative;width:148px;height:164px;border:14px solid #c9ff00;border-radius:18px 18px 58px 58px;display:grid;place-items:center;transform:skew(-3deg);}
.shiva-shield:after{content:"";position:absolute;left:50%;bottom:-34px;width:75px;height:75px;background:#0828bd;border-right:14px solid #c9ff00;border-bottom:14px solid #c9ff00;transform:translateX(-50%) rotate(45deg);}
.shiva-s{position:relative;z-index:2;color:#c9ff00;font:italic 1000 7.2rem/1 "Arial Black",Arial,sans-serif;transform:translateY(-2px) skew(-5deg);}
@keyframes splashFade{0%{opacity:1;visibility:visible;}99%{opacity:0;visibility:visible;}100%{opacity:0;visibility:hidden;pointer-events:none;}}
.shiva-banner{position:sticky;top:0;z-index:999;margin:0 -1rem 12px;padding:14px 18px 12px;background:rgba(5,6,7,.98);border-bottom:1px solid #242629;color:#fff;font-size:clamp(1.15rem,4vw,1.75rem);font-weight:1000;letter-spacing:.015em;line-height:1.05;text-transform:uppercase;backdrop-filter:blur(14px);}
.shiva-banner span{color:var(--green);} .shiva-banner:after{content:"";display:block;height:4px;width:48%;max-width:330px;margin-top:10px;background:var(--green);}
h1,h2,h3,h4,p,label,.stMarkdown{color:var(--white)!important;} h1,h2,h3{font-weight:1000!important;letter-spacing:-.02em;} hr{border-color:#313438;}
[data-baseweb="select"]>div{background:#242628!important;border:1px solid #42464a!important;border-radius:999px!important;min-height:47px;} [data-baseweb="select"] span,[data-baseweb="select"] input{color:var(--blue)!important;font-weight:900!important;}
.stSelectbox label p,.stRadio label p{color:#e8e8e8!important;font-weight:900!important;} div[role="radiogroup"]{background:var(--panel);border:1px solid #303337;border-radius:15px;padding:8px 10px;}
div[data-testid="stMetric"]{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:14px 15px;min-width:0;overflow:visible;box-shadow:0 9px 24px rgba(0,0,0,.24);} div[data-testid="stMetricLabel"]{color:var(--muted);font-size:.73rem;font-weight:900;letter-spacing:.055em;text-transform:uppercase;} div[data-testid="stMetricValue"]{color:var(--green);font-size:clamp(1.4rem,3vw,2.05rem)!important;font-weight:1000;white-space:nowrap!important;overflow:visible!important;text-overflow:clip!important;min-width:max-content;line-height:1.05;} div[data-testid="stMetricDelta"]{color:var(--blue);}
[data-testid="stDataFrame"]{background:var(--panel)!important;border:1px solid #34373a!important;border-radius:14px!important;overflow:hidden;} [data-testid="stDataFrame"] *{font-family:"Arial Narrow",Arial,sans-serif!important;}
section[data-testid="stSidebar"]{background:#090a0b;border-right:1px solid #292c2f;} section[data-testid="stSidebar"] *{color:#fff;} .sidebar-panel{background:var(--panel);border:1px solid #36393c;border-radius:14px;padding:13px 14px;margin:10px 0 8px;} .sidebar-panel-title{color:#fff;font-size:.84rem;font-weight:1000;letter-spacing:.07em;text-transform:uppercase;} .sidebar-panel-sub{color:var(--muted);font-size:.76rem;margin-top:4px;}
.stDownloadButton button,.stButton button{color:var(--blue)!important;background:transparent!important;border:2px solid var(--blue)!important;border-radius:999px!important;font-weight:1000!important;width:100%;}
[data-testid="stPlotlyChart"]{background:var(--panel);border:1px solid #303337;border-radius:16px;padding:8px;}
@media(max-width:900px){.block-container{padding-left:.8rem;padding-right:.8rem;}div[data-testid="stMetricValue"]{font-size:1.25rem!important;}.shiva-banner{font-size:1.05rem;}.shiva-shield{width:118px;height:132px;border-width:11px;}.shiva-shield:after{width:60px;height:60px;bottom:-28px;border-right-width:11px;border-bottom-width:11px;}.shiva-s{font-size:5.8rem;}}
</style>

<style>
:root{
 --espn-bg:#0b0d0f; --espn-black:#000; --espn-card:#1d1f21; --espn-card2:#252729;
 --espn-line:#34373a; --espn-green:#35f23e; --espn-blue:#5b96ff; --espn-white:#f6f7f8;
 --espn-muted:#9fa3a7;
}
.stApp{background:linear-gradient(180deg,#050607 0,#0b0d0f 155px,#0b0d0f 100%)!important;}
.shiva-logo-svg{width:152px;height:178px;display:block;filter:drop-shadow(0 10px 18px rgba(0,0,0,.12));}
.shiva-banner{
 background:#000!important;border-bottom:1px solid #202225!important;
 padding:18px 18px 14px!important;margin:0 -1rem 14px!important;
 font-family:"Arial Narrow","Roboto Condensed",Arial,sans-serif!important;
}
.shiva-banner span{color:#fff!important;}
.shiva-banner:after{background:var(--espn-green)!important;width:100%!important;max-width:none!important;height:4px!important;}
.mobile-filter-shell{
 background:var(--espn-card);border:1px solid var(--espn-line);border-radius:18px;
 padding:14px 14px 4px;margin:0 0 14px;box-shadow:0 8px 24px rgba(0,0,0,.28);
}
.mobile-filter-title{font-size:.82rem;font-weight:1000;letter-spacing:.08em;text-transform:uppercase;color:#fff;margin-bottom:4px;}
.mobile-filter-sub{font-size:.76rem;color:var(--espn-muted);margin-bottom:8px;}
div[data-testid="stMetric"]{background:var(--espn-card)!important;border-color:var(--espn-line)!important;}
div[data-testid="stMetricValue"]{color:var(--espn-green)!important;}
[data-testid="stDataFrame"],[data-testid="stPlotlyChart"]{background:var(--espn-card)!important;}
.stTabs [data-baseweb="tab-list"]{background:#000;border-bottom:1px solid #2b2e31;gap:2px;}
.stTabs [data-baseweb="tab"]{color:#a7aaae;font-weight:900;text-transform:uppercase;}
.stTabs [aria-selected="true"]{color:#fff!important;border-bottom:4px solid var(--espn-green)!important;}
[data-baseweb="select"]>div{background:var(--espn-card2)!important;border-color:#45484c!important;}
div[role="radiogroup"]{background:var(--espn-card)!important;}
@media(max-width:900px){
 section[data-testid="stSidebar"]{display:none!important;}
 .block-container{padding-top:0!important;padding-left:.65rem!important;padding-right:.65rem!important;}
 .shiva-banner{margin-left:-.65rem!important;margin-right:-.65rem!important;}
 .mobile-filter-shell{display:block;}
 div[data-testid="column"]{min-width:0!important;}
 div[data-testid="stMetric"]{padding:11px 9px!important;}
 div[data-testid="stMetricValue"]{font-size:1.08rem!important;white-space:nowrap!important;overflow:visible!important;text-overflow:clip!important;}
}
</style>


''', unsafe_allow_html=True)

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
def load():
    with sqlite3.connect(DB) as con:
        roi = pd.read_sql_query('SELECT * FROM draft_roi_scores ORDER BY league_name,season,overall_pick', con)
    return roi

roi = load()
managers = sorted(roi.manager_name.dropna().unique())
scopes = ['Combined','Shiva','Shiva 2.0']
seasons = ['Career'] + [str(x) for x in sorted(roi.season.unique(), reverse=True)]

def filt(manager, scope, season):
    x = roi[roi.manager_name.eq(manager)].copy()
    if scope != 'Combined': x = x[x.league_name.eq(scope)]
    if season != 'Career': x = x[x.season.eq(int(season))]
    return x

def summary(x):
    if x.empty: return dict(picks=0,avg=np.nan,ppg=np.nan,steal=np.nan,bust=np.nan)
    return dict(picks=len(x),avg=x.final_draft_roi.mean(),ppg=x.ppg_roi.mean(),steal=x.classification.eq('Steal').mean()*100,bust=x.classification.eq('Bust').mean()*100)

def round_table(x):
    if x.empty: return pd.DataFrame()
    return (x.groupby('round',as_index=False).agg(Picks=('player_name','count'),Avg_Final_ROI=('final_draft_roi','mean'),Avg_Total_ROI=('total_points_roi','mean'),Avg_PPG_ROI=('ppg_roi','mean'),Steal_Pct=('classification',lambda s:s.eq('Steal').mean()*100),Met_Pct=('classification',lambda s:s.eq('Met Expectations').mean()*100),Bust_Pct=('classification',lambda s:s.eq('Bust').mean()*100)).rename(columns={'round':'Round','Avg_Final_ROI':'Avg Final ROI','Avg_Total_ROI':'Avg Total ROI','Avg_PPG_ROI':'Avg PPG ROI','Steal_Pct':'Steal %','Met_Pct':'Met %','Bust_Pct':'Bust %'}))

def pos_table(x):
    if x.empty: return pd.DataFrame()
    return (x.groupby('position',as_index=False).agg(Picks=('player_name','count'),Avg_Final_ROI=('final_draft_roi','mean'),Avg_Total_ROI=('total_points_roi','mean'),Avg_PPG_ROI=('ppg_roi','mean'),Steal_Pct=('classification',lambda s:s.eq('Steal').mean()*100),Met_Pct=('classification',lambda s:s.eq('Met Expectations').mean()*100),Bust_Pct=('classification',lambda s:s.eq('Bust').mean()*100)).rename(columns={'position':'Position','Avg_Final_ROI':'Avg Final ROI','Avg_Total_ROI':'Avg Total ROI','Avg_PPG_ROI':'Avg PPG ROI','Steal_Pct':'Steal %','Met_Pct':'Met %','Bust_Pct':'Bust %'}).sort_values('Avg Final ROI',ascending=False))

def show(df, roi_col=None):
    if df.empty: st.info('No data for this selection.'); return
    fmt={c:'{:.2f}' for c in df.columns if 'ROI' in c}
    fmt.update({c:'{:.1f}%' for c in df.columns if c.endswith('%')})
    s=df.style.format(fmt)
    if roi_col in df.columns: s=s.background_gradient(subset=[roi_col],cmap='RdYlGn')
    st.dataframe(s,use_container_width=True,hide_index=True)


def style_fig(fig, title=None):
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='#1d1f21',
        plot_bgcolor='#1d1f21',
        font=dict(color='#f6f7f8'),
        title=title,
        margin=dict(l=18,r=18,t=48,b=18),
        coloraxis_colorbar=dict(tickfont=dict(color='#f6f7f8')),
    )
    fig.update_xaxes(gridcolor='#34373a', zerolinecolor='#34373a')
    fig.update_yaxes(gridcolor='#34373a', zerolinecolor='#34373a')
    return fig

def default_idx():
    for n in ('Chris H','Chris Hart'):
        if n in managers: return managers.index(n)
    return 0


st.markdown(
    '<div class="mobile-filter-shell"><div class="mobile-filter-title">League History Controls</div><div class="mobile-filter-sub">Tap any field to change the manager, league, season, or report.</div></div>',
    unsafe_allow_html=True,
)
fc1, fc2, fc3 = st.columns([1.45,1,1])
manager = fc1.selectbox('👤 Manager', managers, index=default_idx(), key='main_manager')
scope = fc2.selectbox('🏈 League', scopes, key='main_scope')
season = fc3.selectbox('📅 Season', seasons, key='main_season')
page_choice = st.radio(
    'Report',
    ['📈 Manager Dashboard','⚔️ Head-to-Head','🏅 League Leaderboard','🔥 Draft Heatmap','🧾 All Picks','📘 Methodology'],
    horizontal=True,
    key='main_page'
)
page = page_choice.split(' ',1)[1]

st.sidebar.markdown(
    '<div class="sidebar-panel"><div class="sidebar-panel-title">🏆 Shiva Controls</div><div class="sidebar-panel-sub">Desktop navigation mirrors the mobile controls shown in the main screen.</div></div>',
    unsafe_allow_html=True,
)
if page=='Manager Dashboard':
    x=filt(manager,scope,season); s=summary(x)
    st.title('Shiva Draft Intelligence'); st.subheader(f'{manager} · {scope} · {season}')
    a,b,c,d,e=st.columns(5)
    a.metric('Graded Picks',s['picks']); b.metric('Avg Final ROI','—' if pd.isna(s['avg']) else f"{s['avg']:.2f}"); c.metric('Avg PPG ROI','—' if pd.isna(s['ppg']) else f"{s['ppg']:.2f}"); d.metric('Steal Rate','—' if pd.isna(s['steal']) else f"{s['steal']:.1f}%"); e.metric('Bust Rate','—' if pd.isna(s['bust']) else f"{s['bust']:.1f}%")
    st.markdown('### Round-by-Round Performance'); rt=round_table(x); show(rt,'Avg Final ROI')
    if not rt.empty:
        fig=px.bar(rt,x='Round',y='Avg Final ROI',color='Avg Final ROI',color_continuous_scale='RdYlGn'); fig.update_layout(coloraxis_showscale=False); style_fig(fig,'Average Draft ROI by Round'); st.plotly_chart(fig,use_container_width=True)
    st.markdown('### Position Performance'); show(pos_table(x),'Avg Final ROI')
    cols=['league_name','season','round','player_name','position','position_draft_rank','position_finish_total','position_finish_ppg','ppg','games_played','final_draft_roi']; ren={'league_name':'League','season':'Season','round':'Round','player_name':'Player','position':'Pos','position_draft_rank':'Drafted Pos','position_finish_total':'Total Finish','position_finish_ppg':'PPG Finish','ppg':'PPG','games_played':'Games','final_draft_roi':'Final ROI'}
    l,r=st.columns(2)
    with l: st.markdown('### Top 10 Steals'); show(x.nlargest(10,'final_draft_roi')[cols].rename(columns=ren),'Final ROI')
    with r: st.markdown('### Top 10 Busts'); show(x.nsmallest(10,'final_draft_roi')[cols].rename(columns=ren),'Final ROI')

elif page=='Head-to-Head':
    st.title('Manager Head-to-Head'); a,b,c,d=st.columns(4)
    ma=a.selectbox('Manager A',managers,index=default_idx()); mb=b.selectbox('Manager B',managers,index=1 if len(managers)>1 else 0); sc=c.selectbox('League Scope',scopes); se=d.selectbox('Season',seasons)
    xa,xb=filt(ma,sc,se),filt(mb,sc,se); sa,sb=summary(xa),summary(xb)
    st.dataframe(pd.DataFrame([['Graded Picks',sa['picks'],sb['picks']],['Avg Final ROI',sa['avg'],sb['avg']],['Avg PPG ROI',sa['ppg'],sb['ppg']],['Steal %',sa['steal'],sb['steal']],['Bust %',sa['bust'],sb['bust']]],columns=['Metric',ma,mb]),use_container_width=True,hide_index=True)
    pa=pos_table(xa)[['Position','Avg Final ROI']].rename(columns={'Avg Final ROI':ma}) if not xa.empty else pd.DataFrame(columns=['Position',ma]); pb=pos_table(xb)[['Position','Avg Final ROI']].rename(columns={'Avg Final ROI':mb}) if not xb.empty else pd.DataFrame(columns=['Position',mb]); pc=pa.merge(pb,on='Position',how='outer').fillna(0)
    if not pc.empty:
        fig=px.bar(pc.melt(id_vars='Position',var_name='Manager',value_name='Avg Final ROI'),x='Position',y='Avg Final ROI',color='Manager',barmode='group'); style_fig(fig,'Position ROI Comparison'); st.plotly_chart(fig,use_container_width=True)

elif page=='League Leaderboard':
    st.title('League Draft Efficiency Leaderboard'); a,b=st.columns(2); sc=a.selectbox('League Scope',scopes); se=b.selectbox('Season',seasons); x=roi.copy()
    if sc!='Combined': x=x[x.league_name.eq(sc)]
    if se!='Career': x=x[x.season.eq(int(se))]
    board=(x.groupby('manager_name',as_index=False).agg(Picks=('player_name','count'),Avg_Final_ROI=('final_draft_roi','mean'),Avg_Total_ROI=('total_points_roi','mean'),Avg_PPG_ROI=('ppg_roi','mean'),Steal_Pct=('classification',lambda s:s.eq('Steal').mean()*100),Met_Pct=('classification',lambda s:s.eq('Met Expectations').mean()*100),Bust_Pct=('classification',lambda s:s.eq('Bust').mean()*100)).sort_values(['Avg_Final_ROI','Avg_PPG_ROI'],ascending=False).reset_index(drop=True))
    board.insert(0,'Rank',board.index+1); board=board.rename(columns={'manager_name':'Manager','Avg_Final_ROI':'Avg Final ROI','Avg_Total_ROI':'Avg Total ROI','Avg_PPG_ROI':'Avg PPG ROI','Steal_Pct':'Steal %','Met_Pct':'Met %','Bust_Pct':'Bust %'}); show(board,'Avg Final ROI')

elif page=='Draft Heatmap':
    st.title('Draft Heatmap'); x=filt(manager,scope,'Career')
    if x.empty: st.info('No data available.')
    else:
        p=x.pivot_table(index='season',columns='round',values='final_draft_roi',aggfunc='mean').sort_index().reindex(columns=list(range(1,17))); fig=px.imshow(p,aspect='auto',color_continuous_scale='RdYlGn',labels={'x':'Round','y':'Season','color':'Avg ROI'}); style_fig(fig,'Draft ROI Heatmap'); st.plotly_chart(fig,use_container_width=True); st.dataframe(p.style.background_gradient(cmap='RdYlGn',axis=None),use_container_width=True)

elif page=='All Picks':
    st.title('Complete Pick-Level ROI'); x=filt(manager,scope,season)
    d=x[['league_name','season','round','overall_pick','team_name','player_name','position','position_draft_rank','position_finish_total','position_finish_ppg','fantasy_points_ppr','ppg','games_played','total_points_roi','ppg_roi','final_draft_roi','classification']].rename(columns={'league_name':'League','season':'Season','round':'Round','overall_pick':'Overall','team_name':'Team','player_name':'Player','position':'Pos','position_draft_rank':'Drafted Pos Rank','position_finish_total':'Total Finish','position_finish_ppg':'PPG Finish','fantasy_points_ppr':'PPR Points','ppg':'PPG','games_played':'Games','total_points_roi':'Total ROI','ppg_roi':'PPG ROI','final_draft_roi':'Final ROI','classification':'Class'}); show(d,'Final ROI'); st.download_button('Download filtered CSV',d.to_csv(index=False).encode(),file_name=f'{manager}_{scope}_{season}_draft_roi.csv'.replace(' ','_'),mime='text/csv')

else:
    st.title('Methodology'); st.markdown('''1. Position Draft Rank = order drafted within position for each league-season.\n2. Season finishes = total-point positional rank and PPG positional rank.\n3. Near-Hit Buffers: 1–5 ±2; 6–15 ±4; 16–30 ±7; 31+ ±12.\n4. Draft Capital Weight = `1 / square_root(round drafted)`.\n5. Final Draft ROI = 70% Total ROI + 30% PPG ROI.\n6. After Round 8, finishes outside Top 50 are capped at -0.1 for both ROI components.\n\nPositive = steal, zero = met expectations, negative = bust.''')
