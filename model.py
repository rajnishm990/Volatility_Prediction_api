import os
from glob import glob

import joblib
import pandas as pd
from arch import arch_model
from config import settings
from data import AlphaVantageAPI, SQLRepository


class GarchModel:
    """Class for training GARCH model and generating predictions.

    Atttributes
    -----------
    ticker : str
        Ticker symbol of the equity whose volatility will be predicted.
    repo : SQLRepository
        The repository where the training data will be stored.
    use_new_data : bool
        Whether to download new data from the AlphaVantage API to train
        the model or to use the existing data stored in the repository.
    model_directory : str
        Path for directory where trained models will be stored.

    Methods
    -------
    wrangle_data
        Generate equity returns from data in database.
    fit
        Fit model to training data.
    predict
        Generate volatilty forecast from trained model.
    dump
        Save trained model to file.
    load
        Load trained model from file.
    """
    def __init__ (self,ticker,repo,use_new_data):
        self.ticker = ticker
        self.repo = repo
        self.use_new_data = use_new_data
        self.model_directory = settings.model_directory
        
       
    
    def wrangle_data(self,n_observations):
        """Extract data from database (or get from AlphaVantage), transform it
        for training model, and attach it to `self.data`.

        Parameters
        ----------
        n_observations : int
            Number of observations to retrieve from database

        Returns
        -------
        None
        """
        if self.use_new_data:
            api = AlphaVantageAPI(settings.alpha_api_key)
            data = api.get_daily(ticker=self.ticker)
            self.repo.insert_table(table_name=self.ticker,records=data,if_exists='replace')
        df = self.repo.read_table(table_name=self.ticker,limit=n_observations)
        df['returns'] = df["close"].pct_change() * 100

        self.data=df["returns"].dropna()
    
    def fit(self,p,q):
        """Create model, fit to `self.data`, and attach to `self.model` attribute.
        For assignment, also assigns adds metrics to `self.aic` and `self.bic`.

        Parameters
        ----------
        p : int
            Lag order of the symmetric innovation

        q : ind
            Lag order of lagged volatility

        Returns
        -------
        None
        """
        model = arch_model(self.data , p=p,q=q ,rescale=False).fit(disp=0)
        self.model = model
    
    def __clean_predictions(self,predictions):
        """Reformat model prediction to JSON.

        Parameters
        ----------
        prediction : pd.DataFrame
            Variance from a `ARCHModelForecast`

        Returns
        -------
        dict
            Forecast of volatility. Each key is date in ISO 8601 format.
            Each value is predicted volatility.
        """
        start = predictions.index[0] + pd.DateOffset(days=1)
        date_range = pd.bdate_range(start=start,periods=predictions.shape[1])
        date_index = [d.isoformat() for d in date_range]
        data = predictions.values.flatten() ** 0.5
        pred_series = pd.Series(data,index=date_index)
        return pred_series.to_dict()
    
    def predict_volatility(self,horizon=5):

        """Predict volatility using `self.model`

        Parameters
        ----------
        horizon : int
            Horizon of forecast, by default 5.

        Returns
        -------
        dict
            Forecast of volatility. Each key is date in ISO 8601 format.
            Each value is predicted volatility.
        """
        predictions = self.model.forecast(horizon=horizon,reindex=False).variance ** 0.5
        prediction_formatted = self.__clean_predictions(predictions=predictions)
        return prediction_formatted
    def dump(self):
        """Save model to `self.model_directory` with timestamp.

        Returns
        -------
        str
            filepath where model was saved.
        """
        timestamp = pd.Timestamp.now().isoformat()
        timestamp = timestamp.replace(":", "_")
        filepath = os.path.join(self.model_directory,f"{timestamp}_{self.ticker}.pkl")
        joblib.dump(self.model,filepath)
        return filepath
    def load(self):
        """Load most recent model in `self.model_directory` for `self.ticker`,
        attach to `self.model` attribute.

        """
        try:
            pattern = os.path.join(self.model_directory,f"*{self.ticker}.pkl")
            model_path = sorted(glob(pattern))[-1]
        except IndexError:
            raise Exception(f"no model with {self.ticker} name")
        model = joblib.load(model_path)
        self.model=model
    


