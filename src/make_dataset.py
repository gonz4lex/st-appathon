import pandas as pd


def make_clustering_dataset(infile):
    in_data = pd.read_parquet(infile)

    df = in_data[
        [
            "name",
            "release_date",
            "platforms",
            "subscribers_count",
            "float_price",
            "trophies.platinum",
            "flags",
            "last_update_date",
            "last_update.end_date",
            "last_update.discount_percent",
            "scores.metacritic.score",
            "scores.opencritic.scores",
        ]
    ].copy()

    
