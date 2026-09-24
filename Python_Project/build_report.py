"""Build the PDF project report (code images -> result images -> inference).

Run after editing the TITLE_PAGE details below:
    python Python_Project/build_report.py
Output: Python_Project/Insurance_Cost_Analysis_Report.pdf
"""
import contextlib
import inspect
import io
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from pygments import highlight
from pygments.formatters import ImageFormatter
from pygments.lexers import PythonLexer
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (Image as RLImage, KeepTogether, PageBreak,
                                Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

import insurance_analysis as ia

# ---- Fill in your group's details ---------------------------------------
TITLE_PAGE = {
    "students": [("Student 1 Name", "PRN: __________"),
                 ("Student 2 Name", "PRN: __________")],
    "faculty": "Faculty Name",
    "subject": "Programming for Data Science",
    "data_heading": "Medical Insurance Cost Analysis",
    "institute": "",
    "date": "24/09/2026",
}
# --------------------------------------------------------------------------

HERE = Path(__file__).resolve().parent
IMG_DIR = HERE / "report_images"
IMG_DIR.mkdir(exist_ok=True)
OUT_PDF = HERE / "Insurance_Cost_Analysis_Report.pdf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
CONTENT_W = A4[0] - 4 * cm

styles = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=18,
                    textColor=colors.HexColor("#1a365d"), spaceAfter=10)
H2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=14,
                    textColor=colors.HexColor("#2b6cb0"), spaceBefore=8)
H3 = ParagraphStyle("H3", parent=styles["Heading3"], fontSize=11.5,
                    textColor=colors.HexColor("#1a202c"), spaceBefore=6)
BODY = ParagraphStyle("Body", parent=styles["BodyText"], fontSize=10.5,
                      leading=15, alignment=TA_JUSTIFY)
LABEL = ParagraphStyle("Label", parent=BODY, fontName="Helvetica-Bold",
                       textColor=colors.HexColor("#4a5568"), spaceBefore=4)
INFER = ParagraphStyle("Infer", parent=BODY, backColor=colors.HexColor("#ebf8ff"),
                       borderColor=colors.HexColor("#90cdf4"), borderWidth=0.6,
                       borderPadding=6, spaceBefore=6, spaceAfter=10)
CENTER = ParagraphStyle("Center", parent=BODY, alignment=TA_CENTER)


def code_image(func, name):
    src = inspect.getsource(func)
    fmt = ImageFormatter(font_name=MONO, font_size=15, line_numbers=True,
                         style="friendly", line_number_bg="#eeeeee",
                         image_pad=14)
    path = IMG_DIR / f"{name}_code.png"
    path.write_bytes(highlight(src, PythonLexer(), fmt))
    return path


def output_image(text, name):
    font = ImageFont.truetype(MONO, 15)
    lines = text.rstrip("\n").split("\n")
    line_h, pad = 20, 16
    width = max(int(font.getlength(l)) for l in lines) + 2 * pad
    img = Image.new("RGB", (max(width, 400), len(lines) * line_h + 2 * pad), "#1e1e1e")
    draw = ImageDraw.Draw(img)
    for i, line in enumerate(lines):
        draw.text((pad, pad + i * line_h), line, font=font, fill="#e2e8f0")
    path = IMG_DIR / f"{name}_output.png"
    img.save(path)
    return path


def fit(path, max_w=CONTENT_W, max_h=23 * cm):
    w, h = Image.open(path).size
    scale = min(max_w / w, max_h / h, 0.5)  # 0.5 keeps code text crisp but readable
    return RLImage(str(path), width=w * scale, height=h * scale)


def run(func, *args):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        result = func(*args)
    return result, buf.getvalue()


