import streamlit as st

# Set the page configuration
st.set_page_config(page_title="Hospital Management System",
                   page_icon=":hospital:",
                   layout="wide",  # Switch to wide for more content space
                   initial_sidebar_state="collapsed")

# Add a header with a background color and gradient title
st.markdown(
    """
    <div style="background-color: #dde4f0; padding: 20px; border-radius: 10px; text-align: center;">
        <h1 style='color: #2E86C1;'>🏥 Welcome to the <br> 
        <span style="color: #8E44AD;">Hospital Management System</span></h1>
    </div>
    """,
    unsafe_allow_html=True,
)

# Features section with icons
# st.markdown("<hr style='border: 1px solid #D1D8E0;'>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; font-weight: bold;'>🌟 Features</h1>", unsafe_allow_html=True)
st.markdown(
    """
    <div style="font-size: 16px; color: gray; line-height: 1.8; text-align: center;">
        🗓️ <b>Appointment Management:</b> Schedule, view, update, or cancel appointments.<br>
        🩺 <b>Patient Records:</b> Manage patient information and medical history.<br>
        👨‍⚕️ <b>Doctor Management:</b> Maintain a database of doctors and their specialties.<br>
        💳 <b>Billing:</b> Generate invoices for hospital services.<br>
        📊 <b>Report Generation:</b> Create reports for various purposes.<br>
        🛡️ <b>User Management:</b> Add, edit, or delete users.<br>
    </div>
    """,
    unsafe_allow_html=True,
)

# Navigation buttons with gradient styling
# st.markdown("<hr style='border: 1px solid #D1D8E0;'>", unsafe_allow_html=True)

st.subheader(":compass: Navigate to:")
col1, col2 = st.columns(2)

button_style = """
    <style>
        .stButton>button {
            background: linear-gradient(to right, #8E44AD, #3498DB, #8E44AD);
            color: Black;
            border: none;
            padding: 10px;
            border-radius: 10px;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.5);
        }
        .stButton>button:hover {
            # background: linear-gradient(to right, #3498DB, #8E44AD);
            transform: scale(1.02);
            transition: transform 0.2s ease-in-out;
            # color: red;
            font-weight: bold;
        }
    </style>
"""
st.markdown(button_style, unsafe_allow_html=True)

with col1:
    if st.button("🛌 Patient Management", use_container_width=True):
        st.switch_page("pages/1_Patient.py")

    if st.button("🧾 Bill Management", use_container_width=True):
        st.switch_page("pages/4_Billing.py")

with col2:
    if st.button("👨🏻‍⚕️ Doctor Management", use_container_width=True):
        st.switch_page("pages/2_Doctor.py")

    if st.button("🗓️ Appointment Management", use_container_width=True):
        st.switch_page("pages/3_Appointment.py")

# Add a footer with copyright and contact details
# st.markdown("<hr style='border: 1px solid #D1D8E0;'>", unsafe_allow_html=True)
# st.divider()
# st.markdown(
#     """
#     <div style="text-align: center; font-size: 14px; color: #95A5A6;">
#         © 2024 Hospital Management System. All rights reserved.<br>
#         Need help? <a href="mailto:support@hospital.com" style="color: #3498DB;">Contact Support</a>
#     </div>
#     """,
#     unsafe_allow_html=True,
# )
