# mtg-pakkakirjasto
Tietokannat ja web-ohjelmointi kurssin web-sovellus, MTG-korttipakkojen hallintasovellus

Web-sovelluksen ideana on luoda sivusto, jossa käyttäjän on mahdollista luoda, hallinnoida ja pitää kirjaa omista korttipakoista liittyen suosittuun korttipeliin Magic: The Gathering.
Koska pakoissa on useita kymmeniä kortteja samaan aikaan, on käyttäjälle hyödyllistä pitää kirjaa siitä mitä kortteja pakka sisältää ja kuinka monta. Sivuston ideana on toimia
tällaisena työkaluna.

Itse peli sisältää useita tuhansia kortteja, joten tämän projektin aikana ei ole mahdollista siirtää valtavaa tietokantaa käyttäjille käytettäväksi. Siksi annetaan käyttäjälle 
mahdollisuus lisätä sivustolle uusia kortteja, jotka ovat sen jälkeen myös muiden käyttäjien käytettävissä. Annetaan myös ylläpitäjille oikeus tarkastella lisättyjä kortteja ja
tarpeen mukaan myös poistaa niitä. 

Lisäksi sivustolla on mahdollisuus selata muiden käyttäjien pakkoja, mikäli käyttäjä on asettanut pakan julkiseen tilaan.

Päivitys 2.10.2024
Sivuston ominaisuudet
- Pakkojen julkiseksi asettaminen mahdollista
- Viety Boostrap setup ulkoasua varten
- Viety HTMX mahdollisuus korttien lisäykseen, jolloin sivu ei lataudu uudestaan
- Muutettu koodi kokonaan englanniksi
- Korjattu validointia uuden tunnuksen teossa

Päivitys 22.9.2024
Sivuston ominaisuudet:
- Voi lisätä uuden käyttäjätilin
- Kirjautua sisään ja selata omia tietoja
- Voit lisätä uusia kortteja tietokantaan
- Voit lisätä uusia pakkoja omaan profiiliin
- Voit lisätä pakkoihin kortteja ja poistaa pakoista kortteja

Kesken:
- Etusivulle mainosvalikko, joka näyttää random muiden käyttäjien julkisia pakkoja
- Korttihaku tekemättä
- Pakkahaku tekemättä
- Visuaalinen ilme ja elementtien asettelu vaiheessa


Asennusohjeet
- Kloonaa repositorio haluamaasi paikkaan
- Lisää tiedoston kantaan .env tiedosto sisältäen seuraavat arvot:
- DATABASE_URL=postgresql:///<Tähän oma tietokantasi>
- SECRET_KEY=<Tähän oma secret key>
- Käytä komento "python3 -m venv venv" komentorivilläsi
- Käytä komento "source venv/bin/activate"
- Asenna tarvittavat paketit komennolla "pip install -r ./requirements.txt"
- Asenna tarvittava tietokanta komennolla "psql < schema.sql"
- Käynnistä sovellus komennolla "flask run"
- Sovellus on nyt käytettävissä osoitteessa http://127.0.0.1:5000/
