
from fastapi import FastAPI,Request,Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from MyConnection import Employee
from bson.objectid import ObjectId
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="templates")

# Notice that you have to pass the request as part of the key-value pairs in the context for Jinja2.
# So, you also have to declare it in your path operation.
# By declaring response_class=HTMLResponse the docs UI will be able to know that the response will be HTML.

@app.get("/items/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    return templates.TemplateResponse("item.html", {"request": request, "id": id})

# TODO find when to use asyn and when not

@app.get("/", response_class=HTMLResponse)
async def read_items(request:Request):
    emp =None
    employees = None
    try:
        emp = Employee() 
        employees = emp.get_emp_data()
    except BaseException as err:
         print(err,"exception")
    finally:
        emp.delete()
    # print(employees)
    return templates.TemplateResponse("index.html", {"request": request,"employees": employees})

@app.post("/item/add", response_class=HTMLResponse)
async def add_item(request:Request,name: str= Form(), gf:bool = Form(),address:str=Form(),salary:float=Form()):
    emp_dict ={
        "name": name,
        "gf": gf,
        "address": address,
        "salary":salary
    }
    

    print(emp_dict)
    emp = None
    employees = None
    try:
        emp = Employee() 
        emp.add_data(emp_dict)
        employees = emp.get_emp_data()
    except BaseException as err:
         print(err,"exception")
    finally:
        if emp is not None:
            emp.delete()
    return templates.TemplateResponse("index.html", {"request": request,"employees": employees})

@app.post("/item/addAll", response_class=HTMLResponse)
async def add_items(request:Request):
    emp = None
    dict_data = [
            {  "name": "Vishwash", "gf": False, "address":"CSE","salary":10000},
            {  "name": "Vishesh", "gf": False, "address":"IT","salary":10000},
            {  "name": "Shivam", "gf": False, "address":"ME","salary":10000},
            {  "name": "Yash", "gf": False, "address":"ECE","salary":10000},
    ]
    try:
        emp = Employee()
        emp.add_all_data(dict_data)
    except BaseException as e:
        print(e,"exception")
    finally:
        if emp is not None:
            emp.delete()
        else:
            print("check connections")
    return templates.TemplateResponse("index.html", {"request": request, })

@app.post('/item/update',response_class=HTMLResponse)
async def update_item(request:Request,id = Form(),name: str= Form(), gf:bool = Form(),address   =Form(),salary:float=Form()):
    emp_dict ={
        "name": name,
        "gf": gf,
        "address": address,
        "salary":salary
    }
    emp_id={
        '_id':ObjectId(id)
    }

    print(emp_dict,"update")
    emp = None
    employees = None
    try:
        emp = Employee() 
        emp.set_emp_data(emp_id,emp_dict)
    except BaseException as err:
         print(err,"exception")
    finally:
        if emp is not None:
            emp.delete()
    return RedirectResponse('/', status_code=302)


@app.post("/item/delete/{id}", response_class=HTMLResponse)
async def delete_item(request:Request,id):
    emp_id = {
        "_id" :ObjectId(id)
    }
    emp = None
    employees = None
    try:
        emp = Employee() 
        emp.remove_emp_data(emp_id)
    except BaseException as err:
         print(err,"exception")
    finally:
        if emp is not None:
            emp.delete()
    return RedirectResponse('/', status_code=302)


@app.post("/item/delete_many", response_class=HTMLResponse)
async def delete_items(request:Request,ids:str=Form()):
    '''TODO chenge js from string to array'''
    temp_id = ids.split(',')
    try:
        emp = Employee() 
        emp.remove_emps(temp_id)
    except BaseException as err:
         print(err,"exception")
    finally:
        if emp is not None:
            emp.delete()
    return RedirectResponse('/', status_code=302)


@app.get("/test", response_class=HTMLResponse)
async def add_items(request:Request):
 
    return templates.TemplateResponse("edit.html", {"request": request, })


@app.get("/home", response_class=HTMLResponse)
async def read_items(request:Request):
    emp =None
    employees = None
    try:
        emp = Employee() 
        employees = emp.get_emp_data()
    except BaseException as err:
         print(err,"exception")
    finally:
        emp.delete()
    # print(employees)
    return templates.TemplateResponse("home.html", {"request": request,"employees": employees})

@app.post("/home/add", response_class=HTMLResponse)
async def add_item(request:Request,name: str= Form(), gf:bool = Form(),address:str=Form(),salary:float=Form()):
    emp_dict ={
        "name": name,
        "gf": gf,
        "address": address,
        "salary":salary
    }
    

    print(emp_dict)
    emp = None
    employees = None
    try:
        emp = Employee() 
        emp.add_data(emp_dict)
        employees = emp.get_emp_data()
    except BaseException as err:
         print(err,"exception")
    finally:
        if emp is not None:
            emp.delete()
    return templates.TemplateResponse("home.html", {"request": request,"employees": employees})