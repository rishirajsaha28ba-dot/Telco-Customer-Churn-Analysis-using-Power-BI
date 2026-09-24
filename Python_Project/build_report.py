"""
Builds the project report (PDF) for "Telco Customer Churn - Data Analysis using Python".

1. Splits telco_churn_analysis.py into cells ("# %% [ID] Title").
2. Executes every cell in one shared namespace, capturing its printed output.
3. Renders each cell's code and output as images (Pygments).
4. Assembles title page, Chapters 1-3, code/result images, figures and
   inferences into outputs/Telco_Churn_Python_Report.pdf (ReportLab).

Edit STUDENT_DETAILS below before submitting.
"""
import contextlib
import io
import re
from pathlib import Path

from PIL import Image as PILImage
from pygments import highlight
from pygments.formatters import ImageFormatter
from pygments.lexers import PythonLexer, TextLexer
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph,
                                SimpleDocTemplate, Spacer, Table, TableStyle)

BASE = Path(__file__).resolve().parent
SCRIPT = BASE / "telco_churn_analysis.py"
OUT = BASE / "outputs"
IMG_DIR = OUT / "code_images"
FIG_DIR = OUT / "figures"
PDF_PATH = OUT / "Telco_Churn_Python_Report.pdf"
CODE_SCALE = 0.55  # px -> pt, keeps short snippets from being blown up
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

# ---------------------------------------------------------------- edit me --
STUDENT_DETAILS = [
    ("Student 1", "Rishiraj Saha", "PRN: ____________"),
    ("Student 2", "____________", "PRN: ____________"),
]
FACULTY = "Prof. ____________"
SUBJECT = "Programming for Data Science"
INSTITUTE = "Symbiosis Institute of Business Management"
SUBMISSION_DATE = "24 September 2026"
# ---------------------------------------------------------------------------

INFERENCES = {
    "SETUP": """The Excel file loads into a DataFrame of <b>7,043 rows and 33 columns</b>, well above the
        510-row minimum. 23 columns are text (categorical) and 9 are numeric, so the dataset mixes both
        variable types required by the brief.""",
    "PD1": """Only two columns contain missing values. <b>Total Charges</b> has 11 blanks, all for customers with
        0 months tenure who have not yet been billed, so they are filled with 0 rather than dropped.
        The 5,174 blanks in <b>Churn Reason</b> are structural: retained customers have no churn reason.
        After cleaning, the average customer has been with the company for <b>32 months</b> and pays
        <b>$64.76/month</b>. The overall churn rate is <b>26.5%</b>: roughly one in four customers left.""",
    "PD2": """Contract type is the strongest categorical churn driver. <b>Month-to-month customers churn at
        42.7%</b>, against 11.3% on one-year and only 2.8% on two-year contracts. Fibre-optic customers churn
        at 41.9%, more than twice the DSL rate, even though they pay the most ($91.50 on average). This points
        to a price/value problem with the premium product. Customers paying by <b>electronic check churn at
        45.3%</b>, about three times the rate of those on automatic card or bank payments.""",
    "PD3": """The pivot table shows that contract and tenure add to each other's effect. A month-to-month customer in their
        first year has a <b>51.4%</b> churn rate, while no two-year customer in the first 24 months churned.
        Even long-standing month-to-month customers (49-72 m) churn at 26%. The reasons list is led by
        <b>support-staff attitude (10.3%)</b>, with competitor offers on speed, data, price and devices close
        behind. Together, the competitor reasons are the largest group of churn reasons.""",
    "NP1": """Churned customers pay <b>$13.18 more per month</b> on average ($74.44 vs $61.27), and their
        median is $15 higher. Retained customers show a wider spread (std 31.1) because they include many
        low-cost phone-only plans around $20. The Welch t-statistic of <b>18.4</b> is far above the usual
        critical value (about 1.96), so the difference in monthly charges is statistically significant: higher bills are
        associated with more churn.""",
    "NP2": """Among the raw numeric fields, <b>tenure has the strongest (negative) relationship with churn
        (r = -0.35)</b>: the longer a customer stays, the less likely they are to leave. Monthly charges are positively
        related (r = +0.19), and CLTV slightly negatively. Tenure and total charges are highly collinear
        (r = 0.83), which is expected because total charges are roughly tenure x monthly charges. IBM's model-based
        <b>Churn Score</b> tracks actual churn well (r = +0.67).""",
    "NP3": """Vectorised <code>np.where</code> rules split customers into three risk tiers using the churn score.
        The <b>High</b> tier (score >= 80) had a 92% actual churn rate, and the Low tier had none, so the score separates
        customers well enough to target retention offers. Churned customers took <b>$139K of monthly revenue
        (30.5% of the total), or about $1.67M a year</b>. Churned customers pay more than average, so the
        revenue share (30.5%) is higher than the customer share (26.5%).""",
    "MPL1": """The donut chart shows the 26.5% / 73.5% churn split. The bar chart shows how steeply churn changes with
        contract length: moving a customer from month-to-month to a one-year contract cuts expected churn by
        about three quarters. Offering incentives to switch to longer contracts is the clearest retention step.""",
    "MPL2": """The histogram has two peaks. Retained customers cluster at <b>$20-25</b> (basic phone plans), while
        churned customers cluster at <b>$70-105</b>, the fibre/streaming bundle price range. The box plot
        shows that the median churner leaves at about <b>10 months</b>, compared with 38 months tenure for retained
        customers, so most churn happens early in the customer lifecycle.""",
    "MPL3": """Churn is highest in the first few months (about 50-60%) and falls steadily to under 10% after five
        years. This shows that the onboarding period matters most for retention. The reasons chart shows two main
        themes: <b>service experience</b> (support and provider attitude) and <b>competitive pressure</b> (speed,
        data, offers, devices). Retention plans should address both.""",
}


