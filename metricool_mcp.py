import os
import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse
import uvicorn

app = FastAPI()

API_KEY = os.getenv("METRICOOL_API_KEY", "")
TARGET = "https://ai.metricool.com/mcp"


@app.get("/")
async def health():
    return {"status": "ok", "service": "belgrin-metricool-mcp"}


@app.post("/mcp")
async def proxy_post(request: Request):
    body = await request.body()
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            TARGET,
            content=body,
            headers={
                "Content-Type": request.headers.get("Content-Type", "application/json"),
                "Accept": request.headers.get("Accept", "application/json"),
                "X-Mc-Auth": API_KEY,
            },
        )
    return Response(
        content=resp.content,
        status_code=resp.status_code,
        media_type=resp.headers.get("content-type", "application/json"),
    )


@app.get("/mcp")
async def proxy_get(request: Request):
    async def event_stream():
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(
                "GET",
                TARGET,
                headers={
                    "Accept": "text/event-stream",
                    "X-Mc-Auth": API_KEY,
                },
            ) as resp:
                async for chunk in resp.aiter_bytes():
                    yield chunk

    return StreamingResponse(event_stream(), media_type="text/event-stream")


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
