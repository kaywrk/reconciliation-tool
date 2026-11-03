# import pandas as pd
# import streamlit as st

# st.title("Reconciliation Tool")
# st.write("Upload a bank statement and a company ledger to find mismatches.")

# bank_file = st.file_uploader("Bank statement (CSV)", type="csv")
# ledger_file = st.file_uploader("Company ledger (CSV)", type="csv")

# if bank_file and ledger_file:
#     bank = pd.read_csv(bank_file)
#     ledger = pd.read_csv(ledger_file)

#     dupes = bank[bank.duplicated("reference", keep=False)]
#     bank = bank.drop_duplicates("reference")

#     m = ledger.merge(bank, on="reference", how="outer",
#                      suffixes=("_ledger", "_bank"), indicator=True)

#     not_in_bank = m[m["_merge"] == "left_only"]
#     not_in_ledger = m[m["_merge"] == "right_only"]
#     both = m[m["_merge"] == "both"]
#     wrong = both[both["amount_ledger"] != both["amount_bank"]]
#     ok = both[both["amount_ledger"] == both["amount_bank"]]

#     a, b, c, d = st.columns(4)
#     a.metric("Matched", len(ok))
#     b.metric("Missing", len(not_in_bank) + len(not_in_ledger))
#     c.metric("Wrong amount", len(wrong))
#     d.metric("Duplicates", len(dupes))

#     st.subheader("Not in bank statement")
#     st.dataframe(not_in_bank[["reference", "amount_ledger"]])
#     st.subheader("Amount mismatches")
#     st.dataframe(wrong[["reference", "amount_ledger", "amount_bank"]])
#     st.subheader("Duplicate entries")
#     st.dataframe(dupes[["reference", "amount"]])

#     #/opt/anaconda3/envs/py311/bin/python -m streamlit run app.py

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Reconciliation Tool", page_icon="💱", layout="wide")

st.markdown("""
<style>
.hero{background:linear-gradient(90deg,#1B5E20,#43A047);padding:22px 28px;
      border-radius:14px;color:white;margin-bottom:18px}
.hero h1{color:white;margin:0;font-size:32px}
.hero p{margin:4px 0 0;opacity:.9}
.card{padding:18px;border-radius:12px;color:white;text-align:center;
      box-shadow:0 2px 6px rgba(0,0,0,.15)}
.card .num{font-size:34px;font-weight:700}
.card .lab{font-size:14px;opacity:.95}
.sec{padding:8px 14px;border-radius:8px;color:white;font-weight:600;margin:22px 0 8px}
</style>
""", unsafe_allow_html=True)


def card(col, num, label, color):
    col.markdown(f'<div class="card" style="background:{color}">'
                 f'<div class="num">{num:,}</div><div class="lab">{label}</div></div>',
                 unsafe_allow_html=True)


def section(title, color):
    st.markdown(f'<div class="sec" style="background:{color}">{title}</div>',
                unsafe_allow_html=True)


st.markdown('<div class="hero"><h1>Reconciliation Tool</h1>'
            '<p>Upload a bank statement and a company ledger to find mismatches instantly.</p></div>',
            unsafe_allow_html=True)

u1, u2 = st.columns(2)
bank_file = u1.file_uploader("Bank statement (CSV)", type="csv")
ledger_file = u2.file_uploader("Company ledger (CSV)", type="csv")

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
    wrong = both[both["amount_ledger"] != both["amount_bank"]].copy()
    wrong["difference"] = wrong["amount_ledger"] - wrong["amount_bank"]
    ok = both[both["amount_ledger"] == both["amount_bank"]]

    n_missing = len(not_in_bank) + len(not_in_ledger)
    n_issues = n_missing + len(wrong) + dupes["reference"].nunique()
    rate = len(ok) / max(len(ledger), 1)

    c1, c2, c3, c4 = st.columns(4)
    card(c1, len(ok), "Matched", "#2E7D32")
    card(c2, n_missing, "Missing", "#EF6C00")
    card(c3, len(wrong), "Wrong amount", "#C62828")
    card(c4, len(dupes), "Duplicate rows", "#6A1B9A")

    st.write("")
    if n_issues:
        st.warning(f"{n_issues} items need review. Match rate: {rate:.1%}")
    else:
        st.success("Everything matches.")
    st.progress(min(rate, 1.0))

    chart = pd.DataFrame({"Items": [n_missing, len(wrong), dupes["reference"].nunique()]},
                         index=["Missing", "Wrong amount", "Duplicates"])
    st.bar_chart(chart, color="#C62828")

    section("Not in bank statement", "#EF6C00")
    st.dataframe(not_in_bank[["reference", "amount_ledger"]], use_container_width=True)

    if len(not_in_ledger):
        section("Not in company ledger", "#EF6C00")
        st.dataframe(not_in_ledger[["reference", "amount_bank"]], use_container_width=True)

    section("Amount mismatches", "#C62828")
    st.dataframe(wrong[["reference", "amount_ledger", "amount_bank", "difference"]],
                 use_container_width=True)

    section("Duplicate entries", "#6A1B9A")
    st.dataframe(dupes[["reference", "amount"]], use_container_width=True)

    report = pd.concat([
        not_in_bank[["reference", "amount_ledger"]].assign(issue="Missing from bank"),
        wrong[["reference", "amount_ledger", "amount_bank", "difference"]].assign(issue="Wrong amount"),
    ], ignore_index=True)
    st.download_button("Download exceptions (CSV)", report.to_csv(index=False),
                       "exceptions.csv", "text/csv")

