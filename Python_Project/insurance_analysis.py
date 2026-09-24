"""Medical Insurance Cost - Data analysis using Python (Pandas, NumPy, Matplotlib).

Dataset : Medical Cost Personal Datasets (Kaggle, mirichoi0218)
          https://www.kaggle.com/datasets/mirichoi0218/insurance
File    : Python_Project/data/insurance.csv  (1,338 rows x 7 columns)

Run:
    python Python_Project/insurance_analysis.py
Each application prints its result; the Matplotlib applications save figures
in Python_Project/figures/.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
DATA_FILE = HERE / "data" / "insurance.csv"
FIG_DIR = HERE / "figures"
FIG_DIR.mkdir(exist_ok=True)

pd.set_option("display.width", 110)
pd.set_option("display.max_columns", 12)
NON_SMOKER, SMOKER = "#2b6cb0", "#dd6b20"


# --------------------------------------------------------------------------
# Part 2.1 - Pandas
# --------------------------------------------------------------------------
def pandas_1_load_and_profile():
    """Load the Kaggle CSV, profile its structure and clean it."""
    df = pd.read_csv(DATA_FILE)
    print("Shape (rows, columns):", df.shape)
    print("Data types:", dict(df.dtypes.astype(str)))
    print("Missing values (total)   :", df.isna().sum().sum())
    print("Duplicate rows found     :", df.duplicated().sum())
    df = df.drop_duplicates().reset_index(drop=True)
    print("Shape after cleaning     :", df.shape)

    for col in ["sex", "smoker", "region"]:
        df[col] = df[col].astype("category")
        share = df[col].value_counts(normalize=True).mul(100).round(1)
        print(f"{col:<7} distribution (%):", share.to_dict())

    print("\nSummary statistics of numerical variables:")
    print(df.describe().round(2))
    return df


def pandas_2_group_comparisons(df):
    """Compare insurance charges across smoker, sex and region groups."""
    for col in ["smoker", "sex", "region"]:
        summary = (df.groupby(col, observed=True)["charges"]
                     .agg(["count", "mean", "median", "max"])
                     .sort_values("mean", ascending=False)
                     .round(0))
        print(f"\n--- Charges by {col} ---")
        print(summary)

    pivot = pd.pivot_table(df, values="charges", index="region",
                           columns="smoker", aggfunc="mean", observed=True)
    pivot["smoker / non-smoker"] = pivot["yes"] / pivot["no"]
    print("\nMean charges: region x smoker")
    print(pivot.round(1))


def pandas_3_feature_engineering(df):
    """Create age groups and WHO BMI categories, then cross-tabulate."""
    df["age_group"] = pd.cut(df["age"], bins=[17, 29, 39, 49, 64],
                             labels=["18-29", "30-39", "40-49", "50-64"])
    df["bmi_class"] = pd.cut(df["bmi"], bins=[0, 18.5, 25, 30, 100],
                             labels=["Underweight", "Normal", "Overweight", "Obese"],
                             right=False)

    print("Customers per BMI class:")
    print(df["bmi_class"].value_counts().sort_index().to_string())

    table = pd.pivot_table(df, values="charges", index="age_group",
                           columns="smoker", aggfunc="mean", observed=True).round(0)
    print("\nMean charges by age group and smoking status:")
    print(table)

    obese_smoker = (df.assign(obese=df["bmi_class"] == "Obese")
                      .groupby(["smoker", "obese"], observed=True)["charges"]
                      .mean().unstack().round(0))
    print("\nMean charges: smoker x obese (BMI >= 30)")
    print(obese_smoker)
    return df


# --------------------------------------------------------------------------
# Part 2.2 - NumPy
# --------------------------------------------------------------------------
def numpy_1_distribution_statistics(df):
    """Describe the charges distribution and fix its skew with a log transform."""
    charges = df["charges"].to_numpy()

    def skewness(x):
        return np.mean((x - x.mean()) ** 3) / np.std(x) ** 3

    q1, med, q3 = np.percentile(charges, [25, 50, 75])
    iqr = q3 - q1
    upper = q3 + 1.5 * iqr
    print(f"Mean   = {np.mean(charges):10.2f}   Median = {med:10.2f}")
    print(f"Std    = {np.std(charges, ddof=1):10.2f}   IQR    = {iqr:10.2f}")
    print(f"Upper outlier fence (Q3 + 1.5*IQR) = {upper:.2f}")
    outliers = charges[charges > upper]
    print(f"Outliers: {outliers.size} ({outliers.size / charges.size:.1%} of rows)")

    smoker = df["smoker"].to_numpy() == "yes"
    print(f"Share of outliers who smoke: {np.mean(smoker[charges > upper]):.1%}")

    log_charges = np.log(charges)
    print(f"\nSkewness of charges     : {skewness(charges):.3f}")
    print(f"Skewness of log(charges): {skewness(log_charges):.3f}")


def numpy_2_correlation(df):
    """Pearson correlation matrix with np.corrcoef (smoker encoded as 0/1)."""
    cols = ["age", "bmi", "children", "smoker", "charges"]
    X = np.column_stack([
        df["age"].to_numpy(float),
        df["bmi"].to_numpy(float),
        df["children"].to_numpy(float),
        np.where(df["smoker"].to_numpy() == "yes", 1.0, 0.0),
        df["charges"].to_numpy(float),
    ])
    corr = np.corrcoef(X, rowvar=False)
    print("Correlation matrix:")
    print(pd.DataFrame(corr, index=cols, columns=cols).round(3))

    with_charges = corr[:-1, -1]
    print("\nVariables ranked by |r| with charges:")
    for i in np.argsort(-np.abs(with_charges)):
        print(f"  {cols[i]:<9} r = {with_charges[i]:+.3f}")
    return cols, corr


def numpy_3_linear_regression(df):
    """Fit charges = b0 + b1*age + b2*bmi + b3*children + b4*smoker by least squares."""
    X = np.column_stack([
        np.ones(len(df)),
        df["age"].to_numpy(float),
        df["bmi"].to_numpy(float),
        df["children"].to_numpy(float),
        (df["smoker"].to_numpy() == "yes").astype(float),
    ])
    y = df["charges"].to_numpy(float)

    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    y_hat = X @ beta
    r2 = 1 - np.sum((y - y_hat) ** 2) / np.sum((y - y.mean()) ** 2)
    rmse = np.sqrt(np.mean((y - y_hat) ** 2))

    names = ["intercept", "age", "bmi", "children", "smoker"]
    print("Estimated coefficients:")
    for n, b in zip(names, beta):
        print(f"  {n:<10} {b:12.2f}")
    print(f"\nR-squared = {r2:.3f}   RMSE = {rmse:.2f}")

    profile = np.array([1, 40, 30, 2, 0])
    print(f"Predicted charge, 40y, BMI 30, 2 kids, non-smoker: {profile @ beta:9.2f}")
    profile[-1] = 1
    print(f"Predicted charge, same person but a smoker       : {profile @ beta:9.2f}")


# --------------------------------------------------------------------------
# Part 2.3 - Matplotlib
# --------------------------------------------------------------------------
def matplotlib_1_distribution(df):
    """Histogram of charges (raw and log scale) with mean/median lines."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))
    charges = df["charges"]

    ax1.hist(charges, bins=40, color=NON_SMOKER, edgecolor="white")
    ax1.axvline(charges.mean(), color=SMOKER, ls="--",
                label=f"Mean {charges.mean():,.0f}")
    ax1.axvline(charges.median(), color="black", ls=":",
                label=f"Median {charges.median():,.0f}")
    ax1.set_title("Distribution of insurance charges")
    ax1.set_xlabel("Charges (USD)")
    ax1.set_ylabel("Number of beneficiaries")
    ax1.legend()

    ax2.hist(np.log(charges), bins=40, color="#38a169", edgecolor="white")
    ax2.set_title("Distribution of log(charges)")
    ax2.set_xlabel("log(charges)")
    for ax in (ax1, ax2):
        ax.spines[["top", "right"]].set_visible(False)

    fig.tight_layout()
    fig.savefig(FIG_DIR / "mpl_1_distribution.png", dpi=150)
    plt.close(fig)


