from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

from storage import Storage

app = FastAPI()
storage = Storage()


@app.post("/upload")
async def upload(request: Request):
    content = await request.body()
    uid = storage.store(content)
    return {'id': uid, 'url': f'http://127.0.0.1:8000/page/{uid}'}


@app.get("/page/{uid}", response_class=HTMLResponse)
async def resource(uid: int):
    return storage.get(uid)


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
