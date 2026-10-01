from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.routers import analytics, leads

app = FastAPI(title="leadflow")
app.include_router(leads.router)
app.include_router(analytics.router)

Instrumentator(excluded_handlers=["/metrics", "/health"]).instrument(app).expose(
    app, include_in_schema=False
)


@app.get("/")
def root():
    return {"message": "leadflow is running"}


@app.get("/health")
def health():
    return {"status": "ok"}
