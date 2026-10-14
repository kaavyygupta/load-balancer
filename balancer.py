from fastapi import FastAPI
import httpx
import uvicorn

app = FastAPI()

backends = ["http://127.0.0.1:8001", "http://127.0.0.1:8002", "http://127.0.0.1:8003"]
turn = 0

@app.get("/")
async def forward():
    global turn
    active = backends[turn]
    turn += 1
    if turn == len(backends):
        turn = 0

    async with httpx.AsyncClient() as client:
        response = await client.get(active)
        return response.json()

if __name__ == "__main__":
    uvicorn.run(app, port=8000)