def matplotlib_2_scatter(df):
    """Scatter plots of charges against age and BMI, coloured by smoking status."""
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), sharey=True)
    for ax, col in zip(axes, ["age", "bmi"]):
        for flag, color, name in [("no", NON_SMOKER, "Non-smoker"),
                                  ("yes", SMOKER, "Smoker")]:
            part = df[df["smoker"] == flag]
            ax.scatter(part[col], part["charges"], s=12, alpha=0.6,
                       color=color, label=name)
        ax.set_xlabel(col.upper() if col == "bmi" else col.title())
        ax.set_title(f"Charges vs {col.upper() if col == 'bmi' else col}")
        ax.spines[["top", "right"]].set_visible(False)
    axes[1].axvline(30, color="grey", ls="--", lw=1)
    axes[1].text(30.5, 60000, "BMI 30 (obese)", color="grey", fontsize=9)
    axes[0].set_ylabel("Charges (USD)")
    axes[0].legend()

    fig.tight_layout()
    fig.savefig(FIG_DIR / "mpl_2_scatter.png", dpi=150)
    plt.close(fig)


def matplotlib_3_groups_and_heatmap(df, cols, corr):
    """Grouped bar chart by age group x smoker and a correlation heatmap."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.8))

    table = df.pivot_table(values="charges", index="age_group",
                           columns="smoker", aggfunc="mean", observed=True)
    x = np.arange(len(table.index))
    w = 0.38
    ax1.bar(x - w / 2, table["no"], w, color=NON_SMOKER, label="Non-smoker")
    ax1.bar(x + w / 2, table["yes"], w, color=SMOKER, label="Smoker")
    ax1.set_xticks(x, table.index)
    ax1.set_xlabel("Age group")
    ax1.set_ylabel("Mean charges (USD)")
    ax1.set_title("Mean charges by age group and smoking")
    ax1.spines[["top", "right"]].set_visible(False)
    ax1.legend()

    im = ax2.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
    ax2.set_xticks(range(len(cols)), cols, rotation=45, ha="right")
    ax2.set_yticks(range(len(cols)), cols)
    for i in range(len(cols)):
        for j in range(len(cols)):
            ax2.text(j, i, f"{corr[i, j]:.2f}", ha="center", va="center",
                     fontsize=9, color="white" if abs(corr[i, j]) > 0.6 else "black")
    fig.colorbar(im, ax=ax2, shrink=0.85)
    ax2.set_title("Correlation heatmap")

    fig.tight_layout()
    fig.savefig(FIG_DIR / "mpl_3_groups_heatmap.png", dpi=150)
    plt.close(fig)


def main():
    df = pandas_1_load_and_profile()
    pandas_2_group_comparisons(df)
    df = pandas_3_feature_engineering(df)
    numpy_1_distribution_statistics(df)
    cols, corr = numpy_2_correlation(df)
    numpy_3_linear_regression(df)
    matplotlib_1_distribution(df)
    matplotlib_2_scatter(df)
    matplotlib_3_groups_and_heatmap(df, cols, corr)
    print(f"\nFigures saved to {FIG_DIR}")


if __name__ == "__main__":
    main()
