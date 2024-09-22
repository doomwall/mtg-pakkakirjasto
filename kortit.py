from db import db
from sqlalchemy.sql import text

def hae_kortit():
    sql = text("SELECT * FROM cards WHERE visible = TRUE;")
    result = db.session.execute(sql)
    all_cards = result.fetchall()
    return all_cards

def hae_kortit_teksti():
    sql = text("SELECT id, card_name FROM cards WHERE visible = TRUE;")
    result = db.session.execute(sql)
    all_cards = result.fetchall()
    return all_cards

def luo_uusi_kortti_to_db(card_name, card_text, image_data):
    sql = text("INSERT INTO cards (card_name, card_text, image_data, visible) VALUES (:card_name, :card_text, :image_data, TRUE)")
    db.session.execute(sql, {"card_name":card_name, "card_text":card_text, "image_data":image_data})
    db.session.commit()

def hae_kortti(id):
    sql = text("SELECT * FROM cards WHERE id=:id")
    result = db.session.execute(sql, {"id":id})
    card = result.fetchone()
    return card