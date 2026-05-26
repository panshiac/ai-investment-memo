import os
from dotenv import load_dotenv
import streamlit as st
from openai import OpenAI
from pypdf import PdfReader

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.title("AI Investment Memo Generator")

company_name = st.text_input("Enter company name")

uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

def extract_pdf_text(file):
    reader = PdfReader(file)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text

if st.button("Generate Memo"):

    document_text = ""

    if uploaded_file is not None:
        document_text = extract_pdf_text(uploaded_file)

    prompt = f"""
    You are a professional investment analyst.

    Create a structured investment memo for {company_name}.

    If a PDF document is uploaded, use it as the primary source.

    If no PDF is uploaded, generate the memo using your general knowledge about the company.

    If information is uncertain, clearly state assumptions.

    Include:
    1. Executive Summary
    2. Company Overview
    3. Business Model
    4. Growth Opportunities
    5. Key Financial Insights
    6. Risks
    7. SWOT Analysis
    8. Investment Outlook
    9. Questions for Further Due Diligence

    Use professional financial language.

    PDF TEXT:
    {document_text[:8000]}
    """

    response = client.responses.create(
        model="gpt-4.1",
        input=prompt
    )

    memo = response.output_text

    st.subheader("Generated Memo")
    st.write(memo)