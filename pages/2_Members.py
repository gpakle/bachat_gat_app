import streamlit as st
from utils import *
import pandas as pd

def app():
    st.header("Members Management")
    
    # Quick add member form
    with st.expander("➕ Quick Add Member", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input("Full Name*")
            email = st.text_input("Email*")
            phone_number = st.text_input("Phone Number*")
        
        with col2:
            address = st.text_area("Address")
            is_admin = st.checkbox("Is Admin")
        
        if st.button("Add Member"):
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
                    st.success(f"Member {full_name} added successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding member: {e}")
            else:
                st.warning("Please fill in all required fields (Name, Email, Phone).")
    
    st.divider()
    
    # Display existing members
    st.subheader("Current Members")
    try:
        members = supabase.table("members").select("*").order("full_name").execute()
        if members.data:
            df = pd.DataFrame(members.data)
            
            # Format for better display
            df_display = df[['full_name', 'email', 'phone_number', 'joined_date', 'is_active']].copy()
            df_display['is_active'] = df_display['is_active'].apply(lambda x: 'Yes' if x else 'No')
            
            st.dataframe(df_display, use_container_width=True)
            
            # Member actions
            selected_member = st.selectbox("Select member for actions", 
                                         options=df['full_name'].tolist(),
                                         key="member_actions")
            
            if selected_member:
                member_id = df[df['full_name'] == selected_member]['id'].iloc[0]
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("Deactivate Member", key="deactivate_btn"):
                        supabase.table("members").update({"is_active": False}).eq("id", member_id).execute()
                        st.success(f"Member {selected_member} deactivated.")
                        st.rerun()
                
                with col2:
                    if st.button("Activate Member", key="activate_btn"):
                        supabase.table("members").update({"is_active": True}).eq("id", member_id).execute()
                        st.success(f"Member {selected_member} activated.")
                        st.rerun()
        else:
            st.info("No members found. Add your first member above.")
    except Exception as e:
        st.error(f"Error loading members: {e}")
