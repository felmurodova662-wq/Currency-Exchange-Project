create database CurrencyExchange;

use CurrencyExchange;

CREATE TABLE dbo.RawData
(
    raw_id BIGINT IDENTITY(1,1) NOT NULL PRIMARY KEY,
    source_id BIGINT NULL,
    numeric_code NVARCHAR(20) NULL,
    currency_code NVARCHAR(20) NULL,
    ccyName_RU NVARCHAR(255) NULL,
    ccyName_UZ NVARCHAR(255) NULL,
    ccyName_UZC NVARCHAR(255) NULL,
    ccyName_ENG NVARCHAR(255) NULL,
    nominal NVARCHAR(50) NULL,
    rate NVARCHAR(100) NULL,
    diff NVARCHAR(100) NULL,
    [date] NVARCHAR(50) NULL,
    loaded_at DATETIME2 NOT NULL
        CONSTRAINT DF_RawData_loaded_at DEFAULT SYSDATETIME()
);

select * from RawData;

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

CREATE TABLE dbo.CleanData
(
    clean_id BIGINT IDENTITY(1,1) PRIMARY KEY,

    source_raw_id BIGINT NOT NULL,
    source_id BIGINT NOT NULL,

    numeric_code NVARCHAR(20) NOT NULL,
    currency_code NVARCHAR(20) NOT NULL,

    currency_name_ru NVARCHAR(255) NOT NULL,
    currency_name_uz NVARCHAR(255) NOT NULL,
    currency_name_uz_cyrillic NVARCHAR(255) NOT NULL,
    currency_name_en NVARCHAR(255) NOT NULL,

    nominal INT NOT NULL,
    rate DECIMAL(18,4) NOT NULL,
    diff DECIMAL(18,4) NOT NULL,
    rate_date DATE NOT NULL,

    source_loaded_at DATETIME2 NOT NULL,

    rate_per_unit DECIMAL(18,6) NOT NULL,
    change_direction NVARCHAR(20) NOT NULL,

    is_appreciated BIT NOT NULL,
    is_depreciated BIT NOT NULL,

    cleaned_at DATETIME2 NOT NULL
        CONSTRAINT DF_CleanData_cleaned_at DEFAULT SYSDATETIME(),
		CONSTRAINT UQ_CleanData_CurrencyDate
    UNIQUE (source_id, rate_date)
);

select * from CleanData

select*
from CleanData
