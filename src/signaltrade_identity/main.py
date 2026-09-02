from fastapi import FastAPI

app = FastAPI(title="SignalTrade Identity")


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": "identity"}


@app.get("/ready", tags=["system"])
def ready() -> dict[str, str]:
    return {"status": "ready", "service": "identity"}

