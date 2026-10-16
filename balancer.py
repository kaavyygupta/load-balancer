from fastapi import FastAPI, HTTPException
import httpx
import uvicorn

app = FastAPI()

backends = ["http://127.0.0.1:8001", "http://127.0.0.1:8002", "http://127.0.0.1:8003"]
turn = 0

status = {
    "http://127.0.0.1:8001": True,
    "http://127.0.0.1:8002": True,
    "http://127.0.0.1:8003": True
}

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