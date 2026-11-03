import pandas as pd
import streamlit as st

st.title("Reconciliation Tool")
st.write("Upload a bank statement and a company ledger to find mismatches.")

bank_file = st.file_uploader("Bank statement (CSV)", type="csv")
ledger_file = st.file_uploader("Company ledger (CSV)", type="csv")

if bank_file and ledger_file:
    bank = pd.read_csv(bank_file)
    ledger = pd.read_csv(ledger_file)

    dupes = bank[bank.duplicated("reference", keep=False)]
    bank = bank.drop_duplicates("reference")

    m = ledger.merge(bank, on="reference", how="outer",
                     suffixes=("_ledger", "_bank"), indicator=True)

    not_in_bank = m[m["_merge"] == "left_only"]
    not_in_ledger = m[m["_merge"] == "right_only"]
    both = m[m["_merge"] == "both"]
    wrong = both[both["amount_ledger"] != both["amount_bank"]]
    ok = both[both["amount_ledger"] == both["amount_bank"]]

    a, b, c, d = st.columns(4)
    a.metric("Matched", len(ok))
    b.metric("Missing", len(not_in_bank) + len(not_in_ledger))
    c.metric("Wrong amount", len(wrong))
    d.metric("Duplicates", len(dupes))

    st.subheader("Not in bank statement")
    st.dataframe(not_in_bank[["reference", "amount_ledger"]])
    st.subheader("Amount mismatches")
    st.dataframe(wrong[["reference", "amount_ledger", "amount_bank"]])
    st.subheader("Duplicate entries")
    st.dataframe(dupes[["reference", "amount"]])

    #/opt/anaconda3/envs/py311/bin/python -m streamlit run app.py