# ------------------------------------------------------------------ helpers --
def split_cells(src):
    parts = re.split(r"^# %% \[(\w+)\] (.*)$", src, flags=re.M)
    return [(parts[i], parts[i + 1].strip(), parts[i + 2].strip("\n"))
            for i in range(1, len(parts), 3)]


def render(text, lexer, path, style, line_numbers):
    fmt = ImageFormatter(font_name=MONO, font_size=15, style=style,
                         line_numbers=line_numbers, line_pad=3,
                         image_pad=14, line_number_bg="#EEF1F5",
                         line_number_fg="#8A94A6")
    path.write_bytes(highlight(text, lexer, fmt))
    return path


def fit_image(path, max_w, max_h=None, max_scale=1e9):
    w, h = PILImage.open(path).size
    scale = min(max_w / w, (max_h / h) if max_h else 1e9, max_scale)
    return Image(str(path), width=w * scale, height=h * scale)


def boxed(img):
    t = Table([[img]], style=[("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#C9D1DC")),
                              ("LEFTPADDING", (0, 0), (-1, -1), 0),
                              ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                              ("TOPPADDING", (0, 0), (-1, -1), 0),
                              ("BOTTOMPADDING", (0, 0), (-1, -1), 0)], hAlign="LEFT")
    return t


# ------------------------------------------------------------------ styles ---
ss = getSampleStyleSheet()
ACCENT = colors.HexColor("#1F3A5F")
H1 = ParagraphStyle("H1", parent=ss["Heading1"], textColor=ACCENT, fontSize=18, spaceAfter=10)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], textColor=ACCENT, fontSize=13.5, spaceBefore=6)
H3 = ParagraphStyle("H3", parent=ss["Heading3"], textColor=colors.HexColor("#333333"), fontSize=11)
BODY = ParagraphStyle("Body", parent=ss["BodyText"], fontSize=10.3, leading=14.5, alignment=TA_JUSTIFY)
LABEL = ParagraphStyle("Label", parent=BODY, fontName="Helvetica-Bold", fontSize=9.5,
                       textColor=colors.HexColor("#555555"), spaceBefore=4, spaceAfter=3)
INFER = ParagraphStyle("Infer", parent=BODY, backColor=colors.HexColor("#F3F7FC"),
                       borderColor=colors.HexColor("#4C78A8"), borderWidth=0.8,
                       borderPadding=7, spaceBefore=8, spaceAfter=14, leftIndent=7, rightIndent=7)
CENTER = ParagraphStyle("Center", parent=BODY, alignment=TA_CENTER)


def table(data, widths, header=True):
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    st = [("FONT", (0, 0), (-1, -1), "Helvetica", 9),
          ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#C9D1DC")),
          ("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F6F8FB")])]
    if header:
        st += [("BACKGROUND", (0, 0), (-1, 0), ACCENT),
               ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
               ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 9)]
    t.setStyle(TableStyle(st))
    return t


