# Medical Insurance Cost Analysis (Python)

Programming for Data Science project: data analysis using **Pandas**, **NumPy** and **Matplotlib**, with three applications of each library.

## Dataset
- **Medical Cost Personal Datasets** on Kaggle (mirichoi0218): https://www.kaggle.com/datasets/mirichoi0218/insurance
- `data/insurance.csv`: 1,338 rows × 7 columns
  - Categorical: `sex`, `smoker`, `region`
  - Numerical: `age`, `bmi`, `children`, `charges`

## Files
| File | Purpose |
|---|---|
| `insurance_analysis.py` | The nine applications (3 Pandas, 3 NumPy, 3 Matplotlib) |
| `build_report.py` | Runs the analysis and builds the PDF report (code image → result → inference) |
| `Insurance_Cost_Analysis_Report.pdf` | The submission report |
| `figures/` | Charts produced by the Matplotlib applications |

## Run
```bash
pip install -r requirements.txt
python insurance_analysis.py   # prints the results and saves the charts
python build_report.py         # rebuilds the PDF report
```
Before submitting, fill in the names, PRNs and faculty name in the `TITLE_PAGE` dictionary at the top of `build_report.py`, then rebuild the report.

## Report structure
- Title page: names, PRNs, faculty, dataset title, subject
- Chapter 1: Introduction and data description
- Chapter 2: Pandas (loading and cleaning, groupby, new columns with pd.cut), NumPy (basic statistics and outliers, correlation, a simple prediction model), Matplotlib (histogram, scatter plot, bar chart)
- Chapter 3: Conclusion: what we found, the story, suggestions and limitations

## Key findings
- Smokers are charged almost **4×** more ($32,050 vs $8,441 on average).
- Smoking has the strongest correlation with charges (r = 0.79), followed by age (0.30) and BMI (0.20).
- Obesity nearly **doubles** a smoker's charges but barely changes a non-smoker's.
- A simple model using age, BMI and smoking explains about **75%** of the variation in charges.
