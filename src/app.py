import streamlit as st

import pandas as pd
import numpy as np

import random
from datetime import datetime

import utils

if __name__ == "__main__":
    # Page setup
    st.set_page_config(layout="wide", initial_sidebar_state="expanded")
    st.title("Game Discounts Dashboard")

    # Datasets
    products = pd.read_csv("data/raw/products.csv", sep=";")
    prices = pd.read_csv("data/raw/prices.csv")
    product_stats = pd.read_parquet("data/processed/product_statistics.parquet")
    neighbors = pd.read_parquet("data/neighbors_5_auto.parquet")

    # Prepare selector content
    games = products[products["top_category"] == "game"]
    games = games.drop(columns=["subscribers_count", "float_price"])
    games = games.set_index("id").join(product_stats.set_index("id")).reset_index()

    game_names = games.name.tolist()

    # Define sidebar
    with st.sidebar:
        """
        Hi! Welcome to my game discounts dashboard! :video_game:\n
        Select a game below to get started:\n
        """
        selected_game = st.selectbox("Choose a game:", game_names)
        """
        Some stuff you can see in here:\n
        - current and average, prices, discount duration, times discounted...\n
        - price history chart
        - related games and estimation of next discount [(+info)](https://github.com/gonz4lex)

        This app was originally developed for the Streamlit App-A-Thon contest on March 2023.
        Take a look a the source code [here](https://github.com/gonz4lex).

        The data was extracted https://psprices.com/region-es and is currently static and not updating (sorry!).
        """

    # Apply user filtering
    current_game = games[games["name"] == selected_game]
    current_game_id = current_game["id"].values[0]
    selected_prices = prices[prices["game_id"] == current_game_id]

    # Main app
    display_prices = utils.prices_ffill(selected_prices)

    ## Display game data
    ### Section 1
    # "### Game metadata"
    cover_col, info_col = st.columns([1, 1])

    with cover_col:
        st.image(current_game["cover"].values[0])

    with info_col:
        f'#### {current_game["name"].values[0]}'

        current_release_date = current_game["release_date"].values[0]
        if current_release_date is not np.nan:
            f'_Released on {current_release_date}_'  # TODO: improve display format

        change_wrt_average = (
            current_game["float_price"] - current_game["average_discounted_price"]
        )
        cur_price, avg_price = st.columns([1,1])

        with cur_price:
            current_price = current_game["float_price"].values[0]
            st.metric(
                "Current price",
                f"{current_price}€",
                f"{round(change_wrt_average.values[0], 2)}€",
                delta_color="inverse"
            )

        with avg_price:
            average_price = current_game["average_discounted_price"].values[0]
            st.metric(
                "Average discounted price",
                f"{round(average_price, 2)}€",
            )

        f'Available on: {current_game["platforms"].values[0]}'

        stats_1, stats_2 = st.columns([1, 1])
        with stats_1:
            average_discount = round(current_game["average_discount_amount"].values[0], 3)
            st.metric(
                "Average discount",
                f"{average_discount * 100}%",
            )
            lowest_price = current_game["minimum_price"].values[0]
            st.metric(
                "Lowest price",
                f"{lowest_price}€",
            )
            
        with stats_2:
            average_duration = round(current_game["average_discount_duration"].values[0], 2)
            st.metric(
                "Average discount duration",
                f"{average_duration} days",
            )

            times_discounted = current_game["times_discounted"].values[0]
            try:
                times_discounted = int(times_discounted)
            except Exception as e:
                print(e)
            st.metric(
                "Times discounted",
                times_discounted,
            )

    if st.checkbox("Show raw data"):
        st.dataframe(
            selected_prices[["date", "price", "price_plus"]], use_container_width=True
        )

    "#### Price history"
    with st.expander("Click to show the chart"):
        st.line_chart(display_prices, x="date", y=["price", "price_plus"])


    ### Section 3
    cur_neighbors = neighbors[neighbors["game_id"] == current_game_id].drop_duplicates().drop("game_id", axis=1).T
    cur_neighbors.columns = ["game_id"]
    
    neighbor_ids = [x.tolist()[0] for x in cur_neighbors.values]
    neighbor_widget = games.query("id in @neighbor_ids")[["id", "url", "cover", "name"]]

    #### Display neighbors' cover images

    neighbors_images = neighbor_widget["cover"].to_list()
    neighbors_urls = neighbor_widget["url"].to_list()
    

    "#### Related games"
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.image(neighbors_images[0], use_column_width="always")
    with c2:
        st.image(neighbors_images[1], use_column_width="always")
    with c3:
        st.image(neighbors_images[2], use_column_width="always")
    with c4:
        try:
            st.image(neighbors_images[3], use_column_width="always")
        except Exception as e:
            print(e)

    with st.expander("Show next discount predictions (work in progress)"):
        with st.container():
            st.metric(
                "Next discount in",
                f"{random.randint(1, 60)} days"
            )


    