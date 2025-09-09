import streamlit as st
from utils import *
import pandas as pd
from datetime import datetime

def app():
    st.header("Contributions Management")
    
    # Get current cycle
    current_cycle = st.session_state.current_cycle
    if not current_cycle:
        st.error("No active savings cycle found. Please set up a cycle first.")
        return
    
    st.info(f"Current cycle: {current_cycle['start_date']} to {current_cycle['end_date']} | Monthly contribution: ₹{current_cycle['monthly_contribution']}")
    
    # Quick contribution recording
    with st.expander("💰 Record Contribution", expanded=True):
        # Get active members for selection
        try:
            members_response = supabase.table("members").select("id, full_name").eq("is_active", True).execute()
            members = {m['full_name']: m['id'] for m in members_response.data}
        except Exception as e:
            st.error(f"Error loading members: {e}")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            member_name = st.selectbox("Member", options=list(members.keys()))
            amount = st.number_input("Amount (₹)", 
                                    min_value=0, 
                                    value=current_cycle['monthly_contribution'],
                                    step=100)
        
        with col2:
            payment_date = st.date_input("Payment Date", value=datetime.now().date())
            payment_method = st.selectbox("Payment Method", 
                                         options=["Cash", "Bank Transfer", "UPI", "Other"])
        
        description = st.text_input("Description (optional)", 
                                   value=f"Monthly contribution - {payment_date.strftime('%B %Y')}")
        
        if st.button("Record Contribution"):
            if amount > 0:
                try:
                    contribution_data = {
                        "member_id": members[member_name],
                        "amount": amount,
                        "cycle_id": current_cycle['id'],
                        "payment_date": payment_date.isoformat(),
                        "payment_method": payment_method.lower().replace(" ", "_"),
                        "description": description
                    }
                    supabase.table("contributions").insert(contribution_data).execute()
                    st.success("Contribution recorded successfully!")
                except Exception as e:
                    st.error(f"Error recording contribution: {e}")
            else:
                st.warning("Please enter a valid amount.")
    
    st.divider()
    
    # Batch contribution recording for all members
    st.subheader("Record Contributions for All Members")
    st.warning("This will record the standard monthly contribution for all active members.")
    
    batch_date = st.date_input("Batch Payment Date", value=datetime.now().date(), key="batch_date")
    
    if st.button("Record Batch Contributions"):
        try:
            active_members = supabase.table("members").select("id").eq("is_active", True).execute()
            
            success_count = 0
            for member in active_members.data:
                contribution_data = {
                    "member_id": member['id'],
                    "amount": current_cycle['monthly_contribution'],
                    "cycle_id": current_cycle['id'],
                    "payment_date": batch_date.isoformat(),
                    "payment_method": "batch",
                    "description": f"Batch contribution - {batch_date.strftime('%B %Y')}"
                }
                supabase.table("contributions").insert(contribution_data).execute()
                success_count += 1
            
            st.success(f"Recorded contributions for {success_count} members.")
        except Exception as e:
            st.error(f"Error recording batch contributions: {e}")
    
    st.divider()
    
    # Display recent contributions
    st.subheader("Recent Contributions")
    try:
        contributions = supabase.table("contributions").select("*, members(full_name)").eq("cycle_id", current_cycle['id']).order("created_at", desc=True).limit(20).execute()
        if contributions.data:
            df = pd.DataFrame(contributions.data)
            df['member_name'] = df['members'].apply(lambda x: x['full_name'] if x else 'Unknown')
            
            # Format for display
            df_display = df[['member_name', 'amount', 'payment_date', 'payment_method', 'description']].copy()
            df_display['payment_date'] = pd.to_datetime(df_display['payment_date']).dt.strftime('%Y-%m-%d')
            
            st.dataframe(df_display, use_container_width=True)
            
            # Download option
            csv = df_display.to_csv(index=False)
            st.download_button(
                label="Download as CSV",
                data=csv,
                file_name=f"contributions_{datetime.now().date()}.csv",
                mime="text/csv",
            )
        else:
            st.info("No contributions recorded yet.")
    except Exception as e:
        st.error(f"Error loading contributions: {e}")
