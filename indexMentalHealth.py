import pandas as pd

def indexMentalHealth(df: pd.DataFrame):

    df["global_mental_disorders"] = df["depression_disorders"] + df["anxiety_disorders"] + df["bipolar_disorders"] + df["eating_disorders"] +df["schizo_disorders"]
    return df