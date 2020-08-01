import sys
sys.path.append(r'directory')
from reddit_api import subreddit_sentiment
from weighted_sentiment import weighted_sentiments
from tickers_dict_script import tickers_dict
import pandas as pd

sub = ['investing','wallstreetbets','stocks','StockMarket','CanadianInvestor','options','robinhood','personalfinance']

tickers = tickers_dict()

scores = []

for a in sub:
    scores.append(subreddit_sentiment(a, tickers))

temp_results = pd.DataFrame.from_dict(weighted_sentiments(scores, tickers))
final_results = pd.DataFrame.transpose(temp_results)
final_results.rename(columns={0: "Total Score", 1: "Sentiment"})
final_results.insert(0, 'TimeStamp', pd.datetime.now().replace(microsecond=0))
final_results.to_csv(r'file_location')
