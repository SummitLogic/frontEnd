import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page configuration
st.set_page_config(
    page_title="GateFlow Dashboard - SummitLogic",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# Title and header
st.title("🛫 GateFlow Dashboard - SummitLogic")
st.markdown("### All-in-One Galley Operations Platform")
st.markdown("---")

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Overview", 
    "🍾 Alcohol Bottle Handling", 
    "⚠️ Error Detection", 
    "👥 Employee Efficiency"
])

# Sample data
waste_reduction_data = pd.DataFrame({
    'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    'Before GateFlow': [32, 35, 33, 34, 36, 31],
    'After GateFlow': [22, 24, 23, 21, 25, 20]
})

bottle_disposition_data = pd.DataFrame({
    'Action': ['Keep', 'Combine', 'Discard'],
    'Percentage': [55, 25, 20]
})

error_reduction_data = pd.DataFrame({
    'Week': ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6'],
    'Errors': [45, 38, 32, 28, 24, 22]
})

packing_accuracy_data = pd.DataFrame({
    'Error Type': ['Product Swaps', 'Missing Items', 'Wrong Slots', 'Count Errors'],
    'Before': [28, 22, 18, 15],
    'After': [12, 9, 8, 6]
})

training_progress_data = pd.DataFrame({
    'Module': ['Bottle Handling', 'Cart Packing', 'Safety Protocols', 'QR Scanning', 'Photo Verification'],
    'Completion %': [92, 88, 95, 85, 90]
})

leaderboard_data = pd.DataFrame({
    'Rank': [1, 2, 3, 4, 5],
    'Employee': ['Maria Rodriguez', 'James Chen', 'Sarah Johnson', 'Ahmed Hassan', 'Emma Wilson'],
    'Score': [2850, 2720, 2680, 2540, 2490],
    'Badge': ['🏆', '🥈', '🥉', '⭐', '⭐']
})

# TAB 1: OVERVIEW
with tab1:
    # Hero section
    st.markdown("""
        <div style='background: linear-gradient(135deg, #1f77b4 0%, #2c5aa0 100%); 
                    padding: 30px; border-radius: 10px; color: white; margin-bottom: 30px;'>
            <h2>✈️ GateFlow by SummitLogic</h2>
            <p style='font-size: 18px; margin-top: 10px;'>
                Unifying alcohol bottle handling, real-time packing guidance with error detection, 
                and employee training into a single role-aware experience for logistics and airport operations.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Waste Reduction",
            value="20-30%",
            delta="25% improvement"
        )
    
    with col2:
        st.metric(
            label="Error Reduction",
            value="50%",
            delta="Fewer packing errors"
        )
    
    with col3:
        st.metric(
            label="Faster Ramp-Up",
            value="30%",
            delta="Training time saved"
        )
    
    with col4:
        st.metric(
            label="Throughput Gain",
            value="20%",
            delta="Productivity increase"
        )
    
    st.markdown("---")
    
    # What GateFlow Does
    st.subheader("What GateFlow Does")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            **🎯 Role-Aware Experience**
            
            Adapts immediately based on user role - ground operator, flight attendant, or supervisor. 
            Each sees only relevant actions and data.
        """)
    
    with col2:
        st.markdown("""
            **📦 Smart Bottle Management**
            
            QR-based tracking with automated recommendations for keep, combine, or discard decisions. 
            Complete audit trail with photos and timestamps.
        """)
    
    with col3:
        st.markdown("""
            **🎓 Gamified Training**
            
            Language-learning-style modules with instant feedback, leaderboards, and badges. 
            New hire mode for personalized pacing.
        """)
    
    st.markdown("---")
    
    # Mission statement
    st.info("""
        **SummitLogic Mission**: We deliver practical software that fits the rhythm of airport work, 
        removes uncertainty from daily decisions, and turns scattered tasks into a smooth and measurable process.
    """)

