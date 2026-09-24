// Builds the editable Word report: Telco_Churn_Report.docx
// Run make_images.py first, then:  node make_report.js
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell,
  HeadingLevel, AlignmentType, WidthType, ShadingType, BorderStyle, PageBreak,
  LevelFormat, Footer, PageNumber,
} = require("docx");

process.chdir(__dirname);

// ---------------------------------------------------------------- details --
const STUDENTS = [
  ["Rishiraj Saha", "26020845025"],
  ["Ritika Mondol", "26020845026"],
];
const FACULTY = "Prof. ____________";
const SUBJECT = "Programming for Data Science";
const INSTITUTE = "Symbiosis Institute of Business Management";
const DATE = "24 September 2026";

// --------------------------------------------------------------- inference --
const INFERENCE = {
  SETUP: "The dataset loaded without any problem. It has 7,043 rows and 33 columns, so it easily meets the minimum of 510 rows. Each row is one customer, and the columns include categorical data (gender, contract, payment method) as well as numerical data (tenure, monthly charges, CLTV).",
  PD1: "Only two columns had missing values. Total Charges had 11 blanks, and when we checked, all of them were customers with 0 months of tenure who had not been billed yet, so we replaced them with 0. Churn Reason had 5,174 blanks, which is the same as the number of customers who stayed, so those blanks make sense and we left them. On average a customer has been with the company for about 32 months and pays around $65 a month. The overall churn rate is 26.54%, so roughly 1 in every 4 customers left.",
  PD2: "Contract type makes the biggest difference. Customers on a month-to-month plan churned at 42.7%, while only 2.8% of two-year customers left. Fiber optic users churned at almost 42%, which is more than double the DSL rate. This was surprising because fiber is the premium service. Customers paying by electronic check also churned a lot more (45.3%) than those using automatic bank transfer or credit card (15 to 17%).",
  PD3: "The pivot table shows that new customers on month-to-month plans are the most likely to leave: more than half of them (51.4%) churned in their first year. None of the two-year contract customers left in their first 24 months. When we looked at the reasons, the single biggest one was the attitude of the support person (192 customers). However, if we add up all the competitor-related reasons (better speeds, more data, better offer, better devices), they come to more than 600 customers, so competition is the main problem overall.",
  NP1: "Customers who left were paying more. Their average monthly bill was $74.44, compared to $61.27 for customers who stayed, a gap of about $13. The median shows the same pattern ($79.65 vs $64.43). The retained group has a lower 25th percentile ($25.10) because many of them are on cheap phone-only plans. So higher monthly charges seem to go along with a higher chance of leaving.",
  NP2: "Tenure has the strongest link with churn among these columns (-0.35). The negative sign means that the longer someone stays, the less likely they are to leave. Monthly charges have a small positive link (0.19), which matches what we found in NumPy 1. Tenure and Total Charges are strongly related (0.83), but that is expected since total charges build up over time.",
  NP3: "We used np.where to put customers into High, Medium and Low risk groups based on their churn score. The High risk group really did leave: 92% of them churned, while nobody in the Low group did. So the score is useful for deciding who to contact first. The company is losing about $139,131 in monthly revenue because of churn. That is 30.5% of all monthly revenue, or about $1.67 million a year. The revenue share (30.5%) is higher than the customer share (26.5%) because the customers who leave usually pay more.",
  MPL1: "The pie chart shows the overall split of 73.5% stayed and 26.5% churned. The bar chart makes the effect of contract type very clear: the month-to-month bar is far taller than the other two. Moving customers to one-year or two-year contracts looks like the easiest way to cut churn.",
  MPL2: "In the histogram, a lot of the customers who stayed are around $20 a month, while churned customers are bunched between $70 and $105. That is the price range of fiber and streaming plans. The box plot shows that churned customers usually leave early. Their median tenure is only about 10 months, compared to about 38 months for customers who stayed.",
  MPL3: "The line chart shows churn is very high in the first few months (around 50 to 60%) and then keeps going down, reaching below 10% for customers who have been around for 5 to 6 years. The value at 0 months is 0% only because those customers joined very recently. The bar chart of reasons shows two main themes: problems with service or staff attitude, and better offers from competitors.",
};

// ----------------------------------------------------------------- helpers --
const FONT = "Calibri";
const PAGE_W = 11906, MARGIN = 1300;
const CONTENT_W = PAGE_W - 2 * MARGIN;          // DXA
const CONTENT_PX = Math.floor(CONTENT_W / 15);  // 1px = 15 DXA at 96 dpi

