from db import db
from sqlalchemy.sql import text
from flask import current_app

import os

def get_cards():
    sql = text("SELECT id, card_name, card_text, image_url FROM cards WHERE visible = TRUE ORDER BY id;")
    result = db.session.execute(sql)
    all_cards = result.fetchall()
    return all_cards

#def get_cards_text():
#    sql = text("SELECT * FROM cards WHERE visible = TRUE;")
#    result = db.session.execute(sql)
#    all_cards = result.fetchall()
#    return all_cards

def create_new_card_to_db(card_name, card_text):
    sql = text("INSERT INTO cards (card_name, card_text, visible) VALUES (:card_name, :card_text, TRUE)")
    db.session.execute(sql, {"card_name":card_name, "card_text":card_text})
    db.session.commit()

def get_card(id):
    sql = text("SELECT card_name, card_text, image_url FROM cards WHERE id=:id")
    result = db.session.execute(sql, {"id":id})
    card = result.fetchone()
    return card

def get_card_id_by_name(name):
    sql = text("SELECT id FROM cards WHERE card_name=:name")
    result = db.session.execute(sql, {"name":name})
    card = result.fetchone()[0]
    return card

def alter_card_image_url(card_id, filename):
    sql = text("UPDATE cards SET image_url=:filename WHERE id=:card_id")
    db.session.execute(sql, {"filename":filename, "card_id":card_id})
    db.session.commit()

def check_card_name():
    sql = text("SELECT card_name FROM cards")
    result = db.session.execute(sql)
    card_names = result.fetchall()
    return card_names

def remove_card_from_db(id):
    sql = text("UPDATE cards SET visible=FALSE WHERE id=:id")
    db.session.execute(sql, {"id":id})
    db.session.commit()