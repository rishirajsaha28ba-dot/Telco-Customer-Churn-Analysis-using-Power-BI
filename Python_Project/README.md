# Telco Customer Churn Analysis (Python)

Project for **Programming for Data Science**, by Rishiraj Saha (PRN 26020845025) and Ritika Mondol (PRN 26020845026).

Analysis of the IBM Telco Customer Churn dataset (`../DataSet/Telco_customer_churn.xlsx`, 7,043 rows) using
only **pandas, NumPy and Matplotlib**.

## Report

- `Telco_Churn_Report.docx`: editable Word report
- `Telco_Churn_Report.pdf`: the same report as a PDF

Contents: title page; Chapter 1 (introduction and data description); Chapter 2 (3 pandas, 3 NumPy and
3 Matplotlib applications, each with code, output and inference); Chapter 3 (conclusion).

## Files

- `telco_churn_analysis.py`: all the analysis code
- `make_images.py`: runs the code and saves the code, output and chart images to `images/`
- `make_report.js`: builds the Word report from those images (uses the `docx` npm package)

## Run the analysis

```bash
pip install pandas numpy matplotlib openpyxl
python telco_churn_analysis.py
```
