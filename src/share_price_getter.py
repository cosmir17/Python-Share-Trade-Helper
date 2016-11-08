from matplotlib import pyplot as plt
import urllib
import numpy as np
import datetime as dt
import pandas as pd
from pathlib import Path

class SharePriceGetter():
    def __init__(self, share_symbol, sec_interval):
        self.share_symbol = share_symbol
        self.sec_interval = sec_interval
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
        return __google_api_get_price__(self.share_symbol, self.sec_interval, window)

    def getCurrentPrice(self):
        self.share.refresh()
        return self.share.get_price()

    def plot_prices(prices):
        plt.title('Opening stock prices')
        plt.xlabel('day')
        plt.ylabel('price ($)')
        plt.plot(prices)
        plt.savefig('prices.png')

def __google_api_get_price__(share_symbol, sec_interval, window):
    url_root = 'http://www.google.com/finance/getprices?i='
    url_root += str(sec_interval) + '&p=' + str(window)
    url_root += 'd&f=d,o,h,l,c,v&df=cpct&q=' + share_symbol

    response = urllib.request.urlopen(url_root)
    data = response.read().split(b'\n')
    parsed_data = []

    for i in range(7, len(data) - 1):
        cdata = data[i].split(b',')
        cdata0 = cdata[0]
        if b'a' in cdata0:  # first one record anchor timestamp
            anchor_stamp = cdata0.replace(b'a', b'')
            cts = int(anchor_stamp)
        elif b'TIMEZONE_OFFSET=0' in cdata0:
            pass
        else:
            coffset = int(cdata[0])
            cts = int(anchor_stamp) + (coffset * sec_interval)

            yesterday = dt.date.today() - dt.timedelta(1)
            unix_time = yesterday.strftime("%s")  # Second as a decimal number [00,61] (or Unix Timestamp)
            dt.datetime.fromtimestamp(float(cts))

            parsed_data.append((
                               dt.datetime.fromtimestamp(float(cts)), float(cdata[1]), float(cdata[2]), float(cdata[3]),
                               float(cdata[4]), float(cdata[5])))
    df = pd.DataFrame(parsed_data)
    df.columns = ['ts', 'o', 'h', 'l', 'c', 'v']
    df.index = df.ts
    del df['ts']
    return df