import streamlit as st
from utils import *
import pandas as pd

def app():
    st.header("Contributions Management")
    
    # Get current cycle
    current_cycle = st.session_state.current_cycle
    if not current_cycle:
        st.error("No active savings cycle found.")
        return
    
    # Record new contribution
    st.subheader("Record New Contribution")
    
    # Get active members for selection
    try:
        members_response = supabase.table("members").select("id, full_name").eq("is_active", True).execute()
        members = {m['full_name']: m['id'] for m in members_response.data}
    except Exception as e:
        st.error(f"Error loading members: {e}")
        return
    
    with st.form("contribution_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            member_name = st.selectbox("Member", options=list(members.keys()))
            amount = st.number_input("Amount (₹)", min_value=0, step=100)
        
        with col2:
            payment_date = st.date_input("Payment Date", value=datetime.now().date())
            payment_method = st.selectbox("Payment Method", options=["Cash", "Bank Transfer", "UPI"])
        
        description = st.text_input("Description (optional)")
        
        submitted = st.form_submit_button("Record Contribution")
        
        if submitted:
            if amount > 0:
                try:
                    contribution_data = {
                        "member_id": members[member_name],
                        "amount": amount,
                        "cycle_id": current_cycle['id'],
                        "payment_date": payment_date.isoformat(),
                        "payment_method": payment_method,
                        "description": description or f"Contribution by {member_name}"
                    }
                    supabase.table("contributions").insert(contribution_data).execute()
                    st.success("Contribution recorded successfully!")
                except Exception as e:
                    st.error(f"Error recording contribution: {e}")
            else:
                st.warning("Please enter a valid amount.")
    
    # Display recent contributions
    st.subheader("Recent Contributions")
    try:
        contributions = supabase.table("contributions").select("*, members(full_name)").eq("cycle_id", current_cycle['id']).order("created_at", desc=True).limit(20).execute()
        if contributions.data:
            df = pd.DataFrame(contributions.data)
            df['member_name'] = df['members'].apply(lambda x: x['full_name'] if x else 'Unknown')
            st.dataframe(df[['member_name', 'amount', 'payment_date', 'payment_method', 'status']], use_container_width=True)
        else:
            st.info("No contributions recorded yet.")
    except Exception as e:
        st.error(f"Error loading contributions: {e}")
