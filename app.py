import os
from dotenv import load_dotenv
import streamlit as st
from openai import OpenAI
from pypdf import PdfReader
import yfinance as yf
from yahooquery import search
import pandas as pd

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="AI Investment Memo Generator", layout="wide")

st.markdown("""
<style>

.stApp {
    background: linear-gradient(to bottom right, #0b1220, #111827);
    color: #f8fafc;
}

/* MAIN TEXT */
h1, h2, h3, h4 {
    color: #f8fafc !important;
}

.stMarkdown,
.stMarkdown p,
.stMarkdown li,
.stMarkdown strong,
.stMarkdown span,
.stMarkdown p,
.stMarkdown li,
.stMarkdown span,
.stMarkdown code {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif !important;
    line-height: 1.6 !important;
    font-variant-numeric: tabular-nums !important;
}

/* captions */
.stCaption {
    color: #9ca3af !important;
}

/* input text */
.stTextInput input {
    color: black !important;
    background-color: white !important;
    font-size: 16px;
}

/* select box */
.stSelectbox div {
    color: black !important;
}

/* info box */
.stAlert {
    background-color: #1f2937 !important;
    color: #f8fafc !important;
}

/* button */
.stButton>button {
    background-color: #38bdf8;
    color: white;
    border-radius: 10px;
    height: 3em;
    width: 100%;
    font-size: 18px;
    border: none;
}

.stButton>button:hover {
    background-color: #0ea5e9;
}

code {
    background-color: transparent !important;
    color: #e5e7eb !important;
}

mark {
    background: transparent !important;
    color: inherit !important;
}

strong {
    color: #f8fafc !important;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="
    text-align:center;
    padding: 20px;
    border-radius: 12px;
    background: linear-gradient(90deg, #0f172a, #1e293b);
    margin-bottom: 20px;
">
    <h1 style="color:#38bdf8; margin-bottom:5px;">📈 AI Investment Memo Generator</h1>
    <p style="color:#cbd5e1; font-size:16px;">
        Generate institutional-grade investment memos from company data or PDFs
    </p>
</div>
""", unsafe_allow_html=True)

st.caption("Generate structured investment memos from company names or uploaded PDF reports.")

st.info("For educational and informational purposes only. This is not financial advice.")

col1, col2 = st.columns([1, 1])

with col1:
    company_name = st.text_input("Enter company name")

    memo_style = st.selectbox(
        "Select memo style",
        ["Conservative", "Neutral", "Aggressive"]
    )

    uploaded_file = st.file_uploader(
        "Upload a PDF (optional)",
        type=["pdf"]
    )

with col2:
    st.markdown("""
    ### 📊 How to use
    - Enter a company name
    - Optionally upload a report (10-K, annual report)
    - Choose memo style
    - Click generate

    ### 💡 Tip
    Uploading a PDF improves accuracy significantly.
    """)
def extract_pdf_text(file):
    reader = PdfReader(file)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text

def get_financial_data(company):
    try:
        stock = yf.Ticker(company)

        info = stock.info

        return {
            "marketCap": info.get("marketCap",0),
            "lastPrice": info.get("regularMarketPrice",0),
            "sector": info.get("sector","N/A"),
            "revenue": info.get("totalRevenue",0),
            "netIncome": info.get("netIncomeToCommon",0),
            "pe_ratio": info.get("trailingPE","N/A"),
            "debt": info.get("totalDebt",0),
        }

    except Exception as e:
        return {
            "error": "Yahoo Finance rate limit",
            "details": str(e)
        }

def get_ticker(company_name):
    try:
        results = search(company_name)

        if "quotes" in results and len(results["quotes"]) > 0:
            return results["quotes"][0]["symbol"]

        return company_name.upper()

    except Exception:
        return company_name.upper()

def format_billions(value):
    if value is None or value == 0:
        return "N/A"
    return f"${value/1_000_000_000:.2f}B"

