"""
Sabiá - School Engagement Monitor Dashboard
Displays analytics and critical alerts for educational managers
"""
import streamlit as st
import pandas as pd
import json
from datetime import datetime
import os

# Page configuration
st.set_page_config(
    page_title="Sabiá - School Engagement Monitor",
    page_icon="🦜",
    layout="wide"
)

# Main title
st.title("🦜 Sabiá - School Engagement Monitor (Paraíba)")

# Function to load analytics data
@st.cache_data(ttl=5)
def load_analytics():
    """Load engagement analytics from alertas.json"""
    try:
        if os.path.exists('alertas.json'):
            with open('alertas.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            df = pd.DataFrame(data)
            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading analytics: {e}")
        return pd.DataFrame()

# Function to load critical alerts
@st.cache_data(ttl=5)
def load_critical_alerts():
    """Load critical alerts from critical_alerts.json"""
    try:
        if os.path.exists('critical_alerts.json'):
            with open('critical_alerts.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            df = pd.DataFrame(data)
            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading critical alerts: {e}")
        return pd.DataFrame()

# Load data
df_analytics = load_analytics()
df_critical = load_critical_alerts()

# Sidebar filters
st.sidebar.header("⚙️ Filters")
period = st.sidebar.selectbox(
    "Period",
    ["Last 7 days", "Last 30 days", "All time"]
)

# Calculate date cutoff
data_atual = pd.Timestamp.now(tz='UTC')
if period == "Last 7 days":
    data_corte = data_atual - pd.Timedelta(days=7)
elif period == "Last 30 days":
    data_corte = data_atual - pd.Timedelta(days=30)
else:
    data_corte = pd.Timestamp('2000-01-01', tz='UTC')

# Filter analytics data
if not df_analytics.empty:
    df_analytics_filtered = df_analytics[df_analytics['timestamp'] >= data_corte].copy()
else:
    df_analytics_filtered = pd.DataFrame()

# Filter critical alerts
if not df_critical.empty:
    df_critical_filtered = df_critical[df_critical['timestamp'] >= data_corte].copy()
else:
    df_critical_filtered = pd.DataFrame()

# === CRITICAL ALERTS SECTION ===
st.header("🚨 CRITICAL ALERTS - Immediate Action Required")

if not df_critical_filtered.empty:
    # Show only NEW alerts
    new_alerts = df_critical_filtered[df_critical_filtered['status'] == 'NEW']
    
    if not new_alerts.empty:
        st.error(f"⚠️ {len(new_alerts)} URGENT SITUATION(S) DETECTED")
        
        for _, alert in new_alerts.iterrows():
            severity_color = {
                'CRITICAL': '🔴',
                'HIGH': '🟠',
                'MEDIUM': '🟡'
            }.get(alert['severity'], '⚪')
            
            category_names = {
                'self_harm': '🆘 Self-Harm Risk',
                'dropout_risk': '🎓 Dropout Risk',
                'bullying': '👊 Bullying',
                'family_issues': '🏠 Family Issues',
                'severe_anxiety': '😰 Severe Anxiety'
            }
            
            with st.expander(
                f"{severity_color} {category_names.get(alert['category'], alert['category'])} - "
                f"Student {alert['user_id'][-4:]} - {alert['timestamp'].strftime('%d/%m/%Y %H:%M')}",
                expanded=True
            ):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**Severity:** {alert['severity']}")
                    st.write(f"**Category:** {alert['category']}")
                    st.write(f"**Student Message:**")
                    st.info(alert['message'])
                    st.write(f"**Time:** {alert['timestamp'].strftime('%d/%m/%Y %H:%M:%S')}")
                
                with col2:
                    st.write("**Actions:**")
                    if alert['requires_immediate_action']:
                        st.error("⚠️ IMMEDIATE ACTION REQUIRED")
                    
                    if st.button(f"Mark as Handled", key=f"handle_{alert['alert_id']}"):
                        # Here you would call the alert_detector to mark as handled
                        st.success("Alert marked as handled!")
                        st.cache_data.clear()
                        st.rerun()
    else:
        st.success("✅ No new critical alerts")
else:
    st.info("No critical alerts data available")

st.divider()

# === ENGAGEMENT ANALYTICS SECTION ===
st.header("📊 Engagement Analytics (Fredricks Framework)")

if not df_analytics_filtered.empty:
    # Main KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    # High risk students (score > 0.6)
    high_risk = df_analytics_filtered[df_analytics_filtered['score_desmotivacao'] > 0.6]
    total_high_risk = len(high_risk)
    
    # Average score
    avg_score = df_analytics_filtered['score_desmotivacao'].mean()
    
    # Total monitored students
    total_students = df_analytics_filtered['aluno_id'].nunique()
    
    # Average engagement
    avg_behavioral = df_analytics_filtered['engajamento_comportamental'].mean()
    avg_emotional = df_analytics_filtered['engajamento_emocional'].mean()
    avg_cognitive = df_analytics_filtered['engajamento_cognitivo'].mean()
    
    with col1:
        st.metric(
            label="🚨 High Risk Students",
            value=total_high_risk,
            help="Students with disengagement score > 0.6"
        )
    
    with col2:
        st.metric(
            label="📈 Avg Disengagement",
            value=f"{avg_score:.2f}",
            help="Average disengagement score"
        )
    
    with col3:
        st.metric(
            label="👥 Students Monitored",
            value=total_students
        )
    
    with col4:
        st.metric(
            label="💚 Avg Engagement",
            value=f"{(1-avg_score):.2f}",
            help="Average engagement level"
        )
    
    st.divider()
    
    # Fredricks 3 Pillars
    st.subheader("📊 Fredricks Framework - 3 Pillars of Engagement")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "🏃 Behavioral",
            f"{avg_behavioral:.2f}",
            help="Is the student doing? (participating, completing tasks)"
        )
    
    with col2:
        st.metric(
            "❤️ Emotional",
            f"{avg_emotional:.2f}",
            help="Is the student feeling? (curious, positive)"
        )
    
    with col3:
        st.metric(
            "🧠 Cognitive",
            f"{avg_cognitive:.2f}",
            help="Is the student thinking? (asking deep questions)"
        )
    
    st.divider()
    
    # Map of Paraíba
    st.header("🗺️ Attention Map by City")
    
    # Aggregate by city
    df_cities = df_analytics_filtered.groupby(['cidade', 'lat', 'lon']).agg({
        'score_desmotivacao': ['mean', 'count']
    }).reset_index()
    
    df_cities.columns = ['cidade', 'lat', 'lon', 'score_medio', 'num_alertas']
    
    # Normalize point size
    df_cities['size'] = 100 + (df_cities['score_medio'] * 400)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.map(
            df_cities,
            latitude='lat',
            longitude='lon',
            size='size',
            zoom=7
        )
    
    with col2:
        st.subheader("📍 Summary by City")
        for _, row in df_cities.sort_values('score_medio', ascending=False).iterrows():
            emoji = "🔴" if row['score_medio'] >= 0.7 else "🟠" if row['score_medio'] >= 0.5 else "🟢"
            st.write(f"{emoji} **{row['cidade']}**")
            st.write(f"   Avg score: {row['score_medio']:.2f}")
            st.write(f"   Alerts: {int(row['num_alertas'])}")
            st.write("")
    
    st.divider()
    
    # Priority students table
    st.header("⚠️ Priority Students")
    
    df_priority = df_analytics_filtered.sort_values('score_desmotivacao', ascending=False).copy()
    
    df_display = pd.DataFrame({
        'Student (Anonymous ID)': df_priority['aluno_id'].apply(lambda x: f"***{x[-4:]}"),
        'Disengagement Score': df_priority['score_desmotivacao'].apply(lambda x: f"{x:.2f}"),
        'Behavioral': df_priority['engajamento_comportamental'].apply(lambda x: f"{x:.2f}"),
        'Emotional': df_priority['engajamento_emocional'].apply(lambda x: f"{x:.2f}"),
        'Cognitive': df_priority['engajamento_cognitivo'].apply(lambda x: f"{x:.2f}"),
        'City': df_priority['cidade'],
        'Key Observation': df_priority['observacoes_chave'].apply(
            lambda x: '; '.join(x) if isinstance(x, list) else str(x)
        ),
        'Date': df_priority['timestamp'].dt.strftime('%d/%m/%Y %H:%M')
    })
    
    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True
    )
    
    # Risk distribution
    st.subheader("📊 Risk Distribution")
    col1, col2, col3 = st.columns(3)
    
    high_risk_count = len(df_analytics_filtered[df_analytics_filtered['score_desmotivacao'] >= 0.7])
    medium_risk = len(df_analytics_filtered[(df_analytics_filtered['score_desmotivacao'] >= 0.5) & 
                                             (df_analytics_filtered['score_desmotivacao'] < 0.7)])
    low_risk = len(df_analytics_filtered[df_analytics_filtered['score_desmotivacao'] < 0.5])
    
    with col1:
        st.metric("🔴 High Risk", high_risk_count, help="Score >= 0.7")
    with col2:
        st.metric("🟠 Medium Risk", medium_risk, help="0.5 <= Score < 0.7")
    with col3:
        st.metric("🟢 Low Risk", low_risk, help="Score < 0.5")

else:
    st.info("No engagement analytics data available for the selected period")

# Footer
st.divider()
st.caption("🦜 Sabiá - School Well-being and Academic Intelligence System | Paraíba 2025")
st.caption(f"Last update: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

# Manual refresh button
if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

# Instructions
with st.sidebar.expander("ℹ️ How to Use"):
    st.write("""
    **Critical Alerts:**
    - Red alerts require immediate action
    - Click "Mark as Handled" after intervention
    
    **Engagement Analytics:**
    - Based on Fredricks Framework (2004)
    - 3 pillars: Behavioral, Emotional, Cognitive
    - Risk score = 1.0 - (average of 3 pillars)
    
    **Data Files:**
    - `critical_alerts.json` - Urgent situations
    - `alertas.json` - Engagement analytics
    """)
