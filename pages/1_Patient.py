import streamlit as st
import pandas as pd
from database.db import connect_db
import datetime
import re

st.set_page_config(
    page_title="Patient Management",
    page_icon=":hospital:",
    layout="wide",
    initial_sidebar_state="auto"
)

def validate_patient_data(name, dob, age, gender, contact, date_of_admission, address):
    errors = []
    
    # Validate name
    if not name or not name.strip():
        errors.append("Name cannot be empty.")
    
    # Validate age
    if not isinstance(age, int) or age <= 0:
        errors.append("Age should be a positive number.")
    
    # Validate contact number (basic check for length and digits only)
    if not re.match(r'^\d{10}$', str(contact)):
        errors.append("Contact number should be exactly 10 digits.")
    
    # Validate gender
    if gender not in ["Male", "Female", "Other"]:
        errors.append("Gender should be 'Male', 'Female', or 'Other'.")
    
    # Validate dates (DOB and date_of_admission)
    if dob >= datetime.date.today():
        errors.append("Date of Birth should be a past date.")
    if date_of_admission < dob:
        errors.append("Date of Admission cannot be earlier than Date of Birth.")
    
    # Validate address
    if not address or not address.strip():
        errors.append("Address cannot be empty.")
    
    # Return validation status
    if errors:
        return False, errors
    return True, None


def create_patient():
    st.header("Add New Patient", divider="orange")

    col1, col2 = st.columns(2, gap="small")
    with col1:
        st.subheader("Personal Details", divider="red")
        name = st.text_input("Full Name", placeholder="Full name of patient")
        dob = st.date_input("Date of Birth", min_value=datetime.date(1900, 1, 1), max_value=datetime.date.today(), format="DD/MM/YYYY")
        age = st.number_input("Age", min_value=1, value=None,  placeholder="Age", step=1,)
        gender = st.radio("Gender", ["Male", "Female", "Other"], index=None, horizontal=True)
        contact = st.number_input("Contact", placeholder="Contact Number", value=None, step=1, format="%d")
        date_of_admission = st.date_input("Date of Admission", datetime.date.today(), min_value=datetime.date(1900, 1, 1), format="DD/MM/YYYY")
    address = st.text_area("Address", placeholder="Your Address")
    
    with col2:
        st.subheader("Medical Details", divider="red")
        medical_history = st.text_area("Medical History", placeholder="Any Medical History", height=122)
        allergies = st.text_input("Allergies", placeholder="Any Allergies")
        chronic = st.text_input("Chronic Diseases", placeholder="Any Chronic Diseases (e.g., diabetes, hypertension, etc.)")
        surgery = st.text_input("Previous Surgeries", placeholder="Any previous surgery")
        medications = st.text_input("Current Medications", placeholder="Any Current Medications")

    if st.button("Add Patient"):
        is_valid, validation_errors = validate_patient_data(name, dob, age, gender, contact, date_of_admission, address)
        if not is_valid:
            st.error(f"Validation Errors: {', '.join(validation_errors)}")
            return
        
        conn = connect_db()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """INSERT INTO patients 
                   (name, dob, age, gender, contact, date_of_admission, address, medical_history, allergies, chronic, surgery, medications) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
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
    
    st.subheader("Filter Patients by Date of Admission", divider="red")
    col1, col2 = st.columns(2, gap="small")
    with col1:
        start_date = st.date_input("From Date", min_value=datetime.date(1900, 1, 1), value=datetime.date.today(), format="DD/MM/YYYY")
    with col2:
        end_date = st.date_input("To Date", min_value=datetime.date(1900, 1, 1), value=datetime.date.today(), format="DD/MM/YYYY")

    if start_date > end_date:
        st.error("Start Date should be earlier than End Date.")
        return

    conn = connect_db()
    query = "SELECT * FROM patients WHERE date_of_admission BETWEEN ? AND ?"
    df = pd.read_sql_query(query, conn, params=(start_date, end_date))
    conn.close()

    if df.empty:
        st.error("No patients found in the selected date range.")
        return

    st.dataframe(df, use_container_width=True, hide_index=True)


def update_patient():
    st.header("Update Patient", divider="orange")

    st.subheader("Filter Patients by Date of Admission", divider="red")
    col1, col2 = st.columns(2, gap="small", )
    with col1:
        start_date = st.date_input("From Date", value=datetime.date.today(), format="DD/MM/YYYY")
    with col2:
        end_date = st.date_input("To Date", value=datetime.date.today(), format="DD/MM/YYYY")

    if start_date > end_date:
        st.error("Start Date should be earlier than End Date.")
        return
    
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name FROM patients WHERE date_of_admission BETWEEN ? AND ?",
        (start_date, end_date)
    )
    patients = cursor.fetchall()
    conn.close()

    if not patients:
        st.error("No patients found in the selected date range.")
        return

    patient_list = [f"{patient[1]} (ID: {patient[0]})" for patient in patients]
    patient_ids = [patient[0] for patient in patients]

    selected_patient = st.selectbox("Select Patient to Update", options=patient_list, placeholder="Select a patient to update")
    patient_id = patient_ids[patient_list.index(selected_patient)]

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
    patient_data = cursor.fetchone()
    conn.close()

    if not patient_data:
        st.error("Patient data not found.")
        return

    id, name, dob, age, gender, contact, date_of_admission, address, medical_history, allergies, chronic, surgery, medications = patient_data
    dob = pd.to_datetime(dob).date()
    date_of_admission = pd.to_datetime(date_of_admission).date()

    col1, col2 = st.columns(2, gap="small")
    with col1:
        st.subheader("Personal Details", divider="red")
        updated_name = st.text_input("Full Name", value=name)
        updated_dob = st.date_input("Date of Birth", value=dob, min_value=datetime.date(1900, 1, 1), format="DD/MM/YYYY")
        updated_age = st.number_input("Age", min_value=1, value=age)
        updated_gender = st.radio("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(gender), horizontal=True)
        updated_contact = st.number_input("Contact", value=int(contact))
        updated_date_of_admission = st.date_input("Date of Admission", value=date_of_admission, min_value=datetime.date(1900, 1, 1), format="DD/MM/YYYY")
    updated_address = st.text_area("Address", value=address)

    with col2:
        st.subheader("Medical Details", divider="red")
        updated_medical_history = st.text_area("Medical History", value=medical_history, height=122)
        updated_allergies = st.text_input("Allergies", value=allergies)
        updated_chronic = st.text_input("Chronic Diseases", value=chronic)
        updated_surgery = st.text_input("Previous Surgeries", value=surgery)
        update_medications = st.text_input("Current Medications", value=medications)

    if st.button("Update Patient"):
        is_valid, validation_errors = validate_patient_data(updated_name, updated_dob, updated_age, updated_gender, updated_contact, updated_date_of_admission, updated_address)
        if not is_valid:
            st.error(f"Validation Errors: {', '.join(validation_errors)}")
            return

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE patients 
               SET name = ?, dob = ?, age = ?, gender = ?, contact = ?, date_of_admission = ?, address = ?, 
                   medical_history = ?, allergies = ?, chronic = ?, surgery = ?, medications = ? 
               WHERE id = ?""",
            (updated_name, updated_dob, updated_age, updated_gender, updated_contact, updated_date_of_admission, 
             updated_address, updated_medical_history, updated_allergies, updated_chronic, updated_surgery, 
             update_medications, patient_id)
        )
        conn.commit()
        conn.close()
        st.success("Patient updated successfully!")


