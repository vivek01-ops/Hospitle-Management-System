# pages/billing.py
import streamlit as st
import pandas as pd
from database.db import connect_db
import datetime
from datetime import date

st.set_page_config(
    page_title="Billing Management",
    page_icon=":hospital:",
    layout="wide",
    initial_sidebar_state="auto"
)

def create_billing():
    st.subheader("Create Bill", divider="orange")

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name FROM patients")
    patients = cursor.fetchall()
    conn.close()

    if not patients:
        st.error("No patients available to create a bill.")
        return

    patient_id = st.selectbox("Select Patient", [f"{patient[1]} (ID: {patient[0]})" for patient in patients])

    selected_patient_id = patient_id.split(" - ")[0]

    amount = st.number_input("Amount (in ₹)", min_value=0.0)
    status = st.selectbox("Status", ["Paid", "Pending"], placeholder="Select a status", index=None)
    date = st.date_input("Date of discharge", datetime.date.today(), min_value=datetime.date(1900, 1, 1))

    if st.button("Create Bill"):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO billing (patient_id, amount, status, date) VALUES (?, ?, ?, ?)",
                       (selected_patient_id, amount, status, date))
        conn.commit()
        conn.close()
        st.success("Bill created successfully!")


def view_billing():
    st.subheader("View Billing", divider="orange")
    conn = connect_db()
    df = pd.read_sql_query("SELECT * FROM billing", conn)
    conn.close()
    st.dataframe(df, use_container_width=True, hide_index=True)

def delete_billing():

    st.subheader("Delete Bill", divider="orange")
    
    conn = connect_db()
    cursor = conn.cursor()

    # Fetch all bills for selection
    cursor.execute("SELECT id, patient_id, amount, status, date FROM billing")
    bills = cursor.fetchall()
    conn.close()

    # Check if there are any bills
    if not bills:
        st.warning("No bills available to delete.")
        return

    # Select bill to delete
    bill_options = [f"ID: {bill[0]} - Patient ID: {bill[1]}, Amount: {bill[2]}, Status: {bill[3]}, Date: {bill[4]}" for bill in bills]
    selected_bill = st.selectbox("Select Bill to Delete", bill_options, placeholder="Select a bill to delete", index=None)

    if st.button("Delete Bill"):
        # Check if a bill is selected
        if not selected_bill:
            st.error("Please select a bill to delete.")
            return
        
        # Extract the bill ID from the selected option
        selected_bill_id = int(selected_bill.split(" - ")[0].split(": ")[1])  # Extract ID

        # Delete the bill from the database
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM billing WHERE id = ?", (selected_bill_id,))
        conn.commit()
        conn.close()
        st.success("Bill deleted successfully!")


def billing_management():
    st.title("Billing Management")
    menu = ["Create Billing", "View Billing", "Delete Billing"]
    choice = st.sidebar.selectbox("Select an option", menu)

    if choice == "Create Billing":
        create_billing()
    elif choice == "View Billing":
        view_billing()
    elif choice == "Delete Billing":
        delete_billing()

if __name__ == "__main__":
    billing_management()
