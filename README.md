# Volatility Prediction API Documentation

The Volatility Prediction API is designed to facilitate volatility forecasting for stocks using the GARCH(1,1) model. It leverages the ALPHA vantage API to fetch stock data, stores it in a local SQL database, fits the data to the GARCH(1,1) model, and provides predictions for future volatility.

## Base URL

`http://yourapi.com`

## Endpoints

### Fit Data to GARCH Model

#### Endpoint

`POST /fit`

#### Description

This endpoint fits stock data to the GARCH(1,1) model. It allows users to specify whether to use new data from ALPHA vantage API or use existing data from the local SQL database. The fitted model is stored in the local storage for future predictions.

#### Parameters

- `ticker` (string): Ticker symbol for selecting the company's stock data.
- `use_new_data` (boolean): Indicates whether to use new data from ALPHA vantage API (`true`) or existing data from the SQL database (`false`).
- `n_observations` (integer): Number of days of data to be used for fitting.
- `p` (integer): Parameter `p` for the GARCH model.
- `q` (integer): Parameter `q` for the GARCH model.

#### Request Body Example

```json
{
  "ticker": "AAPL",
  "use_new_data": true,
  "n_observations": 100,
  "p": 1,
  "q": 1
}


#### Response
- success (boolean): Indicates whether the fit was successful.
- message (string): Name of the saved model file in the local storage directory.





### Get Result of your Predictios

#### Endpoint

`GET /predict`

#### Description

This endpoint finds the stored model from your local directory and returns the volatility 

#### Parameters

- `ticker` (string): Ticker symbol for selecting the company's stock data.
- `n_days` (integer): Number of days of data to be shown.


#### Request Body Example

```json
{
  "ticker": "AAPL",
  "n_observations": 100,
}


#### Response
- success (boolean): Indicates whether the fit was successful.
- message (string): Name of the saved model file in the local storage directory.
- forecast (dictionary): The volality precitions


