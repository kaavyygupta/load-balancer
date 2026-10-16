from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import asyncio
import httpx
import uvicorn


backends = ["http://127.0.0.1:8001", "http://127.0.0.1:8002", "http://127.0.0.1:8003"]
turn = 0

status = {
    "http://127.0.0.1:8001": True,
    "http://127.0.0.1:8002": True,
    "http://127.0.0.1:8003": True
}

async def check_health():
    async with httpx.AsyncClient() as client:
        while True:
            for url in backends:
                try:
                    response = await client.get(url + "/health", timeout=2.0)
                    status[url] = response.status_code == 200
                except httpx.HTTPError:
                    status[url] = False
            await asyncio.sleep(3)

@asynccontextmanager
async def lifespan(app):
    task = asyncio.create_task(check_health())
    yield
    task.cancel()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def forward():
    global turn

    for _ in range(len(backends)):
        active = backends[turn]
        turn += 1
        if turn == len(backends):
            turn = 0
        if status[active] == False:
            continue
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(active, timeout=5.0)
                return response.json()
        except(httpx.ConnectError, httpx.TimeoutException):
            status[active] = False
            
    raise HTTPException(
        status_code=503,
        detail="No backend found"
    )

if __name__ == "__main__":
    uvicorn.run(app, port=8000)