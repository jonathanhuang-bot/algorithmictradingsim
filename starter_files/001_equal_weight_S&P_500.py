import numpy as np
import pandas as pd
import requests
import xlsxwriter
import math
import os
stocks = pd.read_csv("C:/Users/jonat/Desktop/algorithmictradingsim/starter_files/sp_500_stocks.csv")

from secretsp import IEX_CLOUD_API_TOKEN
os.environ['IEX_API_VERSION'] = 'iexcloud-sandbox'
os.environ['IEX_SANDBOX'] = 'enable'
symbol = 'AAPL'
api_url = f"https://cloud.iexapis.com/stable/stock/{symbol}/quote/?token={IEX_CLOUD_API_TOKEN}"
data = requests.get(api_url)
print(data.status_code)
print(api_url)
price = data['latestPrice']
market_cap = data['marketCap']

my_columns = ['Ticker', 'Stock Price', "Market Capitalization", 'Number of Shares to Buy']
df = pd.DataFrame(columns = my_columns)
df.append(pd.Series[symbol, price, market_cap, 'N/A'],
          index = my_columns)
for stock in stocks['Ticker']:
    api_url = f"https://cloud.iexapis.com/stable/stock/{symbol}/quote/?token={IEX_CLOUD_API_TOKEN}"
    data = requests.get(api_url).json()
    df.append(pd.Series(
        [stock.
         data['latestPrice'],
         data['marketCap'],
         'N/A'],
         index = my_columns),
        ignore_index = True
    )
def chunks (lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
symbol_groups = list(chunks(stocks['Ticker'], 100))
symbol_strings = []
for i in range(0, len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i]))
for symbol_string in symbol_strings:
    batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch?symbols={symbol_string}&types=quote&token={IEX_CLOUD_API_TOKEN}'
    data = requests.get(batch_api_call_url).json()
    for symbol in symbol_string.split(','):
        df = df.append(pd.Series([symbol,
                                  data[symbol]['quote']['latestPrice'],
                                  data[symbol]['quote']['marketCap'],
                                  'N/A'],
                                  index = my_columns),
                                  ignore_index=True)

portfolio_size = input('Enter the value of your portfolio:')
try:
    val = float(portfolio_size)
    print(val)
except ValueError:
    print('Please enter an integer')
    portfolio_size = input('Enter the value of your portfolio:')
    val = float(portfolio_size)

position_size = val/len(df.index)
for i in range(0, len(df.index)):
    df.loc[i, 'Number of Shares to Buy'] = math.floor(position_size/df.loc[i,'Stock Price'])

writer = pd.ExcelWriter('recommended trades.xlsx', engine = 'xlsxwriter')
df.to_excel(writer, 'Recommended Trades', index = False)
background_color = '#0a0a23'
font_color = '#ffffff'
string_format = writer.book.add_format(
    {
        "font_color": font_color,
        "bg_color" : background_color,
        'border': 1
    }
)
dollar_format = writer.book.add_format(
    {
        'num_format':'$0.00',
        "font_color": font_color,
        "bg_color" : background_color,
        'border': 1
    }
)
integer_format = writer.book.add_format(
    {
        "num_format" : '0',
        "font_color": font_color,
        "bg_color" : background_color,
        'border': 1
    }
)
writer.sheets['Recommended Trades'].set_columns('A:A', 18, string_format)
writer.sheets['Recommended Trades'].set_columns('B:B', 18, string_format)
writer.sheets['Recommended Trades'].set_columns('C:C', 18, string_format)
writer.sheets['Recommended Trades'].set_columns('D:D', 18, string_format)
writer.save()
column_formats = {
    'A': ['Ticker', string_format],
    'B' : ['Stock Price', dollar_format],
    'C' : ['Market Capitalization', dollar_format],
    'D' : ['Number of Shares to Buy', integer_format]
}
for column in column_formats.keys():
    writer.sheets['Recommended Trades'].set_column(f'{column}:{column}', 18, column_formats[column][1])
writer.save()