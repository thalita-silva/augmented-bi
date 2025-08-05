import streamlit as st
import pandas as pd
from main import run_agents
import io

# --- Page Configuration ---
st.set_page_config(layout="wide")

# --- Title and Description ---
st.title("🧹✨ CleanMyData.ai - Data Quality Support Agent")
st.write(
    "CleanMyData.ai is a conversational agent that curates your data."
    "It performs quality checks and collaborates with you via chat to clean and deliver a flawless dataframe."
)

st.header("How it works")
st.write(
    "CleanMyData.ai is a team of intelligent agents that automatically analyzes, cleans, and organizes data,"
    "transforming unstructured datasets into robust data models."
    "You interact with the AI, approve corrections, and get data ready for analysis in a collaborative and agile way."
)
st.divider()

# --- User Input: File Uploader ---
st.header("Upload your dataset to start the quality analysis.")
uploaded_file = st.file_uploader("Choose a CSV or XLSX file", type=["csv", "xlsx"])

# This entire block will run only if a file is uploaded
if uploaded_file is not None:
    try:
        # Read the file according to the extension
        file_extension = uploaded_file.name.split('.')[-1]
        
        if file_extension == "csv":
            df = pd.read_csv(uploaded_file)
        elif file_extension == "xlsx":
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        else:
            st.error("Unsupported file type. Please upload a CSV or XLSX file.")
            st.stop()
        
        # Store the DataFrame in session state only once after upload
        if 'df' not in st.session_state:
            st.session_state['df'] = df

        st.write("### Initial Data Preview")
        st.dataframe(st.session_state['df'].head())
        st.divider()

        # --- Run Full Analysis and Display Report ---
        # This button is only displayed and the code inside it is only executed once,
        # when the user clicks it.
        if 'analysis_done' not in st.session_state:
            if st.button("Run Analysis", key="run_analysis_button"):
                with st.spinner("⏳ Running full analysis and cleaning... Our AI team is on it!"):
                    # The run_agents function should return the final report and the cleaned dataframe
                    final_report, df_cleaned = run_agents(st.session_state['df'])
                    st.session_state['final_report'] = final_report
                    st.session_state['df_cleaned'] = df_cleaned
                    st.session_state['analysis_done'] = True
                st.experimental_rerun()
    except Exception as e:
        # This except block should be outside the `if uploaded_file is not None` block to be effective
        st.error(f"An error occurred while processing the file: {e}")
        st.stop()

# --- Display Results and Download Buttons ---
# This block only runs AFTER the analysis is done and the 'analysis_done' state is set
if 'analysis_done' in st.session_state:
    st.subheader("✅ Final Report from CleanMyData.ai:")
    st.write(st.session_state['final_report'])

    st.success("🎉 Your data is ready! See the cleaned dataframe below.")
    st.subheader("Final Data Export")
    st.dataframe(st.session_state['df_cleaned'])

    # Download Buttons
    # CSV Download Button
    csv_file = st.session_state['df_cleaned'].to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download as CSV",
        data=csv_file,
        file_name='clean_data.csv',
        mime='text/csv',
    )

    # XLSX Download Button
    xlsx_file = io.BytesIO()
    st.session_state['df_cleaned'].to_excel(xlsx_file, index=False, engine='openpyxl')
    xlsx_file.seek(0)
    st.download_button(
        label="Download as XLSX",
        data=xlsx_file,
        file_name='clean_data.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
