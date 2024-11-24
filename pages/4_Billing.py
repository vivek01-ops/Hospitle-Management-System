# pages/billing.py
import streamlit as st
import pandas as pd
from database.db import connect_db
import datetime
from datetime import date

import io

st.set_page_config(
    page_title="Billing Management",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="auto"
)

def create_billing():
    st.subheader("Create Bill", divider="orange")

    conn = connect_db()
    cursor = conn.cursor()

    # Fetch all patients
    cursor.execute("SELECT id, name FROM patients")
    patients = cursor.fetchall()
    conn.close()

    if not patients:
        st.error("No patients available to create a bill.")
        return

    patient_id = st.selectbox("Select Patient", [f"{patient[1]} (ID: {patient[0]})" for patient in patients])

    selected_patient_id = int(patient_id.split("(ID: ")[1].strip(")"))
    patient_name = patient_id.split(" (ID:")[0].strip()

    amount = st.number_input("Amount (in ₹)", min_value=0.0)
    status = st.selectbox("Status", ["Paid", "Pending"], placeholder="Select a status", index=0)
    discharge_date = st.date_input("Date of Discharge", datetime.date.today(), min_value=datetime.date(1900, 1, 1))

    if st.button("Create Bill"):
        # Save the bill to the database
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO billing (patient_id, amount, status, date) VALUES (?, ?, ?, ?)",
                       (selected_patient_id, amount, status, discharge_date))
        conn.commit()
        bill_id = cursor.lastrowid  # Get the ID of the newly created bill
        conn.close()

        # Display the bill summary as a "popup"
        st.success("Bill created successfully!")
        with st.expander("View Bill Details", expanded=True):
            st.markdown(f"""
            ### Bill Summary
            - **Bill ID:** {bill_id}
            - **Patient Name:** {patient_name}
            - **Patient ID:** {selected_patient_id}
            - **Amount:** ₹{amount:.2f}
            - **Status:** {status}
            - **Date of Discharge:** {discharge_date.strftime('%d-%m-%Y')}
            - **Date of Billing:** {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}
            """)

            # Prepare data for download
            bill_data = {
                "Bill ID": [bill_id],
                "Patient Name": [patient_name],
                "Patient ID": [selected_patient_id],
                "Amount": [f"₹{amount:.2f}"],
                "Status": [status],
                "Date of Discharge": [discharge_date.strftime('%d-%m-%Y')],
                "Date of Billing": [datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')]
            }
            bill_df = pd.DataFrame(bill_data)

            st.download_button(
                label="Download Bill",
                data=bill_df.to_csv(index=False).encode("utf-8"),
                file_name=f"bill_{bill_id}.csv",
                mime="text/csv",
            )



def view_billing():
    st.subheader("View Billing", divider="orange")

    # Connect to the database and fetch billing data with patient names
    conn = connect_db()
    query = """
        SELECT 
            billing.id AS bill_id,
            patients.name AS patient_name,
            billing.patient_id,
            billing.amount,
            billing.status,
            billing.date 
        FROM 
            billing
        INNER JOIN 
            patients ON billing.patient_id = patients.id
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Check if there is any data
    if df.empty:
        st.error("No billing data available.")
        return

    # Convert 'date' column to datetime for filtering
    df['date'] = pd.to_datetime(df['date'])

    # Filtering Options
    st.markdown("### Filters")

    # Date Range Filter (From Date and To Date in two columns)
    min_date = df['date'].min().date()
    max_date = df['date'].max().date()

    col1, col2 = st.columns(2)
    with col1:
        from_date = st.date_input("From Date", value=min_date, min_value=min_date, max_value=max_date, format="DD/MM/YYYY")
    with col2:
        to_date = st.date_input("To Date", value=max_date, min_value=min_date, max_value=max_date, format="DD/MM/YYYY")

    # Validate date range
    if from_date > to_date:
        st.error("From Date cannot be later than To Date.")
        return

    # Amount Slider Filter
    min_amount = df['amount'].min()
    max_amount = df['amount'].max()

    if min_amount == max_amount:
        # If min and max are the same, use a fixed range
        st.info(f"All bills have the same amount: ₹{min_amount:.2f}")
        amount_range = (min_amount, max_amount)  # Default range
    else:
        # Use a slider for selecting amount range
        amount_range = st.slider(
            "Filter by Amount (₹)",
            min_value=float(min_amount),
            max_value=float(max_amount),
            value=(float(min_amount), float(max_amount)),
            step=1.0
        )

    # Apply Filters
    filtered_df = df[
        (df['date'].between(pd.Timestamp(from_date), pd.Timestamp(to_date))) &
        (df['amount'].between(amount_range[0], amount_range[1]))
    ]

    # Display Filtered Data
    st.markdown("### Filtered Billing Data")
    if filtered_df.empty:
        st.info("No bills match the selected filters.")
    else:
        # Reorganize columns for better readability
        filtered_df = filtered_df.rename(columns={
            "bill_id": "Bill ID",
            "patient_name": "Patient Name",
            "patient_id": "Patient ID",
            "amount": "Amount",
            "status": "Status",
            "date": "Date"
        })
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)




def delete_billing():
    st.subheader("Delete Bill", divider="orange")

    # Connect to the database
    conn = connect_db()
    cursor = conn.cursor()

    # Fetch all bills with patient names
    query = """
        SELECT billing.id, patients.name, billing.patient_id, billing.amount, billing.status, billing.date 
        FROM billing 
        JOIN patients ON billing.patient_id = patients.id
    """
    cursor.execute(query)
    bills = cursor.fetchall()
    conn.close()

    # Check if there are any bills
    if not bills:
        st.error("No bills available to delete.")
        return

    # Format the options for multi-select
    bill_options = [
        f"ID: {bill[0]} - Patient Name: {bill[1]}, Patient ID: {bill[2]}, Amount: ₹{bill[3]:.2f}, Status: {bill[4]}, Date: {bill[5]}"
        for bill in bills
    ]

    # Multi-select for bills
    selected_bills = st.multiselect("Select Bills to Delete", bill_options)

    if st.button("Delete Selected Bills", disabled=not selected_bills, use_container_width=True):
        # Check if any bills are selected
        if not selected_bills:
            st.error("Please select at least one bill to delete.")
            return

        # Extract the bill IDs from the selected options
        selected_bill_ids = [int(option.split(" - ")[0].split(": ")[1]) for option in selected_bills]

        # Delete the selected bills from the database
        conn = connect_db()
        cursor = conn.cursor()
        cursor.executemany("DELETE FROM billing WHERE id = ?", [(bill_id,) for bill_id in selected_bill_ids])
        conn.commit()
        conn.close()
        st.rerun()
        st.success(f"Successfully deleted {len(selected_bills)} bill(s)!")


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
