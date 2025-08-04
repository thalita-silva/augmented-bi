## ADAPTAR PARA O PROJETO

import streamlit as st
from main import run_contest_agent

st.title("🧠 QualiAI - Data Quality Support Agent")

st.write(
    "QualiAI is an autonomous agent that helps ensure data quality in your DWH "
    "by analyzing KPIs and performing automated quality checks."
)

st.header("How it works")
st.write(
    "QualiAI examines KPIs and runs quality tests on your DWH to identify anomalies, missing data, "
    "and inconsistencies—so you can act quickly and confidently."
)

user_input = st.text_area("Ask QualiAI a data quality question or describe a KPI you'd like to analyze:")

if st.button("Run QualiAI Agent"):
    if not user_input.strip():
        st.warning("⚠️ Please enter your question before running.")
    else:
        st.write("⏳ Processing your request... Please wait.")

        result = run_contest_agent(user_input)

        # Display the AI response
        st.subheader("✅ QualiAI Response:")
        st.write(result)