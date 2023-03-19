import pandas as pd

def csv_to_parquet(infile: str):
    outfile_name = infile.split(".")[0]

    df_csv = pd.read_csv(infile, sep=";")
    df_csv.to_parquet(outfile_name + ".parquet")


def prices_ffill(data: pd.DataFrame) -> pd.DataFrame:
    filled = []

    for _id in data["game_id"].unique():
        df = data[data["game_id"] == _id]

        # Define the complete time range
        range = [
            x.strftime("%Y-%m-%d")
            for x in pd.date_range(start=df.date.min(), end=df.date.max())
        ]

        # Forward fill
        df = (
            df.set_index("date")
            .reindex(range)
            .fillna(method="ffill")
            .rename_axis("date")
            .reset_index()
        )

        records = df.to_dict("records")
        filled.append(records)

    # Flatten
    filled = [item for sublist in filled for item in sublist]

    df = pd.DataFrame.from_records(filled)
    df["date"] = pd.to_datetime(df["date"])

    return df

# TODO: cache
def get_game_stats(data: pd.DataFrame, game_id: str):
    game_data = data[data["game_id"] == game_id]
    
    """
    - average price
    - number of price drops
        - is_price_drop
    - average discount
    - average duration
    """
    game_stats = {}
    
    return game_stats

