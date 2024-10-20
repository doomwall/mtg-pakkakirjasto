from db import db
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash, generate_password_hash

def is_user(username):
    sql = text("SELECT id, username FROM users WHERE username=:username")
    result = db.session.execute(sql, {"username":username})
    profile = result.fetchone()
    print(profile)
    return profile[0]

def check_user_id(user_id, username):
    sql = text("SELECT id, username FROM users WHERE id=:user_id")
    result = db.session.execute(sql, {"user_id":user_id})
    profile = result.fetchone()
    if user_id == profile[0] and username == profile[1]:
        return True
    return False 

def get_create_date(id):
    sql = text("SELECT create_date FROM users WHERE id=:id")
    result = db.session.execute(sql, {"id":id})
    create_date = result.fetchone()
    return create_date

def check_password(id, password):
    sql = text("SELECT password FROM users WHERE id=:id")
    result = db.session.execute(sql, {"id":id})
    user_password = result.fetchone()
    hash_value = user_password.password
    if check_password_hash(hash_value, password):
        return True
    else:
        return False

def change_user_password(id, password):
    hash_value = generate_password_hash(password)
    sql = text("UPDATE users SET password=:hash_value WHERE id=:id")
    db.session.execute(sql, {"hash_value":hash_value, "id":id})
    db.session.commit()
    
# type: ignore