# TAB 2: ALCOHOL BOTTLE HANDLING
with tab2:
    st.header("🍾 Alcohol Bottle Handling")
    
    st.markdown("""
        Every bottle carries a QR that links to a record with its product data, batch, and policy for the airline. 
        During service the flight attendant logs each time liquid is served with a fast interaction that updates 
        the remaining volume.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Waste Reduction Over Time")
        fig_waste = go.Figure()
        fig_waste.add_trace(go.Scatter(
            x=waste_reduction_data['Month'],
            y=waste_reduction_data['Before GateFlow'],
            mode='lines+markers',
            name='Before GateFlow',
            line=dict(color='#ef4444', width=3),
            marker=dict(size=8)
        ))
        fig_waste.add_trace(go.Scatter(
            x=waste_reduction_data['Month'],
            y=waste_reduction_data['After GateFlow'],
            mode='lines+markers',
            name='After GateFlow',
            line=dict(color='#10b981', width=3),
            marker=dict(size=8)
        ))
        fig_waste.update_layout(
            yaxis_title="Waste Percentage (%)",
            xaxis_title="Month",
            height=400,
            hovermode='x unified'
        )
        st.plotly_chart(fig_waste, use_container_width=True)
    
    with col2:
        st.subheader("Bottle Disposition Breakdown")
        fig_disposition = px.pie(
            bottle_disposition_data,
            values='Percentage',
            names='Action',
            color='Action',
            color_discrete_map={'Keep': '#10b981', 'Combine': '#3b82f6', 'Discard': '#ef4444'},
            hole=0.4
        )
        fig_disposition.update_traces(textposition='inside', textinfo='percent+label')
        fig_disposition.update_layout(height=400)
        st.plotly_chart(fig_disposition, use_container_width=True)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Average Waste Reduction", "25%", delta="-7% from baseline")
    
    with col2:
        st.metric("Audit Compliance", "100%", delta="Zero violations")
    
    with col3:
        st.metric("Decision Time", "< 30 sec", delta="-45 sec average")
    
    st.markdown("---")
    
    st.subheader("How It Works")
    st.markdown("""
        1. **During Flight**: Flight attendants log usage with fast interactions
        2. **Upon Return**: GateFlow calculates current amounts and applies airline rules
        3. **Clear Instructions**: Operators receive specific actions (keep/combine/discard)
        4. **Audit Trail**: Every decision stored with photo, timestamp, and operator ID
    """)

# TAB 3: ERROR DETECTION
with tab3:
    st.header("⚠️ Real-Time Error Detection")
    
    st.markdown("""
        GateFlow guides the packing process with computer vision assistance and simple barcode sweeps when available. 
        The app shows the correct product, the correct tray or cart slot, and the correct order of loading.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Error Reduction Trend")
        fig_errors = px.line(
            error_reduction_data,
            x='Week',
            y='Errors',
            markers=True,
            line_shape='spline'
        )
        fig_errors.update_traces(
            line=dict(color='#ef4444', width=3),
            marker=dict(size=10)
        )
        fig_errors.update_layout(
            yaxis_title="Number of Errors",
            xaxis_title="Week",
            height=400
        )
        st.plotly_chart(fig_errors, use_container_width=True)
    
    with col2:
        st.subheader("Packing Accuracy: Before vs After")
        fig_accuracy = go.Figure()
        fig_accuracy.add_trace(go.Bar(
            name='Before GateFlow',
            x=packing_accuracy_data['Error Type'],
            y=packing_accuracy_data['Before'],
            marker_color='#ef4444'
        ))
        fig_accuracy.add_trace(go.Bar(
            name='After GateFlow',
            x=packing_accuracy_data['Error Type'],
            y=packing_accuracy_data['After'],
            marker_color='#10b981'
        ))
        fig_accuracy.update_layout(
            barmode='group',
            yaxis_title="Error Count",
            height=400
        )
        st.plotly_chart(fig_accuracy, use_container_width=True)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Error Reduction", "50%", delta="Fewer packing mistakes")
    
    with col2:
        st.metric("Rework Reduction", "45%", delta="Less post-seal fixes")
    
    with col3:
        st.metric("First-Pass Yield", "95%", delta="+45% improvement")
    
    st.markdown("---")
    
    st.subheader("Detection Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            **✅ Real-Time Guidance**
            - Correct product identification
            - Proper tray/cart slot placement
            - Optimal loading sequence
            - Flight-specific requirements
        """)
    
    with col2:
        st.markdown("""
            **📸 Verification System**
            - Top-down photo check before sealing
            - Count reconciliation with plan
            - Computer vision assistance
            - Barcode scanning support
        """)

# TAB 4: EMPLOYEE EFFICIENCY
with tab4:
    st.header("👥 Employee Efficiency")
    
    st.markdown("""
        GateFlow includes a training space that looks and feels like a language learning app. 
        Staff complete short levels tied to the exact tasks they perform on the floor.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Training Module Completion")
        fig_training = px.bar(
            training_progress_data,
            x='Completion %',
            y='Module',
            orientation='h',
            color='Completion %',
            color_continuous_scale='blues',
            text='Completion %'
        )
        fig_training.update_traces(texttemplate='%{text}%', textposition='outside')
        fig_training.update_layout(
            xaxis_title="Completion Percentage",
            yaxis_title="",
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig_training, use_container_width=True)
    
    with col2:
        st.subheader("Ramp-Up Time Comparison")
        fig_rampup = go.Figure()
        fig_rampup.add_trace(go.Bar(
            x=['Traditional Training', 'With GateFlow'],
            y=[12, 8.4],
            marker_color=['#ef4444', '#10b981'],
            text=[12, 8.4],
            texttemplate='%{text} weeks',
            textposition='outside'
        ))
        fig_rampup.update_layout(
            yaxis_title="Weeks to Full Productivity",
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig_rampup, use_container_width=True)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Faster Ramp-Up", "30%", delta="3.6 weeks saved")
    
    with col2:
        st.metric("Throughput Gain", "20%", delta="Higher first-pass yield")
    
    with col3:
        st.metric("Employee Satisfaction", "4.7/5", delta="+0.9 points")
    
    st.markdown("---")
    
    st.subheader("🏆 Current Leaderboard")
    
    # Style the leaderboard
    def style_leaderboard(row):
        if row['Rank'] == 1:
            return ['background-color: #ffd700'] * len(row)
        elif row['Rank'] == 2:
            return ['background-color: #c0c0c0'] * len(row)
        elif row['Rank'] == 3:
            return ['background-color: #cd7f32'] * len(row)
        else:
            return [''] * len(row)
    
    styled_leaderboard = leaderboard_data.style.apply(style_leaderboard, axis=1)
    st.dataframe(styled_leaderboard, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    st.subheader("Training Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            **📚 Learning System**
            - Short, task-specific levels
            - Images and quick checks
            - Instant feedback
            - Progress tracking
        """)
    
    with col2:
        st.markdown("""
            **🎮 Engagement Tools**
            - Friendly leaderboards
            - Achievement badges
            - New hire mode with slower pacing
            - Recognition system
        """)

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/200x80/1f77b4/ffffff?text=SummitLogic", use_column_width=True)
    st.markdown("---")
    
    st.subheader("About GateFlow")
    st.markdown("""
        GateFlow is SummitLogic's all-in-one application for galley operations, unifying:
        
        - 🍾 Alcohol bottle handling
        - ⚠️ Real-time error detection
        - 👥 Employee training & engagement
        
        Into a single role-aware experience.
    """)
    
    st.markdown("---")
    
    st.subheader("Key Benefits")
    st.success("✅ 20-30% waste reduction")
    st.success("✅ 50% fewer packing errors")
    st.success("✅ 30% faster employee ramp-up")
    st.success("✅ 20% throughput gain")
    
    st.markdown("---")
    
    st.subheader("Contact")
    st.info("📧 info@summitlogic.com")
    
    st.markdown("---")
    st.caption("© 2024 SummitLogic. All rights reserved.")