import os
import datetime

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette import status

from util import read_json, add_json, remove_json, update_json

app = FastAPI()

app.mount("/static", StaticFiles(directory="./static"), name="static")

templates = Jinja2Templates(directory="./templates")


# deserialize data
@app.get('/', response_class=HTMLResponse)
async def backend_ui_home(request: Request):
    text, intent =  read_json()
    return templates.TemplateResponse('index.html', {"request": request,"nlu_data" : text, "intends": intent})


@app.post("/add", response_class=HTMLResponse)
async def admin_model_config(sentence=Form(), intent=Form()):
    add_json(sentence, intent)
    return RedirectResponse("/", status_code=status.HTTP_302_FOUND)


@app.post("/delete")
def delete(sentence=Form(), intent: str = Form(default="")):
    print(intent,sentence,'nil')
    # remove_json(sentence, intent)
    return RedirectResponse("/", status_code=status.HTTP_302_FOUND)


@app.post("/update")
async def admin_nlu_update(request: Request):
    request_data_json = await request.json()

    s = request_data_json['sentence']
    i = request_data_json['intent']
    update_json(s, i)
    return {"ok": "done"}
