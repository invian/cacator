import os
from pathlib import Path
from threading import Thread

import uvicorn
from dnslib.server import DNSServer
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from server.adapters.sqlite import SQLiteSessionsStorage
from server.resolver import BeaconResolver
from server.server import Server

PROJECT_PATH = Path(os.path.dirname(__file__))
ADDR = "0.0.0.0"
PORT = 53

app = FastAPI()
api = APIRouter(prefix="/api")


@api.get("/data")
def get_data():
    repo = SQLiteSessionsStorage(PROJECT_PATH / "dump" / "data.db")

    return repo.all_sessions()


app.include_router(api)
app.mount(
    "/",
    StaticFiles(directory=PROJECT_PATH.parent / "dashboard" / "public", html=True),
    name="app",
)
app.mount(
    "/build",
    StaticFiles(directory=PROJECT_PATH.parent / "dashboard" / "public" / "build"),
    name="build",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def run_dns_server():
    repo = SQLiteSessionsStorage(PROJECT_PATH / "dump" / "data.db")
    server = Server(repo)
    resolver = BeaconResolver(server)
    dns_server = DNSServer(resolver, port=PORT, address=ADDR)
    dns_server.start_thread()


thread = Thread(target=run_dns_server, daemon=True)
thread.start()
uvicorn.run(app, host=ADDR, port=5053)
