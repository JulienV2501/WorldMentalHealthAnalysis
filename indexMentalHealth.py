import pandas as pd

def indexMentalHealth(df: pd.DataFrame):

    cols = [
    "depression_disorders",
    "anxiety_disorders",
    "bipolar_disorders",
    "eating_disorders",
    "schizo_disorders"
    ]

    df_norm = (df[cols] - df[cols].min()) / (df[cols].max() - df[cols].min())

    df["global_mental_disorders"] = df_norm.sum(axis=1)

    return df