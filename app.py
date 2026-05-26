import os
from dotenv import load_dotenv
import streamlit as st
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.title("AI Investment Memo Generator")

company_name = st.text_input("Enter company name")

if st.button("Generate Memo"):

    prompt = f"""
    Create a short professional investment memo for {company_name}.

    Include:
    - Company Overview
    - Growth Opportunities
    - Risks
    - Investment Outlook

    Use professional financial language.
    """

    response = client.responses.create(
        model="gpt-4.1",
        input=prompt
    )

    memo = response.output_text

    st.subheader("Generated Memo")
    st.write(memo)