# price_tracker.py

import streamlit as st
import requests
import sqlite3
import datetime
import pandas as pd
from mtg_etl.update_prices import fetch_card_price, insert_price_record


# Search Scryfall for Card (avoid rate limits)
@st.cache_data(ttl=3600)
def search_scryfall(card_name):
    url = "https://api.scryfall.com/cards/search"

    headers = {
        "User-Agent": "price_tracker/1.0 (mcmerkle@gmail.com)"
    }

    params = {
        "q": card_name,
        "unique": "prints"
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print("Error:", response.status_code)
        return None


# -------- Initialize the Database --------
def init_database():
    connect = sqlite3.connect("card_tracker.db")
    cursor = connect.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tracked_cards(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scryfall_id TEXT,
        name TEXT,
        set_name TEXT,
        rarity TEXT,
        added_at TEXT,
        tracking_end_date TEXT,
        finish TEXT
    )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS price_history(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scryfall_id TEXT,
            finish TEXT,
            price_usd REAL,
            price_eur REAL,
            recorded_at TEXT
        )
    """)
    connect.commit()
    connect.close()


# Call database function
init_database()


# -------- Save Tracked Cards in DB --------
def save_tracked_cards(card, tracking_end_date, finish):
    scryfall_id = card["id"]
    name = card["name"]
    set_name = card["set_name"]
    rarity = card["rarity"]
    added_at = datetime.datetime.now().isoformat()

    connect = sqlite3.connect("card_tracker.db")
    cursor = connect.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO tracked_cards
        (scryfall_id, name, set_name, rarity,
         added_at, tracking_end_date, finish)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        scryfall_id,
        name,
        set_name,
        rarity,
        added_at,
        tracking_end_date,
        finish
    ))

    connect.commit()
    connect.close()


# -------- Retrieve Pricing Data --------
def get_latest_price(scryfall_id, finish):
    connect = sqlite3.connect("card_tracker.db")
    cursor = connect.cursor()
    cursor.execute("""
        SELECT price_usd FROM price_history
        WHERE scryfall_id = ?
        AND finish = ?
        ORDER BY recorded_at DESC
        LIMIT 1
    """, (scryfall_id, finish)
    )

    row = cursor.fetchone()
    connect.close()

    if row:
        return row[0]
    return None


# -------- Calculate Percent Change in Price --------
def percent_change(scryfall_id, finish):
    connect = sqlite3.connect("card_tracker.db")
    cursor = connect.cursor()

    cursor.execute("""
        SELECT price_usd FROM price_history
        WHERE scryfall_id = ?
        AND finish = ?
        ORDER BY recorded_at DESC
        LIMIT 4
    """, (scryfall_id, finish)
    )

    rows = cursor.fetchall()
    connect.close()

    if len(rows) < 4:
        return None

    latest_price = rows[0][0]
    three_days_ago_price = rows[3][0]

    if three_days_ago_price == 0:
        return None

    percent = ((latest_price - three_days_ago_price) / three_days_ago_price) * 100

    return percent


# -------- Fetch Tracked Cards ---------
def get_tracked_cards():
    connect = sqlite3.connect("card_tracker.db")
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM tracked_cards")
    rows = cursor.fetchall()
    connect.close()
    return rows


# -------- Delete a Card from Tracking --------
def delete_tracked_card(scryfall_id):
    connect = sqlite3.connect("card_tracker.db")
    cursor = connect.cursor()
    cursor.execute(
        "DELETE FROM tracked_cards WHERE scryfall_id = ?",
        (scryfall_id,)
    )
    connect.commit()
    connect.close()


# -------- Get Price History for a Card
def get_price_history_for_card(scryfall_id, finish):
    connect = sqlite3.connect("card_tracker.db")
    cursor = connect.cursor()
    cursor.execute("""
        SELECT price_usd, price_eur, recorded_at
        FROM price_history
        WHERE scryfall_id = ?
        AND finish = ?
        ORDER BY recorded_at
    """, (scryfall_id, finish))
    rows = cursor.fetchall()
    connect.close()
    return rows


# -------- Streamlit UI --------
st.title("MTG Card Price Tracker")

# Limit results to 15 per page, scroll bar window
if "scroll_to" in st.session_state:
    st.markdown(
        f"""
        <script>
            window.location.hash = "#{st.session_state.scroll_to}";
        </script>
        """,
        unsafe_allow_html=True
    )
    del st.session_state.scroll_to

page_size = 15

card_search = st.text_input(
    "Search for a Card to Track",
    placeholder="Search...",
    label_visibility="visible"
)

# Store results if not already stored
if "search_results" not in st.session_state:
    st.session_state.search_results = None

if "page" not in st.session_state:
    st.session_state.page = 0

search_clicked = st.button("Search")

if (search_clicked or card_search != st.session_state.get("last_search")) and card_search:
    st.session_state.last_search = card_search
    st.session_state.page = 0

    data = search_scryfall(card_search)

    if data:
        st.session_state.search_results = data["data"]
    else:
        st.session_state.search_results = None
        st.warning("No cards found.")

# Display results
st.markdown('<div id="search_top"></div>', unsafe_allow_html=True)

if st.session_state.search_results:

    total_results = len(st.session_state.search_results)
    start_index = st.session_state.page * page_size
    end_index = start_index + page_size
    page_results = st.session_state.search_results[start_index:end_index]

    results_container = st.container(height=400)

    with results_container:
        st.subheader("Search Results")

        for card in page_results:
            col_img, col_info = st.columns([1, 3])

            with col_img:
                if "image_uris" in card:
                    st.image(card["image_uris"]["small"])
                elif "card_faces" in card:
                    st.image(card["card_faces"][0]["image_uris"]["small"])

            with col_info:
                st.write(f"**{card['name']}**")
                st.write(f"Set: {card['set_name']}")

                available_finishes = []

                if card["prices"]["usd"] is not None:
                    available_finishes.append("Nonfoil")

                if card["prices"]["usd_foil"] is not None:
                    available_finishes.append("Foil")

                if not available_finishes:
                    available_finishes = ["Nonfoil"]

                finish = st.selectbox(
                    "Finish",
                    available_finishes,
                    key=f"finish_{card['id']}"
                )

                if finish == "Foil":
                    display_price = card["prices"]["usd_foil"]
                else:
                    display_price = card["prices"]["usd"]

                st.write(f"Price (USD): {display_price}")

                col_a, col_b = st.columns([2, 1])

                with col_a:
                    duration = st.selectbox(
                        "Tracking Duration",
                        ["Indefinite", "7 Days", "30 Days"],
                        key=f"duration_{card['id']}"
                    )

                with col_b:
                    if st.button("Save Card", key=f"save_{card['id']}"):

                        if duration == "Indefinite":
                            tracking_end_date = None
                        elif duration == "7 Days":
                            tracking_end_date = (
                                datetime.datetime.now() + datetime.timedelta(days=7)
                            ).isoformat()
                        else:
                            tracking_end_date = (
                                datetime.datetime.now() + datetime.timedelta(days=30)
                            ).isoformat()

                        save_tracked_cards(card, tracking_end_date, finish)
                        usd_price, eur_price = fetch_card_price(card["id"], finish)

                        if usd_price is not None:
                            insert_price_record(card["id"], finish, usd_price, eur_price)
                        st.success("Card saved successfully and price recorded.")

                st.markdown("---")

    col1, col2, col3 = st.columns(3)

    if col1.button("Previous", key="prev_page"):
        if st.session_state.page > 0:
            st.session_state.page -= 1
            st.rerun()

    col2.write(
        f"""Page {st.session_state.page + 1} of
        {((total_results - 1) // page_size) + 1}"""
        )

    if col3.button("Next", key="next_page"):
        if end_index < total_results:
            st.session_state.page += 1
            st.session_state.scroll_to = "search_top"
            st.rerun()

# Tracked cards
st.divider()
st.subheader("Tracked Cards")

sort_option = st.selectbox(
    "Sort by",
    ["Default", "Price: Low to High", "Price: High to Low"]
)

tracked_cards = get_tracked_cards()

# Attach latest price to each row for sorting
cards_with_price = []

for row in tracked_cards:
    price = get_latest_price(row[1], row[7])
    cards_with_price.append((row, price))

if sort_option == "Price: Low to High":
    cards_with_price.sort(
        key=lambda x: (x[1] is None, x[1])
    )
elif sort_option == "Price: High to Low":
    cards_with_price.sort(
        key=lambda x: (x[1] is None, -x[1] if x[1] is not None else 0)
    )

# Extract sorted rows
tracked_cards = [item[0] for item in cards_with_price]

if "active_chart" not in st.session_state:
    st.session_state.active_chart = None

# Create table with streamlit
for row in tracked_cards:
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

    col1.write(row[2])
    col2.write(row[3])
    col3.write(row[7])

    latest_price = get_latest_price(row[1], row[7])
    change = percent_change(row[1], row[7])

    if latest_price is not None:
        col4.write(f"${latest_price:.2f}")
    else:
        col4.write("—")

    # Display change in pricing
    if change is not None:
        if change > 0:
            col5.markdown(
                f"<span style='color: #0AC440;'>▲ +{change:.2f}%</span>",
                unsafe_allow_html=True
            )
        elif change < 0:
            col5.markdown(
                f"<span style='color: #F71120;'>▼ {change:.2f}%</span>",
                unsafe_allow_html=True
            )
        else:
            col5.markdown(
                "<span style='color: gray;'>0.00%</span>",
                unsafe_allow_html=True
            )
    else:
        col5.markdown(
            "<span style='color: gray;'>—</span>",
            unsafe_allow_html=True
        )

    if col6.button("Chart", key=f"chart_{row[1]}_{row[7]}"):
        if st.session_state.active_chart == (row[1], row[7]):
            st.session_state.active_chart = None
        else:
            st.session_state.active_chart = (row[1], row[7])

    if col7.button("Delete", key=f"delete_{row[1]}_{row[7]}"):
        delete_tracked_card(row[1])
        st.rerun()

    if st.session_state.active_chart == (row[1], row[7]):

        history = get_price_history_for_card(row[1], row[7])

        if history:
            df = pd.DataFrame(history, columns=["TCGplayer (USD)", "Cardmarket (EUR)", "Recorded At"])
            df["Recorded At"] = pd.to_datetime(df["Recorded At"])
            df = df.sort_values("Recorded At")

            eur_to_usd = 1.16

            df["Cardmarket (USD)"] = df["Cardmarket (EUR)"] * eur_to_usd

            df = df.set_index("Recorded At")

            st.line_chart(df[["TCGplayer (USD)", "Cardmarket (USD)"]])

        else:
            st.info("No price history yet.")

        if st.button("Close Chart", key=f"close_{row[1]}_{row[7]}"):
            st.session_state.active_chart = None
            st.rerun()
