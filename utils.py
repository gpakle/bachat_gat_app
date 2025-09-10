import streamlit as st
from supabase import create_client
import os
from datetime import datetime, date
import pandas as pd

# Initialize Supabase client
@st.cache_resource
def init_connection():
    url = st.secrets.get("SUPABASE_URL", os.environ.get("SUPABASE_URL"))
    key = st.secrets.get("SUPABASE_KEY", os.environ.get("SUPABASE_KEY"))
    return create_client(url, key)

supabase = init_connection()

# Authentication functions
def login_user(email, password):
    try:
        # In a real app, you should hash passwords and verify properly
        response = supabase.table("members").select("*").eq("email", email).eq("password", password).execute()
        if response.data:
            user = response.data[0]
            return user
        else:
            return None
    except Exception as e:
        st.error(f"Login error: {e}")
        return None

def get_current_cycle():
    try:
        response = supabase.table("savings_cycles").select("*").eq("is_active", True).execute()
        if response.data:
            return response.data[0]
        else:
            return None
    except Exception as e:
        st.error(f"Error fetching current cycle: {e}")
        return None

def get_group_summary(cycle_id):
    try:
        # Get total contributions
        contrib_response = supabase.table("contributions").select("amount").eq("cycle_id", cycle_id).eq("status", "completed").execute()
        total_contrib = sum(item['amount'] for item in contrib_response.data) if contrib_response.data else 0
        
        # Get total loans issued
        loans_issued_response = supabase.table("loans").select("principal_amount").eq("status", "active").execute()
        total_loans_issued = sum(item['principal_amount'] for item in loans_issued_response.data) if loans_issued_response.data else 0
        
        # Get total loans repaid
        loans_repaid_response = supabase.table("loan_repayments").select("amount").execute()
        total_loans_repaid = sum(item['amount'] for item in loans_repaid_response.data) if loans_repaid_response.data else 0
        
        # Get active members count
        members_response = supabase.table("members").select("id").eq("is_active", True).execute()
        active_members = len(members_response.data) if members_response.data else 0
        
        return {
            "total_contributions": total_contrib,
            "total_loans_issued": total_loans_issued,
            "total_loans_repaid": total_loans_repaid,
            "active_members": active_members,
            "current_fund": total_contrib + total_loans_repaid - total_loans_issued
        }
    except Exception as e:
        st.error(f"Error fetching group summary: {e}")
        return None
