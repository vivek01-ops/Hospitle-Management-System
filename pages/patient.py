import streamlit as st
import pandas as pd
from database.db import connect_db
import datetime

st.set_page_config(
    page_title="Patient Management",
    page_icon=":hospital:",
    layout="wide",
    initial_sidebar_state="expanded"
)

def create_patient():
    st.subheader("Add new patient", divider="orange")

    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.header("Personal Details", divider="red")
        name = st.text_input("Full Name", placeholder="Full name of patient")
        dob = st.date_input("Date of Birth", min_value=datetime.date(1900, 1, 1))
        age = st.number_input("Age", min_value=0)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=None)
        contact = st.number_input("Contact", placeholder="Contact Number", value=None, step=1)
        date_of_admission = st.date_input("Date of Admission", datetime.date.today(), min_value=datetime.date(1900, 1, 1))
    address = st.text_area("Address", placeholder="Your Address")
    
    with col2:
        st.header("Medical Details", divider="red")
        medical_history = st.text_area("Medical History", placeholder="Any Medical History", height=122)
        allergies = st.text_input("Allergies", placeholder="Any Allergies")
        chronic = st.text_input("Chronic Diseases", placeholder="Any Chronic Diseases (e.g., diabetes, hypertension, etc.)")
        surgery = st.text_input("Previous Surgeries", placeholder="Any previous surgery")
        medications = st.text_input("Current Medications", placeholder="Any Current Medications")

    if st.button("Add Patient"):
        conn = connect_db()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO patients (name, dob, age, gender, contact, date_of_admission, address, medical_history, allergies, chronic, surgery, medications) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (name, dob, age, gender, contact, date_of_admission, address, medical_history, allergies, chronic, surgery, medications)
            )
            conn.commit()
            st.success("Patient added successfully!")
        except Exception as e:
            st.error(f"An error occurred: {e}")
        finally:
            conn.close()



def view_patients():
    st.subheader("View Patients", divider="orange")
    conn = connect_db()
    df = pd.read_sql_query("SELECT * FROM patients", conn)
    conn.close()
    st.dataframe(df, use_container_width=True, hide_index=True)

def update_patient():
    st.subheader("Update Patient", divider="orange")
    conn = connect_db()
    cursor = conn.cursor()
    
    # Fetch all patients from the database
    cursor.execute("SELECT id, name, dob, age, gender, contact, date_of_admission, address, medical_history, allergies, chronic, surgery, medications    FROM patients")
    patients = cursor.fetchall()
    conn.close()
    
    if not patients:
        st.error("No patients found in the database.")
        return
    
    # Create a list of patient names and corresponding IDs
    patient_list = [f"{patient[1]} (ID: {patient[0]})" for patient in patients]
    patient_ids = [patient[0] for patient in patients]

    # Select box to choose a patient to update
    selected_patient = st.selectbox("Select Patient to Update", options=patient_list, placeholder="Select a patient to update")
    
    # Get the selected patient ID from the selected option
    patient_id = patient_ids[patient_list.index(selected_patient)]
    
    # Fetch the existing details of the selected patient
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, dob, age, gender, contact, date_of_admission, address, medical_history, allergies, chronic, surgery, medications FROM patients WHERE id = ?", (patient_id,))
    patient_data = cursor.fetchone()
    conn.close()
    
    # If patient data is not found, display an error
    if not patient_data:
        st.error("Patient data not found.")
        return
    
    # Unpack the patient data (ensure the number of variables matches the columns fetched)
    (id, name, dob, age, gender, contact, date_of_admission, address, medical_history, allergies, chronic, surgery, medications) = patient_data
    if isinstance(dob, str):
        dob = pd.to_datetime(dob).date()

    if isinstance(date_of_admission, str):
        date_of_admission = pd.to_datetime(date_of_admission).date()

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.header("Personal Details", divider="red")
        updated_name = st.text_input("Full Name", value=name)
        updated_dob = st.date_input("Date of Birth", value=dob)
        updated_age = st.number_input("Age", min_value=0, value=age)
        updated_gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(gender))
        updated_contact = st.number_input("Contact", value=int(contact))
        updated_date_of_admission = st.date_input("Date of Admission", value=date_of_admission)
    updated_address = st.text_area("Address", value=address)

    with col2:
        st.header("Medical Details", divider="red")
        updated_medical_history = st.text_area("Medical History", value=medical_history, height=122)
        updated_allergies = st.text_input("Allergies", value=allergies)
        updated_chronic = st.text_input("Chronic Diseases", value=chronic)
        updated_surgery = st.text_input("Previous Surgeries", value=surgery)
        update_medications = st.text_input("Current Medications", value=medications)

    # Update the patient data in the database when the "Update Patient" button is clicked
    if st.button("Update Patient"):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE patients SET name = ?, dob = ?, age = ?, gender = ?, contact = ?, date_of_admission = ?, address = ?, medical_history = ?, allergies = ?, chronic = ?, surgery = ?, medications = ? WHERE id = ?",
            (updated_name, updated_dob, updated_age, updated_gender, updated_contact, updated_date_of_admission, updated_address, updated_medical_history, updated_allergies, updated_chronic, updated_surgery, update_medications, patient_id)
        )
        conn.commit()
        conn.close()
        st.success("Patient updated successfully!")




def delete_patient():
    st.subheader("Delete Patient", divider="orange")
    conn = connect_db()
    cursor = conn.cursor()
    
    # Fetch all patients from the database
    cursor.execute("SELECT id, name FROM patients")
    patients = cursor.fetchall()
    conn.close()
    
    if not patients:
        st.error("No patients found in the database.")
        return
    
    # Create a list of patient names and corresponding IDs
    patient_list = [f"{patient[1]} (ID: {patient[0]})" for patient in patients]
    patient_ids = [patient[0] for patient in patients]

    # Select box to choose a patient
    selected_patient = st.selectbox("Select Patient to Delete", options=patient_list, placeholder="Select a patient to delete", index=None)

    if st.button("Delete Patient"):
        # Get the selected patient ID from the selected option
        patient_id = patient_ids[patient_list.index(selected_patient)]
        
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
        conn.commit()
        conn.close()
        st.success("Patient deleted successfully!")

def patient_management():
    st.title("Patient Management")
    menu = ["Create Patient", "View Patients", "Update Patient", "Delete Patient"]
    choice = st.sidebar.selectbox("Select an option", menu)

    if choice == "Create Patient":
        create_patient()
    elif choice == "View Patients":
        view_patients()
    elif choice == "Update Patient":
        update_patient()
    elif choice == "Delete Patient":
        delete_patient()

if __name__ == "__main__":
    patient_management()
