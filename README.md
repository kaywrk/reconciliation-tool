# Reconciliation and Fraud-Flagging Tool

A prototype that compares two financial records (for example a bank statement and a company ledger) and flags what is missing, what has the wrong amount, and what is duplicated. It also includes a fraud-risk model and a small API.

## Try it in 2 minutes

git clone https://github.com/kaywrk/reconciliation-tool.git
cd reconciliation-tool
pip install -r requirements.txt
streamlit run app.py

Then upload `bank.csv` and `ledger.csv` from this folder.

Expected result: 4,995 matched, 3 missing, 2 wrong amounts, 1 duplicated transaction.

## What is inside
- `app.py` - Streamlit web app (colored version)
- `app_basic.py` - plain version of the app
- `make_list.py` - builds the sample bank and ledger files with planted errors
- `analysis.ipynb` - data cleaning and fraud-model training
- `api.py` - FastAPI service (needs `model.pkl`, see below)

## Fraud model and API (optional)
Data: the public PaySim dataset on Kaggle (not included because of its size). Download it, run `analysis.ipynb` to clean the data and train the model (this creates `model.pkl`), then install `fastapi uvicorn python-multipart` and run `uvicorn api:app --reload`.

## Notes and limits
- The bank side is simulated from public sample data, so no real customer records are used.
- The model scores very high on this synthetic data. Real data will be harder, so it would need retraining and validation.
- This is a prototype, not a production system.

