from app import app
from db import db
from flask import render_template, make_response, flash
from flask import redirect, render_template, request, session, url_for
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from profile import is_user, check_user_id
from get_decks import get_own_decks, create_new_deck_to_db, get_deck, add_card_to_deck_db, get_deck_cards
from get_decks import plus_card, minus_card, get_all_public_decks, set_deck_privacy, get_number_public_decks, get_card_quantity
from login import try_login, create_new_user
from cards import get_cards, get_cards_text, create_new_card_to_db, get_card, get_card_id_by_name, alter_card_image_url
from secrets import token_hex

import os
import base64
import visits

UPLOAD_FOLDER = "static/images/"
ALLOWED_EXTENSIONS = {'.jpg', '.png', '.jpeg', '.gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = getenv("SECRET_KEY")

def get_user():
    user = session.get("username")

@app.route("/")
def index():
    visits.add_visit()
    counter = visits.get_counter()
    public_decks_to_show = get_number_public_decks(3)

    error = request.args.get("error")
    return render_template("index.html", counter=counter, error=error, public_decks=public_decks_to_show)

@app.route("/login",methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    user = try_login(username, password)
    print(user)

    if user is None:
        return redirect(url_for('index', error="Virheellinen käyttäjänimi"))
    else:
        hash_value = user[1]
        if check_password_hash(hash_value, password):
            session["username"] = username
            session["csrf_token"] = token_hex(16)
            user_id = is_user(session["username"])
            session["id"] = user_id
            return redirect("/")
        else:
            return redirect(url_for('index', error="Virheellinen salasana"))


@app.route("/logout")
def logout():
    del session["id"]
    del session["username"]
    del session["csrf_token"]
    return redirect("/")


@app.route("/create_user")
def create_user():
    username = request.form.get("username")
    error = request.args.get("error")
    return render_template("create_user.html", error=error)


@app.route("/create_user_to_db",methods=["GET", "POST"])
def create_user_to_db():
    error = ""
    username = request.form.get("username")
    password = request.form.get("password")
    password2 = request.form.get("password2")

    if not username:
        error = "Käyttäjänimi on pakollinen."
        return render_template("create_user.html", error=error)
    
    if not password:
        error = "Salasana on pakollinen."
        return render_template("create_user.html", error=error)
    
    if password != password2:
        error = "Salasanat eivät täsmää."
        return render_template("create_user.html", error=error)
    
    if not password.isalnum():
        error = "Salasanassa on erikoismerkkejä."
        return render_template("create_user.html", error=error)
    
    if len(password) < 8 or len(password) > 20:
        error = "Salasana on liian lyhyt tai pitkä."
        return render_template("create_user.html", error=error)
    
    create_new_user(username, password)
    return redirect("/")

@app.route("/cards")
def cards_page():
    all_cards = get_cards()

    return render_template("cards.html", all_cards=all_cards)

@app.route("/new_card")
def new_card():
    return render_template("new_card.html")

@app.route("/create_new_card",methods=["GET","POST"])
def create_new_card():
    error = ""

    if session["csrf_token"] != request.form["csrf_token"]:
        os.abort(403)
    
    if request.method == "POST":
        if 'file' not in request.files:
            error = "Virheellinen tiedosto."
            return render_template("new_card.html", error=error)
        
        file = request.files['file']
        if file.filename == '':
            error = "Tiedostoa ei valittu."
            return render_template("new_card.html", error=error)
    
        card_name = request.form["card_name"]
        card_text = request.form["card_text"]

        if not card_name:
            error = "Kortilla ei ole nimeä."
            return render_template("new_card.html", error=error)
        
        if not card_text:
            error = "Kortilla ei ole tekstiä."
            return render_template("new_card.html", error=error)
        
        file_ext = os.path.splitext(file.filename)[1]
        print(file_ext)
        if file_ext not in ALLOWED_EXTENSIONS:
            error = "Virheellinen tiedosto."
            return render_template("new_card.html", error=error)

        
        create_new_card_to_db(card_name, card_text)
        file_number = get_card_id_by_name(card_name)
        filename = secure_filename(f"{file_number}{file_ext}")
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        alter_card_image_url(file_number, filename)

        return redirect("/cards")


@app.route("/card/<int:id>")
def card(id):
    card = get_card(id)
    return render_template("card.html", card=card)

@app.route("/profile/<int:id>")
def profile(id):
    #if is_admin():
    #    allow = True

    if "id" not in session or "username" not in session:
        return redirect(url_for('index', error="Sinun täytyy olla kirjautunut sisään!"))
    
    if session["id"] != id:
        return redirect(url_for('index', error="Sinulla ei ole oikeutta nähdä tätä profiilia"))
    
    if check_user_id(session["id"], session["username"]):
        return render_template("profile.html")

    return redirect(url_for('index', error="Sinulla ei ole oikeutta nähdä tätä profiilia"))

@app.route("/decks")
def all_decks():
    all_public_decks = get_all_public_decks()
    return render_template("decks.html", all_public_decks=all_public_decks)
    

@app.route("/my_decks/<int:id>")
def my_decks(id):
    if "id" not in session or "username" not in session:
        return redirect(url_for('index', error="Sinun täytyy olla kirjautunut sisään!"))
    
    if session["id"] != id:
        return redirect(url_for('index', error="Sinulla ei ole oikeutta nähdä tätä"))
    
    if check_user_id(session["id"], session["username"]):
        all_decks = get_own_decks(session["id"])
        return render_template("my_decks.html", all_decks=all_decks)

    return redirect(url_for('index', error="Sinulla ei ole oikeutta nähdä tätä profiilia"))

@app.route("/new_deck")
def new_deck():
    return render_template("new_deck.html")

@app.route("/create_new_deck",methods=["POST"])
def create_new_deck():
    deck_name = request.form["deck_name"]
    deck_text = request.form["deck_text"]

    if session["csrf_token"] != request.form["csrf_token"]:
        os.abort(403)
    
    create_new_deck_to_db(session["id"], deck_name, deck_text)
    return redirect(url_for('my_decks', id=session["id"]))

@app.route("/deck/<int:id>")
def deck(id):
    all_cards = []
    deck = get_deck(id)
    deck_id = deck[0]
    deck_owner = deck[1]
    deck_name = deck[2]
    deck_text = deck[3]
    deck_public = deck[4]


    if deck_public:
        deck_status = "Julkinen"
    else:
        deck_status = "Piilotettu"

    deck_cards = get_deck_cards(deck_id)
    print(deck_cards)
    all_cards = get_cards()

    #tarkistaa public
    if deck[4]:
        return render_template("deck.html", 
                               deck=deck, 
                               deck_id=deck_id, 
                               deck_name=deck_name, 
                               deck_text=deck_text, 
                               deck_cards=deck_cards,
                               deck_status=deck_status,
                               all_cards=all_cards)
    elif not session.get("id"):
         return redirect(url_for('index', error="Sinulla ei ole oikeutta nähdä tätä pakkaa"))
    
    if deck_owner != session.get("id"):
        return redirect(url_for('index', error="Sinulla ei ole oikeutta nähdä tätä pakkaa"))
    else:
        return render_template("deck.html", 
                               deck=deck, 
                               deck_id=deck_id, 
                               deck_name=deck_name, 
                               deck_text=deck_text,
                               deck_cards=deck_cards,
                               deck_status=deck_status)
    
@app.route("/add_card_to_deck",methods=["POST"])
def add_card_to_deck():
    deck_id = request.form["deck_id"]
    card_id = request.form["card_id"]
    add_card_to_deck_db(deck_id, card_id)

    return redirect(url_for("deck", id=deck_id))

@app.route("/plus",methods=["POST"])
def plus():
    deck_id = request.form["deck_id"]
    card_id = request.form["card_id"]
    plus_card(deck_id, card_id)

    new_amount = get_card_quantity(deck_id, card_id)
    return str(new_amount)

@app.route("/minus",methods=["POST"])
def minus():
    deck_id = request.form["deck_id"]
    card_id = request.form["card_id"]
    minus_card(deck_id, card_id)

    new_amount = get_card_quantity(deck_id, card_id)
    return str(new_amount)

@app.route("/set_privacy",methods=["POST"])
def set_privacy():
    status = ""
    deck_id = request.form["deck_id"]
    deck_status = request.form["deck_status"]

    if deck_status == "Julkinen":
        status = False
    elif deck_status == "Piilotettu":
        status = True

    set_deck_privacy(deck_id, status)
    return redirect(url_for("deck", id=deck_id))