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

            # yesterday = dt.date.today() - dt.timedelta(1)
            # unix_time = yesterday.strftime("%s")  # Second as a decimal number [00,61] (or Unix Timestamp)
            now_time = dt.datetime.fromtimestamp(float(cts))
            # now_time_in_format = dt.unicode(now_time)
            parsed_data.append((cts, now_time, float(cdata[1]), float(cdata[2]), float(cdata[3]), float(cdata[4]), float(cdata[5])))
    df = pd.DataFrame(parsed_data)
    df.columns = ['tstamp', 'datetime', 'o', 'h', 'l', 'c', 'v'] #date_time open high low close volume
    # df.index = df.ts
    # del df['ts']

    timestamp_oneday = 86400

    daily_stock_dictionary = {}
    df_next_index = 0
    df_length = len(df.index)

    # for i in range(df.size):
    while df_next_index < df_length:
        initial_timestamp = df.get_value(df_next_index, 'tstamp')
        temp_datetime = dt.datetime.fromtimestamp(initial_timestamp)
        day_plus_timestamp = initial_timestamp + timestamp_oneday
        mask = (df['tstamp'] > initial_timestamp) & (df['tstamp'] <= day_plus_timestamp)
        dframes = df.loc[mask]
        daily_stock_dictionary[temp_datetime] = dframes
        dframe_length = len(dframes.index)
        temp_df_lastindex_timestamp = dframes.get_value(dframe_length, 'tstamp')
        df_next_index += dframe_length

    print (daily_stock_dictionary)
             # = dframes.get_value(lastindex_number, 'tstamp')




    # dframes.
       # for j in range(j, df.size):
       #   j_timestamp = df.get_value(j, 'ts')
       #
       #   if j_timestamp < until_tomorrow:
       #     frame1 = df.iloc[[j]]

    return df


    def getCurrentPrice(self):
        self.share.refresh()
        return self.share.get_price()


    def plot_prices(prices):
        plt.title('Opening stock prices')
        plt.xlabel('day')
        plt.ylabel('price')
        plt.plot(prices)
        plt.savefig('prices.png')