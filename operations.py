from database import cursor as cu, conn as cn
import bcrypt
def add_user(username,email,password,phone_number):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    query = '''
           INSERT INTO users (username, hashed_password, phone_number, email)
           VALUES (?, ?, ?, ?)
       '''

    cu.execute(query, (username, hashed_password, phone_number, email))

    # Commit the changes
    cn.commit()

def check_user_credentials(email, password):
    # Fetch the hashed password from the database for the provided email
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

#add_user("sami","sasla","sasa","00202020")



# Example of using the function

