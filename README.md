# Currency-Exchange-Project


## Project Overview

This project implements an automated ETL pipeline that collects daily currency exchange-rate data from the Central Bank of Uzbekistan API, cleans and transforms the data using Python, stores it in SQL Server, and presents the results through an interactive Power BI dashboard.

## Business Impact

* Reduces manual collection and preparation of exchange-rate data.
* Provides reliable and consistently formatted data for reporting.
* Tracks currency appreciation, depreciation, and daily rate changes.
* Enables faster monitoring and data-driven financial analysis.
* Supports automatic daily updates through a scheduled pipeline.

## ETL Workflow

1. **Extract:** Retrieve daily exchange-rate data from the Central Bank API.
2. **Load RAW:** Store the original API records in a SQL Server RAW table.
3. **Transform:** Clean, validate, and standardize the data using Python and pandas.
4. **Load CLEAN:** Insert the processed records into an analysis-ready SQL table.
5. **Visualize:** Connect Power BI to SQL Server and display exchange-rate insights.

## Data Transformations

* Standardized currency codes and names.
* Converted exchange rates and daily differences to numeric formats.
* Converted API dates into valid date values.
* Calculated the exchange rate per currency unit.
* Classified each currency as `Increased`, `Decreased`, or `No Change`.
* Created appreciation and depreciation indicators.
* Checked missing values and duplicate records.
* Preserved both original RAW data and cleaned analytical data.

## Dashboard Features

* Latest USD exchange rate
* Average exchange rate
* Number of appreciated and depreciated currencies
* Last data refresh date
* Top currencies by exchange rate
* Five largest positive daily changes
* Five largest negative daily changes
* Daily currency movement analysis

## Tools and Technologies

* Python
* pandas
* NumPy
* Requests
* SQL Server
* SQLAlchemy
* pyodbc
* Power BI
* Central Bank of Uzbekistan JSON API
* Windows Task Scheduler




## Data Source

Exchange-rate data is obtained from the official Central Bank of the Republic of Uzbekistan JSON API:

`https://cbu.uz/uz/arkhiv-kursov-valyut/json/`


## Automation

The pipeline can be configured in Windows Task Scheduler to run automatically every day. Each execution retrieves the latest data, processes it, and loads it into SQL Server for Power BI reporting.


## View the Result

To explore the complete interactive dashboard, download and open the following file in Power BI Desktop:

## View the Result

To explore the complete interactive dashboard, download and open the following file in Power BI Desktop:

[Open the Power BI Dashboard](currency_exchange.pbix)


