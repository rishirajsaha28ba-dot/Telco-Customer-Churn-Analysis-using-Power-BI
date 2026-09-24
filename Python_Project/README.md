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
- Chapter 2: Pandas (loading and cleaning, group comparisons, feature engineering), NumPy (distribution and outliers, correlation, least-squares regression), Matplotlib (histograms, scatter plots, grouped bar chart and heatmap)
- Chapter 3: Conclusion: key findings, the story in the data, recommendations and limitations

## Key findings
- Smokers are charged about **3.8×** more ($32,050 vs $8,441 on average), and 97.8% of high-cost outliers are smokers.
- Smoking has the strongest correlation with charges (r = 0.79), followed by age (0.30) and BMI (0.20).
- Obesity nearly **doubles** a smoker's charges but barely changes a non-smoker's.
- A linear model using age, BMI, children and smoker explains **75%** of the variation in charges.
