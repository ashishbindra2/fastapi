from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette import status


from util import read_json, add_json, remove_json
from admin import Model

app = FastAPI()

app.mount("/static", StaticFiles(directory="./static"), name="static")

templates = Jinja2Templates(directory="./templates")


def add_bulk_intent():
    admin = Model()
    d, intents = read_json()
    for intent in intents:
        admin.add_intent(intent)


def get_intent_list():
    admin = Model()
    intents = admin.get_intent()
    admin.close_conn()
    return intents

@app.get("/", response_class=HTMLResponse)
async def bui_add_intent(request: Request):
    intent = get_intent_list()
    context = {"request": request, "intents": intent}
    return templates.TemplateResponse('index.html', context=context)


@app.post("/add_intent")
async def bui_add_intent_db(request: Request, intent: str = Form(), description: str = Form()):
    admin = Model()
    intents = admin.get_intent()
    intent_list = []
    for intent_val in intents:
        intent_list.append(intent_val['intent_name'])
    if  intent in intent_list:
        context = {"request": request, "intent_error": "Intent is already exist!!", "intents": intents}
        return templates.TemplateResponse('index.html', context=context)
    else:
        admin.add_intent(intent, description)
    return RedirectResponse("/", status_code=status.HTTP_302_FOUND)


@app.post("/update_intent")
async def bui_update_intent_db(id=Form(), intent: str = Form(), description: str = Form()):
    admin = Model()
    print(intent)
    admin.set_intent(id, intent, description)
    return RedirectResponse("/", status_code=status.HTTP_302_FOUND)


@app.post("/remove_intent")
async def bui_remove_intent_db(id_intent=Form()):
    admin = Model()
    admin.remove_intent(id_intent)
    return RedirectResponse("/", status_code=status.HTTP_302_FOUND)





@app.get('/nlu_data', response_class=HTMLResponse)
async def backend_ui_nlu(request: Request):
    nlu_data, intends = read_json()
    intent = get_intent_list()
    return templates.TemplateResponse('index.html',
                                      {"request": request, "nlu_data": nlu_data, "intends": intent})

@app.post("/add_nlu", response_class=HTMLResponse)
def admin_model_config(sentence=Form(), intent=Form()):
    add_json(sentence, intent)
    print(sentence, intent)
    return RedirectResponse("/nlu_data", status_code=status.HTTP_302_FOUND)


@app.post("/nlu_delete", response_class=HTMLResponse)
def admin_model_config(sentence=Form(), intent: str = Form(default="")):
    print(sentence, intent)
    remove_json(sentence, intent)

    return RedirectResponse("/nlu_data", status_code=status.HTTP_302_FOUND)
