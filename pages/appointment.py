import streamlit as st
import pandas as pd
from database.db import connect_db
from datetime import datetime

st.set_page_config(
    page_title="Appointment Management",
    page_icon=":hospital:",
    layout="wide",
    initial_sidebar_state="expanded"
)
def create_appointment():
    st.subheader("Create Appointment", divider="orange")

    # Input fields for patient name and reason
    patient_name = st.text_input("Patient Name", placeholder="Full Name of Patient")    
    date = st.date_input("Date of Appointment", datetime.now())
    time = st.time_input("Time of Appointment")
    reason = st.text_area("Reason for Appointment", placeholder="Write detailed reason for appointment here", height=122)
    
    # Fetching the list of doctors from the database
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM doctors")
    doctors = cursor.fetchall()
    conn.close()

    # Check if doctors list is empty
    if not doctors:
        st.error("No doctors available. Please add a doctor to create an appointment.")
        return

    # Select doctor from dropdown
    doctor_options = [f"{doctor[1]} (ID: {doctor[0]})" for doctor in doctors]
    selected_doctor = st.selectbox("Select Doctor", doctor_options, index=None, placeholder="Select a doctor")

    if st.button("Add Appointment"):
        if not selected_doctor:
            st.error("Please select a doctor.")
            return

        if time is None:
            st.error("Please select a valid time for the appointment.")
            return
        
        if not reason:
            st.error("Please enter a reason for the appointment.")
            return
        
        if not patient_name:
            st.error("Please enter a patient name.")
            return

        # Combine date and time into a single datetime object
        date_time = datetime.combine(date, time)

        conn = connect_db()
        cursor = conn.cursor()

        # Extract the doctor ID from the selected option
        try:
            doctor_name = selected_doctor.split(" (ID:")[0].strip(")")   
        except IndexError:
            st.error("Invalid doctor selection.")
            return

        # Combine date and time into a single datetime object
        date_time = datetime.combine(date, time)

        # Check if the doctor is available at the specified date and time
        cursor.execute("""
            SELECT COUNT(*) FROM appointments 
            WHERE doctor_name = ? AND date_time = ?
        """, (doctor_name, date_time))
        appointment_count = cursor.fetchone()[0]

        if appointment_count > 0:
            st.error("Doctor is not available at the selected time. Please choose another time.")
            conn.close()
            return
        
        # Insert appointment into the database
        cursor.execute("INSERT INTO appointments (name, doctor_name, date_time, reason) VALUES (?, ?, ?, ?)",
                       (patient_name, doctor_name, date_time, reason))  # Assuming name can be None initially
        conn.commit()
        conn.close()
        st.success("Appointment added successfully!")



def view_appointments():
    st.subheader("View Appointments", divider="orange")
    conn = connect_db()
    df = pd.read_sql_query("SELECT * FROM appointments", conn)
    conn.close()
    st.dataframe(df, use_container_width=True, hide_index=True)

def update_appointment():
    st.subheader("Update Appointment", divider="orange")
    
    # Input field to enter the Patient Name
    patient_name = st.text_input("Patient Name", placeholder="Full Name of Patient")
    
    # Fetch existing appointment details from the database based on the provided Patient Name
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, doctor_name, date_time, reason FROM appointments WHERE name = ?", (patient_name,))
    appointment = cursor.fetchone()
    conn.close()
    
    if appointment:
        # Extract existing details
        appointment_id = appointment[0]
        existing_doctor_name = appointment[1]
        existing_date_time = appointment[2]
        existing_reason = appointment[3]
        
        # Split existing datetime into date and time
        existing_date = existing_date_time.date()
        existing_time = existing_date_time.time()
        
        # Input fields with existing data
        date = st.date_input("Date of Appointment", existing_date)
        time = st.time_input("Time of Appointment", existing_time)
        reason = st.text_area("Reason for Appointment", value=existing_reason, placeholder="Write detailed reason for appointment here", height=122)

        # Fetch the list of doctors from the database
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM doctors")
        doctors = cursor.fetchall()
        conn.close()
        
        # Select doctor from dropdown with pre-selected value
        doctor_options = [f"{doctor[1]} (ID: {doctor[0]})" for doctor in doctors]
        selected_doctor = st.selectbox("Select Doctor", doctor_options, index=doctor_options.index(f"{[d[1] for d in doctors if d[0] == existing_doctor_name][0]} (ID: {existing_doctor_name})"))

        if st.button("Update Appointment"):
            conn = connect_db()
            cursor = conn.cursor()
            
            # Extract the doctor ID from the selected option
            doctor_name = selected_doctor.split(" (ID:")[1].strip(")")
            
            # Combine date and time into a single datetime object
            date_time = datetime.combine(date, time)
            
            # Check if the doctor is available at the specified date and time, excluding the current appointment
            cursor.execute("""
                SELECT COUNT(*) FROM appointments 
                WHERE doctor_name = ? AND date_time = ? AND id != ?
            """, (doctor_name, date_time, appointment_id))
            appointment_count = cursor.fetchone()[0]
            
            if appointment_count > 0:
                st.error("Doctor is not available at the selected time. Please choose another time.")
                return
            
            # Update the appointment in the database
            cursor.execute("""
                UPDATE appointments 
                SET doctor_name = ?, date_time = ?, reason = ?
                WHERE id = ?
            """, (doctor_name, date_time, reason, appointment_id))
            
            conn.commit()
            conn.close()
            st.success("Appointment updated successfully!")
    else:
        st.error("No appointment found with the given patient name.")


def delete_appointment():
    st.subheader("Delete Appointment", divider="orange")

    # Connect to the database and fetch appointment IDs
    conn = connect_db()
    cursor = conn.cursor()
    
    # Fetch all appointments for selection
    cursor.execute("SELECT id FROM appointments")
    appointments = cursor.fetchall()
    conn.close()

    # Check if there are any appointments
    if not appointments:
        st.warning("No appointments available to delete.")
        return

    # Create a list of appointment IDs for selection
    patient_names = [appointment[2] for appointment in appointments]
    appointment_id = st.selectbox("Select Appointment ID", options=patient_names, placeholder="Select an appointment to delete", index=None)

    if st.button("Delete Appointment"):
        # Check if an appointment is selected
        if not appointment_id:
            st.error("Please select an appointment to delete.")
            return

        # Connect to the database again to delete the selected appointment
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
        conn.commit()
        conn.close()
        
        st.success(f"Appointment ID {appointment_id} deleted successfully!")


def appointment_management():
    st.title("Appointment Management")
    menu = ["Create Appointment", "View Appointments", "Update Appointment", "Delete Appointment"]
    choice = st.sidebar.selectbox("Select an option", menu)

    if choice == "Create Appointment":
        create_appointment()
    elif choice == "View Appointments":
        view_appointments()
    elif choice == "Update Appointment":
        update_appointment()
    elif choice == "Delete Appointment":
        delete_appointment()

if __name__ == "__main__":
    appointment_management()
