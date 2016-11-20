from matplotlib import pyplot as plt
import urllib
import numpy as np
import datetime as dt
import pandas as pd
from pathlib import Path
from pandas_datareader import data as web

class SharePriceGetter():
    def __init__(self, share_symbol):
        self.share_symbol = share_symbol
        self.cache_filename = share_symbol + '_stock_prices.npy'

    def get_price_list(self, start_date, end_date):
        if Path(self.cache_filename).is_file():
            return np.load(self.cache_filename)
        else:
            stock_prices = self.__get_prices__(start_date, end_date)
            np.save(self.cache_filename, stock_prices)
            return stock_prices

    def __get_prices__(self, start_date, end_date):
        dt_start_date = dt.datetime.strptime(start_date, '%Y-%m-%d')
        dt_end_date = dt.datetime.strptime(end_date, '%Y-%m-%d')
        days_between_dates = dt_end_date - dt_start_date
        window = days_between_dates.days
        return __google_api_get_price__(self.share_symbol)

    def getCurrentPrice(self):
        self.share.refresh()
        return self.share.get_price()

def __google_api_get_price__(share_symbol):
    start = dt.datetime(1999, 1, 10)
    end = dt.datetime(2016, 11, 19)
    df = web.DataReader("LSE:"+share_symbol, 'google', start, end)
    ts_list = df.index.tolist()  # a list of Timestamp's
    date_list = [int(round(ts.to_datetime().timestamp())) for ts in ts_list]
    date_str_list = [str(date) for date in date_list]
    df['time_stamp'] = date_str_list
    df['index_c'] = range(0, len(df))
    df['d_time'] = df.index
    del df['d_time']
    df.index = df.index_c
    del df['index_c']
    return df


