from database import cursor as cu, conn as cn
import bcrypt


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
    # Fetch the hashed password from the database for the provided admin_email
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



# Example of using the function

