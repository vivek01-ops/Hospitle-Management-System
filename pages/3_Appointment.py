import streamlit as st
import pandas as pd
from database.db import connect_db
from datetime import datetime

st.set_page_config(
    page_title="Appointment Management",
    page_icon=":hospital:",
    layout="wide",
    initial_sidebar_state="auto"
)

def is_valid_patient_name(name):
    return bool(name.strip())

def is_valid_reason(reason):
    return bool(reason.strip())

def create_appointment():
    st.subheader("Create Appointment", divider="orange")

    patient_name = st.text_input("Patient Name", placeholder="Full Name of Patient")
    date = st.date_input("Date of Appointment", datetime.now())
    time = st.time_input("Time of Appointment")
    reason = st.text_area("Reason for Appointment", placeholder="Write detailed reason for appointment here", height=122)
    
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM doctors")
    doctors = cursor.fetchall()
    conn.close()

    if not doctors:
        st.error("No doctors available. Please add a doctor to create an appointment.")
        return

    doctor_options = [f"{doctor[1]} (ID: {doctor[0]})" for doctor in doctors]
    selected_doctor = st.selectbox("Select Doctor", doctor_options, index=None, placeholder="Select a doctor")

    if st.button("Add Appointment"):
        if not selected_doctor:
            st.error("Please select a doctor.")
            return
        
        if time is None:
            st.error("Please select a valid time for the appointment.")
            return
        
        if not is_valid_reason(reason):
            st.error("Please enter a valid reason for the appointment.")
            return
        
        if not is_valid_patient_name(patient_name):
            st.error("Please enter a patient name.")
            return

        date_time = datetime.combine(date, time)

        conn = connect_db()
        cursor = conn.cursor()
        doctor_name = selected_doctor.split(" (ID:")[0].strip()

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
                       (patient_name, doctor_name, date_time, reason))
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

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM appointments")
    appointments = cursor.fetchall()
    conn.close()

    if not appointments:
        st.warning("No appointments available to update.")
        return

    appointment_options = [f"{appointment[1]} (ID: {appointment[0]})" for appointment in appointments]
    selected_option = st.selectbox("Select Appointment", options=appointment_options, placeholder="Select an appointment to update")

    if selected_option:
        appointment_id = int(selected_option.split("(ID: ")[1].strip(")"))

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, doctor_name, date_time, reason FROM appointments WHERE id = ?", (appointment_id,))
        appointment = cursor.fetchone()
        conn.close()

        if appointment:
            existing_doctor_name = appointment[1]
            existing_date_time_str = appointment[2]
            existing_reason = appointment[3]

            # Convert the existing_date_time from string to a datetime object
            try:
                existing_date_time = datetime.strptime(existing_date_time_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                st.error("Date format is incorrect. Please check the date format in the database.")
                return

            existing_date = existing_date_time.date()
            existing_time = existing_date_time.time()

            date = st.date_input("Date of Appointment", existing_date)
            time = st.time_input("Time of Appointment", existing_time)
            reason = st.text_area("Reason for Appointment", value=existing_reason, placeholder="Write detailed reason for appointment here", height=122)

            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM doctors")
            doctors = cursor.fetchall()
            conn.close()

            doctor_id = next((doctor[0] for doctor in doctors if doctor[1] == existing_doctor_name), None)
            if doctor_id is None:
                st.error("The selected doctor is not available. Please choose a different doctor.")
                return

            doctor_options = [f"{doctor[1]} (ID: {doctor[0]})" for doctor in doctors]
            selected_doctor = st.selectbox(
                "Select Doctor",
                doctor_options,
                index=doctor_options.index(f"{existing_doctor_name} (ID: {doctor_id})")
            )

            if st.button("Update Appointment"):
                if not selected_doctor:
                    st.error("Please select a doctor.")
                    return

                if time is None:
                    st.error("Please select a valid time for the appointment.")
                    return

                if not is_valid_reason(reason):
                    st.error("Please enter a valid reason for the appointment.")
                    return

                if not is_valid_patient_name(patients_name):
                    st.error("Please enter a valid patient name.")
                    return

                doctor_name = selected_doctor.split(" (ID:")[0].strip()
                date_time = datetime.combine(date, time)

                # Check if the doctor is available at the specified date and time, excluding the current appointment
                conn = connect_db()
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM appointments 
                    WHERE doctor_name = ? AND date_time = ? AND id != ?
                """, (doctor_name, date_time, appointment_id))
                appointment_count = cursor.fetchone()[0]

                if appointment_count > 0:
                    st.error("Doctor is not available at the selected time. Please choose another time.")
                    conn.close()
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
            st.error("No appointment found with the selected details.")

def delete_appointment():
    st.subheader("Delete Appointment", divider="orange")

    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name FROM appointments")
    appointments = cursor.fetchall()
    conn.close()

    if not appointments:
        st.warning("No appointments available to delete.")
        return

    appointment_options = [f"{appointment[1]} (ID: {appointment[0]})" for appointment in appointments]
    selected_option = st.selectbox("Select Appointment", options=appointment_options, placeholder="Select an appointment to delete", index=None)

    if st.button("Delete Appointment"):
        if not selected_option:
            st.error("Please select an appointment to delete.")
            return

        appointment_id = int(selected_option.split("(ID: ")[1].strip(")"))

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
        conn.commit()
        conn.close()
        
        st.success(f"Appointment '{selected_option}' deleted successfully!")

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
