from fastapi import FastAPI

app = FastAPI(
    title="Research English Lab API",
    version="3.0"
)


@app.get("/")
def home():
    return {
        "project": "Research English Lab",
        "version": "3.0",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }
