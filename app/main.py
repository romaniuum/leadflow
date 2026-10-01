from fastapi import FastAPI

from app.routers import analytics, leads

app = FastAPI(title="leadflow")
app.include_router(leads.router)
app.include_router(analytics.router)


@app.get("/")
def root():
    return {"message": "leadflow is running"}


@app.get("/health")
def health():
    return {"status": "ok"}
