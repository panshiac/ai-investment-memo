import os
from dotenv import load_dotenv
import streamlit as st
from openai import OpenAI
from pypdf import PdfReader
import yfinance as yf
from yahooquery import search
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak
)
import matplotlib.pyplot as plt

from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(
    page_title="MemoGen",
    page_icon="logo.png",
    layout="wide"
)

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

/* Input labels */
div[data-testid="stTextInput"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stFileUploader"] label {
    color: #e2e8f0 !important;
    font-size: 20px !important;
    font-weight: 600 !important;
    letter-spacing: 0.4px;
}

div[data-baseweb="select"] + label,
div[data-testid="stSelectbox"] p {
    color: white !important;
    font-size: 20px !important;
    font-weight: 600 !important;
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

/* Generate Memo button */
.stButton>button {
    background-color: #38bdf8 !important;
    color: white !important;
    border-radius: 10px;
    height: 3em;
    width: 100%;
    font-size: 18px;
    border: none;
}

.stButton>button:hover {
    background-color: #0ea5e9 !important;
}

/* Download PDF button */
.stDownloadButton>button {
    background-color: #38bdf8 !important;
    color: white !important;
    border-radius: 10px;
    height: 3em;
    width: 100%;
    font-size: 18px;
    border: none;
}

.stDownloadButton>button:hover {
    background-color: #0ea5e9 !important;
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

/* Financial metrics */
div[data-testid="stMetricLabel"],
div[data-testid="stMetricLabel"] *,
div[data-testid="stMetricLabel"] p,
div[data-testid="stMetricLabel"] label,
div[data-testid="stMetricLabel"] span {
    color: #ffffff !important;
    opacity: 1 !important;
    font-size: 18px !important;
    font-weight: 500 !important;
}

div[data-testid="stMetricValue"],
div[data-testid="stMetricValue"] div {
    color: white !important;
    font-size: 34px !important;
    font-weight: 400 !important;
}

/* DCF table */
[data-testid="stTable"] table,
[data-testid="stTable"] th,
[data-testid="stTable"] td,
[data-testid="stTable"] div,
[data-testid="stTable"] p {
    color: white !important;
}

[data-testid="stTable"] th {
    background-color: #1e293b !important;
    font-weight: 500 !important;
}

[data-testid="stTable"] td,
[data-testid="stTable"] th {
    border: 1px solid #334155 !important;
}

/* Slider labels */
.stSlider label,
.stSlider p,
div[data-testid="stSlider"] label,
div[data-testid="stSlider"] p {
    color: white !important;
    font-size: 18px !important;
    font-weight: 600 !important;
    opacity: 1 !important;
}

</style>
""", unsafe_allow_html=True)

st.markdown(
    """
    <div style='text-align:center;'>
    """,
    unsafe_allow_html=True
)

_, col, _ = st.columns([2, 5, 2])

with col:
    st.image("logo.png", width=750)

st.markdown(
    """
    <style>
    div[data-testid="stImage"] {
        margin-bottom: -90px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.caption("Generate professional investment memos from company data, market metrics, and uploaded reports.")

st.info("For educational and informational purposes only. This is not financial advice.")

col1, col2 = st.columns([1, 1])

with col1:

    st.markdown(
        "<p style='color:white; font-size:20px; font-weight:600; margin-bottom:8px;'>Enter company name</p>",
        unsafe_allow_html=True
    )
    company_name = st.text_input(
        "",
        label_visibility="collapsed"
    )

    st.markdown(
        "<p style='color:white; font-size:20px; font-weight:600; margin-bottom:8px;'>Select memo style</p>",
        unsafe_allow_html=True
    )
    memo_style = st.selectbox(
        "",
        ["Conservative", "Neutral", "Aggressive"],
        label_visibility="collapsed"
    )

    st.markdown(
        "<p style='color:white; font-size:20px; font-weight:600; margin-bottom:8px;'>Upload a PDF (optional)</p>",
        unsafe_allow_html=True
    )
    uploaded_file = st.file_uploader(
        "",
        type=["pdf"],
        label_visibility="collapsed"
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

st.markdown("### 📐 DCF Assumptions")

dcf_col1, dcf_col2, dcf_col3, dcf_col4 = st.columns(4)

with dcf_col1:
    growth_assumption = st.slider("Revenue Growth", 0.0, 30.0, 8.0) / 100

with dcf_col2:
    fcf_margin_assumption = st.slider("FCF Margin", 0.0, 40.0, 10.0) / 100

with dcf_col3:
    wacc_assumption = st.slider("WACC", 5.0, 20.0, 9.0) / 100

with dcf_col4:
    terminal_growth_assumption = st.slider("Terminal Growth", 0.0, 5.0, 2.5) / 100

def extract_pdf_text(file):
    reader = PdfReader(file)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text

@st.cache_data(ttl=3600)
def get_financial_data(company):
    try:
        stock = yf.Ticker(company)

        info = stock.info
        fast_info = stock.fast_info
        income_stmt = stock.income_stmt
        balance_sheet = stock.balance_sheet
        cashflow = stock.cashflow

        def get_statement_value(statement, row_name):
            try:
                return statement.loc[row_name].iloc[0]
            except:
                return None

        revenue = info.get("totalRevenue") or get_statement_value(income_stmt, "Total Revenue")
        net_income = info.get("netIncomeToCommon") or get_statement_value(income_stmt, "Net Income")
        debt = info.get("totalDebt") or get_statement_value(balance_sheet, "Total Debt")
        cash = info.get("totalCash") or get_statement_value(balance_sheet, "Cash And Cash Equivalents")
        operating_cash_flow = get_statement_value(cashflow, "Operating Cash Flow")
        capex = get_statement_value(cashflow, "Capital Expenditure")

        if operating_cash_flow is not None and capex is not None:
            free_cash_flow = operating_cash_flow + capex
        else:
            free_cash_flow = info.get("freeCashflow")

        market_cap = info.get("marketCap")
        if market_cap is None:
            try:
                market_cap = fast_info.get("market_cap")
            except:
                market_cap = None

        last_price = info.get("currentPrice") or info.get("regularMarketPrice")
        if last_price is None:
            try:
                last_price = fast_info.get("last_price")
            except:
                last_price = None

        shares_outstanding = info.get("sharesOutstanding")

        if shares_outstanding is None and market_cap and last_price:
            shares_outstanding = market_cap / last_price
        
        return {
            "marketCap": market_cap,
            "lastPrice": last_price,
            "sector": info.get("sector", "N/A"),
            "revenue": revenue,
            "netIncome": net_income,
            "pe_ratio": info.get("trailingPE"),
            "debt": debt,
            "cash": cash,
            "operatingCashFlow": operating_cash_flow,
            "capitalExpenditure": capex,
            "freeCashFlow": free_cash_flow,
            "sharesOutstanding": shares_outstanding,
            "dataSource": "Yahoo Finance",
        }

    except Exception as e:
        st.error(f"Yahoo Finance Error: {e}")

        return {
            "marketCap": None,
            "lastPrice": None,
            "sector": "N/A",
            "revenue": None,
            "netIncome": None,
            "pe_ratio": None,
            "debt": None,
            "cash": None,
            "operatingCashFlow": None,
            "capitalExpenditure": None,
            "freeCashFlow": None,
            "sharesOutstanding": None,
            "dataSource": "Unavailable",
            "error": str(e)
        }

@st.cache_data(ttl=3600)
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

def safe_margin(net_income, revenue):
    if revenue and revenue != 0 and net_income:
        return f"{(net_income / revenue) * 100:.2f}%"
    return "N/A"

@st.cache_data(ttl=3600)
def get_stock_chart(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="10y")
    return hist

def calculate_dcf(financials, growth, fcf_margin, wacc, terminal_growth):
    revenue = financials.get("revenue")
    free_cash_flow = financials.get("freeCashFlow")
    debt = financials.get("debt") or 0
    cash = financials.get("cash") or 0
    shares_outstanding = financials.get("sharesOutstanding")
    current_price = financials.get("lastPrice")

    if not revenue or not shares_outstanding or not current_price:
        return None

    if free_cash_flow and revenue:
        starting_fcf_margin = free_cash_flow / revenue
    else:
        starting_fcf_margin = fcf_margin

    dcf_rows = []
    total_pv_fcf = 0

    for year in range(1, 6):
        yearly_growth = max(growth - ((year - 1) * 0.015), terminal_growth)

        projected_revenue = revenue * ((1 + yearly_growth) ** year)

        projected_margin = starting_fcf_margin + ((fcf_margin - starting_fcf_margin) * (year / 5))

        projected_fcf = projected_revenue * projected_margin

        pv_fcf = projected_fcf / ((1 + wacc) ** year)

        total_pv_fcf += pv_fcf

        dcf_rows.append({
            "Year": year,
            "Revenue Growth": f"{yearly_growth * 100:.1f}%",
            "Projected Revenue": projected_revenue,
            "FCF Margin": f"{projected_margin * 100:.1f}%",
            "Starting FCF Margin": f"{starting_fcf_margin * 100:.1f}%",
            "Projected FCF": projected_fcf,
            "PV of FCF": pv_fcf
        })

    final_year_fcf = dcf_rows[-1]["Projected FCF"]

    terminal_value = final_year_fcf * (1 + terminal_growth) / (wacc - terminal_growth)

    pv_terminal_value = terminal_value / ((1 + wacc) ** 5)

    enterprise_value = total_pv_fcf + pv_terminal_value

    terminal_value_share = pv_terminal_value / enterprise_value if enterprise_value else 0

    equity_value = enterprise_value + cash - debt

    intrinsic_value_per_share = equity_value / shares_outstanding

    upside_downside = ((intrinsic_value_per_share - current_price) / current_price) * 100

    return {
        "growth": growth,
        "fcf_margin": fcf_margin,
        "wacc": wacc,
        "terminal_growth": terminal_growth,
        "enterprise_value": enterprise_value,
        "equity_value": equity_value,
        "intrinsic_value_per_share": intrinsic_value_per_share,
        "current_price": current_price,
        "upside_downside": upside_downside,
        "terminal_value_share": terminal_value_share,
        "starting_fcf_margin": starting_fcf_margin,
        "rows": dcf_rows
    }

def calculate_investment_score(financials, base_dcf):
    revenue = financials.get("revenue")
    net_income = financials.get("netIncome")
    debt = financials.get("debt") or 0
    pe_ratio = financials.get("pe_ratio")
    free_cash_flow = financials.get("freeCashFlow")

    # Valuation score
    if isinstance(pe_ratio, (int, float)):
        if pe_ratio < 15:
            valuation_score = 95
        elif pe_ratio < 25:
            valuation_score = 80
        elif pe_ratio < 35:
            valuation_score = 65
        elif pe_ratio < 50:
            valuation_score = 45
        else:
            valuation_score = 25
    else:
        valuation_score = 50

    # Profitability score
    if revenue and net_income is not None:
        net_margin = net_income / revenue
        if net_margin > 0.20:
            profitability_score = 95
        elif net_margin > 0.10:
            profitability_score = 80
        elif net_margin > 0.05:
            profitability_score = 60
        elif net_margin > 0:
            profitability_score = 40
        else:
            profitability_score = 15
    else:
        profitability_score = 50

    # Balance sheet score
    if revenue and revenue != 0:
        debt_to_revenue = debt / revenue
        if debt_to_revenue < 0.10:
            balance_sheet_score = 95
        elif debt_to_revenue < 0.30:
            balance_sheet_score = 80
        elif debt_to_revenue < 0.60:
            balance_sheet_score = 60
        elif debt_to_revenue < 1.00:
            balance_sheet_score = 40
        else:
            balance_sheet_score = 20
    else:
        balance_sheet_score = 50

    # Cash flow quality score
    if revenue and free_cash_flow is not None:
        fcf_margin = free_cash_flow / revenue
        if fcf_margin > 0.20:
            cash_flow_score = 95
        elif fcf_margin > 0.10:
            cash_flow_score = 80
        elif fcf_margin > 0.05:
            cash_flow_score = 60
        elif fcf_margin > 0:
            cash_flow_score = 40
        else:
            cash_flow_score = 15
    else:
        cash_flow_score = 50

    # DCF score
    if base_dcf:
        upside = base_dcf.get("upside_downside", 0)
        if upside > 40:
            dcf_score = 95
        elif upside > 20:
            dcf_score = 80
        elif upside > 0:
            dcf_score = 65
        elif upside > -20:
            dcf_score = 45
        elif upside > -40:
            dcf_score = 30
        else:
            dcf_score = 15
    else:
        dcf_score = 50

    overall_score = (
        valuation_score * 0.25 +
        profitability_score * 0.25 +
        balance_sheet_score * 0.20 +
        cash_flow_score * 0.15 +
        dcf_score * 0.15
    )

    if overall_score >= 85:
        rating = "Strong Buy"
    elif overall_score >= 70:
        rating = "Buy"
    elif overall_score >= 55:
        rating = "Hold"
    elif overall_score >= 40:
        rating = "Sell"
    else:
        rating = "Strong Sell"

    return {
        "overall": round(overall_score),
        "valuation": valuation_score,
        "profitability": profitability_score,
        "balance_sheet": balance_sheet_score,
        "cash_flow": cash_flow_score,
        "dcf": dcf_score,
        "rating": rating
    }

def create_pdf(memo, company_name, financials, bear_dcf=None, base_dcf=None, bull_dcf=None, chart_data=None):
    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "Title",
        parent=styles["Title"],
        fontSize=22,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=20
    )

    heading_style = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=colors.HexColor("#2563eb"),
        spaceBefore=12,
        spaceAfter=8
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontSize=10,
        leading=14,
        spaceAfter=6
    )

    story = []

    from datetime import datetime
    today = datetime.today().strftime("%d %B %Y")

    story.append(Paragraph("MEMOGEN", title_style))
    story.append(Paragraph("<font size=16><b>AI Investment Research Report</b></font>", styles["Heading2"]))
    story.append(Spacer(1, 8))
    story.append(Paragraph(f"<font size=20><b>{company_name.upper()}</b></font>", styles["Heading1"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"<b>Prepared:</b> {today}", body_style))
    story.append(Spacer(1, 18))

    if base_dcf:
        scorecard = calculate_investment_score(financials, base_dcf)

        story.append(Paragraph("Executive Snapshot", heading_style))

        snapshot_table = [
            ["Metric", "Value"],
            ["Recommendation", scorecard["rating"]],
            ["Investment Score", f"{scorecard['overall']} / 100"],
            ["Current Price", f"${base_dcf['current_price']:.2f}"],
            ["Intrinsic Value", f"${base_dcf['intrinsic_value_per_share']:.2f}"],
            ["Upside / Downside", f"{base_dcf['upside_downside']:.1f}%"]
        ]

        snapshot = Table(snapshot_table, colWidths=[170, 220])

        snapshot.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))

        story.append(snapshot)
        story.append(Spacer(1, 20))
    
        story.append(Paragraph("Investment Scorecard", heading_style))

        scorecard_table = [
            ["Category", "Score"],
            ["Overall", f"{scorecard['overall']} / 100"],
            ["Valuation", f"{scorecard['valuation']} / 100"],
            ["Profitability", f"{scorecard['profitability']} / 100"],
            ["Balance Sheet", f"{scorecard['balance_sheet']} / 100"],
            ["Cash Flow Quality", f"{scorecard['cash_flow']} / 100"],
            ["DCF", f"{scorecard['dcf']} / 100"]
        ]
     
        score_table = Table(scorecard_table, colWidths=[170, 220])

        score_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))

        story.append(score_table)
        story.append(Spacer(1, 20))

        radar_buffer = BytesIO()

        categories = [
            "Valuation",
            "Profitability",
            "Balance Sheet",
            "Cash Flow",
            "DCF"
        ]

        scores = [
            scorecard["valuation"],
            scorecard["profitability"],
            scorecard["balance_sheet"],
            scorecard["cash_flow"],
            scorecard["dcf"]
        ]

        angles = [n / float(len(categories)) * 2 * 3.14159 for n in range(len(categories))]
        scores += scores[:1]
        angles += angles[:1]

        plt.figure(figsize=(4.8, 4.8))
        ax = plt.subplot(111, polar=True)

        ax.plot(angles, scores, linewidth=2)
        ax.fill(angles, scores, alpha=0.25)

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)

        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_ylim(0, 100)

        plt.title("Investment Score Radar")
        plt.tight_layout()
        plt.savefig(radar_buffer, format="png", dpi=200)
        plt.close()

        radar_buffer.seek(0)

        story.append(Image(radar_buffer, width=330, height=330))
        story.append(PageBreak())

    story.append(Paragraph("Financial Overview", heading_style))

    financial_table = [
        ["Metric", "Value"],
        ["Sector", financials.get("sector", "N/A")],
        ["Market Cap", format_billions(financials.get("marketCap"))],
        ["Revenue", format_billions(financials.get("revenue"))],
        ["Net Income", format_billions(financials.get("netIncome"))],
        ["Debt", format_billions(financials.get("debt"))],
        [
            "P/E Ratio",
            str(round(financials.get("pe_ratio"), 2))
            if isinstance(financials.get("pe_ratio"), (int, float))
            else "N/A"
        ],
        [
            "Net Margin",
            safe_margin(financials.get("netIncome"), financials.get("revenue"))
        ]
    ]

    table = Table(financial_table, colWidths=[170, 220])

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 11),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE")
    ]))

    story.append(table)
    story.append(Spacer(1, 20))

    if chart_data is not None and not chart_data.empty and "Close" in chart_data.columns:
        story.append(Paragraph("10-Year Stock Price Chart", heading_style))

        chart_buffer = BytesIO()

        plt.figure(figsize=(7, 3))
        plt.plot(chart_data.index, chart_data["Close"])
        plt.title(f"{company_name.title()} Stock Price - 10Y")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.tight_layout()
        plt.savefig(chart_buffer, format="png", dpi=200)
        plt.close()

        chart_buffer.seek(0)
    
        story.append(Image(chart_buffer, width=460, height=210))
        story.append(Spacer(1, 20))

    if bear_dcf and base_dcf and bull_dcf:
        story.append(Paragraph("5-Year DCF Scenario Analysis", heading_style))

        dcf_summary_table = [
            ["Scenario", "Intrinsic Value", "Upside / Downside"],
            ["Bear", f"${bear_dcf['intrinsic_value_per_share']:.2f}", f"{bear_dcf['upside_downside']:.1f}%"],
            ["Base", f"${base_dcf['intrinsic_value_per_share']:.2f}", f"{base_dcf['upside_downside']:.1f}%"],
            ["Bull", f"${bull_dcf['intrinsic_value_per_share']:.2f}", f"{bull_dcf['upside_downside']:.1f}%"]
        ]

        dcf_table = Table(dcf_summary_table, colWidths=[120, 160, 160])

        dcf_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 11),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
            ("FONTSIZE", (0, 1), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE")
        ]))

        story.append(dcf_table)
        story.append(Spacer(1, 8))

        dcf_chart_buffer = BytesIO()

        scenarios = ["Bear", "Base", "Bull"]
        values = [
            bear_dcf["intrinsic_value_per_share"],
            base_dcf["intrinsic_value_per_share"],
            bull_dcf["intrinsic_value_per_share"]
        ]

        plt.figure(figsize=(6, 3))
        plt.bar(scenarios, values)
        plt.title("DCF Intrinsic Value by Scenario")
        plt.ylabel("Intrinsic Value per Share")
        plt.tight_layout()
        plt.savefig(dcf_chart_buffer, format="png", dpi=200)
        plt.close()

        dcf_chart_buffer.seek(0)

        story.append(Image(dcf_chart_buffer, width=420, height=210))
        story.append(Spacer(1, 16))

        story.append(Paragraph(
            f"Terminal value represents {base_dcf['terminal_value_share']*100:.1f}% of enterprise value.",
            body_style
        ))
 
        story.append(Spacer(1, 12))

        story.append(Paragraph("Base Case 5-Year Forecast", heading_style))

        forecast_table = [
            ["Year", "Growth", "Revenue", "FCF Margin", "FCF", "PV of FCF"]
        ]

        for row in base_dcf["rows"]:
            forecast_table.append([
                str(row["Year"]),
                row["Revenue Growth"],
                format_billions(row["Projected Revenue"]),
                row["FCF Margin"],
                format_billions(row["Projected FCF"]),
                format_billions(row["PV of FCF"])
            ])

        forecast = Table(
            forecast_table,
            colWidths=[45, 70, 90, 75, 90, 90]
        )

        forecast.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
            ("FONTSIZE", (0, 1), (-1, -1), 7),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ]))

        story.append(forecast)
        story.append(PageBreak())

    for line in memo.split("\n"):
        line = line.strip()

        if not line:
            story.append(Spacer(1, 6))
        elif line.startswith("##"):
            story.append(Paragraph(line.replace("#", "").strip(), heading_style))
        elif line.startswith("-"):
            story.append(Paragraph("• " + line[1:].strip(), body_style))
        else:
            story.append(Paragraph(line, body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer
if st.button("Generate Memo"):

    ticker = get_ticker(company_name)
    financials = get_financial_data(ticker)

    bear_dcf = calculate_dcf(
        financials,
        max(growth_assumption - 0.05, 0.01),
        max(fcf_margin_assumption - 0.03, 0.03),
        wacc_assumption + 0.01,
        terminal_growth_assumption
    )
    
    base_dcf = calculate_dcf(
        financials,
        growth_assumption,
        fcf_margin_assumption,
        wacc_assumption,
        terminal_growth_assumption
    )

    bull_dcf = calculate_dcf(
        financials,
        growth_assumption + 0.05,
        fcf_margin_assumption + 0.03,
        max(wacc_assumption - 0.01, 0.05),
        terminal_growth_assumption
    )

    display_name = company_name.title()

    document_text = ""

    if uploaded_file is not None:
        document_text = extract_pdf_text(uploaded_file)
    if bear_dcf and base_dcf and bull_dcf:
        dcf_text = f"""
    Bear Case Intrinsic Value: ${bear_dcf['intrinsic_value_per_share']:.2f}
    
    Base Case Intrinsic Value: ${base_dcf['intrinsic_value_per_share']:.2f}
    
    Bull Case Intrinsic Value: ${bull_dcf['intrinsic_value_per_share']:.2f}

    Base Case Upside/Downside: {base_dcf['upside_downside']:.1f}%
    """
    else:
        dcf_text = """
    DCF analysis could not be completed because some required financial inputs were unavailable.
    Use the available financial data only.
    """

    prompt = f"""
    You are a senior buy-side equity analyst writing for a portfolio manager.
    
    Your job is NOT to describe the company generically.
    Your job is to determine whether the financial data supports an attractive investment case.

    CRITICAL RULES:
    - Use ONLY the financial data and PDF text provided.
    - Do NOT invent numbers, growth rates, margins, competitors, or forecasts.
    - If information is missing, say what cannot be concluded.
    - Every section must contain analytical judgment, not description.
    - Avoid generic phrases such as "strong brand", "competitive industry", or "future growth potential" unless supported by data.
    - Focus on valuation, earnings quality, balance sheet risk, expectations, and downside risk.
    - When mentioning Market Cap, Revenue, Net Income, Debt, or Price, copy the value exactly from FINANCIAL DATA including the $ symbol and B suffix.
    - Do NOT write financial values like 253.49B. You must write them as $253.49B.
    - All monetary values must include a $ symbol.
    Use EXACTLY these sections:

    ## EXECUTIVE SUMMARY
    Write one institutional-style paragraph explaining the investment case, the key concern, and the final recommendation.

    ## INVESTMENT THESIS
    Explain in 3 bullet points what must be true for the stock to be attractive.
    Each point must connect fundamentals to valuation.

    ## KEY FINANCIAL INTERPRETATION
    Analyze the financial data below.
    Do not just repeat the numbers.
    Explain what the relationship between revenue, net income, debt, market cap, and P/E says about business quality.

    ## VALUATION ASSESSMENT
    - Interpret the P/E ratio.
    - Explain whether the valuation looks demanding, reasonable, or cheap.
    - Compare valuation to profitability quality.
    - Explain what expectations appear embedded in the stock price.

    ## PROFITABILITY & EARNINGS QUALITY
    - Analyze margin strength using revenue, net income, and net profit margin.
    - Explain whether profits look scalable, fragile, cyclical, or durable.
    - Identify whether earnings quality supports the valuation.
    
    ## BALANCE SHEET & FINANCIAL RISK
    - Analyze debt relative to revenue and net income.
    - Classify leverage risk as Low, Moderate, or High.
    - Explain how debt could affect downside risk, flexibility, and shareholder returns.

    ## GROWTH & REINVESTMENT OUTLOOK
    - Classify the company as Hypergrowth, Growth, Mature, or Declining.
    - Explain whether the company appears to have room for reinvestment.
    - If the data does not prove growth, explicitly say so.
    - Use PDF evidence if available.
    
    ## MARKET EXPECTATIONS GAP
    Explain the gap between what the market seems to expect and what the financial data actually proves.
    State whether sentiment appears too optimistic, too pessimistic, or balanced.
    
    ## DOWNSIDE CASE
    Explain what could go wrong.
    Focus on valuation compression, margin weakness, debt risk, weak growth, or earnings disappointment.
    Give a rough estimate of what the stock price could be if the downside case materialises.
    
    ## UPSIDE CASE
    Explain what would need to happen for the stock to perform well.
    Do not assume upside unless supported by the data.
    Give a rough estimate of what the stock price could be if the upside case materialises.
    
    ## INVESTMENT DECISION
    Give a final Buy, Hold, or Sell rating.
    The decision must follow logically from:
    1. valuation
    2. profitability
    3. balance sheet risk
    4. growth outlook
    5. expectations gap
    
    Include a confidence score from 1 to 10.
    
    ## RISKS
    Provide specific bullet-point risks.
    
    ## SWOT
    Provide bullet points under:
    - Strengths
    - Weaknesses
    - Opportunities
    - Threats

    Memo style: {memo_style}
    Company: {company_name}
    
    FINANCIAL DATA:
    
    Company: {company_name}
    Sector: {financials.get('sector', 'N/A')}
    Market Cap: {format_billions(financials.get('marketCap'))}
    Revenue: {format_billions(financials.get('revenue'))}
    Net Income: {format_billions(financials.get('netIncome'))}
    Net Profit Margin: {safe_margin(financials.get('netIncome'), financials.get('revenue'))}
    Debt: {format_billions(financials.get('debt'))}
    P/E Ratio: {round(financials.get('pe_ratio'), 2) if isinstance(financials.get('pe_ratio'), (int, float)) else 'N/A'}

    DCF SCENARIOS:
    {dcf_text}

    Bear Case Assumptions:
    Revenue Growth: {max(growth_assumption - 0.05, 0.01)*100:.1f}%
    FCF Margin: {max(fcf_margin_assumption - 0.03, 0.03)*100:.1f}%
    WACC: {(wacc_assumption + 0.01)*100:.1f}%

    Base Case Assumptions:
    Revenue Growth: {growth_assumption*100:.1f}%
    FCF Margin: {fcf_margin_assumption*100:.1f}%
    WACC: {wacc_assumption*100:.1f}%

    Bull Case Assumptions:
    Revenue Growth: {(growth_assumption + 0.05)*100:.1f}%
    FCF Margin: {(fcf_margin_assumption + 0.03)*100:.1f}%
    WACC: {max(wacc_assumption - 0.01, 0.05)*100:.1f}%

    
    PDF TEXT:
    {document_text[:8000]}
    
    STYLE REQUIREMENTS:
    - Write like a professional equity research analyst.
    - Be skeptical and judgment-based.
    - Avoid generic MBA language.
    - Do not simply describe; interpret.
    - Explain implications for investors.
    - Use markdown only.
    - Do not use HTML.
    - Do not add extra sections.
    - Do NOT use italics.
    - Do NOT use asterisks.
    - Use normal paragraphs with spaces between words.
    - Do not use superscript, subscript, small text, or HTML formatting.
    - Do not use inline markdown formatting inside paragraphs.
    - Do NOT use underscores.
    - Do NOT use markdown emphasis.
    - Do NOT place financial values directly next to words.
    - Always write financial values with spaces around them, for example: $253.49B revenue, not $253.49Brevenue.
    - Discuss why the bear and bull valuations differ.
    - Assess whether the current valuation already prices in a bull-case outcome.
    - If the stock appears overvalued, explain what assumptions are required to justify today's price.
    """

    with st.spinner("Generating memo..."):
     
        response = client.responses.create(
            model="gpt-4.1",
            input=prompt
        )

        memo = response.output_text

    st.subheader("📄 Investment Memo")

    memo = memo.replace("***", "")
    memo = memo.replace("**", "")
    memo = memo.replace("_", "")
    memo = memo.replace("$", "\\$")

    st.markdown(
    memo,
    help=None
    )

    st.subheader("📈 Stock Price (10Y)")

    chart_data = get_stock_chart(ticker)

    if chart_data is not None and not chart_data.empty and "Close" in chart_data.columns:
        st.line_chart(chart_data["Close"])
    else:
        st.warning("Stock price chart unavailable at the moment.")

    st.subheader("📊 Financial Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric("Company", display_name)
    col2.metric("Market Cap", format_billions(financials.get("marketCap")))
    col3.metric("Price", f"${financials.get('lastPrice', 0):,.2f}" if financials.get("lastPrice") else "N/A")

    col4, col5, col6 = st.columns(3)

    col4.metric("Revenue", format_billions(financials.get("revenue")))
    col5.metric("Net Income", format_billions(financials.get("netIncome")))
    col6.metric("Debt", format_billions(financials.get("debt")))

    st.caption(
        f"Sector: {financials.get('sector', 'N/A')} | Data Source: {financials.get('dataSource', 'N/A')}"
    )

    st.subheader("🧠 Investment Scorecard")

    scorecard = calculate_investment_score(financials, base_dcf)

    score_col1, score_col2, score_col3 = st.columns(3)

    score_col1.metric("Overall Score", f"{scorecard['overall']} / 100")
    score_col2.metric("Suggested Rating", scorecard["rating"])
    score_col3.metric("DCF Score", f"{scorecard['dcf']} / 100")

    score_col4, score_col5, score_col6 = st.columns(3)

    score_col4.metric("Valuation", f"{scorecard['valuation']} / 100")
    score_col5.metric("Profitability", f"{scorecard['profitability']} / 100")
    score_col6.metric("Balance Sheet", f"{scorecard['balance_sheet']} / 100")

    score_col7, _, _ = st.columns(3)

    score_col7.metric("Cash Flow Quality", f"{scorecard['cash_flow']} / 100")
    
    with st.expander("How the Investment Scorecard is calculated"):
        st.markdown("""
        The scorecard is a rule-based summary of the company's financial profile.

        **Overall Score:**
        Weighted average of valuation, profitability, balance sheet strength, cash flow quality, and DCF upside.

        **Valuation:**
        Based mainly on the P/E ratio. Lower P/E ratios generally receive higher scores.

        **Profitability:**
        Based on net profit margin. Higher margins suggest stronger earnings quality.

        **Balance Sheet:**
        Based on debt relative to revenue. Lower debt burden receives a higher score.

        **Cash Flow Quality:**
        Based on free cash flow margin. Strong free cash flow relative to revenue receives a higher score.

        **DCF Score:**
        Based on the base-case DCF upside or downside versus the current market price.

        The scorecard is not a final recommendation by itself. It is a structured diagnostic tool to support the full investment memo.
        """)

    st.subheader("📐 5-Year DCF Scenario Analysis")

    if bear_dcf and base_dcf and bull_dcf:

        scenario_df = pd.DataFrame({
            "Scenario": ["Bear", "Base", "Bull"],
            "Intrinsic Value": [
                f"${bear_dcf['intrinsic_value_per_share']:.2f}",
                f"${base_dcf['intrinsic_value_per_share']:.2f}",
                f"${bull_dcf['intrinsic_value_per_share']:.2f}"
            ],
            "Upside / Downside": [
                f"{bear_dcf['upside_downside']:.1f}%",
                f"{base_dcf['upside_downside']:.1f}%",
                f"{bull_dcf['upside_downside']:.1f}%"
            ]
        })

        assumption_df = pd.DataFrame({
            "Scenario": ["Bear", "Base", "Bull"],
            "Revenue Growth": [
                f"{max(growth_assumption - 0.05, 0.01)*100:.1f}%",
                f"{growth_assumption*100:.1f}%",
                f"{(growth_assumption + 0.05)*100:.1f}%"
            ],
            "FCF Margin": [
                f"{max(fcf_margin_assumption - 0.03, 0.03)*100:.1f}%",
                f"{fcf_margin_assumption*100:.1f}%",
                f"{(fcf_margin_assumption + 0.03)*100:.1f}%"
            ],
            "WACC": [
                f"{(wacc_assumption + 0.01)*100:.1f}%",
                f"{wacc_assumption*100:.1f}%",
                f"{max(wacc_assumption - 0.01, 0.05)*100:.1f}%"
            ],
            "Terminal Growth": [
                f"{terminal_growth_assumption*100:.1f}%",
                f"{terminal_growth_assumption*100:.1f}%",
                f"{terminal_growth_assumption*100:.1f}%"
            ]
        })

        st.markdown("### Scenario Assumptions")
        st.table(assumption_df)

        st.markdown("### Scenario Valuation")
        st.table(scenario_df)

        st.caption(
            f"Terminal value represents {base_dcf['terminal_value_share']*100:.1f}% of enterprise value."
        )

        if base_dcf["terminal_value_share"] > 0.80:
            st.warning(
                "DCF is highly dependent on terminal value. Small changes in WACC or terminal growth can materially change the valuation."
            )

        st.markdown("### Base Case Forecast")

        dcf_col1, dcf_col2, dcf_col3 = st.columns(3)

        dcf_col1.metric(
            "Intrinsic Value",
            f"${base_dcf['intrinsic_value_per_share']:.2f}"
        )

        dcf_col2.metric(
            "Current Price",
            f"${base_dcf['current_price']:.2f}"
        )

        dcf_col3.metric(
            "Upside / Downside",
            f"{base_dcf['upside_downside']:.1f}%"
        )

        dcf_table = pd.DataFrame(base_dcf["rows"])

        dcf_table["Projected Revenue"] = dcf_table["Projected Revenue"].apply(format_billions)
        dcf_table["Projected FCF"] = dcf_table["Projected FCF"].apply(format_billions)
        dcf_table["PV of FCF"] = dcf_table["PV of FCF"].apply(format_billions)

        st.table(dcf_table)

    else:
        st.warning("DCF unavailable because some required financial data is missing.")

    pdf_file = create_pdf(
        memo,
        company_name,
        financials,
        bear_dcf,
        base_dcf,
        bull_dcf,
        chart_data
    )
    st.download_button(
        "Download Memo as PDF",
        data=pdf_file,
        file_name=f"{company_name}_investment_memo.pdf",
        mime="application/pdf"
    )