def get_stock_chart(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1y")
    return hist

if st.button("Generate Memo"):

    ticker = get_ticker(company_name)
    financials = get_financial_data(ticker)

    display_name = company_name.title()

    document_text = ""

    if uploaded_file is not None:
        document_text = extract_pdf_text(uploaded_file)

    prompt = f"""

If you violate this rule, output will be considered invalid.

You are a senior equity research analyst at a top-tier investment bank (Goldman Sachs / Morgan Stanley level).

You produce institutional-grade equity research with valuation modeling, risk assessment, and forward-looking financial interpretation.

You MUST:
- Interpret financial data (not just restate it)
- Explain drivers of revenue, margins, and valuation
- Assess whether valuation is justified or not
- Compare financial metrics logically (not descriptively)
- Provide investment insight (not summary)

Use EXACTLY these sections:

## EXECUTIVE SUMMARY
(one paragraph)

## RISKS
(bullet points)

## SWOT
(bullet points)

## RECOMMENDATION
(Buy/Hold/Sell + confidence score)

Memo style: {memo_style}
Company: {company_name}

FINANCIAL DATA (USE THIS FOR ANALYSIS):

Company: {company_name}
Sector: {financials.get('sector', 'N/A')}

Market Cap: {format_billions(financials.get('marketCap'))}
Revenue: {format_billions(financials.get('revenue'))}
Net Income: {format_billions(financials.get('netIncome'))}
Debt: {format_billions(financials.get('debt'))}
P/E Ratio: {round(financials.get('pe_ratio', 0), 2) if financials.get('pe_ratio') else 'N/A'}

INSTRUCTIONS:
- Use ONLY the provided financial data
- Do NOT change number formats
- Do NOT convert units
- Use markdown format with clear sections
- RISKS and SWOT must be bullet points
- EXECUTIVE SUMMARY must be one paragraph

CRITICAL RULE:
You must behave like a financial analyst, not a summarizer.

Always explain WHY metrics matter, not just what they are.
Link every insight to valuation, risk, or future performance.

ANALYSIS FRAMEWORK (MANDATORY):

1. VALUATION (CORE DRIVER)
- Assess whether P/E ratio implies undervaluation, fair value, or overvaluation
- Compare profitability vs valuation
- Identify if market is pricing in growth or stagnation

2. UNIT ECONOMICS & PROFIT QUALITY
- Evaluate revenue vs net income efficiency
- Identify margin strength or weakness
- Comment on earnings durability

3. BALANCE SHEET STRENGTH
- Evaluate debt relative to revenue and earnings power
- Identify leverage risk (low / moderate / high)

4. GROWTH TRAJECTORY
- Classify company: Hypergrowth / Growth / Mature / Declining
- Explain drivers of future growth or slowdown

5. MARKET EXPECTATIONS GAP
- Identify difference between market pricing and fundamentals
- Explain if sentiment is too optimistic or pessimistic

6. INVESTMENT DECISION LOGIC
- Your recommendation MUST be derived from valuation + growth + risk
- Do NOT guess BUY/HOLD/SELL — justify it from analysis

PDF TEXT:
{document_text[:8000]}

Do NOT use HTML.
Do NOT add extra sections.
"""

    with st.spinner("Generating memo..."):

        response = client.responses.create(
            model="gpt-4.1",
            input=prompt
        )

        memo = response.output_text

    st.subheader("📄 Investment Memo")

    st.markdown(
    memo,
    help=None
    )

    st.subheader("📈 Stock Price (1Y)")

    chart_data = get_stock_chart(ticker)

    st.line_chart(chart_data["Close"])

    st.subheader("📊 Financial Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric("Company", display_name)
    col2.metric("Market Cap", format_billions(financials.get("marketCap")))
    col3.metric("Price", f"${financials.get('lastPrice', 0):,.2f}" if financials.get("lastPrice") else "N/A")

    col4, col5, col6 = st.columns(3)

    col4.metric("Revenue", format_billions(financials.get("revenue")))
    col5.metric("Net Income", format_billions(financials.get("netIncome")))
    col6.metric("Debt", format_billions(financials.get("debt")))

    st.caption(f"Sector: {financials.get('sector', 'N/A')}")

    st.download_button(
        "Download Memo",
        memo,
        file_name=f"{company_name}_memo.md"
    )