def delete_patient():
    col1, col2 = st.columns(2)
    st.subheader("Delete Patient", divider="orange")
    
    st.header("Filter Patients by Date of Admission", divider="red")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("From Date", min_value=datetime.date(1900, 1, 1), value=datetime.date.today(), format="DD/MM/YYYY")
    with col2:
        end_date = st.date_input("To Date", min_value=datetime.date(1900, 1, 1), value=datetime.date.today(), format="DD/MM/YYYY")

    if start_date > end_date:
        st.error("Start Date should be earlier than End Date.")
        return
    
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, date_of_admission FROM patients WHERE date_of_admission BETWEEN ? AND ?",
        (start_date, end_date)
    )
    patients = cursor.fetchall()
    conn.close()
    
    if not patients:
        st.error("No patients found in the selected date range.")
        return

    with col1:
        patients_df = pd.DataFrame(patients, columns=["ID", "Name", "Date of Admission"])
        st.dataframe(patients_df, use_container_width=True, hide_index=True)

        patient_list = [f"{row['Name']} (ID: {row['ID']})" for _, row in patients_df.iterrows()]
        patient_ids = patients_df["ID"].tolist()

    with col2:
        selected_patient = st.selectbox("Select Patient to Delete", options=patient_list, placeholder="Select a patient to delete")
        
    if st.button("Delete Patient", use_container_width=True):
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



hide_streamlit_style = """
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    #header {visibility: hidden;}
    git
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)