function pngSize(file) {
  const b = fs.readFileSync(file);
  return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) };
}

function image(file, maxScale) {
  const { w, h } = pngSize(file);
  const scale = Math.min(CONTENT_PX / w, maxScale);
  return new Paragraph({
    spacing: { after: 120 },
    children: [new ImageRun({
      type: "png", data: fs.readFileSync(file),
      transformation: { width: Math.round(w * scale), height: Math.round(h * scale) },
      altText: { title: path.basename(file), description: path.basename(file), name: path.basename(file) },
    })],
  });
}

const p = (text, opts = {}) => new Paragraph({
  spacing: { after: 140, line: 300 }, alignment: AlignmentType.JUSTIFIED, ...opts,
  children: Array.isArray(text) ? text : [new TextRun(text)],
});
const b = (t) => new TextRun({ text: t, bold: true });
const t = (s) => new TextRun(s);
const bullet = (children) => new Paragraph({
  numbering: { reference: "bullets", level: 0 }, spacing: { after: 80, line: 290 },
  children: typeof children === "string" ? [t(children)] : children,
});
const h1 = (s) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [t(s)] });
const h2 = (s) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [t(s)] });
const h3 = (s) => new Paragraph({ heading: HeadingLevel.HEADING_3, children: [t(s)] });
const label = (s) => new Paragraph({ spacing: { before: 80, after: 60 },
  children: [new TextRun({ text: s, bold: true, color: "555555", size: 20 })] });
const pageBreak = () => new Paragraph({ children: [new PageBreak()] });

const border = { style: BorderStyle.SINGLE, size: 4, color: "BFC8D6" };
const borders = { top: border, bottom: border, left: border, right: border };

function table(rows, widths, { header = true, firstColBold = false } = {}) {
  const total = widths.reduce((a, c) => a + c, 0);
  return new Table({
    width: { size: total, type: WidthType.DXA },
    columnWidths: widths,
    rows: rows.map((row, r) => new TableRow({
      tableHeader: header && r === 0,
      children: row.map((cell, c) => new TableCell({
        borders,
        width: { size: widths[c], type: WidthType.DXA },
        margins: { top: 70, bottom: 70, left: 110, right: 110 },
        shading: header && r === 0 ? { fill: "1F3A5F", type: ShadingType.CLEAR, color: "auto" }
          : (firstColBold && c === 0) ? { fill: "E8EEF6", type: ShadingType.CLEAR, color: "auto" }
          : undefined,
        children: [new Paragraph({ children: [new TextRun({
          text: cell, size: 20,
          bold: (header && r === 0) || (firstColBold && c === 0),
          color: header && r === 0 ? "FFFFFF" : "000000",
        })] })],
      })),
    })),
  });
}

function inference(id) {
  return new Paragraph({
    spacing: { before: 120, after: 280, line: 300 },
    alignment: AlignmentType.JUSTIFIED,
    shading: { fill: "F1F5FB", type: ShadingType.CLEAR, color: "auto" },
    border: { left: { style: BorderStyle.SINGLE, size: 18, color: "4C78A8", space: 6 } },
    children: [b("Inference: "), t(INFERENCE[id])],
  });
}

// ------------------------------------------------------------------ content --
const manifest = JSON.parse(fs.readFileSync("images/manifest.json"));
const children = [];

// Title page
children.push(
  new Paragraph({ spacing: { before: 1800, after: 200 }, alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: SUBJECT.toUpperCase(), size: 24, color: "4C78A8", bold: true })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 160 },
    children: [new TextRun({ text: "Telco Customer Churn Analysis", size: 52, bold: true, color: "1F3A5F" })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 1200 },
    children: [new TextRun({ text: "Data Analysis using Pandas, NumPy and Matplotlib", size: 26, color: "444444" })] }),
  table([
    ["Data heading", "IBM Telco Customer Churn Dataset (7,043 customers)"],
    ["Subject", SUBJECT],
    ["Faculty", FACULTY],
    ["Student 1", `${STUDENTS[0][0]}    PRN: ${STUDENTS[0][1]}`],
    ["Student 2", `${STUDENTS[1][0]}    PRN: ${STUDENTS[1][1]}`],
    ["Institute", INSTITUTE],
    ["Date of submission", DATE],
  ], [2600, CONTENT_W - 2600], { header: false, firstColBold: true }),
  pageBreak(),
);

