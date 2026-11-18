from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
async def get_health() -> dict[str, str]:
    return {"status": "ok"}