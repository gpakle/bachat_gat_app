import streamlit as st
from utils import *
import pandas as pd

def app():
    st.header("Members Management")
    
    # Display existing members
    st.subheader("Current Members")
    try:
        members = supabase.table("members").select("*").order("full_name").execute()
        if members.data:
            df = pd.DataFrame(members.data)
            st.dataframe(df[['full_name', 'email', 'phone_number', 'joined_date', 'is_active']], use_container_width=True)
        else:
            st.info("No members found.")
    except Exception as e:
        st.error(f"Error loading members: {e}")
    
    # Add new member form
    st.subheader("Add New Member")
    with st.form("add_member_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input("Full Name")
            email = st.text_input("Email")
            phone_number = st.text_input("Phone Number")
        
        with col2:
            address = st.text_area("Address")
            is_admin = st.checkbox("Is Admin")
        
        submitted = st.form_submit_button("Add Member")
        
        if submitted:
            if full_name and email and phone_number:
                try:
                    member_data = {
                        "full_name": full_name,
                        "email": email,
                        "phone_number": phone_number,
                        "address": address,
                        "is_admin": is_admin
                    }
                    supabase.table("members").insert(member_data).execute()
                    st.success("Member added successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding member: {e}")
            else:
                st.warning("Please fill in all required fields (Name, Email, Phone).")
