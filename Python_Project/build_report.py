# Builds the PDF report: for each application -> code image, result, inference.
# Fill in TITLE_PAGE below, then run:  python build_report.py

import contextlib
import inspect
import io
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from pygments import highlight
from pygments.formatters import ImageFormatter
from pygments.lexers import PythonLexer
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (Image as RLImage, KeepTogether, PageBreak,
                                Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

import insurance_analysis as ia

TITLE_PAGE = {
    "students": [("Student 1 Name", "__________"), ("Student 2 Name", "__________")],
    "faculty": "Faculty Name",
    "subject": "Programming for Data Science",
    "title": "Medical Insurance Cost Analysis",
    "date": "24/09/2026",
}

HERE = Path(__file__).resolve().parent
IMG_DIR = HERE / "report_images"
IMG_DIR.mkdir(exist_ok=True)
OUT_PDF = HERE / "Insurance_Cost_Analysis_Report.pdf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
PAGE_W = A4[0] - 4 * cm

base = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=base["Heading1"], textColor=colors.HexColor("#1a365d"))
H2 = ParagraphStyle("H2", parent=base["Heading2"], textColor=colors.HexColor("#2b6cb0"))
H3 = ParagraphStyle("H3", parent=base["Heading3"])
BODY = ParagraphStyle("Body", parent=base["BodyText"], fontSize=11, leading=16)
LABEL = ParagraphStyle("Label", parent=BODY, fontName="Helvetica-Bold",
                       textColor=colors.HexColor("#4a5568"), spaceBefore=6)
NOTE = ParagraphStyle("Note", parent=BODY, backColor=colors.HexColor("#f0f7ff"),
                      borderPadding=7, spaceBefore=6)
CENTER = ParagraphStyle("Center", parent=BODY, alignment=1)


def code_image(func, name):
    fmt = ImageFormatter(font_name=MONO, font_size=16, line_numbers=False,
                         style="friendly", image_pad=16)
    path = IMG_DIR / f"{name}_code.png"
    path.write_bytes(highlight(inspect.getsource(func), PythonLexer(), fmt))
    return path


def output_image(text, name):
    font = ImageFont.truetype(MONO, 16)
    lines = text.rstrip().split("\n")
    width = max(int(font.getlength(line)) for line in lines) + 32
    img = Image.new("RGB", (max(width, 500), len(lines) * 21 + 32), "#1e1e1e")
    draw = ImageDraw.Draw(img)
    for i, line in enumerate(lines):
        draw.text((16, 16 + i * 21), line, font=font, fill="#e2e8f0")
    path = IMG_DIR / f"{name}_output.png"
    img.save(path)
    return path


def picture(path, max_w=PAGE_W, scale=0.5):
    w, h = Image.open(path).size
    s = min(scale, max_w / w)
    return RLImage(str(path), width=w * s, height=h * s)


def add_application(story, title, func, args, inference, figure=None):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        result_value = func(*args)
    name = func.__name__

    story.append(Paragraph(title, H3))
    story.append(Paragraph("Code", LABEL))
    story.append(picture(code_image(func, name)))
    result = [Paragraph("Result", LABEL)]
    if buf.getvalue().strip():
        result.append(picture(output_image(buf.getvalue(), name)))
    if figure:
        result.append(picture(ia.FIG_DIR / figure, max_w=14 * cm, scale=1))
    story.append(KeepTogether(result))
    story.append(KeepTogether([Paragraph("Inference", LABEL), Paragraph(inference, NOTE)]))
    story.append(PageBreak())
    return result_value


def bullets(story, items):
    for item in items:
        story.append(Paragraph("• " + item, BODY))


