import sqlite3

from config import settings
from data import SQLRepository
from fastapi import FastAPI
from model import GarchModel
from pydantic_settings import BaseSettings


#classes for type hinting using Pydantic

class FitIn(BaseSettings):
    ticker: str 
    use_new_data: bool 
    n_observations: int
    p: int 
    q: int 

class FitOut(FitIn):
    success: bool 
    message: str 

class PredictIn(BaseSettings):
    ticker: str
    n_days: int 

class PredictOut(PredictIn):
    success: bool
    message: str
    forecast: dict 

#helper Function for Model 
def build_model(ticker,use_new_data):

    # Create DB connection
    connection = sqlite3.connect(settings.db_name,check_same_thread=False)

    # Create `SQLRepository`
    repo = SQLRepository(connection=connection)

    # Create model
    model = GarchModel(ticker=ticker,repo=repo,use_new_data=use_new_data)

    # Return model
    return model

app = FastAPI()

#API endpoints 
@app.get("/",status_code=200)
def index():
    return {"message":"Welcome to the GARCH model API"}

@app.post("/fit",response_model=FitOut,status_code=200)
def fit(request: FitIn):
    """Fit model, return confirmation message.

    Parameters
    ----------
    request : FitIn

    Returns
    ------
    dict
        Must conform to `FitOut` class
    """
    #payload
    response = request.dict()
    try:
        model = build_model(ticker=request.ticker,use_new_data=request.use_new_data)
        model.wrangle_data(n_observations=request.n_observations)
        model.fit(p=request.p,q=request.q)
        filename= model.dump()
        response["success"] = True 
        response["message"] = f"Model saved as '{filename}' "
    except Exception as e:
        response["success"] = False 
        response["message"] = str(e)
    
    return response

@app.get("/predict",response_model=PredictOut ,status_code=200)
def get_prediction(request: PredictIn):
    #payload
    response = request.dict()

    try:
        model = build_model(ticker=request.ticker,use_new_data=False)
        model.load()
        forecast = model.predict_volatility(horizon=request.n_days)
        response["success"] = True 
        response["message"] = "Forecast generated"
        response["forecast"] = forecast
    except Exception as e:
        response["success"] = False 
        response["message"] = str(e)
        response["forecast"] = {}
    
    return response


