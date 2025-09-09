import streamlit as st
from utils import *
from streamlit_option_menu import option_menu

# Page configuration
st.set_page_config(
    page_title="Savings Group Management",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #2E86AB;
    }
    .metric-label {
        font-size: 1rem;
        color: #7f8c8d;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for authentication
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'current_cycle' not in st.session_state:
    st.session_state.current_cycle = get_current_cycle()

# Login Section
if not st.session_state.logged_in:
    st.markdown('<h1 class="main-header">Savings Group Management System</h1>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            st.subheader("Login")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("Login")
            
            if login_button:
                user = login_user(email, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid email or password.")

# Main Application
else:
    # Sidebar with navigation
    with st.sidebar:
        st.title(f"Welcome, {st.session_state.user['full_name']}")
        
        # Navigation menu
        selected = option_menu(
            menu_title="Main Menu",
            options=["Dashboard", "Members", "Contributions", "Loans", "Meetings", "Fines", "Reports"],
            icons=["house", "people", "cash-coin", "bank", "calendar-event", "exclamation-circle", "bar-chart"],
            menu_icon="cast",
            default_index=0,
        )
        
        # Logout button
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.rerun()
    
    # Load the selected page
    if selected == "Dashboard":
        from pages import dashboard
        dashboard.app()
    elif selected == "Members":
        from pages import members
        members.app()
    elif selected == "Contributions":
        from pages import contributions
        contributions.app()
    elif selected == "Loans":
        from pages import loans
        loans.app()
    elif selected == "Meetings":
        from pages import meetings
        meetings.app()
    elif selected == "Fines":
        from pages import fines
        fines.app()
    elif selected == "Reports":
        from pages import reports
        reports.app()
