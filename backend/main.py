from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "Integrity Ledger Backend Online", "engine": "Chaos/Bayesian"}
