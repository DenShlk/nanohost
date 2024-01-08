import random
import sched
import time
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from threading import Thread

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from pydantic_core import Url
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


class UploadResponse(BaseModel):
    id: str
    url: Url


@app.post("/upload")
async def upload(request: Request, duration: str | None = None, uses: int | None = None) -> UploadResponse:
    """
    Uploads content to storage with optional expiration duration and usage limit.

    Parameters:
    - request (Request): The FastAPI request object.
    - duration (str | None): Optional. A string representing the expiration duration.
    Format is 1d, 1h, 1h 30m 15s and so on. (check https://github.com/wroberts/pytimeparse)
    If None, default (1d) expiration is set.
    - uses (int | None): Optional. The maximum number of uses for the uploaded content.
    If None, default (1000) will be set.

    Returns:
    - dict: A dictionary containing the ID and URL of the stored content.
   """
    content = await request.body()
    if duration is not None:
        if duration:
            duration = timedelta(seconds=pytimeparse.parse(duration))
        else:
            duration = None
    uid = storage.store(content, duration=duration, uses=uses)
    return UploadResponse(id=uid, url=f'https://realnice.page/id/{uid}')


@app.get("/id/{uid}")
async def resource(uid: str):
    """
    Retrieves content from storage based on the provided ID. Returns content as html page.

    Parameters:
    - uid (str): The unique identifier of the stored content.

    Returns:
    - HTMLResponse: The content if found, else HTTPException with status code 404.
    """
    res = storage.get(uid)
    return HTTPException(status_code=404, detail="Not found.") if res is None else HTMLResponse(res)


@app.get("/", response_class=HTMLResponse)
async def root():
    """
    Returns an HTML page displaying information about the objects in storage and memory usage.

    Returns:
    - HTMLResponse: An HTML page containing information about the storage and memory usage.
    """
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
    """
    Performs a health check and returns a random health status message.

    Returns:
    - str: A random health status message if app is online, otherwise ???.
    """
    return random.choice(['hear you loud and clear', '5/5', 'we hear you'])
