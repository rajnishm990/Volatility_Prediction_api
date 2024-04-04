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
  "ticker": "SHOPERSTOP.BSE",
  "use_new_data": true,
  "n_observations": 100,
  "p": 1,
  "q": 1
} ```

#### Response
```json

{
  "success": true,
  "message": "Model saved as AAPL_garch_model.pkl"
}```

`GET /predict`

#### Description

This endpoint predicts volatility using a fitted GARCH model.

#### Request Parameters

- `ticker` (string): Ticker symbol for selecting the company's stock data.
- `n_days` (integer): Number of days for which volatility is to be predicted.

#### Request Body Example

```json
{
  "ticker": "SHOPERSTOP.BSE",
  "n_days": 100,
}```


#### Response
```json
{
  "success": true,
  "predictions": [0.025, 0.032, 0.021, ...],
  "message": "" ,
}```

#### Status Codes
`200 OK`: Successful request.
`400 Bad Request`: Invalid parameters or missing required parameters.
`404 Not Found`: Resource not found.
`500 Internal Server Error`: Server encountered an error while processing the request.

