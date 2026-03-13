from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
app = FastAPI()

@app.get("/", response_class=PlainTextResponse)
async def index(request: Request):
    return "<h1>It worked.</h1>"
