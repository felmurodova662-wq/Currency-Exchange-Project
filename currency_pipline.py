import pandas as pd
import numpy as np
import requests
from sqlalchemy import create_engine
from urllib.parse import quote_plus
from sqlalchemy import text

url = "https://cbu.uz/ru/arkhiv-kursov-valyut/json/"

response = requests.get(url, timeout=30)
response.raise_for_status()

data = response.json()

df = pd.json_normalize(data)

if df.empty:
    raise ValueError("The API returned no currency records.")


df_to_load = df.rename(columns={
    "id": "source_id",
    "Code": "numeric_code",
    "Ccy": "currency_code",
    "CcyNm_RU": "ccyName_RU",
    "CcyNm_UZ": "ccyName_UZ",
    "CcyNm_UZC": "ccyName_UZC",
    "CcyNm_EN": "ccyName_ENG",
    "Nominal": "nominal",
    "Rate": "rate",
    "Diff": "diff",
    "Date": "date"
}).copy()

raw_columns = [
    "source_id",
    "numeric_code",
    "currency_code",
    "ccyName_RU",
    "ccyName_UZ",
    "ccyName_UZC",
    "ccyName_ENG",
    "nominal",
    "rate",
    "diff",
    "date"
]

df_to_load = df_to_load[raw_columns]


connection_string = quote_plus(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-BDQ61GT;"
    "DATABASE=CurrencyExchange;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

engine = create_engine(
    f"mssql+pyodbc:///?odbc_connect={connection_string}",
    fast_executemany=True
)

with engine.connect() as connection:
    print(
        "Connected to:",
        connection.execute(text("SELECT DB_NAME()")).scalar()
    )


df_to_load.to_sql(
    name="RawData",
    con=engine,
    schema="dbo",
    if_exists="append",
    index=False
)

print(f"RAW rows loaded: {len(df_to_load)}")


query = text("""
    WITH LatestRaw AS
    (
        SELECT
            r.raw_id,
            r.source_id,
            r.numeric_code,
            r.currency_code,
            r.ccyName_RU,
            r.ccyName_UZ,
            r.ccyName_UZC,
            r.ccyName_ENG,
            r.nominal,
            r.rate,
            r.diff,
            r.[date],
            r.loaded_at,
            ROW_NUMBER() OVER
            (
                PARTITION BY r.source_id, r.[date]
                ORDER BY r.loaded_at DESC, r.raw_id DESC
            ) AS row_num
        FROM dbo.RawData AS r
    )
    SELECT
        r.raw_id,
        r.source_id,
        r.numeric_code,
        r.currency_code,
        r.ccyName_RU,
        r.ccyName_UZ,
        r.ccyName_UZC,
        r.ccyName_ENG,
        r.nominal,
        r.rate,
        r.diff,
        r.[date],
        r.loaded_at
    FROM LatestRaw AS r
    WHERE r.row_num = 1
      AND NOT EXISTS
      (
          SELECT 1
          FROM dbo.CleanData AS c
          WHERE c.source_id = r.source_id
            AND c.rate_date =
                TRY_CONVERT(DATE, r.[date], 104)
      );
""")

with engine.connect() as connection:
    df_raw = pd.read_sql(query, connection)

print(f"New records awaiting cleaning: {len(df_raw)}")


if df_raw.empty:
    print("CleanData is already up to date.")

else:
    df_clean = df_raw.copy()

    df_clean = df_clean.rename(columns={
        "raw_id": "source_raw_id",
        "ccyName_RU": "currency_name_ru",
        "ccyName_UZ": "currency_name_uz",
        "ccyName_UZC": "currency_name_uz_cyrillic",
        "ccyName_ENG": "currency_name_en",
        "date": "rate_date",
        "loaded_at": "source_loaded_at"
    })

    text_columns = [
        "numeric_code",
        "currency_code",
        "currency_name_ru",
        "currency_name_uz",
        "currency_name_uz_cyrillic",
        "currency_name_en"
    ]

    for column in text_columns:
        df_clean[column] = (
            df_clean[column]
            .astype("string")
            .str.strip()
            .replace("", pd.NA)
        )

    df_clean["currency_code"] = (
        df_clean["currency_code"].str.upper()
    )

    df_clean["source_id"] = pd.to_numeric(
        df_clean["source_id"],
        errors="coerce"
    ).astype("Int64")

    df_clean["nominal"] = pd.to_numeric(
        df_clean["nominal"],
        errors="coerce"
    ).astype("Int64")

    df_clean["rate"] = pd.to_numeric(
        df_clean["rate"],
        errors="coerce"
    )

    df_clean["diff"] = pd.to_numeric(
        df_clean["diff"],
        errors="coerce"
    )

    df_clean["rate_date"] = pd.to_datetime(
        df_clean["rate_date"],
        format="%d.%m.%Y",
        errors="coerce"
    )

    required_columns = [
        "source_raw_id",
        "source_id",
        "numeric_code",
        "currency_code",
        "currency_name_ru",
        "currency_name_uz",
        "currency_name_uz_cyrillic",
        "currency_name_en",
        "nominal",
        "rate",
        "diff",
        "rate_date",
        "source_loaded_at"
    ]

    if df_clean[required_columns].isna().any().any():
        raise ValueError(
            "Cleaning created NULL values. CleanData was not loaded."
        )

    if (df_clean["nominal"] <= 0).any():
        raise ValueError(
            "Nominal contains zero or a negative value."
        )

    df_clean["rate_per_unit"] = (
        df_clean["rate"] / df_clean["nominal"]
    )

    df_clean["change_direction"] = np.select(
        [
            df_clean["diff"] > 0,
            df_clean["diff"] < 0
        ],
        [
            "Increased",
            "Decreased"
        ],
        default="No Change"
    )

    df_clean["is_appreciated"] = df_clean["diff"] > 0
    df_clean["is_depreciated"] = df_clean["diff"] < 0

    clean_columns = [
        "source_raw_id",
        "source_id",
        "numeric_code",
        "currency_code",
        "currency_name_ru",
        "currency_name_uz",
        "currency_name_uz_cyrillic",
        "currency_name_en",
        "nominal",
        "rate",
        "diff",
        "rate_date",
        "source_loaded_at",
        "rate_per_unit",
        "change_direction",
        "is_appreciated",
        "is_depreciated"
    ]

    df_clean_to_load = df_clean[clean_columns].copy()

    df_clean_to_load.to_sql(
        name="CleanData",
        con=engine,
        schema="dbo",
        if_exists="append",
        index=False
    )

    print(
        f"CLEAN rows loaded: {len(df_clean_to_load)}"
    )


engine.dispose()
print("Currency pipeline completed successfully.")
