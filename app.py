import streamlit as st
import pandas as pd
from user_codes.chatbot import chatbot_ui

# Function to load data from a file
def load_data(file):
    return pd.read_csv(file)

def main():
    st.set_page_config(page_title="NL2Python", page_icon=":bar_chart:", layout="wide")
    st.markdown("""
        <h1 style="text-align: center; color: #4CAF50;">NL2Python</h1>
        <p style="text-align: center; font-size: 20px; color: #777;">Natural Language to Python converter.</p>
    """, unsafe_allow_html=True)

    github_repo_url="https://github.com/balamurugan-shanmuganathan/NL2Python"

    st.markdown(f"""
        <style>
            .github-icon {{
                position: absolute;
                top: 10px;
                right: 20px;
            }}
        </style>

        <a href="{github_repo_url}" class="github-icon" target="_blank">
            <img src="https://cdn-icons-png.flaticon.com/512/25/25231.png"  alt="GitHub Logo" width="30"/>
            View on GitHub
        </a><br><br>
     """, unsafe_allow_html=True)
    # Sidebar components
    with st.sidebar:
        uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
        submit = st.button("Upload")
        
        ui_list = ['Chatbot', 'Dashboard']
        ui_type = st.selectbox("Select UI", ui_list)

    # Initialize session state variables
    if "submitted" not in st.session_state:
        st.session_state["submitted"] = False
    if "data" not in st.session_state:
        st.session_state["data"] = None

    # Handle file upload
    if submit:
        if uploaded_file is None:
            st.info("Please upload a file to proceed.", icon="ℹ️")
            return  # Stops execution further

        st.session_state.data = load_data(uploaded_file)
        st.session_state.submitted = True
        st.success("File uploaded successfully!")

    # Main UI after file uploaded
    if st.session_state.submitted:
        with st.expander("Data Preview"):
            st.dataframe(st.session_state.data)

        if ui_type == 'Chatbot':
            chatbot_ui(st.session_state.data)

        if ui_type == 'Dashboard':
            st.write("Working on it.")

if __name__ == "__main__":
    main()
