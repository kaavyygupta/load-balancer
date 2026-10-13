from fastapi import FastAPI
import sys
import uvicorn

app = FastAPI()

@app.get("/")
def root():
    return f"hello from server {name}"

@app.get("/health")
def health():
    return "server's health ok"

name = sys.argv[1]
port = int(sys.argv[2])

if __name__ == "__main__":
    uvicorn.run(app, port=port)

