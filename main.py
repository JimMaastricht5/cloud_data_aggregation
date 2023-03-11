# MIT License
#
# 2023 Jim Maastricht
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import pandas as pd
from datetime import datetime
from datetime import timedelta
import pytz
import urllib.request
from urllib.error import HTTPError


def build_common_name(df, target_col):
    df['Common Name'] = df[target_col]
    df['Common Name'] = [name[name.find(' ') + 1:] if name.find(' ') >= 0 else name
                         for name in df['Common Name']]
    df['Common Name'] = [name[name.find('(') + 1: name.find(')')] if name.find('(') >= 0 else name
                         for name in df['Common Name']]
    return df


def load_bird_occurrences(dates):
    # setup df like file, pulled from streamlit website function
    url_prefix = 'https://storage.googleapis.com/tweeterssp-web-site-contents/'
    df = pd.DataFrame(data=None, columns=['Unnamed: 0', 'Feeder Name', 'Species',
                                          'Date Time', 'Hour'], dtype=None)
    df['Date Time'] = pd.to_datetime(df['Date Time'])
    for date in dates:
        try:  # read 3 days of files
            urllib.request.urlretrieve(url_prefix + date + 'web_occurrences.csv', 'web_occurrences.csv')
            df_read = pd.read_csv('web_occurrences.csv')
            df_read['Date Time'] = pd.to_datetime(df_read['Date Time'])
            df_read['Hour'] = pd.to_numeric(df_read['Date Time'].dt.strftime('%H')) + \
                pd.to_numeric(df_read['Date Time'].dt.strftime('%M')) / 60
            df_read['Day.Hour'] = pd.to_numeric(df_read['Date Time'].dt.strftime('%d')) + \
                pd.to_numeric(df_read['Date Time'].dt.strftime('%H')) / 100 + \
                pd.to_numeric(df_read['Date Time'].dt.strftime('%M')) / 100 / 60
            df = pd.concat([df, df_read])
        except urllib.error.URLError as e:
            print(f'no web occurrences found for {date}')
            print(e)
            dates.remove(date)  # remove date if not found
    df = build_common_name(df, 'Species')  # build common name for merged df
    df = df.drop(['Unnamed: 0'], axis='columns')
    return df


def main():
    dates = []
    tz = pytz.timezone("America/Chicago")  # localize time to current madison wi cst bird feeder
    dates.append(datetime.now(tz).strftime('%Y-%m-%d'))
    dates.append((datetime.now(tz) - timedelta(days=1)).strftime('%Y-%m-%d'))
    dates.append((datetime.now(tz) - timedelta(days=2)).strftime('%Y-%m-%d'))
    df = load_bird_occurrences([dates[1]])  # only process yesterday's date, date[1]
    print(df)

    return


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
