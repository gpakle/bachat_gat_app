import streamlit as st
import pandas as pd
import os
from datetime import date
import io

# === File paths ===
DATA_DIR = "data"
MEMBERS_FILE = os.path.join(DATA_DIR, "members.csv")
SAVINGS_FILE = os.path.join(DATA_DIR, "savings.csv")
LOANS_FILE = os.path.join(DATA_DIR, "loans.csv")
REPAYMENTS_FILE = os.path.join(DATA_DIR, "repayments.csv")

# === Ensure data folder exists ===
os.makedirs(DATA_DIR, exist_ok=True)

# === Load or initialize CSVs ===
def load_csv(path, cols):
    if os.path.exists(path):
        return pd.read_csv(path)
    else:
        return pd.DataFrame(columns=cols)

members = load_csv(MEMBERS_FILE, ["id", "name", "phone", "join_date"])
savings = load_csv(SAVINGS_FILE, ["member_id", "date", "amount"])
loans = load_csv(LOANS_FILE, ["loan_id", "member_id", "date", "amount", "status"])
repayments = load_csv(REPAYMENTS_FILE, ["loan_id", "date", "amount"])

# === Streamlit UI ===
st.set_page_config(page_title="Savings Group Management", layout="wide")
st.title("💰 Small Savings Group Management System")

menu = ["👥 Members", "💵 Savings", "📑 Loans", "📊 Reports"]
choice = st.sidebar.radio("Navigate", menu)

# --- MEMBERS ---
if choice == "👥 Members":
    st.header("👥 Members Management")

    with st.form("member_form"):
        name = st.text_input("Name")
        phone = st.text_input("Phone")
        join_date = st.date_input("Join Date", date.today())
        submitted = st.form_submit_button("Add Member")
        if submitted and name:
            new_id = len(members) + 1
            new_member = {"id": new_id, "name": name, "phone": phone, "join_date": join_date}
            members = pd.concat([members, pd.DataFrame([new_member])], ignore_index=True)
            members.to_csv(MEMBERS_FILE, index=False)
            st.success(f"✅ Member {name} added!")

    st.subheader("Members List")
    st.dataframe(members)

# --- SAVINGS ---
elif choice == "💵 Savings":
    st.header("💵 Record Savings")
    if members.empty:
        st.warning("No members found. Please add members first.")
    else:
        with st.form("savings_form"):
            member = st.selectbox("Select Member", members["name"])
            amount = st.number_input("Amount", min_value=10, step=10)
            today = date.today()
            submitted = st.form_submit_button("Record Savings")
            if submitted:
                member_id = members[members["name"] == member]["id"].values[0]
                new_saving = {"member_id": member_id, "date": today, "amount": amount}
                savings = pd.concat([savings, pd.DataFrame([new_saving])], ignore_index=True)
                savings.to_csv(SAVINGS_FILE, index=False)
                st.success(f"✅ {member} saved {amount}")

    st.subheader("Savings Records")
    st.dataframe(savings)

