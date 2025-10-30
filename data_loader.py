import pandas as pd

def load_data(save_as_file: bool):
    df_mental = pd.read_csv('data/mental-illness.csv')
    df_unemp = pd.read_csv('data/unemployment.csv', skiprows=4)
    df_hfi = pd.read_csv('data/human-freedom-index.csv')

    # rename base datasets columns
    df_mental = df_mental.rename(columns={
        'Entity': 'country',
        'Code': 'code',
        'Year': 'year',
        'Depressive disorders (share of population) - Sex: Both - Age: Age-standardized': 'depression_disorders',
        'Anxiety disorders (share of population) - Sex: Both - Age: Age-standardized': 'anxiety_disorders',
        'Bipolar disorders (share of population) - Sex: Both - Age: Age-standardized': 'bipolar_disorders',
        'Eating disorders (share of population) - Sex: Both - Age: Age-standardized': 'eating_disorders',
        'Schizophrenia disorders (share of population) - Sex: Both - Age: Age-standardized': 'schizo_disorders'
    })

    # unpivot unemp dataset from wide to long format
    df_unemp = df_unemp.melt(
        id_vars=['Country Name', 'Country Code'],
        var_name='year',
        value_name='unemployment_rate'
    )
    df_unemp['year'] = df_unemp['year'].astype(str).str.extract(r'(\d{4})')
    df_unemp = df_unemp.dropna(subset=['year', 'unemployment_rate'])
    df_unemp['year'] = df_unemp['year'].astype(int)
    df_unemp = df_unemp[['Country Name', 'year', 'unemployment_rate']]

    df_unemp['unemployment_rate'] = pd.to_numeric(df_unemp['unemployment_rate'], errors='coerce')

    # rename hfi columns
    df_hfi = df_hfi.rename(columns={
        'countries': 'country',
    })
    df_hfi = df_hfi[['year', 'country', 'hf_score']]

    df_merged = df_mental.merge(
        df_unemp,
        left_on=['country', 'year'],
        right_on=['Country Name', 'year'],
        how='left'
    )

    df_merged = df_merged.merge(df_hfi, on=['country', 'year'], how='left')

    if 'Country Name' in df_merged.columns:
        df_merged.drop(columns=['Country Name'], inplace=True)

    if save_as_file:
        output_path = 'mental_health_merged.csv'
        df_merged.to_csv(output_path, index=False)

    return df_merged