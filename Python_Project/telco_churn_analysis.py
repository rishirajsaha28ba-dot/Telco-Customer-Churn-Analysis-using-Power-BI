# Telco Customer Churn Analysis
# Libraries used: pandas, numpy, matplotlib
# Dataset: IBM Telco Customer Churn (7043 customers)

# %% [SETUP] Importing libraries and loading the data
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

pd.set_option("display.width", 120)
pd.set_option("display.max_columns", None)

df = pd.read_excel("../DataSet/Telco_customer_churn.xlsx")

print("Rows and columns:", df.shape)
print(df[["CustomerID", "Gender", "Tenure Months", "Contract",
          "Monthly Charges", "Churn Label"]].head())

# %% [PD1] Pandas 1 - Cleaning the data and basic statistics
# Total Charges is stored as text, so we convert it to numbers
df["Total Charges"] = pd.to_numeric(df["Total Charges"], errors="coerce")

# checking missing values
print("Missing values in Total Charges:", df["Total Charges"].isnull().sum())
print("Missing values in Churn Reason:", df["Churn Reason"].isnull().sum())

# new customers have not paid anything yet, so we put 0
df["Total Charges"] = df["Total Charges"].fillna(0)

# removing columns we don't need
df = df.drop(columns=["Count", "Country", "State", "Lat Long"])
print("Shape after cleaning:", df.shape)

print(df[["Tenure Months", "Monthly Charges", "Total Charges", "CLTV"]].describe().round(2))

churn_rate = df["Churn Value"].mean() * 100
print("Overall churn rate:", round(churn_rate, 2), "%")

# %% [PD2] Pandas 2 - Churn rate by contract, internet service and payment method
contract_churn = df.groupby("Contract")["Churn Value"].mean() * 100
print("Churn % by Contract")
print(contract_churn.round(2))

internet_churn = df.groupby("Internet Service")["Churn Value"].mean() * 100
print("\nChurn % by Internet Service")
print(internet_churn.round(2))

payment_churn = df.groupby("Payment Method")["Churn Value"].mean() * 100
print("\nChurn % by Payment Method")
print(payment_churn.round(2))

# %% [PD3] Pandas 3 - Tenure groups, pivot table and churn reasons
df["Tenure Group"] = pd.cut(df["Tenure Months"], bins=[-1, 12, 24, 48, 72],
                            labels=["0-12", "13-24", "25-48", "49-72"])

table = pd.pivot_table(df, values="Churn Value", index="Tenure Group",
                       columns="Contract", aggfunc="mean", observed=False)
print("Churn % by Tenure Group and Contract")
print((table * 100).round(1))

churned = df[df["Churn Value"] == 1]
print("\nTop 8 reasons for churn")
print(churned["Churn Reason"].value_counts().head(8))

# %% [NP1] NumPy 1 - Comparing monthly charges of churned and retained customers
churn_yes = df[df["Churn Value"] == 1]["Monthly Charges"].values
churn_no = df[df["Churn Value"] == 0]["Monthly Charges"].values

print("Churned customers:", len(churn_yes))
print("Mean:", np.round(np.mean(churn_yes), 2))
print("Median:", np.round(np.median(churn_yes), 2))
print("Std deviation:", np.round(np.std(churn_yes), 2))
print("25th and 75th percentile:", np.percentile(churn_yes, [25, 75]))

print("\nRetained customers:", len(churn_no))
print("Mean:", np.round(np.mean(churn_no), 2))
print("Median:", np.round(np.median(churn_no), 2))
print("Std deviation:", np.round(np.std(churn_no), 2))
print("25th and 75th percentile:", np.percentile(churn_no, [25, 75]))

print("\nDifference in mean:", np.round(np.mean(churn_yes) - np.mean(churn_no), 2))

# %% [NP2] NumPy 2 - Correlation between numeric columns
cols = ["Tenure Months", "Monthly Charges", "Total Charges", "CLTV", "Churn Value"]
data = df[cols].values

corr = np.corrcoef(data.T)
print(pd.DataFrame(np.round(corr, 2), index=cols, columns=cols))

# %% [NP3] NumPy 3 - Risk groups and revenue lost
score = df["Churn Score"].values
churn = df["Churn Value"].values
monthly = df["Monthly Charges"].values

risk = np.where(score >= 80, "High", np.where(score >= 50, "Medium", "Low"))

for group in ["High", "Medium", "Low"]:
    customers = np.sum(risk == group)
    rate = np.mean(churn[risk == group]) * 100
    print(group, "risk:", customers, "customers, churn rate =", round(rate, 1), "%")

lost = np.sum(monthly[churn == 1])
total = np.sum(monthly)
print("\nMonthly revenue lost: $", round(lost, 2))
print("Share of total revenue lost:", round(lost / total * 100, 1), "%")
print("Yearly revenue lost: $", round(lost * 12, 2))

# %% [MPL1] Matplotlib 1 - Overall churn and churn by contract
plt.figure(figsize=(11, 4))

plt.subplot(1, 2, 1)
counts = df["Churn Label"].value_counts()
plt.pie(counts, labels=["Stayed", "Churned"], autopct="%1.1f%%",
        colors=["steelblue", "salmon"], startangle=90)
plt.title("Overall Churn")

plt.subplot(1, 2, 2)
plt.bar(contract_churn.index, contract_churn.values, color=["salmon", "gold", "mediumseagreen"])
plt.title("Churn % by Contract Type")
plt.ylabel("Churn %")

plt.tight_layout()
plt.show()

# %% [MPL2] Matplotlib 2 - Monthly charges and tenure of churned vs retained customers
plt.figure(figsize=(11, 4))

plt.subplot(1, 2, 1)
plt.hist(churn_no, bins=30, alpha=0.6, label="Stayed", color="steelblue")
plt.hist(churn_yes, bins=30, alpha=0.6, label="Churned", color="salmon")
plt.title("Monthly Charges")
plt.xlabel("Monthly Charges ($)")
plt.ylabel("Number of customers")
plt.legend()

plt.subplot(1, 2, 2)
tenure_no = df[df["Churn Value"] == 0]["Tenure Months"]
tenure_yes = df[df["Churn Value"] == 1]["Tenure Months"]
plt.boxplot([tenure_no, tenure_yes])
plt.xticks([1, 2], ["Stayed", "Churned"])
plt.title("Tenure of Customers")
plt.ylabel("Tenure (months)")

plt.tight_layout()
plt.show()

# %% [MPL3] Matplotlib 3 - Churn over tenure and top churn reasons
plt.figure(figsize=(12, 4.5))

plt.subplot(1, 2, 1)
tenure_churn = df.groupby("Tenure Months")["Churn Value"].mean() * 100
plt.plot(tenure_churn.index, tenure_churn.values, color="salmon")
plt.title("Churn % by Tenure")
plt.xlabel("Tenure (months)")
plt.ylabel("Churn %")
plt.grid(alpha=0.3)

plt.subplot(1, 2, 2)
reasons = churned["Churn Reason"].value_counts().head(8)
plt.barh(reasons.index, reasons.values, color="orange")
plt.gca().invert_yaxis()
plt.title("Top 8 Churn Reasons")
plt.xlabel("Number of customers")

plt.tight_layout()
plt.show()
