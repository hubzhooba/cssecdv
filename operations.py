from database import cursor as cu, conn as cn
import bcrypt
from typing import List, Optional


def check_user_email_exists(email):
    # Check if the email exists in the users table
    query_user = '''
        SELECT email FROM users
        WHERE email = ?
    '''
    cu.execute(query_user, (email,))
    user_result = cu.fetchone()

    # Return True if the email exists in the users table
    return bool(user_result)

def check_admin_email_exists(email):
    # Check if the email exists in the admins table
    query_admin = '''
        SELECT admin_email FROM admins
        WHERE admin_email = ?
    '''
    cu.execute(query_admin, (email,))
    admin_result = cu.fetchone()

    # Return True if the email exists in the admins table
    return bool(admin_result)

def add_user(username, email, password, phone_number):
    if not check_user_email_exists(email):
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        query = '''
               INSERT INTO users (username, hashed_password, phone_number, email)
               VALUES (?, ?, ?, ?)
           '''
        cu.execute(query, (username, hashed_password, phone_number, email))
        cn.commit()
        print("User added successfully.")
    else:
        print("Email already exists for a user. Please choose a different email.")

def check_user_credentials(email, password):
    query = '''
        SELECT hashed_password FROM users
        WHERE email = ?
    '''
    cu.execute(query, (email,))
    result = cu.fetchone()

    if result:
        # If user with the provided email exists, check the password
        hashed_password_from_db = result[0]
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password_from_db)

    return False
def add_admin(username, email, password):
    if not check_admin_email_exists(email):
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        query = '''
               INSERT INTO admins (username, admin_email, hashed_password)
               VALUES (?, ?, ?)
           '''
        cu.execute(query, (username, email, hashed_password))
        cn.commit()
        print("Admin added successfully.")
    else:
        print("Email already exists for an admin. Please choose a different email.")

def check_admin_credentials(admin_email, password):
    # Fetch the hashed password from the database for the provided admin-email
    query = '''
        SELECT hashed_password FROM admins
        WHERE admin_email = ?
    '''
    cu.execute(query, (admin_email,))
    result = cu.fetchone()

    if result:
        hashed_password_from_db = result[0]
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password_from_db)

    return False
#add_user("sami","sasla","sasa","00202020")


def getallusernames() -> List[str]:
    query = '''
        SELECT username FROM users
    '''
    cu.execute(query)
    usernames = cu.fetchall()

    userlist = [username[0] for username in usernames]

    return userlist


def getuser_id_byusername(username: str) -> Optional[int]:
    query = '''
        SELECT user_id FROM users
        WHERE username = ?
    '''
    cu.execute(query, (username,))
    result = cu.fetchone()

    return result[0] if result else None

def get_titles_and_contents_by_user_id(user_id: int) -> List[dict]:
    query = '''
        SELECT post_id, title, content FROM posts
        WHERE user_id = ?
    '''
    cu.execute(query, (user_id,))
    posts = cu.fetchall()

    posts_list = [
        {
            "id": post[0], 
            "title": post[1],
            "content": post[2],
        }
        for post in posts
    ]

    return posts_list

def deleteposts_by_user_id(user_id: int):
    query = '''
        DELETE FROM posts
        WHERE user_id = ?
    '''
    cu.execute(query, (user_id,))
    cn.commit()
    print(f"All posts by user_id {user_id} deleted successfully.")

def delete_user(user_id: int):
    query = '''
        DELETE FROM users
        WHERE user_id = ?
    '''
    cu.execute(query, (user_id,))
    cn.commit()
    print(f"User with user_id {user_id} deleted successfully.")

def get_titles_and_contents_by_user_id_articles(user_id: int) -> List[dict]:
    query = '''
        SELECT article_id, title, content FROM articles
        WHERE user_id = ?
    '''
    cu.execute(query, (user_id,))
    articles = cu.fetchall()

    articles_list = [
        {
            "id": article[0], 
            "title": article[1],
            "content": article[2],
        }
        for article in articles
    ]

    return articles_list

def delete_articles_by_user_id(user_id: int):
    query = '''
        DELETE FROM articles
        WHERE user_id = ?
    '''
    cu.execute(query, (user_id,))
    cn.commit()
    print(f"All articles by user_id {user_id} deleted successfully.")


def deletepost(post_id:int):
    query='''
    DELETE FROM posts 
    where post_id = ?
    '''
    cu.execute(query,(post_id,))
    cn.commit()

def deletearticle(article_id:int):
    query='''
    DELETE FROM articles
    where article_id = ?
    '''
    cu.execute(query,(article_id,))
    cn.commit()

