from fastapi import FastAPI

from app.routers import leads

app = FastAPI(title="leadflow")
app.include_router(leads.router)


@app.get("/")
def root():
    return {"message": "leadflow is running"}


@app.get("/health")
def health():
    return {"status": "ok"}
