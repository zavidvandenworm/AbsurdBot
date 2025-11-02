import asyncio

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
from modules.upload import public_folder
app = FastAPI()

@app.get("/")
async def root():
    return {"absurdAPI": "this url is truly absurd"}

app.mount("/static", StaticFiles(directory=public_folder), name="static")

async def start_uvicorn():
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=3000,
        log_level="info",
        lifespan="off"
    )
    server = uvicorn.Server(config)
    await server.serve()