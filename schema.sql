CREATE TABLE users (
    id SERIAL PRIMARY KEY, 
    username TEXT, 
    password TEXT,
    admin BOOLEAN DEFAULT FALSE
);

CREATE TABLE visitors (
    id SERIAL PRIMARY KEY,
    time TIMESTAMP
);

CREATE TABLE cards (
    id SERIAL PRIMARY KEY, 
    card_name TEXT, 
    card_text TEXT,
    image_url TEXT,
    visible BOOLEAN
);

CREATE TABLE decks (
    id SERIAL PRIMARY KEY,
    deck_owner INTEGER REFERENCES users(id),
    deck_name TEXT,
    deck_text TEXT,
    public BOOLEAN DEFAULT FALSE,
    visible BOOLEAN DEFAULT TRUE
);

CREATE TABLE deck_with_cards (
    deck_id INTEGER REFERENCES decks(id),
    card_id INTEGER REFERENCES cards(id),
    quantity INTEGER DEFAULT 1,
    PRIMARY KEY (deck_id, card_id)
);