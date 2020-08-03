import sys
sys.path.append(r'directory')
from reddit_api import subreddit_sentiment
from weighted_sentiment import weighted_sentiments
from tickers_dict_script import tickers_dict
import pandas as pd
import pyodbc

sub = ['investing','wallstreetbets','stocks','StockMarket','CanadianInvestor','options','robinhood','personalfinance']

tickers = tickers_dict()

scores = []

for a in sub:
    scores.append(subreddit_sentiment(a, tickers))

temp_results = pd.DataFrame.from_dict(weighted_sentiments(scores, tickers))
final_results = pd.DataFrame.transpose(temp_results)
final_results.rename(columns={'Unnamed: 0':'Tickers','0': "Total Score", '1': "Sentiment"})
final_results.insert(0, 'TimeStamp', pd.datetime.now().replace(microsecond=0))
final_results.to_csv(r'file_location')

final_results = final_results[final_results['tickers'].notnull()]
connection = pyodbc.connect('Driver={SQL Server};Server=server.database.windows.net;Database=database;uid=uid;pwd=pwd')
cursor = connection.cursor()
for index,row in final_results.iterrows():
    cursor.execute("INSERT INTO dbo.Test_Table3([tickers],[timestamp],[0],[1]) values (?,?,?,?)", row['Tickers'], row['TimeStamp'] , row['Total Score'],row['Sentiment']) 
    connection.commit()
cursor.close()
connection.close()
