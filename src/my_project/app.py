import streamlit as st
import pandas as pd
import io
import os
from crew import AugmentedBICrew # A classe AugmentedBICrew é importada aqui

# --- Page Configuration ---
st.set_page_config(page_icon="🤖", page_title="CleanMyData.ai", layout="wide")

# --- Title and Description ---
st.title("🧹📊CleanMyData.ai - Data Quality Agent")
st.text("CleanMyData.ai is a conversational agent that collaborates with you via chat to clean and deliver a flawless dataframe.")
st.markdown("**How it works**")
st.write(
    "Our AI agent guides you through a simple, four-step process to get your data ready for analysis:\n\n"
    "1. **Upload**: Upload your dataset (CSV or XLSX) to begin.\n"
    "2. **Analyze**: Click 'Start Quality Analysis' to let our AI team investigate your data for inconsistencies.\n"
    "3. **Interact**: The AI will present its findings in the chat. You can then interact and approve corrections.\n"
    "4. **Download**: Once you're satisfied, type 'download' to receive your clean, ready-to-use file."
)
st.divider()

# --- User Input: File Uploader ---
if 'file_uploaded' not in st.session_state:
    st.subheader("Upload your dataset to start the quality analysis.")
    uploaded_file = st.file_uploader("Choose a CSV or XLSX file", type=["csv", "xlsx"])

    if uploaded_file is not None:
        try:
            file_extension = uploaded_file.name.split('.')[-1]
            if file_extension == "csv":
                df = pd.read_csv(uploaded_file)
            elif file_extension == "xlsx":
                df = pd.read_excel(uploaded_file, engine='openpyxl')
            else:
                st.error("Unsupported file type. Please upload a CSV or XLSX file.")
                st.stop()
            
            st.session_state['df'] = df
            st.session_state['file_uploaded'] = True
            st.success("File uploaded successfully! Click 'Start Quality Analysis' to proceed.")
            st.write("### Initial Data Preview")
            st.dataframe(st.session_state['df'].head())
            st.divider()

        except Exception as e:
            st.error(f"An error occurred while processing the file: {e}")
            st.stop()

# --- Main App Logic ---
if 'file_uploaded' in st.session_state:
    # Button to start the proactive analysis
    if 'analysis_done' not in st.session_state:
        if st.button("Start Quality Analysis", key="start_analysis_button"):
            with st.spinner("⏳ Analyzing your data... Our AI team is on it!"):
                inputs = {'dataframe': st.session_state['df']}
                crew = AugmentedBICrew(inputs).proactive_crew()
                proactive_result = crew.kickoff()
                st.session_state['report_proactive'] = proactive_result
                st.session_state['analysis_done'] = True
                
                # The first message is the proactive report from the AI
                st.session_state['messages'] = [{"role": "assistant", "content": st.session_state['report_proactive']}]
            st.experimental_rerun()
    
    # Conversational Interface
    if 'analysis_done' in st.session_state:
        st.write("### Interactive Chat with the AI Agent")
        
        # Define avatars for the chat messages
        USER_AVATAR = "👤"
        BOT_AVATAR = "🤖"
        
        for message in st.session_state.get('messages', []):
            avatar = USER_AVATAR if message["role"] == "user" else BOT_AVATAR
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])

        if prompt := st.chat_input("Enter your command (e.g., 'yes', 'download', 'show me what you did')"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar=USER_AVATAR):
                st.markdown(prompt)

            with st.spinner("⏳ Processing your request..."):
                # --- The logic to continue the conversation based on user input ---
                # Check for approval to start the cleaning process
                if 'cleaning_done' not in st.session_state and ("yes" in prompt.lower() or "sim" in prompt.lower()):
                    inputs = {'dataframe': st.session_state['df']}
                    crew = AugmentedBICrew(inputs).post_approval_crew()
                    final_report = crew.kickoff()
                    st.session_state['final_report'] = final_report
                    st.session_state['df_cleaned'] = AugmentedBICrew(inputs).get_final_dataframe()
                    st.session_state['cleaning_done'] = True
                    response = "Great! I've applied all the necessary corrections. What would you like to do next? You can ask me to 'download' the file or 'show me what you did'."
                
                # Check for other commands
                elif 'cleaning_done' in st.session_state and ("download" in prompt.lower() or "finalizar" in prompt.lower()):
                    response = "Ok! Here are the download options."
                    with st.chat_message("assistant", avatar=BOT_AVATAR):
                        st.markdown(response)
                        st.subheader("Final Data Export")
                        st.dataframe(st.session_state['df_cleaned'])

                        # Download Buttons
                        csv_file = st.session_state['df_cleaned'].to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="Download as CSV",
                            data=csv_file,
                            file_name='clean_data.csv',
                            mime='text/csv',
                        )

                        xlsx_file = io.BytesIO()
                        st.session_state['df_cleaned'].to_excel(xlsx_file, index=False, engine='openpyxl')
                        xlsx_file.seek(0)
                        st.download_button(
                            label="Download as XLSX",
                            data=xlsx_file,
                            file_name='clean_data.xlsx',
                            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                        )
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.stop()
                
                else:
                    response = "I'm not yet configured to handle free-form chat. Please use simple commands like 'yes' or 'download'."
                
                # Display assistant response and add to chat history (if not already handled)
                if response:
                    with st.chat_message("assistant", avatar=BOT_AVATAR):
                        st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                
                st.experimental_rerun()
