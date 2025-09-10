import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Savings Group Management",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Savings Group Management System")
st.write("Application is loading...")

# Simple authentication bypass for initial testing
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = True
    st.session_state.user = {"full_name": "Test User", "is_admin": True}

if st.session_state.logged_in:
    st.sidebar.title(f"Welcome, {st.session_state.user['full_name']}")
    
    menu = st.sidebar.selectbox(
        "Main Menu",
        ["Dashboard", "Members", "Contributions", "Loans", "Meetings", "Fines", "Reports"]
    )
    
    if menu == "Dashboard":
        st.header("Dashboard")
        st.write("Dashboard will be implemented soon.")
    
    elif menu == "Members":
        st.header("Members Management")
        st.write("Members management will be implemented soon.")
    
    # Add other menu options similarly
    
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()
else:
    st.header("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        # Simple bypass for testing
        if email and password:
            st.session_state.logged_in = True
            st.session_state.user = {"full_name": "Test User", "is_admin": True}
            st.experimental_rerun()
        else:
            st.error("Please enter email and password")
