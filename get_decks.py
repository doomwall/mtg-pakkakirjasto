from db import db
from sqlalchemy.sql import text

import random

def get_own_decks(id):
    sql = text("SELECT id, deck_name, deck_text  FROM decks WHERE deck_owner=:id AND visible=TRUE ORDER BY id")
    result = db.session.execute(sql, {"id":id})
    all_decks = result.fetchall()
    return all_decks

def get_all_public_decks():
    sql = text("SELECT id, deck_name, deck_text FROM decks WHERE public = TRUE ORDER BY id")
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
    
    sql2 = text("SELECT id, deck_name FROM decks WHERE public = TRUE")
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
    sql = text("SELECT id, deck_owner, deck_name, deck_text, public FROM decks WHERE id=:id")
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
    sql = text("""SELECT d.card_id, c.card_name, c.card_text, c.image_url, d.quantity
               FROM deck_with_cards AS d
               LEFT JOIN cards AS c
               ON d.card_id = c.id
               WHERE d.deck_id=:deck_id
               AND quantity>0
               """)
    result = db.session.execute(sql, {"deck_id":deck_id})
    decks_cards = result.fetchall()
    print(decks_cards)
    return decks_cards


def plus_card(deck_id, card_id):
    sql = text("UPDATE deck_with_cards SET quantity = quantity + 1 WHERE deck_id=:deck_id AND card_id=:card_id")
    db.session.execute(sql, {"deck_id":deck_id, "card_id":card_id})
    db.session.commit()


def minus_card(deck_id, card_id):
    sql_quantity = text("SELECT quantity FROM deck_with_cards WHERE deck_id=:deck_id AND card_id=:card_id")
    result = db.session.execute(sql_quantity, {"deck_id":deck_id, "card_id":card_id})
    quant = result.fetchone()[0]
    if quant > 0:
        sql = text("UPDATE deck_with_cards SET quantity = quantity - 1 WHERE deck_id=:deck_id AND card_id=:card_id")
        db.session.execute(sql, {"deck_id":deck_id, "card_id":card_id})
        db.session.commit()
    else:
        return
    
def remove_card_from_deck(deck_id, card_id):
    sql = text("UPDATE deck_with_cards SET quantity = 0 WHERE deck_id=:deck_id AND card_id=:card_id")
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

def remove_deck_from_db(id):
    sql = text("UPDATE decks SET visible = FALSE WHERE id=:id")
    db.session.execute(sql, {"id":id})
    db.session.commit()