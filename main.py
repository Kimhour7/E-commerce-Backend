from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import os
# For using in every module
app = FastAPI()

@app.get("/custom/docs", include_in_schema=False)
async def custom_docs():
    if os.path.exists("templates/docs.html") :
        with open("templates/docs.html", encoding="utf-8") as f:  
            return HTMLResponse(f.read())
    pass

@app.get('/', response_class=HTMLResponse)
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