def application(story, title, aim, func, name, output, inference, figure=None):
    story.append(Paragraph(title, H3))
    story.append(Paragraph(f"<b>Objective:</b> {aim}", BODY))
    story.append(Paragraph("Code", LABEL))
    story.append(fit(code_image(func, name)))
    result = [Paragraph("Result", LABEL)]
    if output.strip():
        result.append(fit(output_image(output, name)))
    if figure:
        w, h = Image.open(figure).size
        result.append(RLImage(str(figure), width=CONTENT_W, height=CONTENT_W * h / w))
    story.append(KeepTogether(result))
    story.append(KeepTogether([Paragraph("Inference", LABEL),
                               Paragraph(inference, INFER)]))
    story.append(PageBreak())


def title_page(story):
    t = TITLE_PAGE
    story.append(Spacer(1, 3 * cm))
    story.append(Paragraph(t["subject"], ParagraphStyle(
        "s", parent=CENTER, fontSize=14, textColor=colors.HexColor("#4a5568"))))
    story.append(Spacer(1, 0.6 * cm))
    story.append(Paragraph(t["data_heading"], ParagraphStyle(
        "t", parent=CENTER, fontSize=26, leading=32, fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1a365d"))))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("Data analysis using Pandas, NumPy and Matplotlib",
                           ParagraphStyle("st", parent=CENTER, fontSize=13)))
    story.append(Spacer(1, 2 * cm))
    rows = [["Name", "PRN"]] + [list(s) for s in t["students"]]
    rows += [["Faculty", t["faculty"]], ["Subject", t["subject"]],
             ["Dataset", "Medical Cost Personal Datasets (Kaggle)"],
             ["Submission date", t["date"]]]
    table = Table(rows, colWidths=[6 * cm, 8 * cm])
    table.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2b6cb0")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONT", (0, 1), (0, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e0")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fafc")]),
        ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(table)
    if t["institute"]:
        story.append(Spacer(1, 1.5 * cm))
        story.append(Paragraph(t["institute"], CENTER))
    story.append(PageBreak())


