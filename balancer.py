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

total_requests = 0
total_failures = 0

requests_served = {
    "http://127.0.0.1:8001": 0,
    "http://127.0.0.1:8002": 0,
    "http://127.0.0.1:8003": 0
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
    global turn, total_requests, total_failures
    
    total_requests += 1

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
                requests_served[active] += 1
                return response.json()
        except(httpx.ConnectError, httpx.TimeoutException):
            status[active] = False

    total_failures += 1   

    raise HTTPException(
        status_code=503,
        detail="No backend found"
    )

@app.get("/metrics")
async def metrics():
    return {
        "Total_requests": total_requests,
        "Total_failures": total_failures,
        "Requests_per_backend": requests_served,
        "Status": status
    }


if __name__ == "__main__":
    uvicorn.run(app, port=8000)