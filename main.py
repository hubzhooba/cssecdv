from typing import List
from fastapi import Depends, HTTPException, FastAPI,Query
#import sqlalchemy.orm as _orm
import fastapi as _fastapi
from fastapi import HTTPException, Form
from fastapi.responses import HTMLResponse,RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import operations as op
from fastapi.security import APIKeyQuery
from typing import List, Optional


templates = Jinja2Templates(directory="templates")

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


@app.get("/login", response_class=HTMLResponse)
def login_page(request: _fastapi.Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
def login(request: _fastapi.Request, email: str = Form(...), password: str = Form(...)):
    if op.check_user_credentials(email, password):
        # If credentils are correct, redirect to register page
        print("Crendtails are true")
        return RedirectResponse("/register")
    else:
        # If credentials are incorrect, reload login page
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
    if op.check_user_email_exists(email):
        # If the email already exists, reload the registration page
        return templates.TemplateResponse("register.html", {"request": request, "message": "Email already exists. Please choose a different email."})

    op.add_user(full_name, email, password, phone_number)
    registration_results = {"full_name": full_name, "email": email, "phone_number": phone_number}

    return templates.TemplateResponse("registration_successful.html", {"request": request, **registration_results})
@app.get("/registration-successful", response_class=HTMLResponse)
def registration_successful(request: _fastapi.Request):
    return templates.TemplateResponse("registration_successful.html", {"request": request, "message": "Registration successful"})


@app.get("/admin/login", response_class=HTMLResponse)
def admin_login_page(request: _fastapi.Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})


@app.post("/admin/login", response_class=HTMLResponse)
def admin_login(request: _fastapi.Request, email: str = Form(...), password: str = Form(...)):
    if op.check_admin_credentials(email, password):
        # Direct to Admin Panel if credentials are correct
        print("Admin Credentials are true")
        return templates.TemplateResponse("admin_panel.html", {"request": request})
    else:
        # If credentials are incorrect, reload the login page
        print("Admin Credentials are false")
        return templates.TemplateResponse("admin_login.html",
                                          {"request": request, "message": "Invalid email or password"})
API_KEY_QUERY_PARAMETER = APIKeyQuery(name="key", auto_error=False)


SECURITY_KEY = "hoobadooba"

def verify_security_key(api_key: str = Depends(API_KEY_QUERY_PARAMETER)):
    if api_key is None or api_key != SECURITY_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return api_key

@app.get("/admin/register", response_class=HTMLResponse, dependencies=[Depends(verify_security_key)])
def admin_register_page(request: _fastapi.Request):
    return templates.TemplateResponse("admin_register.html", {"request": request})

@app.post("/admin/register", response_class=HTMLResponse, dependencies=[Depends(verify_security_key)])
def admin_register(
        request: _fastapi.Request,
        username: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
        key: str = Depends(verify_security_key),  # Ensure key is present and valid
):
    if op.check_admin_email_exists(email):
        return templates.TemplateResponse("admin_register.html", {"request": request, "message": "Email already exists for an admin. Please choose a different email."})

    op.add_admin(username, email, password)
    registration_results = {"username": username, "email": email}

    return templates.TemplateResponse("admin_registration_successful.html",
                                      {"request": request, **registration_results})
@app.get("/admin/registration-successful", response_class=HTMLResponse)
def admin_registration_successful(request: _fastapi.Request):
    return templates.TemplateResponse("admin_registration_successful.html",
                                      {"request": request, "message": "Admin Registration successful"})


@app.get("/usernames", response_class=JSONResponse)
def get_all_usernames():
    usernames = op.getallusernames()
    return JSONResponse(content={"usernames": usernames}, status_code=200)


@app.get("/user_id/{username}", response_class=JSONResponse)
def get_user_id_by_username(username: str):
    user_id = op.getuser_id_byusername(username)
    if user_id is not None:
        return JSONResponse(content={"user_id": user_id}, status_code=200)
    else:
        raise HTTPException(status_code=404, detail="User not found")


@app.get("/user/{user_id}/posts", response_class=JSONResponse)
def get_titles_and_contents_by_user(user_id: int):
    posts = op.get_titles_and_contents_by_user_id(user_id)
    return JSONResponse(content={"posts": posts}, status_code=200)


@app.delete("/user/{user_id}/posts", response_class=JSONResponse)
def delete_posts_by_user(user_id: int):
    op.deleteposts_by_user_id(user_id)
    return JSONResponse(content={"message": f"All posts by user_id {user_id} deleted successfully."}, status_code=200)


@app.delete("/user/{user_id}", response_class=JSONResponse)
def delete_user_by_id(user_id: int):
    op.delete_user(user_id)
    return JSONResponse(content={"message": f"User with user_id {user_id} deleted successfully."}, status_code=200)


@app.get("/articles/{user_id}", response_class=JSONResponse)
def get_articles_by_user_id(user_id: int):
    articles = op.get_titles_and_contents_by_user_id_articles(user_id)
    return JSONResponse(content=articles)

@app.delete("/articles/{user_id}")
def delete_articles_by_user_id_endpoint(user_id: int):
    op.delete_articles_by_user_id(user_id)
    return {"message": f"All articles for user_id {user_id} deleted successfully."}

@app.delete("/posts/{post_id}")
def deletepostby_id(post_id: int ):
    op.deletepost(post_id)

@app.delete("/articles/{article_id}")
def deletearticleby_id(article_id:int):
    op.deletearticle(article_id)

