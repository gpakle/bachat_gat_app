import streamlit as st
from utils import *
import plotly.express as px
import pandas as pd

def app():
    st.header("Dashboard")
    
    # Get current cycle and group summary
    current_cycle = st.session_state.current_cycle
    if not current_cycle:
        st.error("No active savings cycle found. Please contact an administrator.")
        return
    
    summary = get_group_summary(current_cycle['id'])
    if not summary:
        st.error("Error retrieving data.")
        return
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">₹{summary['total_contributions']}</div>
            <div class="metric-label">Total Contributions</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">₹{summary['total_loans_issued']}</div>
            <div class="metric-label">Total Loans Issued</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">₹{summary['total_loans_repaid']}</div>
            <div class="metric-label">Total Loans Repaid</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{summary['active_members']}</div>
            <div class="metric-label">Active Members</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Current fund
    st.markdown(f"""
    <div class="metric-card" style="margin-top: 20px;">
        <div class="metric-value">₹{summary['current_fund']}</div>
        <div class="metric-label">Current Group Fund</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Charts and visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # Contribution trends
        st.subheader("Contribution Trends")
        try:
            contributions = supabase.table("contributions").select("amount, payment_date").eq("cycle_id", current_cycle['id']).execute()
            if contributions.data:
                df = pd.DataFrame(contributions.data)
                df['payment_date'] = pd.to_datetime(df['payment_date'])
                df = df.groupby(df['payment_date'].dt.to_period('M')).sum().reset_index()
                df['payment_date'] = df['payment_date'].dt.to_timestamp()
                
                fig = px.bar(df, x='payment_date', y='amount', title="Monthly Contributions")
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating chart: {e}")
    
    with col2:
        # Loan status
        st.subheader("Loan Status")
        try:
            loans = supabase.table("loans").select("status, count(*)").group("status").execute()
            if loans.data:
                df = pd.DataFrame(loans.data)
                fig = px.pie(df, values='count', names='status', title="Loan Status Distribution")
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating chart: {e}")
    
    # Recent transactions
    st.subheader("Recent Transactions")
    try:
        transactions = supabase.table("contributions").select("*, members(full_name)").eq("cycle_id", current_cycle['id']).order("created_at", desc=True).limit(10).execute()
        if transactions.data:
            df = pd.DataFrame(transactions.data)
            df['member_name'] = df['members'].apply(lambda x: x['full_name'] if x else 'Unknown')
            st.dataframe(df[['member_name', 'amount', 'payment_date', 'status']], use_container_width=True)
        else:
            st.info("No transactions found.")
    except Exception as e:
        st.error(f"Error loading transactions: {e}")
