# pages/doctor.py
import streamlit as st
import pandas as pd
from database.db import connect_db

st.set_page_config(
    page_title="Doctor Management",
    page_icon=":hospital:",
    layout="wide",
    initial_sidebar_state="expanded"
)

def create_doctor():
    st.subheader("Add a new doctor", divider="orange")
    name = st.text_input("Name", placeholder="Name of Doctor")
    specialization = st.text_input("Specialization", placeholder="Specialization of Doctor")
    contact = st.number_input("Contact", placeholder="Contact number of Doctor", step=1)
    
    # Get availability days
    availability_days = st.multiselect("Available on days", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], default=None)
    
    col1, col2 = st.columns(2)
    with col1:
        availability_from = st.time_input("Availabile from", value=None)
    with col2:
        availability_to = st.time_input("Availabile to", value=None)

    # Check if any availability is selected
    if st.button("Add Doctor"):
        if not availability_days:
            st.error("Please select at least one day for availability.")
            return
        if availability_from is None or availability_to is None:
            st.error("Please specify the availability time range.")
            return

        # Combine days and time into a single string
        availability = f"{', '.join(availability_days)} from {availability_from.strftime('%H:%M')} to {availability_to.strftime('%H:%M')}"
        
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO doctors (name, specialization, contact, availability) VALUES (?, ?, ?, ?)",
                       (name, specialization, contact, availability))
        conn.commit()
        conn.close()
        st.success("Doctor added successfully!")


def view_doctors():
    st.subheader("View Doctors", divider="orange")
    conn = connect_db()
    df = pd.read_sql_query("SELECT * FROM doctors", conn)
    conn.close()
    st.dataframe(df, use_container_width=True, hide_index=True)

def update_doctor():
    st.subheader("Update Doctor", divider="orange")
    conn = connect_db()
    cursor = conn.cursor()
    
    # Fetch all doctors for selection
    cursor.execute("SELECT id, name FROM doctors")
    doctors = cursor.fetchall()
    conn.close()

    # Check if there are any doctors
    if not doctors:
        st.warning("No doctors available to update.")
        return
    
    # Select doctor to update
    doctor_id = st.selectbox("Select a doctor", [doctor[0] for doctor in doctors], format_func=lambda x: [doc[1] for doc in doctors if doc[0] == x][0])

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM doctors WHERE id = ?", (doctor_id,))
    doctor = cursor.fetchone()
    conn.close()

    if doctor:
        name = st.text_input("Name", doctor[1])
        specialization = st.text_input("Specialization", doctor[2])
        contact = st.text_input("Contact", doctor[3])
        availability = doctor[4].split(" from ")
        
        availability_days = availability[0].split(", ")
        time_range = availability[1].split(" to ")
        availability_from = time_range[0]
        availability_to = time_range[1]

        # Multiselect for availability days
        availability_days_selected = st.multiselect("Available on days", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], default=availability_days)

        col1, col2 = st.columns(2)
        with col1:
            availability_time_from = st.time_input("Availability from", value=pd.to_datetime(availability_from, format='%H:%M').time())
        with col2:
            availability_time_to = st.time_input("Availability to", value=pd.to_datetime(availability_to, format='%H:%M').time())

        if st.button("Update Doctor"):
            if not availability_days_selected:
                st.error("Please select at least one day for availability.")
                return
            if availability_time_from is None or availability_time_to is None:
                st.error("Please specify the availability time range.")
                return

            # Combine days and time into a single string
            availability = f"{', '.join(availability_days_selected)} from {availability_time_from.strftime('%H:%M')} to {availability_time_to.strftime('%H:%M')}"
            
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("UPDATE doctors SET name=?, specialization=?, contact=?, availability=? WHERE id=?",
                           (name, specialization, contact, availability, doctor_id))
            conn.commit()
            conn.close()
            st.success("Doctor updated successfully!")
    else:
        st.error("Doctor not found.")

def delete_doctor():
    st.subheader("Delete Doctor", divider="orange")
    conn = connect_db()
    cursor = conn.cursor()
    
    # Fetch all doctors for selection
    cursor.execute("SELECT id, name FROM doctors")
    doctors = cursor.fetchall()
    conn.close()

    if not doctors:
        st.error("No doctors available to delete.")
        return
    
    # Select doctor to delete
    doctor_id = st.selectbox("Select a doctor to delete", [f"{doctor[1]} (ID: {doctor[0]})" for doctor in doctors], index=None, placeholder="Select a doctor to delete")

    if st.button("Delete Doctor"):
        # Extract the ID from the selected option
        selected_id = doctor_id.split(" (ID: ")[1][:-1]  # Extract ID from the selected text
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM doctors WHERE id = ?", (selected_id,))
        conn.commit()
        conn.close()
        
        st.success("Doctor deleted successfully!")


def doctor_management():
    st.title("Doctor Management")
    menu = ["Create Doctor", "View Doctors", "Update Doctor", "Delete Doctor"]
    choice = st.sidebar.selectbox("Select an option", menu)

    if choice == "Create Doctor":
        create_doctor()
    elif choice == "View Doctors":
        view_doctors()
    elif choice == "Update Doctor":
        update_doctor()
    elif choice == "Delete Doctor":
        delete_doctor()

if __name__ == "__main__":
    doctor_management()
