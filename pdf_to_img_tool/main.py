from os import path
from os import makedirs

from uvicorn import run
from fastapi import FastAPI
from fastapi import UploadFile
from fastapi import HTTPException
from fastapi import Request
# from fastapi import red
from fastapi import Form
from fastapi import Path

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from time import perf_counter
from threading import Thread,Event
from cpu import get_free_cpu_count, cpu_check
from util import NUM_CPUS
from util import pdf_to_images_multiprocessing
UPLOAD_DIRECTORY = "./static/output"

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/static/output", StaticFiles(directory="static/output"), name="output")

templates = Jinja2Templates(directory="templates")

origins_urls = [
    "http://localhost",
    "http://localhost:8080",
    "http://http://127.0.0.1:8000",
    "https://http://127.0.0.1:8000", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins_urls,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request, msg: str = None):
    """
    Home Page for uploading a PDF
    :param request:
    :return:
    """
    return templates.TemplateResponse(request=request, name="index.html", context={"msg": msg})

@app.post("/select-folder/")
def select_folder(folder_path: str = Form(...)):
    print(f"Selected folder: {folder_path}")  # Display on console
    return {"folder_path": folder_path}

@app.post("/upload_file", response_class=HTMLResponse)
async def upload_pdf_file(request: Request, pdf_file: UploadFile):
    if pdf_file.content_type != "application/pdf":
        # raise HTTPException(status_code=400, detail="Only PDF files are supported!")
        return RedirectResponse(url="/?msg=Only PDF files are supported", status_code=302)

    file_name = pdf_file.filename
    file_path = path.join(UPLOAD_DIRECTORY, file_name)

    makedirs(path.dirname(file_path), exist_ok=True)
    time =None
    try:
        with open(file_path, "wb+") as buffer:
            buffer.write(await pdf_file.read())
        stop_event = Event()

        # Start CPU monitoring in a separate thread
        cpu_monitor_thread = Thread(target=cpu_check, args=(stop_event,))
        
        # Create a threading event to signal when to stop the CPU monitoring
        cpu_monitor_thread.daemon = True  # This allows the thread to exit when the main program does
        cpu_monitor_thread.start()
       
        time_start = perf_counter()
        pdf_to_images_multiprocessing(pdf_file= file_path, start_count=1184,max_workers=NUM_CPUS)
        time_end = perf_counter()

        # Signal the CPU monitoring thread to stop
        stop_event.set()

        # Optionally, wait for the monitoring thread to finish (not necessary as it's a daemon thread)
        cpu_monitor_thread.join(timeout=1)       
        time = f"{time_end-time_start:.5f}"
        print(f"{time=:}")
    except Exception as e:
        print("except", e)
        
    else:
        print("done convertion")
    return templates.TemplateResponse("display.html", {"request": request, "msg": "file convert into image", "time": time})

if __name__ == "__main__":
    run("main:app", host="0.0.0.0", port=8001, reload=True)