# --- LOANS ---
elif choice == "📑 Loans":
    st.header("📑 Manage Loans")
    if members.empty:
        st.warning("No members found. Please add members first.")
    else:
        with st.form("loan_form"):
            member = st.selectbox("Select Member", members["name"])
            amount = st.number_input("Loan Amount", min_value=100, step=100)
            today = date.today()
            submitted = st.form_submit_button("Grant Loan")
            if submitted:
                member_id = members[members["name"] == member]["id"].values[0]
                loan_id = len(loans) + 1
                new_loan = {"loan_id": loan_id, "member_id": member_id, "date": today, "amount": amount, "status": "active"}
                loans = pd.concat([loans, pd.DataFrame([new_loan])], ignore_index=True)
                loans.to_csv(LOANS_FILE, index=False)
                st.success(f"✅ Loan of {amount} granted to {member}")

        st.subheader("Loan Records")
        st.dataframe(loans)

        st.subheader("Record Repayment")
        active_loans = loans[loans["status"] == "active"]
        if not active_loans.empty:
            with st.form("repayment_form"):
                loan_id = st.selectbox("Select Loan ID", active_loans["loan_id"])
                repay_amount = st.number_input("Repayment Amount", min_value=10, step=10)
                submitted = st.form_submit_button("Record Repayment")
                if submitted:
                    new_repayment = {"loan_id": loan_id, "date": date.today(), "amount": repay_amount}
                    repayments = pd.concat([repayments, pd.DataFrame([new_repayment])], ignore_index=True)
                    repayments.to_csv(REPAYMENTS_FILE, index=False)

                    total_repaid = repayments[repayments["loan_id"] == loan_id]["amount"].sum()
                    loan_amount = loans[loans["loan_id"] == loan_id]["amount"].values[0]
                    if total_repaid >= loan_amount:
                        loans.loc[loans["loan_id"] == loan_id, "status"] = "closed"
                        loans.to_csv(LOANS_FILE, index=False)
                        st.success(f"✅ Loan {loan_id} fully repaid and closed!")
                    else:
                        st.success(f"✅ Repayment of {repay_amount} recorded for Loan {loan_id}")

        else:
            st.info("No active loans to repay.")

# --- REPORTS ---
elif choice == "📊 Reports":
    st.header("📊 Group Reports")

    # Summary Metrics
    total_savings = savings["amount"].sum() if not savings.empty else 0
    total_loans = loans["amount"].sum() if not loans.empty else 0
    total_repayments = repayments["amount"].sum() if not repayments.empty else 0
    outstanding_loans = total_loans - total_repayments

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💵 Total Savings", f"₹{total_savings}")
    col2.metric("📑 Total Loans", f"₹{total_loans}")
    col3.metric("↩️ Total Repaid", f"₹{total_repayments}")
    col4.metric("❗ Outstanding Loans", f"₹{outstanding_loans}")

    # --- Member-wise Savings ---
    st.subheader("📈 Member-wise Savings")
    if not savings.empty:
        member_savings = savings.groupby("member_id")["amount"].sum().reset_index()
        report = members.merge(member_savings, left_on="id", right_on="member_id", how="left").fillna(0)
        st.dataframe(report[["name", "amount"]].rename(columns={"amount": "total_savings"}))
        st.bar_chart(report.set_index("name")["amount"])
    else:
        st.info("No savings recorded yet.")

    # --- Savings Growth Over Time ---
    st.subheader("📊 Savings Growth Over Time")
    if not savings.empty:
        savings_over_time = savings.groupby("date")["amount"].sum().reset_index()
        savings_over_time["date"] = pd.to_datetime(savings_over_time["date"])
        savings_over_time = savings_over_time.set_index("date").sort_index()
        st.line_chart(savings_over_time["amount"])
    else:
        st.info("No savings data to show trend.")

    # --- Loans vs Repayments ---
    st.subheader("📉 Loans vs Repayments")
    if not loans.empty:
        loan_sum = loans["amount"].sum()
        repay_sum = repayments["amount"].sum() if not repayments.empty else 0
        compare_df = pd.DataFrame({
            "Type": ["Loans Given", "Repayments"],
            "Amount": [loan_sum, repay_sum]
        })
        st.bar_chart(compare_df.set_index("Type"))
    else:
        st.info("No loans data to compare.")

    # --- Export Section ---
    st.subheader("📂 Export Reports")
    if st.button("Export to Excel"):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            members.to_excel(writer, sheet_name="Members", index=False)
            savings.to_excel(writer, sheet_name="Savings", index=False)
            loans.to_excel(writer, sheet_name="Loans", index=False)
            repayments.to_excel(writer, sheet_name="Repayments", index=False)

            # Summary Sheet
            summary_df = pd.DataFrame({
                "Metric": ["Total Savings", "Total Loans", "Total Repaid", "Outstanding Loans"],
                "Value": [total_savings, total_loans, total_repayments, outstanding_loans]
            })
            summary_df.to_excel(writer, sheet_name="Summary", index=False)

        st.download_button(
            label="📥 Download Excel Report",
            data=output.getvalue(),
            file_name=f"savings_group_report_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
