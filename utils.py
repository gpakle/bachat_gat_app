import streamlit as st
import os
from datetime import datetime, date
import pandas as pd
import supabase

# Initialize Supabase client
@st.cache_resource
def init_connection():
    url = st.secrets.get("SUPABASE_URL", os.environ.get("SUPABASE_URL"))
    key = st.secrets.get("SUPABASE_KEY", os.environ.get("SUPABASE_KEY"))
    return supabase.create_client(url, key)

# Try to initialize connection but don't break if it fails
try:
    supabase_client = init_connection()
except Exception as e:
    st.error(f"Database connection failed: {e}")
    supabase_client = None

# Authentication functions
def login_user(email, password):
    try:
        if not supabase_client:
            return None
            
        response = supabase_client.table("members").select("*").eq("email", email).eq("password", password).execute()
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
        if not supabase_client:
            return None
            
        response = supabase_client.table("savings_cycles").select("*").eq("is_active", True).execute()
        if response.data:
            return response.data[0]
        else:
            return None
    except Exception as e:
        st.error(f"Error fetching current cycle: {e}")
        return None
