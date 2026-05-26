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

    memo = f"""
# Investment Memo: {company_name}

## Company Overview
{company_name} operates in a growing market with strong brand recognition and significant scalability potential.

## Growth Opportunities
- Expansion into international markets
- Product diversification
- Increased operational efficiency
- AI and technology integration

## Risks
- Competitive pressure
- Regulatory uncertainty
- Macroeconomic volatility
- Execution risk

## Investment Outlook
{company_name} appears to have attractive long-term growth potential, though investors should carefully monitor profitability and market conditions.
"""
    st.subheader("Generated Memo")
    st.write(memo)