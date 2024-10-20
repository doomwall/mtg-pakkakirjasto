from db import db
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date

def try_login(username, password):
    error = None
    sql = text("SELECT id, password FROM users WHERE username=:username")
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()
    if user is None:
        error = "Virheellinen käyttäjänimi"
        return error
    else:
        hash_value = user.password
        if check_password_hash(hash_value, password):
            return user
        else:
            error = "Virheellinen salasana"
            return error

def create_new_user(username, password):
    hash_value = generate_password_hash(password)
    create_date = date.today()
    sql = text("INSERT INTO users (username, password, create_date) VALUES (:username, :password, :create_date)")
    db.session.execute(sql, {"username":username, "password":hash_value, "create_date":create_date})
    db.session.commit()

def check_username():
    sql = text("SELECT username FROM users")
    result = db.session.execute(sql)
    all_users = result.fetchall()
    return all_users