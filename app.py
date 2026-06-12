import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="IPL Analytics Dashboard",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border: 1px solid #0f3460;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .metric-value { font-size: 2rem; font-weight: 700; color: #e94560; }
    .metric-label { font-size: 0.85rem; color: #a0aec0; margin-top: 4px; }
    .section-header {
        font-size: 1.3rem; font-weight: 600;
        color: #e2e8f0; margin: 20px 0 10px 0;
        border-left: 4px solid #e94560;
        padding-left: 12px;
    }
    div[data-testid="stTabs"] button { font-size: 15px; font-weight: 500; }
</style>
""", unsafe_allow_html=True)

# ─── Load Data ───────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    matches = pd.read_csv("data/matches.csv")
    deliveries = pd.read_csv("data/deliveries.csv")

    # Standardise column names to lowercase
    matches.columns = matches.columns.str.lower().str.strip()
    deliveries.columns = deliveries.columns.str.lower().str.strip()

    # Rename 'id' → 'match_id' in matches if needed
    if 'id' in matches.columns and 'match_id' not in matches.columns:
        matches.rename(columns={'id': 'match_id'}, inplace=True)

    # Clean team names
    team_rename = {
        'Delhi Daredevils': 'Delhi Capitals',
        'Deccan Chargers': 'Sunrisers Hyderabad',
        'Pune Warriors': 'Rising Pune Supergiant',
    }
    for col in ['team1', 'team2', 'winner', 'toss_winner']:
        if col in matches.columns:
            matches[col] = matches[col].replace(team_rename)

    return matches, deliveries

try:
    matches, deliveries = load_data()
    data_loaded = True
except FileNotFoundError:
    data_loaded = False

# ─── Header ─────────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center; padding: 10px 0 20px 0;'>
    <h1 style='color:#e94560; font-size:2.8rem; font-weight:800;'>🏏 IPL Analytics Dashboard</h1>
    <p style='color:#a0aec0; font-size:1rem;'>Indian Premier League — Complete Data Intelligence Platform</p>
</div>
""", unsafe_allow_html=True)

if not data_loaded:
    st.error("⚠️ Dataset not found! Please add `matches.csv` and `deliveries.csv` inside the `data/` folder.")
    st.info("Download from: https://www.kaggle.com/datasets/ramjidoolla/ipl-data-set")
    st.stop()

# ─── Sidebar Filters ────────────────────────────────────────────────────────
st.sidebar.markdown("## 🎛️ Filters")
all_seasons = sorted(matches['season'].unique())
selected_seasons = st.sidebar.multiselect("Season(s)", all_seasons, default=all_seasons)

all_teams = sorted(set(matches['team1'].dropna()) | set(matches['team2'].dropna()))
selected_team = st.sidebar.selectbox("Focus Team", ["All Teams"] + all_teams)

# Filter matches
filtered = matches[matches['season'].isin(selected_seasons)]
if selected_team != "All Teams":
    filtered = filtered[(filtered['team1'] == selected_team) | (filtered['team2'] == selected_team)]

st.sidebar.markdown("---")
st.sidebar.markdown(f"**{len(filtered)}** matches selected")

# ─── KPI Row ────────────────────────────────────────────────────────────────
total_matches  = len(filtered)
total_seasons  = filtered['season'].nunique()
total_teams    = len(all_teams)
total_sixes    = deliveries[deliveries['match_id'].isin(filtered['match_id'])]['batsman_runs'].apply(lambda x: 1 if x == 6 else 0).sum() if 'batsman_runs' in deliveries.columns else 0

