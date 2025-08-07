import streamlit as st
import pandas as pd
from main import run_agents
import io
import traceback

# --- Page Configuration ---
st.set_page_config(layout="wide")

# --- Title and Description ---
st.title("🧹✨ CleanMyData.ai - Data Quality Support Agent")
st.write(
    "CleanMyData.ai is a conversational agent that curates your data. "
    "It performs quality checks and collaborates with you via chat to clean and deliver a flawless dataframe."
)

st.header("How it works")
st.write(
    "CleanMyData.ai is a team of intelligent agents that automatically analyzes, cleans, and organizes data, "
    "transforming unstructured datasets into robust data models. "
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
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        if file_extension == "csv":
            df = pd.read_csv(uploaded_file)
        elif file_extension == "xlsx":
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        else:
            st.error("Unsupported file type. Please upload a CSV or XLSX file.")
            st.stop()
        
        # Store the DataFrame in session state
        st.session_state['df'] = df
        st.session_state['uploaded_filename'] = uploaded_file.name

        st.write("### Initial Data Preview")
        st.dataframe(st.session_state['df'].head())
        
        # Show basic info about the dataset
        st.write(f"**Dataset Shape:** {df.shape[0]} rows, {df.shape[1]} columns")
        st.write(f"**File:** {uploaded_file.name}")
        
        st.divider()

        # --- Run Full Analysis and Display Report ---
        if 'analysis_done' not in st.session_state or st.session_state.get('current_file') != uploaded_file.name:
            if st.button("🚀 Run Analysis", key="run_analysis_button", type="primary"):
                try:
                    with st.spinner("⏳ Running full analysis and cleaning... Our AI team is on it!"):
                        # Pass the DataFrame to the agents
                        result = run_agents(st.session_state['df'])
                        
                        # Handle the result based on its type
                        if isinstance(result, tuple) and len(result) == 2:
                            final_report, df_cleaned = result
                        else:
                            # If result is just a string/report, use original DataFrame
                            final_report = str(result)
                            df_cleaned = st.session_state['df'].copy()  # Use a copy as fallback
                        
                        st.session_state['final_report'] = final_report
                        st.session_state['df_cleaned'] = df_cleaned
                        st.session_state['analysis_done'] = True
                        st.session_state['current_file'] = uploaded_file.name
                        
                    st.success("✅ Analysis completed successfully!")
                    st.rerun()  # Use st.rerun() instead of deprecated st.experimental_rerun()
                    
                except Exception as analysis_error:
                    st.error(f"An error occurred during analysis: {str(analysis_error)}")
                    st.error("Please check your configuration files and try again.")
                    # Show detailed error for debugging
                    with st.expander("Debug Information"):
                        st.code(traceback.format_exc())
                    
    except Exception as e:
        st.error(f"An error occurred while processing the file: {str(e)}")
        # Show detailed error for debugging
        with st.expander("Debug Information"):
            st.code(traceback.format_exc())
        st.stop()

# --- Display Results and Download Buttons ---
if st.session_state.get('analysis_done', False):
    st.subheader("✅ Final Report from CleanMyData.ai:")
    
    # Display the report in a nice format
    if isinstance(st.session_state['final_report'], str):
        st.markdown(st.session_state['final_report'])
    else:
        st.write(st.session_state['final_report'])

    st.success("🎉 Your data is ready! See the cleaned dataframe below.")
    
    # Show comparison if we have both original and cleaned data
    if 'df' in st.session_state and 'df_cleaned' in st.session_state:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Original Data")
            st.dataframe(st.session_state['df'].head())
            st.write(f"Shape: {st.session_state['df'].shape}")
            
        with col2:
            st.subheader("✨ Cleaned Data")
            st.dataframe(st.session_state['df_cleaned'].head())
            st.write(f"Shape: {st.session_state['df_cleaned'].shape}")
    
    st.subheader("📁 Download Cleaned Data")
    
    # Download Buttons
    col1, col2 = st.columns(2)
    
    with col1:
        # CSV Download Button
        csv_file = st.session_state['df_cleaned'].to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📄 Download as CSV",
            data=csv_file,
            file_name='clean_data.csv',
            mime='text/csv',
        )
    
    with col2:
        # XLSX Download Button
        xlsx_file = io.BytesIO()
        st.session_state['df_cleaned'].to_excel(xlsx_file, index=False, engine='openpyxl')
        xlsx_file.seek(0)
        st.download_button(
            label="📊 Download as XLSX",
            data=xlsx_file,
            file_name='clean_data.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )

# Reset button
if st.session_state.get('analysis_done', False):
    if st.button("🔄 Start New Analysis", type="secondary"):
        # Clear session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()