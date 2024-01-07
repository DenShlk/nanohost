import random
import sched
import time
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from threading import Thread

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine
import pytimeparse

from db_storage import DbStorage


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    storage.shutdown()


app = FastAPI(lifespan=lifespan)

db_engine = create_engine('postgresql+psycopg2://postgres:example@postgres:5432/postgres', echo=True)
storage = DbStorage(db_engine)

print('lol')


@app.post("/upload")
async def upload(request: Request, duration: str | None = None, uses: int | None = None):
    content = await request.body()
    if duration is not None:
        if duration:
            duration = timedelta(seconds=pytimeparse.parse(duration))
        else:
            duration = None
    uid = storage.store(content, duration=duration, uses=uses)
    return {'id': uid, 'url': f'https://realnice.page/id/{uid}'}


@app.get("/id/{uid}")
async def resource(uid: str):
    res = storage.get(uid)
    return HTTPException(status_code=404, detail="Not found.") if res is None else HTMLResponse(res)


@app.get("/", response_class=HTMLResponse)
async def root():
    return f"""
    <html>
        <head>
            <title>Nanohost</title>
        </head>
        <body>
            <h1>Objects in storage: {storage.count()}</h1>
            
            <h1>Memory use by objects: {storage.size()}b ({storage.size() // 2 ** 23}Mb)</h1>
        </body>
    </html>
    """


@app.get("/healthcheck", response_class=HTMLResponse)
async def healthcheck() -> str:
    return random.choice(['hear you loud and clear', '5/5', 'we hear you'])
