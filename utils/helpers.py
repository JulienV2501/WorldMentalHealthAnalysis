def code_to_name(df, code: str) -> str:
    row = df[df['code'] == code].head(1)
    return row['country'].iloc[0] if not row.empty else code