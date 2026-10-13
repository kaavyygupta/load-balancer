from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return "hello from server"

@app.get("/health")
def health():
    return "server's health ok"