def title_page(story):
    t = TITLE_PAGE
    story.append(Spacer(1, 4 * cm))
    story.append(Paragraph(t["subject"], CENTER))
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(t["title"], ParagraphStyle(
        "T", parent=CENTER, fontSize=26, leading=32, fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1a365d"))))
    story.append(Spacer(1, 2 * cm))
    rows = [["Name", "PRN"]] + [list(s) for s in t["students"]]
    rows += [["Faculty", t["faculty"]], ["Subject", t["subject"]],
             ["Dataset", "Medical Cost Personal Datasets (Kaggle)"],
             ["Date", t["date"]]]
    table = Table(rows, colWidths=[6 * cm, 8 * cm])
    table.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONT", (0, 1), (0, -1), "Helvetica-Bold"),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#bee3f8")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(table)
    story.append(PageBreak())


def chapter_1(story):
    story.append(Paragraph("Chapter 1: Introduction and Data Description", H1))
    story.append(Paragraph("1.1 Introduction", H2))
    story.append(Paragraph(
        "Why do some people pay much more for health insurance than others? "
        "Insurance companies need to know this so they can set fair premiums. "
        "In this project we look at the medical bills of 1,338 people in the US "
        "and try to find out which things, like age, weight or smoking, make "
        "the bill go up.", BODY))
    story.append(Paragraph(
        "We use three Python libraries: Pandas to load and group the data, "
        "NumPy to do the calculations, and Matplotlib to draw the charts.", BODY))

    story.append(Paragraph("1.2 Where the data comes from", H2))
    story.append(Paragraph(
        "We took the <i>Medical Cost Personal Datasets</i> from Kaggle "
        "(kaggle.com/datasets/mirichoi0218/insurance). It is a single CSV file, "
        "insurance.csv. The data comes from the book <i>Machine Learning with R</i> "
        "and is based on US Census figures, so it is secondary data.", BODY))

    story.append(Paragraph("1.3 What is in the data", H2))
    story.append(Paragraph(
        "There are 1,338 rows (one per person) and 7 columns. Three columns are "
        "categorical and four are numerical.", BODY))
    story.append(Spacer(1, 6))
    rows = [["Column", "Type", "Meaning"],
            ["age", "Numerical", "Age of the person (18 to 64)"],
            ["sex", "Categorical", "male or female"],
            ["bmi", "Numerical", "Body mass index (30 or more means obese)"],
            ["children", "Numerical", "Number of children covered (0 to 5)"],
            ["smoker", "Categorical", "yes or no"],
            ["region", "Categorical", "northeast, northwest, southeast, southwest"],
            ["charges", "Numerical", "Medical cost billed by the insurer, in USD"]]
    table = Table(rows, colWidths=[3 * cm, 3.5 * cm, PAGE_W - 6.5 * cm])
    table.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#bee3f8")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(table)

    story.append(Paragraph("1.4 What we want to find out", H2))
    bullets(story, ["Is the data clean, and what does it look like?",
                    "Do smokers, men or women, or people in some regions pay more?",
                    "How much do age and BMI add to the bill?",
                    "Which factor matters the most?"])
    story.append(PageBreak())


def chapter_2(story):
    story.append(Paragraph("Chapter 2: Data Analysis using Python", H1))
    story.append(Paragraph(
        "All the code is in insurance_analysis.py. For each part we show the "
        "code, what it printed, and what we learned from it.", BODY))

    story.append(Paragraph("Part 2.1: Pandas", H2))
    df = add_application(story, "Application 1: Loading and cleaning the data",
                    ia.pandas_1_load_and_clean, (),
                    "The data is in good shape. There are no missing values and only one "
                    "duplicate row, which we removed, so we are left with 1,337 people. "
                    "About one in five people smoke (274 out of 1,337). The average bill is "
                    "$13,279, but the median is only $9,386. That gap tells us a few people "
                    "have very large bills that pull the average up.")

    add_application(story, "Application 2: Comparing groups with groupby",
                    ia.pandas_2_group_by, (df,),
                    "Smoking makes a huge difference. Smokers pay about $32,050 on average, "
                    "while non-smokers pay about $8,441, which is almost four times less. "
                    "Men pay a little more than women, and the southeast is a bit more "
                    "expensive than other regions, but these gaps are small compared with "
                    "the smoking gap.")

    add_application(story, "Application 3: Creating new columns with pd.cut",
                    ia.pandas_3_new_columns, (df,),
                    "Bills go up with age for everyone. A non-smoker aged 50-64 pays about "
                    "three times as much as one aged 18-29. More than half of the people "
                    "(706) are obese. Being obese hardly changes the bill for non-smokers "
                    "($7,977 vs $8,856), but for smokers it almost doubles it ($21,363 vs "
                    "$41,558). So smokers who are also obese are the most expensive group.")

    story.append(Paragraph("Part 2.2: NumPy", H2))
    add_application(story, "Application 1: Basic statistics and outliers",
                    ia.numpy_1_statistics, (df,),
                    "The mean ($13,279) is much higher than the median ($9,386), and the "
                    "standard deviation is about $12,100, so the bills are spread out a lot. "
                    "Using the usual rule (Q3 + 1.5 x IQR), 139 people are outliers with "
                    "bills above $34,525. We kept them, because these are real people with "
                    "high costs, not mistakes in the data.")

    add_application(story, "Application 2: Correlation with np.corrcoef",
                    ia.numpy_2_correlation, (df,),
                    "We turned smoker into 1 (yes) and 0 (no) so we could measure it. "
                    "Smoking has by far the strongest link with charges (0.79). Age comes "
                    "next (0.30), then BMI (0.20). The number of children has almost no "
                    "link (0.07).")

    add_application(story, "Application 3: A simple prediction model",
                    ia.numpy_3_regression, (df,),
                    "We fitted a straight-line model using age, BMI and smoking. It says "
                    "each extra year of age adds about $259, each BMI point adds about "
                    "$323, and smoking adds about $23,800. These three columns alone "
                    "explain about 75% of the differences in charges (R squared = 0.747), "
                    "which is quite good for such a simple model.")

    story.append(Paragraph("Part 2.3: Matplotlib", H2))
    add_application(story, "Application 1: Histogram of charges",
                    ia.matplotlib_1_histogram, (df,),
                    "Most people pay less than $15,000, but the chart has a long tail on the "
                    "right that goes past $60,000. The mean line sits to the right of the "
                    "median line because of those few big bills.",
                    figure="mpl_1_histogram.png")

    add_application(story, "Application 2: Scatter plot of charges vs age",
                    ia.matplotlib_2_scatter, (df,),
                    "This is the most useful chart. The dots form three bands. The bottom "
                    "band is almost all non-smokers, and the top band is only smokers. In "
                    "every band, the bill rises steadily as people get older.",
                    figure="mpl_2_scatter.png")

    add_application(story, "Application 3: Bar chart by age group",
                    ia.matplotlib_3_bar_chart, (df,),
                    "In every age group the orange bar (smokers) is far taller than the "
                    "blue bar (non-smokers). A young smoker pays more than twice what the "
                    "oldest non-smokers pay on average.",
                    figure="mpl_3_bar_chart.png")


def chapter_3(story):
    story.append(Paragraph("Chapter 3: Conclusion", H1))
    story.append(Paragraph("What we found", H2))
    bullets(story, [
        "Smoking is the biggest reason for high medical bills. Smokers pay almost "
        "four times more than non-smokers.",
        "Older people pay more. Each year of age adds about $259 to the bill.",
        "Being obese mostly hurts smokers. It nearly doubles their bill but barely "
        "changes a non-smoker's.",
        "Sex, region and number of children make only a small difference.",
    ])
    story.append(Paragraph("The story", H2))
    story.append(Paragraph(
        "If we had to guess someone's medical bill, the first question to ask is "
        "\"Do you smoke?\" The next questions would be their age and their weight. "
        "Put simply, a young non-smoker is cheap to insure, and an older, obese "
        "smoker is very expensive. Pandas helped us spot these groups, NumPy "
        "measured how big the effects are, and the Matplotlib charts made the "
        "pattern easy to see.", BODY))
    story.append(Paragraph("Suggestions for the insurer", H2))
    bullets(story, [
        "Price policies mainly on smoking, age and BMI.",
        "Offer programmes to help people quit smoking and lose weight. This is "
        "where the biggest savings are.",
        "Do not charge more based on sex or region.",
    ])
    story.append(Paragraph("Limitations", H2))
    story.append(Paragraph(
        "The data is simulated and has only 1,338 people. It has no medical history "
        "or income, so our results show links, not proof of cause.", BODY))


def footer(canvas, doc):
    if doc.page > 1:
        canvas.setFont("Helvetica", 9)
        canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Page {doc.page}")


def main():
    doc = SimpleDocTemplate(str(OUT_PDF), pagesize=A4, leftMargin=2 * cm,
                            rightMargin=2 * cm, topMargin=1.8 * cm,
                            bottomMargin=1.8 * cm, title=TITLE_PAGE["title"])
    story = []
    title_page(story)
    chapter_1(story)
    chapter_2(story)
    chapter_3(story)
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print("Report saved to", OUT_PDF)


if __name__ == "__main__":
    main()