def on_page(canvas, doc):
    if doc.page == 1:
        return
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#777777"))
    canvas.drawString(2 * cm, 1.2 * cm, "Telco Customer Churn - Data Analysis using Python")
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Page {doc.page}")
    canvas.restoreState()


# ------------------------------------------------------------------- build --
def main():
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    cells = split_cells(SCRIPT.read_text())

    ns = {"__file__": str(SCRIPT), "__name__": "__report__"}
    results = {}
    for cid, title, code in cells:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            exec(compile(code, f"<{cid}>", "exec"), ns)
        out = buf.getvalue().rstrip()
        code_img = render(code, PythonLexer(), IMG_DIR / f"{cid}_code.png", "friendly", True)
        out_img = render(out, TextLexer(), IMG_DIR / f"{cid}_output.png", "default", False) if out else None
        results[cid] = (title, code_img, out_img)
        print(f"[ok] {cid}: {title}")

    df = ns["df"]
    W = A4[0] - 4 * cm
    story = []

    # ---------------- Title page
    story += [Spacer(1, 2.5 * cm),
              Paragraph(SUBJECT.upper(), ParagraphStyle("s", parent=CENTER, fontSize=12,
                                                        textColor=colors.HexColor("#4C78A8"))),
              Spacer(1, 0.6 * cm),
              Paragraph("Telco Customer Churn Analysis", ParagraphStyle("t", parent=CENTER, fontSize=26,
                        leading=32, fontName="Helvetica-Bold", textColor=ACCENT)),
              Spacer(1, 0.3 * cm),
              Paragraph("Data Analysis using Python: Pandas, NumPy and Matplotlib",
                        ParagraphStyle("st", parent=CENTER, fontSize=13, textColor=colors.HexColor("#444444"))),
              Spacer(1, 1.6 * cm)]
    tp = [["Data heading", "IBM Telco Customer Churn (7,043 customers, 33 variables)"],
          ["Subject", SUBJECT],
          ["Faculty", FACULTY]]
    for role, name, prn in STUDENT_DETAILS:
        tp.append([role, f"{name}     {prn}"])
    tp += [["Institute", INSTITUTE], ["Submission date", SUBMISSION_DATE]]
    t = table(tp, [4.2 * cm, 11.5 * cm], header=False)
    t.setStyle(TableStyle([("FONT", (0, 0), (0, -1), "Helvetica-Bold", 10),
                           ("FONT", (1, 0), (1, -1), "Helvetica", 10),
                           ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E8EEF6")),
                           ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
    story += [t, PageBreak()]

    # ---------------- Contents
    story += [Paragraph("Contents", H1)]
    toc = [["Chapter 1", "Introduction and Data Description"],
           ["Chapter 2", "Data Analysis using Python"],
           ["", "2.1  Pandas: 3 applications with inference"],
           ["", "2.2  NumPy: 3 applications with inference"],
           ["", "2.3  Matplotlib: 3 applications with inference"],
           ["Chapter 3", "Conclusion: Inference and Storytelling"]]
    story += [table([["", "Section"]] + toc, [3 * cm, 12.7 * cm]), PageBreak()]

    # ---------------- Chapter 1
    story += [Paragraph("Chapter 1: Introduction and Data Description", H1),
              Paragraph("1.1 Introduction", H2),
              Paragraph("""Customer churn is when a subscriber ends their relationship with a service
              provider. It is one of the most expensive problems in telecommunications: winning a new
              customer typically costs five to seven times more than keeping an existing one, and every churned
              customer takes their future recurring revenue with them. Knowing <i>who</i> churns, <i>when</i> and
              <i>why</i> lets a telecom operator target retention spending where it has the most effect.""", BODY),
              Spacer(1, 6),
              Paragraph("""This project analyses the IBM Telco Customer Churn dataset with the core Python
              data-science stack. <b>Pandas</b> is used for loading, cleaning, grouping and pivoting; <b>NumPy</b>
              for vectorised statistics, correlation and segmentation; and <b>Matplotlib</b> for visual
              storytelling. Each application is shown as an image of the code, followed by its output and an
              inference.""", BODY),
              Paragraph("1.2 Objectives", H2)]
    for o in ["Measure the overall churn rate and its revenue impact.",
              "Identify the service, contract and billing characteristics associated with churn.",
              "Understand how churn changes over the customer lifecycle (tenure).",
              "Summarise the stated reasons for churn and recommend retention actions."]:
        story.append(Paragraph("&bull; " + o, BODY))

    story += [Paragraph("1.3 Data Source", H2),
              Paragraph("""<b>Dataset:</b> Telco Customer Churn (IBM Cognos Analytics sample, version 11.1.3+),
              published on Kaggle: <i>kaggle.com/datasets/ylchang/telco-customer-churn-1113</i>. It is a
              secondary dataset describing a fictional telecom company in California, USA, with one row per
              customer. The file used is <i>DataSet/Telco_customer_churn.xlsx</i>.""", BODY),
              Spacer(1, 6)]
    facts = [["Property", "Value"],
             ["Rows (customers)", "7,043 (minimum required: 510)"],
             ["Columns", "33 in raw file (29 after dropping constant / duplicate columns)"],
             ["Categorical variables", "e.g. Gender, Contract, Internet Service, Payment Method, Churn Label"],
             ["Numerical variables", "Tenure Months, Monthly Charges, Total Charges, CLTV, Churn Score, Latitude/Longitude"],
             ["Target variable", "Churn Value (1 = customer left this quarter, 0 = stayed)"],
             ["Geography", f"California, USA: {df['City'].nunique():,} cities"]]
    story += [table(facts, [4.5 * cm, 11.2 * cm]), PageBreak(), Paragraph("1.4 Data Dictionary", H2)]
    dd = [["Variable", "Type", "Description"],
          ["CustomerID", "ID", "Unique customer identifier"],
          ["City, Zip Code, Latitude, Longitude", "Categorical / Numeric", "Customer's primary residence"],
          ["Gender, Senior Citizen, Partner, Dependents", "Categorical", "Demographic attributes (Yes/No, Male/Female)"],
          ["Tenure Months", "Numeric", "Months the customer has been with the company (0-72)"],
          ["Phone Service, Multiple Lines", "Categorical", "Phone subscription details"],
          ["Internet Service", "Categorical", "DSL, Fiber optic or No internet"],
          ["Online Security, Online Backup, Device Protection, Tech Support", "Categorical", "Add-on services (Yes / No / No internet service)"],
          ["Streaming TV, Streaming Movies", "Categorical", "Streaming add-ons"],
          ["Contract", "Categorical", "Month-to-month, One year, Two year"],
          ["Paperless Billing, Payment Method", "Categorical", "Billing preferences"],
          ["Monthly Charges", "Numeric", "Current monthly bill (USD)"],
          ["Total Charges", "Numeric", "Total billed to date (USD)"],
          ["Churn Label / Churn Value", "Categorical / Binary", "Whether the customer left this quarter"],
          ["Churn Score", "Numeric", "IBM SPSS model-predicted churn likelihood (0-100)"],
          ["CLTV", "Numeric", "Predicted Customer Lifetime Value"],
          ["Churn Reason", "Categorical", "Customer's stated reason for leaving"]]
    dd = [[Paragraph(c, ParagraphStyle("c", parent=BODY, fontSize=8.8, leading=11,
                                       textColor=colors.white if i == 0 else colors.black,
                                       fontName="Helvetica-Bold" if i == 0 else "Helvetica"))
           for c in row] for i, row in enumerate(dd)]
    story += [table(dd, [5.6 * cm, 3.4 * cm, 6.7 * cm]),
              Paragraph("1.5 Tools and Environment", H2),
              Paragraph(f"""Python 3 with pandas, NumPy and Matplotlib (openpyxl is used to read the Excel file).
              All code is in <i>Python_Project/telco_churn_analysis.py</i>. The report is generated
              reproducibly by <i>build_report.py</i>, which executes the code and captures its real output.""", BODY),
              PageBreak()]

    # ---------------- Chapter 2
    story.append(Paragraph("Chapter 2: Data Analysis using Python", H1))
    sections = {"SETUP": None,
                "PD1": "2.1 Pandas: Three Applications",
                "NP1": "2.2 NumPy: Three Applications",
                "MPL1": "2.3 Matplotlib: Three Applications"}
    figures = {"MPL1": "mpl1_churn_contract.png", "MPL2": "mpl2_distributions.png",
               "MPL3": "mpl3_tenure_reasons.png"}
    first = True
    for cid, (title, code_img, out_img) in results.items():
        if cid in sections and sections[cid]:
            if not first:
                story.append(PageBreak())
            story.append(Paragraph(sections[cid], H2))
        first = False
        heading = "2.0 Setup: Importing Libraries and Loading the Data" if cid == "SETUP" else title
        block = [Paragraph(heading, H3), Paragraph("Code", LABEL),
                 boxed(fit_image(code_img, W, 17 * cm, CODE_SCALE))]
        story.append(KeepTogether(block[:3]))
        if out_img:
            story.append(KeepTogether([Paragraph("Output", LABEL), boxed(fit_image(out_img, W, 12 * cm, CODE_SCALE))]))
        if cid in figures:
            story.append(KeepTogether([Paragraph("Result: chart", LABEL),
                                       fit_image(FIG_DIR / figures[cid], W)]))
        story.append(Paragraph("<b>Inference:</b> " + INFERENCES[cid], INFER))

    # ---------------- Chapter 3
    story += [PageBreak(), Paragraph("Chapter 3: Conclusion: Inference and Storytelling", H1),
              Paragraph("3.1 The Story the Data Tells", H2),
              Paragraph("""About <b>one in four customers (26.5%) left</b> the company, and because churners
              pay more than average they took <b>30.5% of monthly revenue</b> with them, roughly <b>$1.67 million a
              year</b>. Churn is concentrated in a clear profile rather than spread evenly across customers:""", BODY),
              Spacer(1, 4)]
    profile = [["Driver", "High-churn group", "Low-churn group", "Tool / evidence"],
               ["Contract", "Month-to-month: 42.7%", "Two-year: 2.8%", "Pandas groupby, Matplotlib bar"],
               ["Tenure", "First 12 months: 47.4%", "49-72 months: 9.5%", "pd.cut, NumPy corr (r = -0.35)"],
               ["Internet", "Fibre optic: 41.9%", "No internet: 7.4%", "Pandas groupby"],
               ["Payment", "Electronic check: 45.3%", "Credit card (auto): 15.2%", "Pandas groupby"],
               ["Price", "Churners pay $74.4 / month", "Stayers pay $61.3 / month", "NumPy Welch t = 18.4"],
               ["Reasons", "Competitor offers, support attitude", "-", "value_counts, Matplotlib barh"]]
    story += [table(profile, [2.4 * cm, 4.6 * cm, 4.2 * cm, 4.5 * cm]),
              Paragraph("3.2 Key Findings", H2)]
    for f in ["<b>Commitment protects revenue.</b> Contract length is the single strongest lever. Two-year customers almost never leave, even in their first year.",
              "<b>The first year is the danger zone.</b> Churn peaks in the first few months and falls steadily with tenure. The median churner leaves after about 10 months.",
              "<b>The premium product is under-delivering.</b> Fibre-optic customers pay about $91/month yet churn at twice the DSL rate. Together with 'competitor offered higher speeds / more data', this suggests a value-for-money gap.",
              "<b>Manual payers are less attached.</b> Electronic-check payers churn about three times more than customers on automatic payments.",
              "<b>People matter.</b> The single most-cited reason is the attitude of support staff, so service quality problems are driving customers away as well as price.",
              "<b>Churn risk can be predicted.</b> A simple NumPy rule on churn score isolates a High-risk tier with 92% actual churn, so retention budgets can be targeted."]:
        story.append(Paragraph("&bull; " + f, BODY))
    story += [Paragraph("3.3 Recommendations", H2)]
    for r in ["Offer discounts or loyalty benefits to move month-to-month customers onto 1- or 2-year contracts.",
              "Run a structured <b>first-90-days onboarding programme</b> (welcome calls, set-up help, early-tenure offers).",
              "Review fibre pricing and speeds against competitors. Bundle Online Security and Tech Support to add value.",
              "Encourage auto-pay (card / bank transfer) with a small bill credit.",
              "Invest in support-staff training and track CSAT, as support attitude is the top stated reason for leaving.",
              "Use the churn-score segmentation to trigger proactive retention calls for High-risk customers."]:
        story.append(Paragraph("&bull; " + r, BODY))
    story += [Paragraph("3.4 Limitations and Future Scope", H2),
              Paragraph("""The data is a fictional, single-quarter snapshot from one US state, so the findings describe
              associations, not causes. Future work could fit a predictive model (e.g. logistic regression)
              and estimate the ROI of each retention action.""", BODY)]

    doc = SimpleDocTemplate(str(PDF_PATH), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=1.8 * cm, bottomMargin=1.8 * cm,
                            title="Telco Customer Churn - Data Analysis using Python",
                            author=", ".join(n for _, n, _ in STUDENT_DETAILS))
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    print(f"\nReport written to {PDF_PATH}")


if __name__ == "__main__":
    main()
