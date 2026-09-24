# Telco Customer Churn: Data Analysis using Python

Project for **Programming for Data Science**. It analyses the IBM Telco Customer Churn dataset
(`../DataSet/Telco_customer_churn.xlsx`, 7,043 rows x 33 columns, with categorical and numerical variables)
using Pandas, NumPy and Matplotlib.

## Deliverable

**[`outputs/Telco_Churn_Python_Report.pdf`](outputs/Telco_Churn_Python_Report.pdf)**. It contains:

| Section | Content |
|---|---|
| Title page | Names, PRNs, faculty, data heading, subject |
| Chapter 1 | Introduction, objectives, data source, data dictionary |
| Chapter 2.1 | Pandas: cleaning and describe; groupby churn summaries; `pd.cut` + pivot table + churn reasons |
| Chapter 2.2 | NumPy: descriptive statistics + Welch t-test; correlation matrix; `np.where` risk segmentation and revenue at risk |
| Chapter 2.3 | Matplotlib: donut + bar by contract; histogram + box plot; tenure trend line + churn-reason bars |
| Chapter 3 | Conclusion, key findings, recommendations, limitations |

Every application appears as a **code image, then its output, then an inference**.

## Files

- `telco_churn_analysis.py`: all analysis code, split into cells (`# %% [ID] Title`)
- `build_report.py`: runs each cell, renders code and output images, and builds the PDF
- `outputs/figures/`: Matplotlib charts
- `outputs/code_images/`: code and output images used in the report

## Reproduce

```bash
pip install -r requirements.txt
python telco_churn_analysis.py   # run the analysis only
python build_report.py           # regenerate the PDF report
```

Before submitting, fill in the student names, PRNs and faculty name in `STUDENT_DETAILS` / `FACULTY` at the top of
`build_report.py`, then rebuild.
