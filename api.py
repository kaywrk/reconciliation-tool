import io
import joblib
import pandas as pd
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel

app = FastAPI(title="Reconciliation & Fraud API")
model = joblib.load("model.pkl")

FEATURES = ["amount", "oldbalanceOrg", "newbalanceOrig", "oldbalanceDest",
            "newbalanceDest", "errorOrig", "errorDest", "is_transfer"]


class Txn(BaseModel):
    type: str
    amount: float
    oldbalanceOrg: float
    newbalanceOrig: float
    oldbalanceDest: float
    newbalanceDest: float


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(t: Txn):
    row = {
        "amount": t.amount,
        "oldbalanceOrg": t.oldbalanceOrg,
        "newbalanceOrig": t.newbalanceOrig,
        "oldbalanceDest": t.oldbalanceDest,
        "newbalanceDest": t.newbalanceDest,
        "errorOrig": t.newbalanceOrig + t.amount - t.oldbalanceOrg,
        "errorDest": t.oldbalanceDest + t.amount - t.newbalanceDest,
        "is_transfer": int(t.type.strip().upper() == "TRANSFER"),
    }
    prob = float(model.predict_proba(pd.DataFrame([row])[FEATURES])[0][1])
    return {"fraud_probability": round(prob, 4), "flagged": prob >= 0.5}


@app.post("/reconcile")
async def reconcile(bank_file: UploadFile = File(...),
                    ledger_file: UploadFile = File(...)):
    bank = pd.read_csv(io.BytesIO(await bank_file.read()))
    ledger = pd.read_csv(io.BytesIO(await ledger_file.read()))

    dupes = bank[bank.duplicated("reference", keep=False)]
    bank = bank.drop_duplicates("reference")

    m = ledger.merge(bank, on="reference", how="outer",
                     suffixes=("_ledger", "_bank"), indicator=True)
    missing = m[m["_merge"] != "both"]
    both = m[m["_merge"] == "both"]
    wrong = both[both["amount_ledger"] != both["amount_bank"]]

    return {
        "matched": int(len(both) - len(wrong)),
        "missing": missing["reference"].tolist(),
        "wrong_amount": wrong[["reference", "amount_ledger", "amount_bank"]].to_dict("records"),
        "duplicates": dupes["reference"].tolist(),
    }