// Chapter 1
children.push(
  h1("Chapter 1: Introduction and Data Description"),
  h2("1.1 Introduction"),
  p("Customer churn means customers stopping their service and leaving a company. For telecom companies this is a big problem, because getting a new customer usually costs a lot more than keeping an existing one. When a customer leaves, the company also loses all the monthly payments that customer would have made in the future."),
  p("In this project we looked at data from a telecom company to understand which customers are leaving, when they leave, and why. We used Python for the full analysis. Pandas was used to load, clean and summarise the data, NumPy for calculations like averages, percentiles and correlation, and Matplotlib to make charts. For each part we have shown the code, the output we got, and what we understood from it."),
  h2("1.2 Objectives"),
  bullet("To find out what percentage of customers left the company and how much revenue was lost."),
  bullet("To see which types of customers (by contract, internet service and payment method) churn the most."),
  bullet("To check how churn changes with tenure, meaning how long the customer has been with the company."),
  bullet("To look at the main reasons customers gave for leaving and suggest ways to reduce churn."),
  h2("1.3 About the Dataset"),
  p([t("We used the "), b("Telco Customer Churn"), t(" dataset created by IBM. We downloaded it from Kaggle (kaggle.com/datasets/ylchang/telco-customer-churn-1113). It is about a made-up telecom company in California, USA, and has one row for each customer. The file we used is Telco_customer_churn.xlsx.")]),
  table([
    ["Detail", "Value"],
    ["Number of rows", "7,043 customers"],
    ["Number of columns", "33"],
    ["Categorical columns", "Gender, Partner, Contract, Internet Service, Payment Method, Churn Label, etc."],
    ["Numerical columns", "Tenure Months, Monthly Charges, Total Charges, CLTV, Churn Score"],
    ["Target column", "Churn Value (1 = customer left, 0 = customer stayed)"],
    ["Source", "IBM sample data, available on Kaggle"],
  ], [2600, CONTENT_W - 2600]),
  pageBreak(),
  h2("1.4 Important Columns"),
  table([
    ["Column", "Type", "What it means"],
    ["CustomerID", "Text", "Unique ID of each customer"],
    ["City, Zip Code", "Categorical", "Where the customer lives"],
    ["Gender, Senior Citizen, Partner, Dependents", "Categorical", "Basic details about the customer"],
    ["Tenure Months", "Numerical", "How many months the customer has been with the company"],
    ["Phone Service, Multiple Lines", "Categorical", "Phone plan details"],
    ["Internet Service", "Categorical", "DSL, Fiber optic or no internet"],
    ["Online Security, Tech Support, etc.", "Categorical", "Extra services taken by the customer"],
    ["Contract", "Categorical", "Month-to-month, One year or Two year"],
    ["Payment Method", "Categorical", "How the customer pays the bill"],
    ["Monthly Charges", "Numerical", "Current monthly bill in dollars"],
    ["Total Charges", "Numerical", "Total amount paid till now"],
    ["Churn Value / Churn Label", "Numerical / Categorical", "Whether the customer left (1 / Yes) or not (0 / No)"],
    ["Churn Score", "Numerical", "A score from 0 to 100 given by IBM showing chance of leaving"],
    ["CLTV", "Numerical", "Customer Lifetime Value, i.e. expected value of the customer"],
    ["Churn Reason", "Categorical", "The reason given by the customer for leaving"],
  ], [3300, 2000, CONTENT_W - 5300]),
  h2("1.5 Tools Used"),
  p("We used Python 3 with three libraries: Pandas, NumPy and Matplotlib. The code was written as a single Python file (telco_churn_analysis.py) and divided into small parts, one for each application."),
  pageBreak(),
);

// Chapter 2
const SECTION = {
  PD1: "2.1 Pandas: Three Applications",
  NP1: "2.2 NumPy: Three Applications",
  MPL1: "2.3 Matplotlib: Three Applications",
};
children.push(h1("Chapter 2: Data Analysis using Python"));
let fig = 1;
manifest.forEach((item, i) => {
  if (SECTION[item.id]) {
    if (item.id !== "PD1") children.push(pageBreak());
    children.push(h2(SECTION[item.id]));
  }
  children.push(h3(item.id === "SETUP" ? "Getting Started: Importing Libraries and Loading the Data" : item.title));
  children.push(label("Code"), image(item.code, 0.72));
  if (item.output) children.push(label("Output"), image(item.output, 0.72));
  if (item.chart) {
    children.push(label("Chart"), image(item.chart, 1));
    children.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 },
      children: [new TextRun({ text: `Figure ${fig++}: ${item.title.split(" - ")[1]}`, italics: true, size: 19, color: "555555" })] }));
  }
  children.push(inference(item.id));
});

