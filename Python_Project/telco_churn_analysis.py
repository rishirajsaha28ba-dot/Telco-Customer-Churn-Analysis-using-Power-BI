"""
Telco Customer Churn - Data Analysis using Python (Pandas, NumPy, Matplotlib)

Dataset : IBM Telco Customer Churn (11.1.3+), DataSet/Telco_customer_churn.xlsx
Rows    : 7,043 customers x 33 columns (categorical + numerical)

The script is split into cells ("# %% [ID] Title"). build_report.py executes
each cell in order and places its code, output and inference into the report.
Run it directly with:  python telco_churn_analysis.py
"""

# %% [SETUP] Imports and data loading
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

BASE = Path(__file__).resolve().parent
DATA = BASE.parent / "DataSet" / "Telco_customer_churn.xlsx"
FIG_DIR = BASE / "outputs" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_excel(DATA)
print("Shape:", df.shape)
print(df.dtypes.value_counts().to_string())

# %% [PD1] Pandas 1 - Data inspection and cleaning
# 'Total Charges' is stored as text: blank strings for brand-new customers
df["Total Charges"] = pd.to_numeric(df["Total Charges"], errors="coerce")
print("Missing values per column (non-zero only):")
print(df.isna().sum()[lambda s: s > 0].to_string())

# New customers (tenure 0) have not been billed yet -> total charges = 0
df["Total Charges"] = df["Total Charges"].fillna(0)
# Drop columns that carry no analytical information
df = df.drop(columns=["Count", "Country", "State", "Lat Long"])

num_cols = ["Tenure Months", "Monthly Charges", "Total Charges",
            "CLTV", "Churn Score"]
print("\nCleaned shape:", df.shape)
print(df[num_cols].describe().round(2).to_string())
print("\nOverall churn rate: {:.2%}".format(df["Churn Value"].mean()))

# %% [PD2] Pandas 2 - Churn rate by contract, internet service and payment method
def churn_summary(col):
    return (df.groupby(col)
              .agg(Customers=("CustomerID", "count"),
                   Churned=("Churn Value", "sum"),
                   Churn_Rate=("Churn Value", "mean"),
                   Avg_Monthly=("Monthly Charges", "mean"))
              .sort_values("Churn_Rate", ascending=False)
              .round(3))

for col in ["Contract", "Internet Service", "Payment Method"]:
    print(f"\n--- Churn by {col} ---")
    print(churn_summary(col).to_string())

# %% [PD3] Pandas 3 - Tenure bands, pivot table and churn reasons
bins = [0, 12, 24, 48, 72]
labels = ["0-12 m", "13-24 m", "25-48 m", "49-72 m"]
df["Tenure Band"] = pd.cut(df["Tenure Months"], bins=bins, labels=labels,
                           include_lowest=True)

pivot = pd.pivot_table(df, values="Churn Value", index="Tenure Band",
                       columns="Contract", aggfunc="mean", observed=True)
print("Churn rate by Tenure Band x Contract:")
print((pivot * 100).round(1).to_string())

print("\nTop 8 churn reasons (share of churned customers):")
reasons = (df.loc[df["Churn Value"] == 1, "Churn Reason"]
             .value_counts(normalize=True))
print((reasons.head(8) * 100).round(1).to_string())

# %% [NP1] NumPy 1 - Descriptive statistics and a Welch t-test on monthly charges
churned = df.loc[df["Churn Value"] == 1, "Monthly Charges"].to_numpy()
stayed = df.loc[df["Churn Value"] == 0, "Monthly Charges"].to_numpy()

for name, arr in [("Churned", churned), ("Retained", stayed)]:
    q1, med, q3 = np.percentile(arr, [25, 50, 75])
    print(f"{name:9s} n={arr.size:5d}  mean={np.mean(arr):6.2f}  "
          f"median={med:6.2f}  std={np.std(arr, ddof=1):5.2f}  IQR=[{q1:.2f}, {q3:.2f}]")

# Welch's t-statistic computed from first principles with NumPy
m1, m2 = churned.mean(), stayed.mean()
v1, v2 = churned.var(ddof=1), stayed.var(ddof=1)
t_stat = (m1 - m2) / np.sqrt(v1 / churned.size + v2 / stayed.size)
print(f"\nDifference in means: {m1 - m2:.2f} USD  |  Welch t = {t_stat:.2f}")

# %% [NP2] NumPy 2 - Correlation matrix of numerical drivers
corr_cols = ["Tenure Months", "Monthly Charges", "Total Charges",
             "CLTV", "Churn Score", "Churn Value"]
X = df[corr_cols].to_numpy(dtype=float)
corr = np.corrcoef(X, rowvar=False)

print(pd.DataFrame(corr, index=corr_cols, columns=corr_cols).round(2).to_string())
churn_corr = corr[-1, :-1]
order = np.argsort(-np.abs(churn_corr))
print("\nStrongest linear relationships with churn:")
for i in order:
    print(f"  {corr_cols[i]:16s} r = {churn_corr[i]:+.3f}")

