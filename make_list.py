import pandas as pd

def clean_data(data):
    data = data.drop_duplicates()
    data = data.dropna(subset=["type", "amount"])
    data["type"] = data["type"].str.strip().str.upper()

    numeric_cols = data.select_dtypes(include="number").columns
    data = data[(data[numeric_cols] >= 0).all(axis=1)]

    return data.reset_index(drop=True)

path = ("/Users/macbookair/Documents/Reconciliation-Demo./PS_20174392719_1491204439457_log.csv")

df = pd.read_csv(path, nrows=5000)
df = clean_data(df)

cols = ["step", "type", "amount", "oldbalanceOrg", "newbalanceOrig",
        "oldbalanceDest", "newbalanceDest", "isFraud"]
ledger = df[cols].copy()
ledger["reference"] = [f"TXN{i:05d}" for i in range(len(ledger))]

bank = ledger.copy()
bank = bank.drop(index=[10, 45, 300])
bank.loc[20, "amount"] -= 500
bank.loc[60, "amount"] += 2000
bank = pd.concat([bank, bank.iloc[[30]]])

ledger.to_csv("ledger.csv", index=False)
bank.to_csv("bank.csv", index=False)
print("Ledger:", len(ledger), "rows | Bank:", len(bank), "rows")

