from db import db
from sqlalchemy.sql import text

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
# type: ignore