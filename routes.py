from app import app
from db import db
from flask import render_template
from flask import redirect, render_template, request, session, url_for
from os import getenv
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from profile import is_user, check_user_id, get_create_date, change_user_password, check_password
from get_decks import get_own_decks, create_new_deck_to_db, get_deck, add_card_to_deck_db, get_deck_cards, remove_card_from_deck
from get_decks import plus_card, minus_card, get_all_public_decks, set_deck_privacy, get_number_public_decks, get_card_quantity
from get_decks import remove_deck_from_db
from login import try_login, create_new_user, check_username
from cards import get_cards, create_new_card_to_db, get_card, get_card_id_by_name, alter_card_image_url, check_card_name, remove_card_from_db
from secrets import token_hex

import os
import visits

UPLOAD_FOLDER = "static/images/"
ALLOWED_EXTENSIONS = {'.jpg', '.png', '.jpeg', '.gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = getenv("SECRET_KEY")

def get_user():
    user = session.get("username")

@app.route("/")
def index():
    error = ""
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
    
    if user is None:
        return render_template('index.html', error="Virheellinen käyttäjänimi")
    else:
        hash_value = user[1]
        if check_password_hash(hash_value, password):
            session["username"] = username
            session["csrf_token"] = token_hex(16)
            user_id = is_user(session["username"])
            session["id"] = user_id

            return redirect("/")
        else:
            return render_template("index.html", error="Väärä salasana")


@app.route("/logout")
def logout():
    del session["id"]
    del session["username"]
    del session["csrf_token"]
    return redirect("/")


@app.route("/create_user")
def create_user():
    return render_template("create_user.html")


@app.route("/create_user_to_db",methods=["GET", "POST"])
def create_user_to_db():
    errors = []
    username = request.form.get("username")
    password = request.form.get("password")
    password2 = request.form.get("password2")
    
    usernames = check_username()
    all_users = [i[0] for i in usernames]

    if username in all_users:
        errors.append("Käyttäjänimi on jo käytössä")

    if not username:
        errors.append("Käyttäjänimi on pakollinen.")
    
    if not password:
        errors.append("Salasana on pakollinen.")
    
    if password != password2:
        errors.append("Salasanat eivät täsmää.")
    
    if not password.isalnum():
        errors.append("Salasanassa on erikoismerkkejä.")

    if len(password) < 8 or len(password) > 20:
        errors.append("Salasana on liian lyhyt tai pitkä.")

    if errors:
        return render_template("create_user.html", errors=errors)
    
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
    errors = []

    if session["csrf_token"] != request.form["csrf_token"]:
        os.abort(403)
    
    if request.method == "POST":
        card_name = request.form["card_name"]
        card_text = request.form["card_text"]

        card_names = check_card_name()
        names_list = [i[0] for i in card_names]

        if card_name in names_list:
            errors.append("Samalla nimellä on jo luotu kortti.")

        if 'file' not in request.files:
            errors.append("Virheellinen tiedosto.")
            
        file = request.files['file']
        
        if file.filename == '':
            errors.append("Tiedostoa ei valittu.")

        if not card_name:
            errors.append("Kortilla ei ole nimeä.")
        
        if not card_text:
            errors.append("Kortilla ei ole tekstiä.")
        
        file_ext = os.path.splitext(file.filename)[1]

        if file_ext not in ALLOWED_EXTENSIONS:
            errors.append("Virheellinen tiedosto-muoto.")

        if errors:
            return render_template("new_card.html", errors=errors)

        
        create_new_card_to_db(card_name, card_text)
        file_number = get_card_id_by_name(card_name)
        filename = secure_filename(f"{file_number}{file_ext}")
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        alter_card_image_url(file_number, filename)

        return redirect("/cards")


@app.route("/delete_card",methods=["POST"])
def delete_card():
    if session["csrf_token"] != request.form["csrf_token"]:
        os.abort(403)

    card_id = request.form["card_id"]
    remove_card_from_db(card_id)
    return redirect("/cards")


@app.route("/card/<int:id>")
def card(id):
    card = get_card(id)
    return render_template("card.html", card=card)

@app.route("/profile/<int:id>")
def profile(id):
    errors = []
    success = []

    if "id" not in session or "username" not in session:
        return redirect(url_for('index', error="Sinun täytyy olla kirjautunut sisään!"))
    
    if session["id"] != id:
        return redirect(url_for('index', error="Sinulla ei ole oikeutta nähdä tätä profiilia"))
    
    if check_user_id(session["id"], session["username"]):
        time_to_convert = get_create_date(id)[0]
        create_date = time_to_convert.strftime('%d.%m.%Y')
        return render_template("profile.html", create_date=create_date)

    return redirect(url_for('index', error="Sinulla ei ole oikeutta nähdä tätä profiilia"))


@app.route("/change_password",methods=["POST"])
def change_password():
    errors = []
    success = []
    id = session["id"]
    current_password = request.form["current_password"]
    new_password = request.form["new_password"]
    new_password2 = request.form["new_password2"]

    if session["csrf_token"] != request.form["csrf_token"]:
        os.abort(403)
    
    if request.method == "POST":
        if not current_password:
            errors.append("Syötä nykyinen salasana.")
        
        if new_password != new_password2:
            errors.append("Uudet salasanat eivät täsmää.")
        
        if not new_password.isalnum():
            errors.append("Salasanassa on erikoismerkkejä.")

        if len(new_password) < 8 or len(new_password) > 20:
            errors.append("Salasana on liian lyhyt tai pitkä.")

        password_check = check_password(id, current_password)

        if password_check and not errors:
            change_user_password(id, new_password)
            success.append("Salasanan vaihto onnistui!")
            return render_template("profile.html", id=id, success=success)
        else:
            errors.append("Nykyinen salasana on väärin")
        
        if errors:
            return render_template("profile.html", id=id, errors=errors)
        
        return redirect(url_for('profile', id=id))



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

@app.route("/delete_deck",methods=["POST"])
def delete_deck():
    if session["csrf_token"] != request.form["csrf_token"]:
        os.abort(403)

    deck_id = request.form["deck_id"]
    remove_deck_from_db(deck_id)
    return redirect(url_for("my_decks", id=session["id"]))



@app.route("/new_deck")
def new_deck():
    return render_template("new_deck.html")

@app.route("/create_new_deck",methods=["POST"])
def create_new_deck():
    error = ""

    deck_name = request.form["deck_name"]
    deck_text = request.form["deck_text"]

    if session["csrf_token"] != request.form["csrf_token"]:
        os.abort(403)

    if not deck_name:
        error = "Pakalla ei ole nimeä."

    if error:
        return render_template("new_deck.html", error=error)
    
    create_new_deck_to_db(session["id"], deck_name, deck_text)
    return redirect(url_for('my_decks', id=session["id"]))

@app.route("/deck/<int:id>")
def deck(id):
    all_cards = []
    deck = get_deck(id)
    deck_public = deck[4]


    if deck_public:
        deck_status = "Julkinen"
    else:
        deck_status = "Piilotettu"

    deck_cards = get_deck_cards(deck[0])
    
    all_cards = get_cards()

    #tarkistaa public
    if deck[4]:
        return render_template("deck.html", 
                               deck=deck,
                               deck_status=deck_status,
                               deck_cards=deck_cards,
                               all_cards=all_cards)
    elif not session.get("id"):
         return redirect(url_for('index', error="Sinulla ei ole oikeutta nähdä tätä pakkaa"))
    
    if deck[1] != session.get("id"):
        return redirect(url_for('index', error="Sinulla ei ole oikeutta nähdä tätä pakkaa"))
    else:
        return render_template("deck.html", 
                               deck=deck,
                               deck_cards=deck_cards,
                               deck_status=deck_status,
                               all_cards=all_cards)
    
@app.route("/add_card_to_deck",methods=["POST"])
def add_card_to_deck():
    #if session["csrf_token"] != request.form["csrf_token"]:
    #    os.abort(403)

    deck_id = request.form["deck_id"]
    card_id = request.form["card_id"]
    
    add_card_to_deck_db(deck_id, card_id)
    return redirect(url_for("deck", id=deck_id))

@app.route("/plus",methods=["POST"])
def plus():
    if session["csrf_token"] != request.form["csrf_token"]:
        os.abort(403)

    deck_id = request.form["deck_id"]
    card_id = request.form["card_id"]
    
    plus_card(deck_id, card_id)

    new_amount = get_card_quantity(deck_id, card_id)
    return str(new_amount)

@app.route("/minus",methods=["POST"])
def minus():
    if session["csrf_token"] != request.form["csrf_token"]:
        os.abort(403)

    deck_id = request.form["deck_id"]
    card_id = request.form["card_id"]
    
    minus_card(deck_id, card_id)
    new_amount = get_card_quantity(deck_id, card_id)
    
    return str(new_amount)


@app.route("/remove_card",methods=["POST"])
def remove_card():
    if session["csrf_token"] != request.form["csrf_token"]:
        os.abort(403)

    deck_id = request.form["deck_id"]
    card_id = request.form["card_id"]

    remove_card_from_deck(deck_id, card_id)
    return redirect(url_for("deck", id=deck_id))

@app.route("/set_privacy",methods=["POST"])
def set_privacy():
    if session["csrf_token"] != request.form["csrf_token"]:
        os.abort(403)

    status = ""
    deck_id = request.form["deck_id"]
    deck_status = request.form["deck_status"]

    if deck_status == "Julkinen":
        status = False
    elif deck_status == "Piilotettu":
        status = True

    set_deck_privacy(deck_id, status)
    return redirect(url_for("deck", id=deck_id))