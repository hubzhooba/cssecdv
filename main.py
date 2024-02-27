from typing import List
from fastapi import Depends, HTTPException, FastAPI
import sqlalchemy.orm as _orm
import fastapi as _fastapi
from fastapi import HTTPException, Form
from fastapi.responses import HTMLResponse,RedirectResponse
from fastapi.templating import Jinja2Templates
import operations as op


templates = Jinja2Templates(directory="templates")

app = FastAPI()




@app.get("/login", response_class=HTMLResponse)
def login_page(request: _fastapi.Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
def login(request: _fastapi.Request, email: str = Form(...), password: str = Form(...)):
    if op.check_user_credentials(email, password):
        # If credentials are correct, redirect to /register or any other endpoint
        print("Crendtails are true")
        return RedirectResponse("/register")
    else:
        # If credentials are incorrect, reload the login page
        print("Credentails are false")
        return templates.TemplateResponse("login.html", {"request": request, "message": "Invalid email or password"})
@app.get("/register", response_class=HTMLResponse)
def register_page(request: _fastapi.Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register", response_class=HTMLResponse)
def register(
    request: _fastapi.Request,
    full_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    phone_number: str = Form(...),
):
    op.add_user(full_name, email, password, phone_number)
    # Process the form data and get registration results
    registration_results = {"full_name": full_name, "email": email, "phone_number": phone_number}

    # Pass the data to the template
    return templates.TemplateResponse("registration_successful.html", {"request": request, **registration_results})
@app.get("/registration-successful", response_class=HTMLResponse)
def registration_successful(request: _fastapi.Request):
    return templates.TemplateResponse("registration_successful.html", {"request": request, "message": "Registration successful"})
