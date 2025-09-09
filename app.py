import streamlit as st
from utils import *
from streamlit_option_menu import option_menu

# Page configuration
st.set_page_config(
    page_title="बचत गट व्यवस्थापन",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for authentication
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'current_cycle' not in st.session_state:
    st.session_state.current_cycle = get_current_cycle()

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

# Login Section
if not st.session_state.logged_in:
    st.markdown('<h1 class="main-header">बचत गट व्यवस्थापन प्रणाली</h1>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            st.subheader("लॉगिन करा")
            email = st.text_input("ईमेल")
            password = st.text_input("पासवर्ड", type="password")
            login_button = st.form_submit_button("लॉगिन")
            
            if login_button:
                user = login_user(email, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.success("यशस्वीरीत्या लॉगिन केले!")
                    st.rerun()
                else:
                    st.error("अवैध ईमेल किंवा पासवर्ड.")

# Main Application
else:
    # Sidebar with navigation
    with st.sidebar:
        st.title(f"नमस्कार, {st.session_state.user['full_name']}")
        
        # Navigation menu
        selected = option_menu(
            menu_title="मुख्य मेनू",
            options=["डॅशबोर्ड", "सदस्य", "योगदान", "उधार", "मीटिंग", "जुलेबी", "अहवाल"],
            icons=["house", "people", "cash-coin", "bank", "calendar-event", "exclamation-circle", "bar-chart"],
            menu_icon="cast",
            default_index=0,
        )
        
        # Logout button
        if st.button("लॉगआउट"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.rerun()
    
    # Load the selected page
    if selected == "डॅशबोर्ड":
        from pages import 1_डॅशबोर्ड
        1_डॅशबोर्ड.app()
    elif selected == "सदस्य":
        from pages import 2_सदस्य
        2_सदस्य.app()
    elif selected == "योगदान":
        from pages import 3_योगदान
        3_योगदान.app()
    elif selected == "उधार":
        from pages import 4_उधार
        4_उधार.app()
    elif selected == "मीटिंग":
        from pages import 5_मीटिंग
        5_मीटिंग.app()
    elif selected == "जुलेबी":
        from pages import 6_जुलेबी
        6_जुलेबी.app()
    elif selected == "अहवाल":
        from pages import 7_अहवाल
        7_अहवाल.app()
