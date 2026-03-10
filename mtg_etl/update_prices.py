# update_prices.py

import requests
import sqlite3
import datetime


def get_tracked_cards():
    connect = sqlite3.connect("card_tracker.db")
    cursor = connect.cursor()

    iso_time = datetime.datetime.now().isoformat()

    cursor.execute("""
        SELECT scryfall_id, finish
        FROM tracked_cards
        WHERE tracking_end_date IS NULL
        OR tracking_end_date >= ?
    """, (iso_time,))

    rows = cursor.fetchall()
    connect.close()

    tracked = []

    for row in rows:
        tracked.append({
            "scryfall_id": row[0],
            "finish": row[1]
        })

    return tracked


def fetch_card_price(scryfall_id, finish):
    url = f"https://api.scryfall.com/cards/{scryfall_id}"

    headers = {
        "User-Agent": "price_tracker_etl/1.0"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()

        if finish == "Foil":
            usd = data["prices"]["usd_foil"]
            eur = data["prices"]["eur_foil"]
        else:
            usd = data["prices"]["usd"]
            eur = data["prices"]["eur"]

        if usd is not None:
            usd = float(usd)
        else:
            usd = None

        if eur is not None:
            eur = float(eur)
        else:
            eur = None

        return usd, eur

    return None, None


def insert_price_record(scryfall_id, finish, usd_price, eur_price):
    connect = sqlite3.connect("card_tracker.db")
    cursor = connect.cursor()

    recorded_at = datetime.datetime.now().isoformat()

    cursor.execute("""
        INSERT INTO price_history
        (scryfall_id, finish, price_usd, price_eur, recorded_at)
        VALUES (?, ?, ?, ?, ?)
    """, (scryfall_id, finish, usd_price, eur_price, recorded_at))

    connect.commit()
    connect.close()


def update_all_prices():
    active_cards = get_tracked_cards()

    for card in active_cards:
        scryfall_id = card["scryfall_id"]
        finish = card["finish"]

        usd_price, eur_price = fetch_card_price(scryfall_id, finish)

        if usd_price is not None:
            insert_price_record(scryfall_id, finish, usd_price, eur_price)
        else:
            print(f"Skipped {scryfall_id} ({finish}) — no price")


if __name__ == "__main__":
    update_all_prices()
