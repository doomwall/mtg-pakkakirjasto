from db import db
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash, generate_password_hash

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
    sql = text("INSERT INTO users (username, password) VALUES (:username, :password)")
    db.session.execute(sql, {"username":username, "password":hash_value})
    db.session.commit()