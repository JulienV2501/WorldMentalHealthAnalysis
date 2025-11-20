import pandas as pd

def load_data(save_as_file: bool):
    df_mental = pd.read_csv('data/mental-illness.csv')
    df_unemp = pd.read_csv('data/unemployment.csv', skiprows=4)
    df_hfi = pd.read_csv('data/human-freedom-index.csv')
    df_alcool = pd.read_csv('data/alcohol-consumption.csv')
    df_gii = pd.read_csv('data/gender-inequality-index.csv')

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

    # rename continent name
    df_mental.loc[df_mental["country"] == "Europe (IHME GBD)", "country"] = "Europe"
    df_mental.loc[df_mental["country"] == "Africa (IHME GBD)", "country"] = "Africa"
    df_mental.loc[df_mental["country"] == "America (IHME GBD)", "country"] = "America"
    df_mental.loc[df_mental["country"] == "Asia (IHME GBD)", "country"] = "Asia"

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

    df_merged = df_mental.merge(
        df_unemp,
        left_on=['country', 'year'],
        right_on=['Country Name', 'year'],
        how='left'
    )

    # rename hfi columns
    df_hfi = df_hfi.rename(columns={
        'countries': 'country',
    })
    df_hfi = df_hfi[['year', 'country', 'hf_score']]
    df_merged = df_merged.merge(df_hfi, on=['country', 'year'], how='left')

    df_alcool=df_alcool.rename(columns={
        'Entity': 'country',
        'Code': 'code',
        'Year': 'year',
        "Total alcohol consumption per capita (liters of pure alcohol, projected estimates, 15+ years of age)": 'alcohol_consumption'}
    )
    df_alcool = df_alcool[['year', 'country', 'alcohol_consumption']]
    df_merged = df_merged.merge(df_alcool, on=['country', 'year'], how='left')

    df_gii = df_gii.rename(columns={
        'Entity': 'country',
        'Code': 'code',
        'Year': 'year',
        "Gender Inequality Index": 'gii'}
    )
    df_gii = df_gii[['year', 'country', 'gii']]
    df_merged = df_merged.merge(df_gii, on=['country', 'year'], how='left')

    if 'Country Name' in df_merged.columns:
        df_merged.drop(columns=['Country Name'], inplace=True)

    if save_as_file:
        output_path = 'mental_health_merged.csv'
        df_merged.to_csv(output_path, index=False)

    return df_merged