k1, k2, k3, k4 = st.columns(4)
for col, val, label in zip(
    [k1, k2, k3, k4],
    [total_matches, total_seasons, total_teams, int(total_sixes)],
    ["Total Matches", "Seasons", "Teams", "Total Sixes"]
):
    col.markdown(f"""
    <div class='metric-card'>
        <div class='metric-value'>{val}</div>
        <div class='metric-label'>{label}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Tabs ───────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["🏆 Team Analysis", "🏏 Batting", "🎯 Bowling", "🏟️ Venues"])

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — TEAM ANALYSIS
# ════════════════════════════════════════════════════════════════════════════
with tab1:
    col_a, col_b = st.columns(2)

    # Most Wins Overall
    with col_a:
        st.markdown("<div class='section-header'>Most Wins (All Time)</div>", unsafe_allow_html=True)
        wins = filtered['winner'].value_counts().head(10).reset_index()
        wins.columns = ['Team', 'Wins']
        fig = px.bar(wins, x='Wins', y='Team', orientation='h',
                     color='Wins', color_continuous_scale='Reds',
                     template='plotly_dark')
        fig.update_layout(showlegend=False, coloraxis_showscale=False,
                          plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                          yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)

    # Wins per Season (stacked)
    with col_b:
        st.markdown("<div class='section-header'>Season-wise Win Distribution</div>", unsafe_allow_html=True)
        season_wins = filtered.groupby(['season', 'winner']).size().reset_index(name='wins')
        top_teams = filtered['winner'].value_counts().head(8).index.tolist()
        season_wins = season_wins[season_wins['winner'].isin(top_teams)]
        fig2 = px.bar(season_wins, x='season', y='wins', color='winner',
                      barmode='stack', template='plotly_dark',
                      color_discrete_sequence=px.colors.qualitative.Bold)
        fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                           legend_title_text='Team', xaxis_title='Season', yaxis_title='Wins')
        st.plotly_chart(fig2, use_container_width=True)

    col_c, col_d = st.columns(2)

    # Toss Decision Analysis
    with col_c:
        st.markdown("<div class='section-header'>Toss Decision Preference</div>", unsafe_allow_html=True)
        toss = filtered['toss_decision'].value_counts().reset_index()
        toss.columns = ['Decision', 'Count']
        fig3 = px.pie(toss, values='Count', names='Decision',
                      color_discrete_sequence=['#e94560', '#0f3460'],
                      template='plotly_dark', hole=0.45)
        fig3.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig3, use_container_width=True)

    # Toss win vs Match win
    with col_d:
        st.markdown("<div class='section-header'>Toss Win → Match Win Rate (%)</div>", unsafe_allow_html=True)
        toss_match = filtered.copy()
        toss_match['toss_won_match'] = toss_match['toss_winner'] == toss_match['winner']
        toss_rate = toss_match.groupby('toss_winner')['toss_won_match'].mean().mul(100).round(1)
        toss_rate = toss_rate.reset_index().rename(columns={'toss_winner': 'Team', 'toss_won_match': 'Win Rate %'})
        toss_rate = toss_rate.sort_values('Win Rate %', ascending=False).head(10)
        fig4 = px.bar(toss_rate, x='Team', y='Win Rate %',
                      color='Win Rate %', color_continuous_scale='Blues',
                      template='plotly_dark')
        fig4.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                           coloraxis_showscale=False, xaxis_tickangle=-30)
        st.plotly_chart(fig4, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — BATTING
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    match_ids = filtered['match_id'].tolist()
    bat_data = deliveries[deliveries['match_id'].isin(match_ids)].copy()

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("<div class='section-header'>Top 15 Run Scorers</div>", unsafe_allow_html=True)
        batsman_col = 'batter' if 'batter' in bat_data.columns else 'batsman'
        top_batsmen = bat_data.groupby(batsman_col)['batsman_runs'].sum().sort_values(ascending=False).head(15)
        top_batsmen = top_batsmen.reset_index()
        top_batsmen.columns = ['Batsman', 'Runs']
        fig5 = px.bar(top_batsmen, x='Runs', y='Batsman', orientation='h',
                      color='Runs', color_continuous_scale='OrRd',
                      template='plotly_dark')
        fig5.update_layout(yaxis={'categoryorder': 'total ascending'},
                           plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                           coloraxis_showscale=False)
        st.plotly_chart(fig5, use_container_width=True)

    with col_b:
        st.markdown("<div class='section-header'>Boundary Analysis (4s vs 6s)</div>", unsafe_allow_html=True)
        fours = bat_data[bat_data['batsman_runs'] == 4].groupby(batsman_col).size()
        sixes = bat_data[bat_data['batsman_runs'] == 6].groupby(batsman_col).size()
        boundary = pd.DataFrame({'Fours': fours, 'Sixes': sixes}).fillna(0)
        boundary['Total'] = boundary['Fours'] + boundary['Sixes']
        boundary = boundary.sort_values('Total', ascending=False).head(12).reset_index()
        boundary.columns = ['Batsman', 'Fours', 'Sixes', 'Total']
        fig6 = go.Figure()
        fig6.add_trace(go.Bar(name='Fours', x=boundary['Batsman'], y=boundary['Fours'], marker_color='#4ecdc4'))
        fig6.add_trace(go.Bar(name='Sixes', x=boundary['Batsman'], y=boundary['Sixes'], marker_color='#e94560'))
        fig6.update_layout(barmode='group', template='plotly_dark',
                           plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                           xaxis_tickangle=-30)
        st.plotly_chart(fig6, use_container_width=True)

    # Run rate per over across all matches
    st.markdown("<div class='section-header'>Average Runs Per Over (Power Play vs Death Overs)</div>", unsafe_allow_html=True)
    over_runs = bat_data.groupby('over')['total_runs'].mean().reset_index()
    over_runs.columns = ['Over', 'Avg Runs']
    over_runs['Phase'] = over_runs['Over'].apply(
        lambda x: 'Power Play (1-6)' if x <= 5 else ('Middle (7-15)' if x <= 14 else 'Death (16-20)')
    )
    fig7 = px.bar(over_runs, x='Over', y='Avg Runs', color='Phase',
                  color_discrete_map={'Power Play (1-6)': '#4ecdc4', 'Middle (7-15)': '#ffe66d', 'Death (16-20)': '#e94560'},
                  template='plotly_dark')
    fig7.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig7, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — BOWLING
# ════════════════════════════════════════════════════════════════════════════
with tab3:
    bowl_data = deliveries[deliveries['match_id'].isin(match_ids)].copy()

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("<div class='section-header'>Top 15 Wicket Takers</div>", unsafe_allow_html=True)
        wickets = bowl_data[bowl_data['player_dismissed'].notna() & (bowl_data['dismissal_kind'] != 'run out')]
        top_bowlers = wickets.groupby('bowler').size().sort_values(ascending=False).head(15).reset_index()
        top_bowlers.columns = ['Bowler', 'Wickets']
        fig8 = px.bar(top_bowlers, x='Wickets', y='Bowler', orientation='h',
                      color='Wickets', color_continuous_scale='Purples',
                      template='plotly_dark')
        fig8.update_layout(yaxis={'categoryorder': 'total ascending'},
                           plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                           coloraxis_showscale=False)
        st.plotly_chart(fig8, use_container_width=True)

    with col_b:
        st.markdown("<div class='section-header'>Dismissal Types Breakdown</div>", unsafe_allow_html=True)
        dismissals = bowl_data[bowl_data['player_dismissed'].notna()]
        dim_type = dismissals['dismissal_kind'].value_counts().reset_index()
        dim_type.columns = ['Type', 'Count']
        fig9 = px.pie(dim_type, values='Count', names='Type', hole=0.4,
                      template='plotly_dark',
                      color_discrete_sequence=px.colors.qualitative.Pastel)
        fig9.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig9, use_container_width=True)

    # Economy rate
    st.markdown("<div class='section-header'>Best Economy Rate (min 30 overs bowled)</div>", unsafe_allow_html=True)
    econ = bowl_data.groupby('bowler').agg(
        total_runs=('total_runs', 'sum'),
        balls=('total_runs', 'count')
    ).reset_index()
    econ['overs'] = econ['balls'] / 6
    econ['economy'] = (econ['total_runs'] / econ['overs']).round(2)
    econ = econ[econ['overs'] >= 30].sort_values('economy').head(15)
    fig10 = px.bar(econ, x='economy', y='bowler', orientation='h',
                   color='economy', color_continuous_scale='Greens_r',
                   template='plotly_dark')
    fig10.update_layout(yaxis={'categoryorder': 'total descending'},
                        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                        coloraxis_showscale=False, xaxis_title='Economy Rate')
    st.plotly_chart(fig10, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 4 — VENUES
# ════════════════════════════════════════════════════════════════════════════
with tab4:
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("<div class='section-header'>Most Matches Hosted</div>", unsafe_allow_html=True)
        venues = filtered['venue'].value_counts().head(12).reset_index()
        venues.columns = ['Venue', 'Matches']
        fig11 = px.bar(venues, x='Matches', y='Venue', orientation='h',
                       color='Matches', color_continuous_scale='Teal',
                       template='plotly_dark')
        fig11.update_layout(yaxis={'categoryorder': 'total ascending'},
                            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                            coloraxis_showscale=False)
        st.plotly_chart(fig11, use_container_width=True)

    with col_b:
        st.markdown("<div class='section-header'>Bat First vs Field First Wins by Venue</div>", unsafe_allow_html=True)
        venue_toss = filtered[filtered['result'] == 'normal'].copy()
        venue_toss['bat_first_won'] = (
            ((venue_toss['toss_decision'] == 'bat') & (venue_toss['toss_winner'] == venue_toss['winner'])) |
            ((venue_toss['toss_decision'] == 'field') & (venue_toss['toss_winner'] != venue_toss['winner']))
        )
        venue_rate = venue_toss.groupby('venue')['bat_first_won'].agg(['sum', 'count']).reset_index()
        venue_rate.columns = ['Venue', 'Bat First Wins', 'Total']
        venue_rate = venue_rate[venue_rate['Total'] >= 5]
        venue_rate['Field First Wins'] = venue_rate['Total'] - venue_rate['Bat First Wins']
        venue_rate = venue_rate.sort_values('Total', ascending=False).head(10)
        fig12 = go.Figure()
        fig12.add_trace(go.Bar(name='Bat First', x=venue_rate['Venue'], y=venue_rate['Bat First Wins'], marker_color='#ffe66d'))
        fig12.add_trace(go.Bar(name='Field First', x=venue_rate['Venue'], y=venue_rate['Field First Wins'], marker_color='#4ecdc4'))
        fig12.update_layout(barmode='stack', template='plotly_dark',
                            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                            xaxis_tickangle=-30)
        st.plotly_chart(fig12, use_container_width=True)

    # City-wise match count
    st.markdown("<div class='section-header'>Matches by City</div>", unsafe_allow_html=True)
    city_data = filtered['city'].value_counts().head(15).reset_index()
    city_data.columns = ['City', 'Matches']
    fig13 = px.treemap(city_data, path=['City'], values='Matches',
                       color='Matches', color_continuous_scale='RdBu',
                       template='plotly_dark')
    fig13.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig13, use_container_width=True)

# ─── Footer ─────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center; color:#4a5568; font-size:0.85rem; padding:10px 0'>
    IPL Analytics Dashboard • Built with Streamlit & Plotly • Data: IPL 2008–2022
</div>
""", unsafe_allow_html=True)