def chapter_1(story):
    story.append(Paragraph("Chapter 1: Introduction and Data Description", H1))
    story.append(Paragraph("1.1 Introduction", H2))
    story.append(Paragraph(
        "Health insurers must price policies so that premiums cover the expected "
        "medical costs of each beneficiary. Understanding which personal attributes "
        "drive those costs helps an insurer set fair premiums, design wellness "
        "programmes and manage risk. This project analyses individual medical "
        "insurance charges billed in the United States and asks: <i>which factors "
        "(age, sex, BMI, number of children, smoking status, region) explain the "
        "variation in charges, and by how much?</i>", BODY))
    story.append(Paragraph(
        "The analysis is carried out in Python with three core libraries: "
        "<b>Pandas</b> for loading, cleaning, grouping and reshaping the data; "
        "<b>NumPy</b> for vectorised statistics, correlation and a least-squares "
        "regression; and <b>Matplotlib</b> for visual storytelling.", BODY))
    story.append(Paragraph("1.2 Data source", H2))
    story.append(Paragraph(
        "<b>Dataset:</b> Medical Cost Personal Datasets, published on Kaggle by "
        "Miri Choi (https://www.kaggle.com/datasets/mirichoi0218/insurance). "
        "The data originates from the book <i>Machine Learning with R</i> by Brett "
        "Lantz and is simulated from U.S. Census Bureau demographic statistics. "
        "It is a secondary data source in CSV format (insurance.csv).", BODY))
    story.append(Paragraph("1.3 Data description", H2))
    story.append(Paragraph(
        "The file has <b>1,338 rows</b> (one per insured person) and <b>7 columns</b>: "
        "3 categorical and 4 numerical variables, which meets the requirement of at "
        "least 510 rows with both variable types.", BODY))
    story.append(Spacer(1, 6))
    rows = [["Variable", "Type", "Description"],
            ["age", "Numerical (int)", "Age of the primary beneficiary (18-64 years)"],
            ["sex", "Categorical", "Gender of the policy holder (male / female)"],
            ["bmi", "Numerical (float)", "Body mass index, kg/m² (ideal 18.5-24.9)"],
            ["children", "Numerical (int)", "Number of children / dependents covered (0-5)"],
            ["smoker", "Categorical", "Whether the beneficiary smokes (yes / no)"],
            ["region", "Categorical", "U.S. residential area: northeast, northwest, "
                                      "southeast, southwest"],
            ["charges", "Numerical (float)", "Individual medical costs billed by health "
                                             "insurance (USD) - target variable"]]
    rows = [[Paragraph(c, BODY) for c in r] for r in rows]
    table = Table(rows, colWidths=[2.6 * cm, 3.4 * cm, CONTENT_W - 6 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#bee3f8")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e0")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(table)
    story.append(Paragraph("1.4 Objectives", H2))
    for o in ["Profile and clean the dataset (types, missing values, duplicates).",
              "Compare charges across smoker, sex, region, age and BMI groups.",
              "Quantify the distribution, skewness and outliers of charges.",
              "Measure correlation of each factor with charges and fit a linear model.",
              "Visualise the key relationships and derive business recommendations."]:
        story.append(Paragraph(f"• {o}", BODY))
    story.append(PageBreak())


def chapter_2(story):
    story.append(Paragraph("Chapter 2: Data Analysis using Python", H1))
    story.append(Paragraph(
        "All code is in <b>insurance_analysis.py</b>. Each application below shows "
        "the code, the output produced when it runs, and the inference drawn.", BODY))

    story.append(Paragraph("Part 2.1: Pandas", H2))
    df, out = run(ia.pandas_1_load_and_profile)
    application(story, "Pandas Application 1 - Loading, profiling and cleaning",
                "Read the CSV, check data types, missing values and duplicates, "
                "convert text columns to categories and summarise the numbers.",
                ia.pandas_1_load_and_profile, "pd1", out,
                "The dataset is clean: no missing values and only <b>one duplicate "
                "row</b>, which was removed, leaving 1,337 records. The sample is "
                "balanced by sex (50.5% male) and region (~24-27% each), but only "
                "<b>20.5% are smokers</b>. Charges range from $1,122 to $63,770; the "
                "mean ($13,279) is far above the median ($9,386), a first sign that a "
                "small group of very expensive customers pulls the average up. "
                "The mean BMI of 30.7 means the average beneficiary is clinically obese.")

    _, out = run(ia.pandas_2_group_comparisons, df)
    application(story, "Pandas Application 2 - Group comparisons with groupby and pivot_table",
                "Compare count, mean, median and maximum charges by smoker, sex and "
                "region, and cross smoker with region in a pivot table.",
                ia.pandas_2_group_comparisons, "pd2", out,
                "Smoking is the dominant difference: smokers are charged "
                "<b>$32,050 on average vs $8,441</b> for non-smokers, about "
                "<b>3.8 times more</b>. Sex makes little difference (medians are "
                "almost identical: $9,378 vs $9,413). The southeast has the highest "
                "mean charge ($14,735), and the pivot table shows this is where the "
                "smoker premium is largest (4.3x), so regional differences are "
                "mainly about smoking and BMI, not the region itself.")

    df, out = run(ia.pandas_3_feature_engineering, df)
    application(story, "Pandas Application 3 - Feature engineering with pd.cut",
                "Group ages into bands and BMI into WHO categories, then "
                "cross-tabulate mean charges.",
                ia.pandas_3_feature_engineering, "pd3", out,
                "Over half of beneficiaries (706 of 1,337) are <b>obese</b> and only "
                "225 have a normal BMI. Charges rise steadily with age in both "
                "groups, e.g. non-smokers go from $4,427 (18-29) to $13,431 (50-64). "
                "The key finding is an <b>interaction</b>: obesity adds only about "
                "$900 for non-smokers, but for smokers it almost <b>doubles</b> the "
                "cost ($21,363 to $41,558). Obese smokers are the highest-risk "
                "segment.")

    story.append(Paragraph("Part 2.2: NumPy", H2))
    _, out = run(ia.numpy_1_distribution_statistics, df)
    application(story, "NumPy Application 1 - Distribution, outliers and skewness",
                "Use NumPy to compute central tendency, spread, IQR outliers and "
                "skewness, and test a log transform.",
                ia.numpy_1_distribution_statistics, "np1", out,
                "Charges are strongly <b>right-skewed</b> (skewness 1.51). 139 "
                "beneficiaries (10.4%) lie above the outlier fence of $34,525, and "
                "<b>97.8% of these outliers are smokers</b>, so the outliers are "
                "real high-risk customers, not data errors, and should be kept. "
                "Taking the log reduces skewness to -0.09 (nearly symmetric), which "
                "is useful if the data is later used in statistical models.")

    (cols, corr), out = run(ia.numpy_2_correlation, df)
    application(story, "NumPy Application 2 - Correlation matrix with np.corrcoef",
                "Encode smoker as 0/1, build a feature matrix with np.column_stack "
                "and measure Pearson correlation with charges.",
                ia.numpy_2_correlation, "np2", out,
                "Smoking has a <b>strong positive correlation (r = 0.79)</b> with "
                "charges, far above age (0.30) and BMI (0.20). Number of children "
                "has almost no linear link (0.07). The predictors are nearly "
                "uncorrelated with each other (all |r| &lt; 0.11), so each one "
                "contributes separate information and there is no multicollinearity "
                "problem for a regression model.")

    _, out = run(ia.numpy_3_linear_regression, df)
    application(story, "NumPy Application 3 - Multiple linear regression with np.linalg.lstsq",
                "Estimate how much each factor adds to charges using ordinary least "
                "squares solved with linear algebra, and make a prediction.",
                ia.numpy_3_linear_regression, "np3", out,
                "Four simple variables explain <b>75% of the variation</b> in charges "
                "(R² = 0.750). Holding other factors equal, each extra year of "
                "age adds about <b>$258</b>, each BMI point about <b>$322</b>, each "
                "child about $473, and being a smoker adds about <b>$23,810</b>. A "
                "40-year-old with BMI 30 and two children is predicted at $8,814 as a "
                "non-smoker but $32,625 as a smoker. The RMSE of about $6,059 shows "
                "the model misses the smoker-obesity interaction found in Pandas "
                "Application 3.")

    story.append(Paragraph("Part 2.3: Matplotlib", H2))
    run(ia.matplotlib_1_distribution, df)
    application(story, "Matplotlib Application 1 - Histograms of charges",
                "Visualise the shape of the charges distribution before and after a "
                "log transformation.",
                ia.matplotlib_1_distribution, "mpl1", "",
                "The left histogram confirms the NumPy result: most people are "
                "charged under $15,000 with a long right tail reaching $64,000, and "
                "the mean line sits well to the right of the median. The log-scale "
                "histogram is much more symmetric and shows <b>several peaks</b>, "
                "a hint that the data contains distinct customer groups.",
                figure=ia.FIG_DIR / "mpl_1_distribution.png")

    run(ia.matplotlib_2_scatter, df)
    application(story, "Matplotlib Application 2 - Scatter plots by smoking status",
                "Show how charges change with age and BMI and how smokers differ.",
                ia.matplotlib_2_scatter, "mpl2", "",
                "The age plot shows <b>three parallel bands</b>: a low band of "
                "non-smokers, a middle band mixing both groups and a top band of "
                "smokers only. Within every band charges rise linearly with age. "
                "The BMI plot reveals a clear break at <b>BMI 30</b>: smokers above "
                "it jump to $35,000-$50,000, while for non-smokers BMI has almost no "
                "effect. This confirms the smoker-obesity interaction visually.",
                figure=ia.FIG_DIR / "mpl_2_scatter.png")

    run(ia.matplotlib_3_groups_and_heatmap, df, cols, corr)
    application(story, "Matplotlib Application 3 - Grouped bar chart and correlation heatmap",
                "Compare mean charges by age group and smoking status, and display "
                "the NumPy correlation matrix as a heatmap.",
                ia.matplotlib_3_groups_and_heatmap, "mpl3", "",
                "In every age group smokers pay far more; the gap is widest in "
                "relative terms for the young (18-29: about 6x) and largest in "
                "absolute terms for the old (50-64: about $25,000). The heatmap "
                "summarises the whole story in one picture: the only dark cell "
                "linked to charges is <b>smoker (0.79)</b>, followed by age and BMI.",
                figure=ia.FIG_DIR / "mpl_3_groups_heatmap.png")


def chapter_3(story):
    story.append(Paragraph("Chapter 3: Conclusion", H1))
    story.append(Paragraph("3.1 Key findings", H2))
    for f in [
        "<b>Smoking is the single biggest cost driver.</b> Smokers are 20.5% of "
        "beneficiaries but are charged about 3.8 times more on average, account for "
        "almost all extreme-cost cases (97.8% of outliers), and add about $23,800 to "
        "the expected charge.",
        "<b>Age raises costs steadily.</b> Each extra year adds roughly $258; people "
        "aged 50-64 cost about three times as much as those aged 18-29.",
        "<b>BMI matters mainly for smokers.</b> Obesity nearly doubles a smoker's "
        "cost but barely changes a non-smoker's, a clear interaction effect.",
        "<b>Sex, region and number of children have little effect</b> once smoking "
        "is considered; the southeast's higher average reflects more smokers and "
        "higher BMI there.",
        "<b>A simple model works well.</b> A NumPy least-squares model with four "
        "variables explains 75% of the variation in charges.",
    ]:
        story.append(Paragraph(f"• {f}", BODY))
    story.append(Paragraph("3.2 The story in the data", H2))
    story.append(Paragraph(
        "The customers form three groups: a large low-cost group of non-smokers whose "
        "charges grow gently with age; a middle group of non-obese smokers (and some "
        "non-smokers with other health issues); and a small but very expensive group "
        "of obese smokers. Pandas showed the group differences, NumPy measured their "
        "size and statistical strength, and Matplotlib made the three-band pattern "
        "and the BMI-30 threshold easy to see.", BODY))
    story.append(Paragraph("3.3 Recommendations", H2))
    for r in [
        "Price policies on smoking status, age and BMI together, with an extra "
        "loading for the smoker + BMI 30 or above combination.",
        "Fund smoking-cessation and weight-management programmes: moving one "
        "obese smoker to non-smoker could save about $20,000-$30,000 a year.",
        "Do not base pricing on sex or region; they add little beyond smoking.",
        "Add a smoker x obesity interaction term (or use a log-scale model) to "
        "improve on the R² of 0.75.",
    ]:
        story.append(Paragraph(f"• {r}", BODY))
    story.append(Paragraph("3.4 Limitations", H2))
    story.append(Paragraph(
        "The dataset is simulated from census statistics, covers only 1,338 people "
        "and lacks medical history, income and plan type, so the findings describe "
        "associations, not causes, and should be checked on real claims data.", BODY))


def footer(canvas, doc):
    if doc.page == 1:
        return
    canvas.saveState()
    canvas.setFont("Helvetica", 8.5)
    canvas.setFillColor(colors.HexColor("#718096"))
    canvas.drawString(2 * cm, 1.2 * cm, TITLE_PAGE["data_heading"])
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Page {doc.page}")
    canvas.restoreState()


def main():
    doc = SimpleDocTemplate(str(OUT_PDF), pagesize=A4, leftMargin=2 * cm,
                            rightMargin=2 * cm, topMargin=1.8 * cm,
                            bottomMargin=1.8 * cm, title=TITLE_PAGE["data_heading"])
    story = []
    title_page(story)
    chapter_1(story)
    chapter_2(story)
    chapter_3(story)
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(f"Report written to {OUT_PDF}")


if __name__ == "__main__":
    main()
