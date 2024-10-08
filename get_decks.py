from db import db
from sqlalchemy.sql import text

import base64
import random

def get_own_decks(id):
    sql = text("SELECT * FROM decks WHERE deck_owner=:id AND visible=TRUE ORDER BY id")
    result = db.session.execute(sql, {"id":id})
    all_decks = result.fetchall()
    return all_decks

def get_all_public_decks():
    sql = text("SELECT * FROM decks WHERE public = TRUE ORDER BY id")
    result = db.session.execute(sql)
    all_public_decks = result.fetchall()
    return all_public_decks

def get_number_public_decks(number):
    decks_to_show = []

    sql = text("SELECT COUNT(*) FROM decks WHERE public = TRUE")
    result = db.session.execute(sql)
    number_of_public_decks = result.fetchone()[0]
    

    if number > number_of_public_decks:
        number = number_of_public_decks

    randoms = random.sample(range(number_of_public_decks), number)
    
    sql2 = text("SELECT * FROM decks WHERE public = TRUE")
    result2 = db.session.execute(sql2)
    all_of_public_decks = result2.fetchall()
    for i in randoms:
        decks_to_show.append(all_of_public_decks[i])

    return decks_to_show

def create_new_deck_to_db(user_id, deck_name, deck_text):
    sql = text("INSERT INTO decks (deck_owner, deck_name, deck_text) VALUES (:deck_owner, :deck_name, :deck_text)")
    db.session.execute(sql, {"deck_owner":user_id, "deck_name":deck_name, "deck_text":deck_text})
    db.session.commit()

def get_deck(id):
    sql = text("SELECT * FROM decks WHERE id=:id")
    result = db.session.execute(sql, {"id":id})
    deck = result.fetchone()
    return deck

def add_card_to_deck_db(deck_id, card_id):
    sql_check = text("SELECT card_id FROM deck_with_cards WHERE deck_id=:deck_id AND card_id=:card_id")
    result = db.session.execute(sql_check, {"deck_id":deck_id, "card_id":card_id})
    check_cards = result.fetchall()

    if not check_cards:
        sql = text("INSERT INTO deck_with_cards (deck_id, card_id) VALUES (:deck_id, :card_id)")
        db.session.execute(sql, {"deck_id":deck_id, "card_id":card_id})
        db.session.commit()
    else:
        sql = text("UPDATE deck_with_cards SET quantity = quantity + 1 WHERE deck_id=:deck_id AND card_id=:card_id")
        db.session.execute(sql, {"deck_id":deck_id, "card_id":card_id})
        db.session.commit()

def get_deck_cards(deck_id):
    card_names = []
    sql = text("SELECT card_id, quantity FROM deck_with_cards WHERE deck_id=:deck_id AND quantity>0")
    result = db.session.execute(sql, {"deck_id":deck_id})
    decks_cards = result.fetchall()
    sql2 = text("SELECT id, card_name, card_text, image_url FROM cards WHERE id=:card_id")
    for card_id in decks_cards:
        search = db.session.execute(sql2, {"card_id":card_id[0]})
        card = search.fetchone()
        card = (card, card_id[1], str(card[0]))
        print(card)
        card_names.append(card)
    return card_names

def plus_card(deck_id, card_id):
    sql = text("UPDATE deck_with_cards SET quantity = quantity + 1 WHERE deck_id=:deck_id AND card_id=:card_id")
    db.session.execute(sql, {"deck_id":deck_id, "card_id":card_id})
    db.session.commit()

def minus_card(deck_id, card_id):
    sql = text("UPDATE deck_with_cards SET quantity = quantity - 1 WHERE deck_id=:deck_id AND card_id=:card_id")
    db.session.execute(sql, {"deck_id":deck_id, "card_id":card_id})
    db.session.commit()

def set_deck_privacy(deck_id, status):
    sql = text("UPDATE decks SET public=:public WHERE id=:deck_id")
    db.session.execute(sql, {"deck_id":deck_id, "public":status})
    db.session.commit()

def get_card_quantity(deck_id, card_id):
    sql = text("SELECT quantity FROM deck_with_cards WHERE deck_id=:deck_id AND card_id=:card_id")
    result = db.session.execute(sql, {"deck_id":deck_id, "card_id":card_id})
    card_quantity = result.fetchone()[0]
    return card_quantity