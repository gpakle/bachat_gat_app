import streamlit as st
from utils import *
import pandas as pd
from datetime import datetime

def app():
    st.header("Loan Management")
    
    # Loan issuance form
    with st.expander("📝 Issue New Loan", expanded=True):
        # Get active members for selection
        try:
            members_response = supabase.table("members").select("id, full_name").eq("is_active", True).execute()
            members = {m['full_name']: m['id'] for m in members_response.data}
        except Exception as e:
            st.error(f"Error loading members: {e}")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            borrower_name = st.selectbox("Borrower", options=list(members.keys()))
            principal_amount = st.number_input("Loan Amount (₹)", min_value=0, step=1000)
            interest_rate = st.slider("Interest Rate (%)", min_value=0.0, max_value=30.0, value=12.0, step=0.5)
        
        with col2:
            issue_date = st.date_input("Issue Date", value=datetime.now().date())
            due_date = st.date_input("Due Date", value=datetime.now().replace(month=datetime.now().month+6).date())
            purpose = st.text_input("Purpose")
        
        if st.button("Issue Loan"):
            if principal_amount > 0:
                try:
                    # Calculate total amount with interest
                    interest_amount = principal_amount * (interest_rate / 100)
                    total_due = principal_amount + interest_amount
                    
                    loan_data = {
                        "borrower_id": members[borrower_name],
                        "principal_amount": principal_amount,
                        "interest_rate": interest_rate,
                        "total_amount_due": total_due,
                        "issue_date": issue_date.isoformat(),
                        "due_date": due_date.isoformat(),
                        "purpose": purpose,
                        "status": "active"
                    }
                    supabase.table("loans").insert(loan_data).execute()
                    st.success("Loan issued successfully!")
                except Exception as e:
                    st.error(f"Error issuing loan: {e}")
            else:
                st.warning("Please enter a valid loan amount.")
    
    st.divider()
    
    # Loan repayment form
    st.subheader("Record Loan Repayment")
    
    try:
        # Get active loans
        loans_response = supabase.table("loans").select("*, members(full_name)").eq("status", "active").execute()
        if loans_response.data:
            loans = {f"{loan['members']['full_name']} - ₹{loan['principal_amount']}": loan['id'] for loan in loans_response.data}
            
            selected_loan = st.selectbox("Select Loan", options=list(loans.keys()))
            loan_id = loans[selected_loan]
            
            col1, col2 = st.columns(2)
            
            with col1:
                repayment_amount = st.number_input("Repayment Amount (₹)", min_value=0, step=100)
                repayment_date = st.date_input("Repayment Date", value=datetime.now().date(), key="repayment_date")
            
            with col2:
                payment_method = st.selectbox("Payment Method", 
                                            options=["Cash", "Bank Transfer", "UPI", "Other"],
                                            key="repayment_method")
            
            if st.button("Record Repayment"):
                if repayment_amount > 0:
                    try:
                        # Get current loan details
                        loan_details = supabase.table("loans").select("*").eq("id", loan_id).execute().data[0]
                        
                        # Update loan record
                        new_amount_repaid = loan_details['amount_repaid'] + repayment_amount
                        new_status = "paid" if new_amount_repaid >= loan_details['total_amount_due'] else "active"
                        
                        supabase.table("loans").update({
                            "amount_repaid": new_amount_repaid,
                            "status": new_status
                        }).eq("id", loan_id).execute()
                        
                        # Create repayment record
                        repayment_data = {
                            "loan_id": loan_id,
                            "amount": repayment_amount,
                            "payment_date": repayment_date.isoformat(),
                            "payment_method": payment_method.lower().replace(" ", "_")
                        }
                        supabase.table("loan_repayments").insert(repayment_data).execute()
                        
                        st.success("Repayment recorded successfully!")
                    except Exception as e:
                        st.error(f"Error recording repayment: {e}")
                else:
                    st.warning("Please enter a valid repayment amount.")
        else:
            st.info("No active loans found.")
    except Exception as e:
        st.error(f"Error loading loans: {e}")
    
    st.divider()
    
    # Display active loans
    st.subheader("Active Loans")
    try:
        loans = supabase.table("loans").select("*, members(full_name)").eq("status", "active").execute()
        if loans.data:
            df = pd.DataFrame(loans.data)
            df['member_name'] = df['members'].apply(lambda x: x['full_name'] if x else 'Unknown')
            
            # Calculate remaining amount
            df['remaining_amount'] = df['total_amount_due'] - df['amount_repaid']
            
            # Format for display
            df_display = df[['member_name', 'principal_amount', 'interest_rate', 'total_amount_due', 
                           'amount_repaid', 'remaining_amount', 'issue_date', 'due_date']].copy()
            
            st.dataframe(df_display, use_container_width=True)
        else:
            st.info("No active loans.")
    except Exception as e:
        st.error(f"Error loading loans: {e}")
