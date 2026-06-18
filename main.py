from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from fastapi.responses import Response
import os

from core.logger import log_request, log_response

app = FastAPI()
website = app


@app.middleware("http")
async def log_middleware(request: Request, call_next):
    body = None
    try:
        body = await request.json()
    except Exception:
        body = None

    log_request(request.method, request.url.path, dict(request.query_params), body)
    response: Response = await call_next(request)
    log_response(request.method, request.url.path, response.status_code)
    return response

@app.get("/custom/docs", include_in_schema=False)
async def custom_docs():
    if os.path.exists("templates/docs.html") :
        with open("templates/docs.html", encoding="utf-8") as f:  
            return HTMLResponse(f.read())
    pass

@website.get('/', response_class=HTMLResponse)
async def home_page():
    html_path = "templates/home.html"
    
    html = '''
        <center>
        <h1>Welcome To InnoTech</h1>
        <p><a href="/docs">Visit Backend API Document</a></p>
        <p><a href="/api/v1/pos/docs">Visit POS API Document</a></p>
        <p><a href="/api/v1/m/docs">Visit Mobile API Document</a></p>
        </center>        
    '''
    return HTMLResponse(content=html, status_code=200)

# Import all modules here
from api.register import *