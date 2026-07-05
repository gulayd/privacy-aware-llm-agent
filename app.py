import streamlit as st
from privacy_agent import run_privacy_agent

st.set_page_config(
    page_title="Privacy-Aware LLM Agent",
    page_icon="🔐",
    layout="centered"
)

st.title("🔐 Privacy-Aware LLM Agent")

st.write(
    "This AI Agent analyzes user-provided text, detects sensitive personal information, "
    "assesses the privacy risk level, and generates a safer anonymized version."
)

user_text = st.text_area(
    "Enter the text you want to analyze:",
    height=180,
    placeholder="Example: Hi, my name is John. I live in New York. My monthly salary is $4,000 and I have allergic rhinitis."
)

if st.button("Analyze"):
    if not user_text.strip():
        st.warning("Please enter some text to analyze.")
    else:
        with st.spinner("Analyzing your text..."):
            findings, risk_level, result = run_privacy_agent(user_text)

        st.subheader("Rule-Based Detection")

        if findings:
            for item in findings:
                st.write(f"- {item}")
        else:
            st.write("No sensitive information detected.")

        st.subheader("Initial Risk Level")
        st.write(risk_level)

        st.subheader("LLM Analysis")
        st.write(result)