# %% [NP3] NumPy 3 - Vectorised risk segmentation and revenue at risk
score = df["Churn Score"].to_numpy()
monthly = df["Monthly Charges"].to_numpy()
actual = df["Churn Value"].to_numpy()

segment = np.where(score >= 80, "High",
                   np.where(score >= 50, "Medium", "Low"))
print(f"{'Segment':8s}{'Customers':>10s}{'Actual churn':>14s}{'Monthly rev.':>14s}")
for seg in ["High", "Medium", "Low"]:
    mask = segment == seg
    print(f"{seg:8s}{mask.sum():10d}{actual[mask].mean():14.1%}"
          f"{monthly[mask].sum():14,.0f}")

lost_monthly = np.sum(monthly * actual)
at_risk = np.sum(monthly[(segment == "High") & (actual == 0)])
print(f"\nMonthly revenue lost to churn : ${lost_monthly:,.0f} "
      f"({lost_monthly / monthly.sum():.1%} of total)")
print(f"Annualised revenue lost       : ${lost_monthly * 12:,.0f}")
print(f"Retained but high-risk revenue: ${at_risk:,.0f} per month")

# %% [MPL1] Matplotlib 1 - Churn overview and churn rate by contract
fig, axes = plt.subplots(1, 2, figsize=(11, 4.3))
counts = df["Churn Label"].value_counts()
axes[0].pie(counts, labels=["Retained", "Churned"], autopct="%1.1f%%",
            colors=["#4C78A8", "#E45756"], startangle=90,
            wedgeprops=dict(width=0.45, edgecolor="white"))
axes[0].set_title("Overall customer churn")

rate = df.groupby("Contract")["Churn Value"].mean().sort_values() * 100
bars = axes[1].barh(rate.index, rate.values, color=["#72B7B2", "#F2CF5B", "#E45756"])
axes[1].bar_label(bars, fmt="%.1f%%", padding=3)
axes[1].set_xlabel("Churn rate (%)")
axes[1].set_title("Churn rate by contract type")
axes[1].set_xlim(0, 55)
axes[1].spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(FIG_DIR / "mpl1_churn_contract.png", dpi=160)
plt.close(fig)
print("Saved figure: mpl1_churn_contract.png")

# %% [MPL2] Matplotlib 2 - Distribution of monthly charges and tenure by churn
fig, axes = plt.subplots(1, 2, figsize=(11, 4.3))
bins = np.linspace(18, 120, 35)
axes[0].hist(stayed, bins=bins, alpha=0.65, label="Retained", color="#4C78A8", density=True)
axes[0].hist(churned, bins=bins, alpha=0.65, label="Churned", color="#E45756", density=True)
axes[0].set_xlabel("Monthly charges (USD)")
axes[0].set_ylabel("Density")
axes[0].set_title("Monthly charges: churned vs retained")
axes[0].legend(frameon=False)

groups = [df.loc[df["Churn Value"] == v, "Tenure Months"] for v in (0, 1)]
bp = axes[1].boxplot(groups, patch_artist=True, widths=0.5)
axes[1].set_xticks([1, 2], ["Retained", "Churned"])
for patch, c in zip(bp["boxes"], ["#4C78A8", "#E45756"]):
    patch.set_facecolor(c); patch.set_alpha(0.7)
axes[1].set_ylabel("Tenure (months)")
axes[1].set_title("Tenure distribution by churn status")
for ax in axes:
    ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(FIG_DIR / "mpl2_distributions.png", dpi=160)
plt.close(fig)
print("Saved figure: mpl2_distributions.png")

# %% [MPL3] Matplotlib 3 - Churn trend over tenure and top churn reasons
fig, axes = plt.subplots(1, 2, figsize=(12, 4.6), gridspec_kw={"width_ratios": [1, 1.25]})
trend = df.groupby("Tenure Months")["Churn Value"].mean() * 100
smooth = trend.rolling(6, center=True, min_periods=1).mean()
axes[0].scatter(trend.index, trend.values, s=10, color="#9D9D9D", label="Monthly value")
axes[0].plot(smooth.index, smooth.values, color="#E45756", lw=2.2, label="6-month rolling mean")
axes[0].set_xlabel("Tenure (months)")
axes[0].set_ylabel("Churn rate (%)")
axes[0].set_title("Churn rate falls as tenure grows")
axes[0].legend(frameon=False)

top = reasons.head(8).sort_values() * 100
axes[1].barh(top.index, top.values, color="#F58518")
for y, v in enumerate(top.values):
    axes[1].text(v + 0.3, y, f"{v:.1f}%", va="center", fontsize=9)
axes[1].set_xlabel("Share of churned customers (%)")
axes[1].set_title("Top churn reasons")
for ax in axes:
    ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(FIG_DIR / "mpl3_tenure_reasons.png", dpi=160)
plt.close(fig)
print("Saved figure: mpl3_tenure_reasons.png")
