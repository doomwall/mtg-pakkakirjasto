from app import app
from db import db
from flask import render_template, make_response
from flask import redirect, render_template, request, session, url_for
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash
from profiili import is_user, check_user_id
from hae_pakat import hae_omat_pakat, luo_uusi_pakka_to_db, hae_pakka
from login import try_login

import base64
import visits
import kortit

app.secret_key = getenv("SECRET_KEY")

def hae_kayttaja():
    user = session.get("username")

@app.route("/")
def index():
    visits.add_visit()
    counter = visits.get_counter()

    error = request.args.get("error")
    return render_template("index.html", counter=counter, error=error)

@app.route("/login",methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    user = try_login(username)
    print(user)

    if user is None:
        return redirect(url_for('index', error="Virheellinen käyttäjänimi"))
    else:
        hash_value = user[1]
        if check_password_hash(hash_value, password):
            session["username"] = username
            user_id = is_user(session["username"])
            session["id"] = user_id
            return redirect("/")
        else:
            return redirect(url_for('index', error="Virheellinen salasana"))


@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")


@app.route("/create_user")
def create_user():
    return render_template("create_user.html")


@app.route("/create_user_to_db",methods=["POST"])
def create_user_to_db():
    username = request.form["username"]
    password = request.form["password"]
    try_login.create_new_user(username, password)
    return redirect("/")

@app.route("/kortit")
def kortit_sivu():
    all_cards = kortit.hae_kortit()
    return render_template("kortit.html", all_cards=all_cards)

@app.route("/uusi_kortti")
def uusi_kortti():
    return render_template("uusi_kortti.html")

@app.route("/luo_uusi_kortti",methods=["POST"])
def luo_uusi_kortti():
    card_name = request.form["card_name"]
    card_text = request.form["card_text"]
    data = request.files["image_data"]

    image_name = data.filename
    image_data = data.read()
    
    if not image_name.endswith(".jpg"):
        return "Invalid filename"
    
    kortit.luo_uusi_kortti_to_db(card_name, card_text, image_data)
    all_cards = kortit.hae_kortit()
    return redirect("/kortit")

@app.route("/kortti/<int:id>")
def kortti(id):
    card = kortit.hae_kortti(id)
    print(id)
    card_name = card[1]
    card_text = card[2]
    image_data = card[3]
    image_base64 = base64.b64encode(image_data).decode('utf-8')
    
    img_tag = f"data:image/jpeg;base64,{image_base64}"

    return render_template("kortti.html", id=id, card_name=card_name, card_text=card_text, image=img_tag)

@app.route("/profiili/<int:id>")
def profiili(id):
    #if is_admin():
    #    allow = True

    if "id" not in session or "username" not in session:
        return redirect(url_for('index', error="Sinun täytyy olla kirjautunut sisään!"))
    
    if session["id"] != id:
        return redirect(url_for('index', error="Sinulla ei ole oikeutta nähdä tätä profiilia"))
    
    if check_user_id(session["id"], session["username"]):
        return render_template("profiili.html")

    return redirect(url_for('index', error="Sinulla ei ole oikeutta nähdä tätä profiilia"))

@app.route("/omat_pakat/<int:id>")
def omat_pakat(id):
    if "id" not in session or "username" not in session:
        return redirect(url_for('index', error="Sinun täytyy olla kirjautunut sisään!"))
    
    if session["id"] != id:
        return redirect(url_for('index', error="Sinulla ei ole oikeutta nähdä tätä"))
    
    if check_user_id(session["id"], session["username"]):
        all_decks = hae_omat_pakat(session["id"])
        return render_template("omat_pakat.html", all_decks=all_decks)

    return redirect(url_for('index', error="Sinulla ei ole oikeutta nähdä tätä profiilia"))

@app.route("/uusi_pakka")
def uusi_pakka():
    return render_template("uusi_pakka.html")

@app.route("/luo_uusi_pakka",methods=["POST"])
def luo_uusi_pakka():
    deck_name = request.form["deck_name"]
    deck_text = request.form["deck_text"]
    
    luo_uusi_pakka_to_db(session["id"], deck_name, deck_text)
    return redirect(url_for('omat_pakat', id=session["id"]))

@app.route("/pakka/<int:id>")
def pakka(id):
    deck = hae_pakka(id)
    deck_name = deck[1]
    deck_text = deck[2]

    all_cards = kortit.hae_kortit_teksti()
    #tarkistaa public
    if deck[3]:
        return render_template("pakka.html", deck=deck, deck_name=deck_name, deck_text=deck_text, all_cards=all_cards)
    
    if deck[0] != session["id"]:
        return redirect(url_for('index', error="Sinulla ei ole oikeutta nähdä tätä pakkaa"))
    else:
        return render_template("pakka.html", deck=deck, deck_name=deck_name, deck_text=deck_text, all_cards=all_cards)
    
@app.route("/lisaa_kortti_pakkaan",methods=["POST"])
def lisaa_kortti_pakkaan():
    deck_id = request.form["deck_id"]
    card_id = request.form["card_id"]

