import logging
from fastapi import Depends, HTTPException, FastAPI
import fastapi as _fastapi
from fastapi import HTTPException, Form
from fastapi.responses import HTMLResponse,RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import operations as op
from fastapi.security import APIKeyQuery
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware


logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Authentication logging
def log_authentication(request: Request, user_id: int):
    logging.info(f"Authentication - User {user_id} logged in from {request.client.host}")

# Transactions logging
def log_transaction(request: Request, user_id: int, action: str):
    logging.info(f"Transaction - User {user_id}: {action} - IP: {request.client.host}")

# Admin actions logging
def log_admin_action(request: Request, admin_action: str):
    logging.info(f"Admin Action - {admin_action} from {request.client.host}")
templates = Jinja2Templates(directory="templates")

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
DEBUG_MODE = True

# Custom middleware for error handling
class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except HTTPException as exc:
            return self.handle_http_exception(request, exc)
        except Exception as exc:
            return self.handle_generic_exception(request, exc)

    def handle_http_exception(self, request: Request, exc: HTTPException):
        if DEBUG_MODE:
            # Include detailed stack trace
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail, "stack_trace": exc.__traceback__.as_list()}
            )
        else:
            # Generic error message
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": "An error occurred. Please try again later."}
            )

    def handle_generic_exception(self, request: Request, exc: Exception):
        if DEBUG_MODE:
            # Include detailed stack trace
            return JSONResponse(
                status_code=500,
                content={"detail": "An error occurred. Please try again later.", "stack_trace": exc.__traceback__.as_list()}
            )
        else:
            # Generic error message
            return JSONResponse(
                status_code=500,
                content={"detail": "An error occurred. Please try again later."}
            )

# Apply the custom middleware
app.add_middleware(ErrorHandlerMiddleware)
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

app.add_middleware(SessionMiddleware, secret_key="some-random-key",max_age=1500)

templates = Jinja2Templates(directory="templates")

# Use sessions to store user_id
@app.post("/login", response_class=HTMLResponse)
def login(request: _fastapi.Request, email: str = Form(...), password: str = Form(...)):
    user_id = op.check_user_credentials(email, password)
    if user_id is not False:
        # Store user_id in session
        request.session['user_id'] = user_id
        log_authentication(request, user_id)
        return RedirectResponse("/user_page",  status_code=303)
    else:
        # Handle invalid credentials
        logging.warning(f"Authentication failed for email: {email}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/user_page", response_class=HTMLResponse)
def user_page(request: _fastapi.Request):
    # Fetch user details or any other necessary data based on session user_id
    user_id = request.session.get('user_id')
    if user_id is None:
        # Handle if user_id is not found in session
        logging.warning("Unauthorized access to user page")
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    log_transaction(request, user_id, "Accessed user page")

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
        log_admin_action(request, "Admin logged in")
        print("Admin Credentials are true")
        return templates.TemplateResponse("admin_panel.html", {"request": request})
    else:
        # If credentials are incorrect, reload the login page
        print("Admin Credentials are false")
        logging.warning(f"Admin login failed for email: {email}")
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
        logging.warning(f"Admin registration failed: Email '{email}' already exists.")
        return templates.TemplateResponse("admin_register.html", {"request": request, "message": "Email already exists for an admin. Please choose a different email."})

    op.add_admin(username, email, password)
    registration_results = {"username": username, "email": email}
    
    logging.info(f"Admin registration successful: {email}")
    return templates.TemplateResponse("admin_registration_successful.html",
                                      {"request": request, **registration_results})

@app.get("/admin/registration-successful", response_class=HTMLResponse)
def admin_registration_successful(request: _fastapi.Request):
    return templates.TemplateResponse("admin_registration_successful.html",
                                      {"request": request, "message": "Admin Registration successful"})


@app.get("/usernames", response_class=JSONResponse)
def get_all_usernames():
    try:
        usernames = op.getallusernames()
        logging.info("Retrieved all usernames successfully")
        return JSONResponse(content={"usernames": usernames}, status_code=200)
    except Exception as e:
        logging.error(f"Failed to retrieve all usernames with error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/user_id/{username}", response_class=JSONResponse)
def get_user_id_by_username(username: str):
   try:
        user_id = op.getuser_id_byusername(username)
        if user_id is not None:
            logging.info(f"Retrieved user_id for username '{username}' successfully")
            return JSONResponse(content={"user_id": user_id}, status_code=200)
        else:
            logging.warning(f"User not found for username '{username}'")
            raise HTTPException(status_code=404, detail="User not found")
   except Exception as e:
        logging.error(f"Failed to retrieve user_id by username '{username}' with error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/user/{user_id}/posts", response_class=JSONResponse)
