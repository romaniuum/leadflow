from fastapi import FastAPI

app = FastAPI(title="leadflow")


@app.get("/")
def root():
    return {"message": "leadflow is running"}


@app.get("/health")
def health():
    return {"status": "ok"}
