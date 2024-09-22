from db import db
from sqlalchemy.sql import text

def hae_omat_pakat(id):
    sql = text("SELECT * FROM decks WHERE deck_owner=:id AND visible=TRUE")
    result = db.session.execute(sql, {"id":id})
    all_decks = result.fetchall()
    return all_decks

def luo_uusi_pakka_to_db(user_id, deck_name, deck_text):
    sql = text("INSERT INTO decks (deck_owner, deck_name, deck_text) VALUES (:deck_owner, :deck_name, :deck_text)")
    db.session.execute(sql, {"deck_owner":user_id, "deck_name":deck_name, "deck_text":deck_text})
    db.session.commit()

def hae_pakka(id):
    sql = text("SELECT * FROM decks WHERE id=:id")
    result = db.session.execute(sql, {"id":id})
    deck = result.fetchone()
    return deck

def lisaa_kortti_pakkaan_db(deck_id, card_id):
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

def hae_pakan_kortit(deck_id):
    card_names = []
    sql = text("SELECT card_id, quantity FROM deck_with_cards WHERE deck_id=:deck_id AND quantity>0")
    result = db.session.execute(sql, {"deck_id":deck_id})
    decks_cards = result.fetchall()
    sql2 = text("SELECT id, card_name FROM cards WHERE id=:card_id")
    for card_id in decks_cards:
        search = db.session.execute(sql2, {"card_id":card_id[0]})
        card = search.fetchone()
        card = (card, card_id[1])
        card_names.append(card)
    return card_names

def nosta_maaraa(deck_id, card_id):
    sql = text("UPDATE deck_with_cards SET quantity = quantity + 1 WHERE deck_id=:deck_id AND card_id=:card_id")
    db.session.execute(sql, {"deck_id":deck_id, "card_id":card_id})
    db.session.commit()

def laske_maaraa(deck_id, card_id):
    sql = text("UPDATE deck_with_cards SET quantity = quantity - 1 WHERE deck_id=:deck_id AND card_id=:card_id")
    db.session.execute(sql, {"deck_id":deck_id, "card_id":card_id})
    db.session.commit()