def get_titles_and_contents_by_user(user_id: int):
    try:
        posts = op.get_titles_and_contents_by_user_id(user_id)
        logging.info(f"Retrieved posts for user_id {user_id} successfully")
        return JSONResponse(content={"posts": posts}, status_code=200)
    except Exception as e:
        logging.error(f"Failed to retrieve posts for user_id {user_id} with error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Delete posts by user ID endpoint
@app.delete("/user/{user_id}/posts", response_class=JSONResponse)
def delete_posts_by_user(user_id: int):
    try:
        op.deleteposts_by_user_id(user_id)
        logging.info(f"All posts by user_id {user_id} deleted successfully")
        return JSONResponse(content={"message": f"All posts by user_id {user_id} deleted successfully."}, status_code=200)
    except Exception as e:
        logging.error(f"Failed to delete posts for user_id {user_id} with error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Delete user by ID endpoint
@app.delete("/user/{user_id}", response_class=JSONResponse)
def delete_user_by_id(user_id: int):
    try:
        op.delete_user(user_id)
        logging.info(f"User with user_id {user_id} deleted successfully")
        return JSONResponse(content={"message": f"User with user_id {user_id} deleted successfully."}, status_code=200)
    except Exception as e:
        logging.error(f"Failed to delete user with user_id {user_id} with error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Get articles by user ID endpoint
@app.get("/articles/{user_id}", response_class=JSONResponse)
def get_articles_by_user_id(user_id: int):
    try:
        articles = op.get_titles_and_contents_by_user_id_articles(user_id)
        logging.info(f"Retrieved articles for user_id {user_id} successfully")
        return JSONResponse(content=articles)
    except Exception as e:
        logging.error(f"Failed to retrieve articles for user_id {user_id} with error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Delete articles by user ID endpoint
@app.delete("/articles/{user_id}")
def delete_articles_by_user_id_endpoint(user_id: int):
    try:
        op.delete_articles_by_user_id(user_id)
        logging.info(f"All articles for user_id {user_id} deleted successfully")
        return {"message": f"All articles for user_id {user_id} deleted successfully."}
    except Exception as e:
        logging.error(f"Failed to delete articles for user_id {user_id} with error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    # Delete post by post ID endpoint
@app.delete("/posts/post/{post_id}")
def deletepostby_id(post_id: int):
    try:
        op.deletepost(post_id)
        logging.info(f"Post with post_id {post_id} deleted successfully")
        return JSONResponse(content={"message": f"Post with post_id {post_id} deleted successfully."}, status_code=200)
    except Exception as e:
        logging.error(f"Failed to delete post with post_id {post_id} with error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Delete article by article ID endpoint
@app.delete("/articles/article/{article_id}")
def deletearticleby_id(article_id: int):
    try:
        op.deletearticle(article_id)
        logging.info(f"Article with article_id {article_id} deleted successfully")
        return JSONResponse(content={"message": f"Article with article_id {article_id} deleted successfully."}, status_code=200)
    except Exception as e:
        logging.error(f"Failed to delete article with article_id {article_id} with error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Add post endpoint
@app.post("/add-post", response_class=JSONResponse)
def add_post_endpoint(
    user_id: int = Form(...),
    title: str = Form(...),
    content: str = Form(...),
):
    try:
        op.add_post(user_id, title, content)
        logging.info("Post added successfully")
        return JSONResponse(content={"message": "Post added successfully."}, status_code=200)
    except Exception as e:
        logging.error(f"Failed to add post with error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
# Add article endpoint
@app.post("/add-article", response_class=JSONResponse)
def add_article_endpoint(
    user_id: int = Form(...),
    title: str = Form(...),
    content: str = Form(...),
):
    try:
        op.add_article(user_id, title, content)
        logging.info("Article added successfully")
        return JSONResponse(content={"message": "Article added successfully."}, status_code=200)
    except Exception as e:
        logging.error(f"Failed to add article with error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Edit post endpoint
@app.put("/edit-post/{post_id}", response_class=JSONResponse)
def edit_post_endpoint(
    post_id: int,
    title: str = Form(...),
    content: str = Form(...),
):
    try:
        op.edit_post(post_id, title, content)
        logging.info(f"Post with post_id {post_id} edited successfully")
        return JSONResponse(content={"message": f"Post with post_id {post_id} edited successfully."}, status_code=200)
    except Exception as e:
        logging.error(f"Failed to edit post with post_id {post_id} with error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Edit article endpoint
@app.put("/edit-article/{article_id}", response_class=JSONResponse)
def edit_article_endpoint(
    article_id: int,
    title: str = Form(...),
    content: str = Form(...),
):
    try:
        op.edit_article(article_id, title, content)
        logging.info(f"Article with article_id {article_id} edited successfully")
        return JSONResponse(content={"message": f"Article with article_id {article_id} edited successfully."}, status_code=200)
    except Exception as e:
        logging.error(f"Failed to edit article with article_id {article_id} with error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Change password endpoint
@app.post("/change-password", response_class=JSONResponse)
def change_password_endpoint(
    user_id: int = Form(...),
    new_password: str = Form(...),
):
    try:
        op.change_user_password(user_id, new_password)
        logging.info(f"Password changed successfully for user_id {user_id}")
        return JSONResponse(content={"message": "Password changed successfully"}, status_code=200)
    except Exception as e:
        logging.error(f"Failed to change password for user_id {user_id} with error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Get username by user ID endpoint
@app.get("/username/{user_id}", response_class=JSONResponse)
def getusernamebyid(user_id: int):
    try:
        username = op.getusername_by_id(user_id)
        logging.info(f"Username retrieved successfully for user_id {user_id}")
        return JSONResponse(content={"username": username}, status_code=200)
    except Exception as e:
        logging.error(f"Failed to retrieve username for user_id {user_id} with error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
