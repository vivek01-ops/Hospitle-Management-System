import streamlit as st

# Set the page configuration
st.set_page_config(page_title="Hospital Management System", page_icon=":hospital:", layout="centered", initial_sidebar_state="collapsed")

# Add title with custom color
st.markdown("<h1 style='text-align: center; color: #96C3D9;'>Welcome to the <br> <span style='color: #DAA8D6;'>Hospital Management System</span></h1>", unsafe_allow_html=True)

st.subheader("Features:", divider="orange")
st.markdown(
        """
        - **Appointment Management:** Schedule, view, update, or cancel appointments.
        - **Patient Records:** Manage patient information and medical history.
        - **Doctor Management:** Maintain a database of doctors and their specialties.
        - **Billing:** Generate invoices for hospital services.
        - **Report Generation:** Create reports for various purposes.
        - **User Management:** Add, edit, or delete users.
        """
    )


st.divider()
st.subheader("Navigate to:", divider="violet")
col1, col2 = st.columns(2)

with col1:
    if st.button("🛌 Add new Patient", use_container_width=True):
        st.switch_page("pages/1_Patient.py") 
    
    if st.button("🧾 Create Bill", use_container_width=True):
        st.switch_page("pages/4_Billing.py") 
    
with col2:
    if st.button("👨🏻‍⚕️ Add new Doctor", use_container_width=True):
        st.switch_page("pages/2_Doctor.py")

    if st.button("🗓️ Crate new Appointment", use_container_width=True):
        st.switch_page("pages/3_Appointment.py")
    
    
    
# st.sidebar.divider()
    
    
# Footer
# st.markdown("<p style='text-align: center; color: #777;'>© 2024 Hospital Management System | All Rights Reserved</p>", unsafe_allow_html=True)
