# Medical Insurance Cost Analysis
# Dataset: Medical Cost Personal Datasets (Kaggle)
# https://www.kaggle.com/datasets/mirichoi0218/insurance

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
pd.set_option("display.width", 100)


# ---------------- Pandas ----------------

def pandas_1_load_and_clean():
    df = pd.read_csv(DATA_FILE)
    print("Rows and columns:", df.shape)
    print("Missing values:", df.isnull().sum().sum())
    print("Duplicate rows:", df.duplicated().sum())

    df = df.drop_duplicates()
    print("Rows after removing duplicates:", len(df))

    print("\nSmokers:")
    print(df["smoker"].value_counts())
    print("\nSummary of numeric columns:")
    print(df.describe().round(1))
    return df


def pandas_2_group_by(df):
    print("Average charges by smoker:")
    print(df.groupby("smoker")["charges"].mean().round(0))

    print("\nAverage charges by sex:")
    print(df.groupby("sex")["charges"].mean().round(0))

    print("\nAverage charges by region:")
    print(df.groupby("region")["charges"].mean().round(0))


def pandas_3_new_columns(df):
    df["age_group"] = pd.cut(df["age"], bins=[17, 29, 39, 49, 64],
                             labels=["18-29", "30-39", "40-49", "50-64"])
    df["obese"] = df["bmi"] >= 30

    print("Number of obese people:", df["obese"].sum())
    print("\nAverage charges by age group and smoker:")
    print(df.pivot_table(values="charges", index="age_group",
                         columns="smoker", observed=True).round(0))
    print("\nAverage charges by obese and smoker:")
    print(df.pivot_table(values="charges", index="obese",
                         columns="smoker").round(0))
    return df


# ---------------- NumPy ----------------

def numpy_1_statistics(df):
    charges = df["charges"].to_numpy()

    print("Mean:  ", np.mean(charges).round(2))
    print("Median:", np.median(charges).round(2))
    print("Std:   ", np.std(charges).round(2))

    q1, q3 = np.percentile(charges, [25, 75])
    limit = q3 + 1.5 * (q3 - q1)
    outliers = charges[charges > limit]
    print("\nOutlier limit:", limit.round(2))
    print("Number of outliers:", len(outliers))


def numpy_2_correlation(df):
    smoker = np.where(df["smoker"] == "yes", 1, 0)
    data = np.array([df["age"], df["bmi"], df["children"], smoker, df["charges"]])
    names = ["age", "bmi", "children", "smoker", "charges"]

    corr = np.corrcoef(data)
    print("Correlation with charges:")
    for name, value in zip(names[:-1], corr[:-1, -1]):
        print(f"  {name:<9} {value:.2f}")
    return names, corr


def numpy_3_regression(df):
    smoker = np.where(df["smoker"] == "yes", 1, 0)
    X = np.column_stack([np.ones(len(df)), df["age"], df["bmi"], smoker])
    y = df["charges"].to_numpy()

    b = np.linalg.lstsq(X, y, rcond=None)[0]
    predicted = X @ b
    r2 = 1 - np.sum((y - predicted) ** 2) / np.sum((y - y.mean()) ** 2)

    print("Intercept:", b[0].round(0))
    print("Per year of age:", b[1].round(0))
    print("Per BMI point:", b[2].round(0))
    print("For smoking:", b[3].round(0))
    print("R squared:", r2.round(3))


# ---------------- Matplotlib ----------------

def matplotlib_1_histogram(df):
    plt.figure(figsize=(8, 4.5))
    plt.hist(df["charges"], bins=40, color="steelblue", edgecolor="white")
    plt.axvline(df["charges"].mean(), color="red", linestyle="--", label="Mean")
    plt.axvline(df["charges"].median(), color="black", linestyle=":", label="Median")
    plt.title("Distribution of insurance charges")
    plt.xlabel("Charges (USD)")
    plt.ylabel("Number of people")
    plt.legend()
    plt.savefig(FIG_DIR / "mpl_1_histogram.png", dpi=150, bbox_inches="tight")
    plt.close()


def matplotlib_2_scatter(df):
    smokers = df[df["smoker"] == "yes"]
    non_smokers = df[df["smoker"] == "no"]

    plt.figure(figsize=(8, 4.5))
    plt.scatter(non_smokers["age"], non_smokers["charges"], s=10, label="Non-smoker")
    plt.scatter(smokers["age"], smokers["charges"], s=10, color="orange", label="Smoker")
    plt.title("Charges vs age")
    plt.xlabel("Age")
    plt.ylabel("Charges (USD)")
    plt.legend()
    plt.savefig(FIG_DIR / "mpl_2_scatter.png", dpi=150, bbox_inches="tight")
    plt.close()


def matplotlib_3_bar_chart(df):
    table = df.pivot_table(values="charges", index="age_group",
                           columns="smoker", observed=True)
    table.columns = ["Non-smoker", "Smoker"]

    table.plot(kind="bar", figsize=(8, 4.5), color=["steelblue", "orange"])
    plt.title("Average charges by age group")
    plt.xlabel("Age group")
    plt.ylabel("Average charges (USD)")
    plt.xticks(rotation=0)
    plt.savefig(FIG_DIR / "mpl_3_bar_chart.png", dpi=150, bbox_inches="tight")
    plt.close()


if __name__ == "__main__":
    df = pandas_1_load_and_clean()
    pandas_2_group_by(df)
    df = pandas_3_new_columns(df)
    numpy_1_statistics(df)
    numpy_2_correlation(df)
    numpy_3_regression(df)
    matplotlib_1_histogram(df)
    matplotlib_2_scatter(df)
    matplotlib_3_bar_chart(df)
