import pandas as pd
import ipdb
from datetime import datetime 
import numpy as np

def process(orders, deposits, withdrawals, sys_dep):
    required_cols = ['Date', 'Received Quantity', 'Received Currency',	'Sent Quantity',	'Sent Currency',	'Fee Amount',	'Fee Currency', 'Tag']
    dfs_to_concat = []
    
    # must add first page first. must copy header of first page. no header copied from any other page
    if deposits is not None:
        deposits_df = pd.read_csv(deposits, header = None)
        # change from 1d array to proper shape
        deposits_df = pd.DataFrame(deposits_df.values.reshape(int(deposits_df.shape[0] / 7), 7))
        new_header = deposits_df.iloc[0] #grab the first row for the header
        deposits_df = deposits_df[1:] #take the data less the header row
        deposits_df.columns = new_header #set the header row as the df header

        # reformat to cointracker standards
        deposits_df.rename(columns = {'Amount':'Received Quantity', 'Coin':'Received Currency', 'Fee':'Fee Amount'}, inplace = True)
        deposits_df['Sent Quantity'] = ''
        deposits_df['Sent Currency'] = ''
        deposits_df['Fee Currency'] = ''
        deposits_df['Tag'] = ''
        
        dfs_to_concat.append(deposits_df[required_cols])

    if sys_dep is not None:
        system_deposits_df = pd.read_csv(sys_dep, header = None)
        
        # change from 1d array to proper shape
        system_deposits_df = pd.DataFrame(system_deposits_df.values.reshape(int(system_deposits_df.shape[0] / 4),4))
        new_header = system_deposits_df.iloc[0] #grab the first row for the header
        system_deposits_df = system_deposits_df[1:] #take the data less the header row
        system_deposits_df.columns = new_header #set the header row as the df header

        # reformat to cointracker standards
        system_deposits_df.rename(columns = {'Amount':'Received Quantity', 'Coin':'Received Currency'}, inplace = True)
        system_deposits_df['Sent Quantity'] = ''
        system_deposits_df['Sent Currency'] = ''
        system_deposits_df['Fee Currency'] = ''
        system_deposits_df['Fee Amount'] = ''
        system_deposits_df['Tag'] = 'staked'
        
        dfs_to_concat.append(system_deposits_df[required_cols])

    if withdrawals is not None:
        withdrawals_df = pd.read_csv(withdrawals, header = None)
        
        # change from 1d array to proper shape
        withdrawals_df = pd.DataFrame(withdrawals_df.values.reshape(int(withdrawals_df.shape[0] / 7), 7))
        new_header = withdrawals_df.iloc[0] #grab the first row for the header
        withdrawals_df = withdrawals_df[1:] #take the data less the header row
        withdrawals_df.columns = new_header #set the header row as the df header

        # reformat to cointracker standards
        withdrawals_df.rename(columns = {'Amount':'Sent Quantity', 'Coin':'Sent Currency', 'Fee':'Fee Amount'}, inplace = True)
        withdrawals_df['Received Quantity'] = ''
        withdrawals_df['Received Currency'] = ''
        withdrawals_df['Fee Currency'] = withdrawals_df['Sent Currency']
        withdrawals_df['Tag'] = ''

        dfs_to_concat.append(withdrawals_df[required_cols])
    
    # be sure to download from spot order > order, not spot order > order history
    if orders is not None:
        df = pd.read_csv(orders)
        df['Date'] = pd.to_datetime(df['time'],format=' %Y-%m-%d_%H:%M:%S')
        
        for index, row in df.iterrows():
            # all hotbit markets are denominated by one of these
            for ticker in ['USDT', 'BTC']:
                if ticker in row['market']:
                    tickers = row['market'].split(ticker)
                    first_ticker = ticker if tickers[0] == '' else tickers[0]
                    second_ticker = ticker if tickers[1] == '' else tickers[1]

                    # reformat to cointracker standards
                    if row['side'] == 'buy':
                        df.loc[index, 'Received Currency'] = first_ticker
                        df.loc[index, 'Received Quantity'] = row['amount']
                        df.loc[index, 'Sent Currency'] = second_ticker
                        df.loc[index, 'Sent Quantity'] = row['deal']
                        
                    elif row['side'] == 'sell':
                        df.loc[index, 'Received Currency'] = second_ticker
                        df.loc[index, 'Received Quantity'] = row['deal']
                        df.loc[index, 'Sent Currency'] = first_ticker
                        df.loc[index, 'Sent Quantity'] = row['amount']
                        
                    else:
                        return "invalid value for column 'side' in Hotbit csv. Expected either 'sell' or 'buy'"
    
                    df.loc[index, 'Fee Currency'] = second_ticker
                    df.loc[index, 'Fee Amount'] = df.loc[index, 'fee']
    
        df['Tag'] = ''
        dfs_to_concat.append(df[required_cols])

    if len(dfs_to_concat) > 1:
        return pd.concat(dfs_to_concat)
    else:
        return dfs_to_concat[0]