// Chapter 3
children.push(
  pageBreak(),
  h1("Chapter 3: Conclusion"),
  h2("3.1 What the Data Tells Us"),
  p("About one out of every four customers (26.5%) left the company. The customers who left were paying more than average, so the company lost 30.5% of its monthly revenue, which comes to around $1.67 million a year. The churn is not spread evenly across customers. Most of it comes from a few clear groups, as shown in the table below."),
  table([
    ["Factor", "Churns the most", "Churns the least"],
    ["Contract", "Month-to-month (42.7%)", "Two year (2.8%)"],
    ["Tenure", "First 12 months (47.4%)", "49 to 72 months (9.5%)"],
    ["Internet service", "Fiber optic (41.9%)", "No internet (7.4%)"],
    ["Payment method", "Electronic check (45.3%)", "Credit card, automatic (15.2%)"],
    ["Monthly charges", "Churned: $74.44 on average", "Stayed: $61.27 on average"],
  ], [2400, (CONTENT_W - 2400) / 2, (CONTENT_W - 2400) / 2]),
  h2("3.2 Key Findings"),
  bullet([b("Contract type matters the most. "), t("Customers on longer contracts hardly ever leave, even when they are new.")]),
  bullet([b("The first year is the riskiest time. "), t("Churn is highest in the first few months and keeps falling as customers stay longer. Most customers who leave do so within about 10 months.")]),
  bullet([b("Fiber optic customers are not happy. "), t("They pay the most but churn twice as much as DSL users. Many customers also said competitors offered better speed or more data.")]),
  bullet([b("Payment method is linked to churn. "), t("People paying by electronic check leave about three times more often than people on automatic payments.")]),
  bullet([b("Customer service is a real issue. "), t("The single most common reason for leaving was the attitude of the support person.")]),
  bullet([b("Churn can be predicted. "), t("The churn score correctly picks out a high risk group where 92% of customers left.")]),
  h2("3.3 Suggestions"),
  bullet("Give discounts or small rewards to customers who move from month-to-month to a one-year or two-year contract."),
  bullet("Pay extra attention to new customers in their first 3 to 6 months, for example with welcome calls and help with setup."),
  bullet("Compare fiber prices and speeds with competitors, and think about adding free extras like online security or tech support."),
  bullet("Encourage customers to switch to automatic payments by offering a small discount on the bill."),
  bullet("Train support staff better and track customer satisfaction regularly."),
  bullet("Use the churn score to contact high risk customers before they decide to leave."),
  h2("3.4 Limitations"),
  p("This dataset is from a made-up company and only covers one quarter in one US state, so the results may not exactly match a real company. Also, our analysis shows which things are linked to churn, but it does not prove that they cause it. In the future, a machine learning model could be built on this data to predict churn more accurately."),
);

// ------------------------------------------------------------------ document --
const doc = new Document({
  creator: STUDENTS.map((s) => s[0]).join(", "),
  title: "Telco Customer Churn Analysis",
  styles: {
    default: { document: { run: { font: FONT, size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 34, bold: true, color: "1F3A5F", font: FONT },
        paragraph: { spacing: { before: 120, after: 240 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 27, bold: true, color: "1F3A5F", font: FONT },
        paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 23, bold: true, italics: true, color: "333333", font: FONT },
        paragraph: { spacing: { before: 200, after: 80 }, outlineLevel: 2, keepNext: true } },
    ],
  },
  numbering: { config: [{ reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•",
    alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 270 } } } }] }] },
  sections: [{
    properties: { page: { size: { width: PAGE_W, height: 16838 },
      margin: { top: 1200, bottom: 1200, left: MARGIN, right: MARGIN } }, titlePage: true },
    footers: {
      default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.RIGHT,
        children: [new TextRun({ text: "Telco Customer Churn Analysis  |  Page ", size: 17, color: "777777" }),
          new TextRun({ children: [PageNumber.CURRENT], size: 17, color: "777777" })] })] }),
      first: new Footer({ children: [new Paragraph("")] }),
    },
    children,
  }],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync("Telco_Churn_Report.docx", buf);
  console.log("Wrote Telco_Churn_Report.docx");
});
