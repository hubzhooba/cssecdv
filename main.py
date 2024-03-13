from fastapi import Depends, HTTPException, FastAPI
import fastapi as _fastapi
from fastapi import HTTPException, Form
from fastapi.responses import HTMLResponse,RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import operations as op
from fastapi.security import APIKeyQuery
from starlette.middleware.sessions import SessionMiddleware


# comment

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
##done

@app.get("/login", response_class=HTMLResponse)
def login_page(request: _fastapi.Request):
    return templates.TemplateResponse("login.html", {"request": request})

app.add_middleware(SessionMiddleware, secret_key="some-random-key")

templates = Jinja2Templates(directory="templates")

# Use sessions to store user_id
@app.post("/login", response_class=HTMLResponse)
def login(request: _fastapi.Request, email: str = Form(...), password: str = Form(...)):
    user_id = op.check_user_credentials(email, password)
    if user_id is not False:
        # Store user_id in session
        request.session['user_id'] = user_id
        return RedirectResponse("/user_page",  status_code=303)
    else:
        # Handle invalid credentials
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/user_page", response_class=HTMLResponse)
def user_page(request: _fastapi.Request):
    # Fetch user details or any other necessary data based on session user_id
    user_id = request.session.get('user_id')
    if user_id is None:
        # Handle if user_id is not found in session
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Render the user page template with the fetched details
    return templates.TemplateResponse("user_page.html", {"request": request, "user_id": user_id})
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


SECURITY_KEY = "hooba"

def verify_security_key(api_key: str = Depends(API_KEY_QUERY_PARAMETER)):
    if api_key is None or api_key != SECURITY_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return api_key

@app.get("/admin/register", response_class=HTMLResponse, dependencies=[Depends(verify_security_key)])
def admin_register_page(request: _fastapi.Request):
    return templates.TemplateResponse("admin_register.html", {"request": request})

@app.post("/admin/register", response_class=HTMLResponse)
def admin_register(
        request: _fastapi.Request,
        username: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
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

@app.delete("/posts/post/{post_id}")
def deletepostby_id(post_id: int ):
    op.deletepost(post_id)

@app.delete("/articles/article/{article_id}")
def deletearticleby_id(article_id:int):
    op.deletearticle(article_id)

@app.post("/add-post", response_class=JSONResponse)
def add_post_endpoint(
    user_id: int = Form(...),
    title: str = Form(...),
    content: str = Form(...),
):
    op.add_post(user_id, title, content)
    return JSONResponse(content={"message": "Post added successfully."}, status_code=200)

@app.post("/add-article", response_class=JSONResponse)
def add_article_endpoint(
    user_id: int = Form(...),
    title: str = Form(...),
    content: str = Form(...),
):
    op.add_article(user_id, title, content)
    return JSONResponse(content={"message": "Article added successfully."}, status_code=200)

@app.put("/edit-post/{post_id}", response_class=JSONResponse)
def edit_post_endpoint(
    post_id: int,
    title: str = Form(...),
    content: str = Form(...),
):
    op.edit_post(post_id, title, content)
    return JSONResponse(content={"message": f"Post with post_id {post_id} edited successfully."}, status_code=200)

@app.put("/edit-article/{article_id}", response_class=JSONResponse)
def edit_article_endpoint(
    article_id: int,
    title: str = Form(...),
    content: str = Form(...),
):
    op.edit_article(article_id, title, content)
    return JSONResponse(content={"message": f"Article with article_id {article_id} edited successfully."}, status_code=200)

@app.post("/change-password", response_class=JSONResponse)
def change_password_endpoint(
    user_id: int = Form(...),
    new_password: str = Form(...),
):
    try:
        # Call the existing function to change the user password
        op.change_user_password(user_id, new_password)

        return JSONResponse(content={"message": "Password changed successfully"}, status_code=200)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/username/{user_id}", response_class=JSONResponse)
def getusernamebyid(user_id: int):
    username = op.getusername_by_id(user_id)
    return JSONResponse(content={"username": username}, status_code=200)