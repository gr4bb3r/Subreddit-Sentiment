#https://github.com/aleszu/reddit-sentiment-analysis/blob/master/r_subreddit.py
#https://textblob.readthedocs.io/en/dev/quickstart.html#sentiment-analysis

import praw
import pandas as pd
#import datetime as dt
from textblob import TextBlob
import numpy as np

sub = 'investing' 
tickers = {0:['TSLA','Telsa','tesla'],
        1:['SPY','S&P','S&P 500','s&p','spy'],
        2:['AMD'],
        3:['DIS','Disney','disney'],
        4:['AAPL','Apple','apple'],
        5:['market','Market'],
        6:['Vaccine','vaccine','oxford','Oxford'],
        7:['PFE','Pfizer','pfizer']} 
def subreddit_sentiment(sub,tickers):
    reddit = praw.Reddit(client_id='PERSONAL_USE_SCRIPT_14_CHARS', \
                     client_secret='SECRET_KEY_27_CHARS ', \
                     user_agent='YOUR_APP_NAME', \
                     username='YOUR_REDDIT_USER_NAME', \
                     password='YOUR_REDDIT_LOGIN_PASSWORD')
    
    subreddit = reddit.subreddit(sub)
    top_subreddit = subreddit.top('day',limit=1000)
    
    #collect posts from sub    
    topics_dict = { "title":[], 
                    "score":[], 
                    "id":[], "url":[],  
                    "comms_num": [], 
                    "created": [], 
                    "body":[]}
    
    for submission in top_subreddit:
        topics_dict["title"].append(submission.title)
        topics_dict["score"].append(submission.score)
        topics_dict["id"].append(submission.id)
        topics_dict["url"].append(submission.url)
        topics_dict["comms_num"].append(submission.num_comments)
        topics_dict["created"].append(submission.created)
        topics_dict["body"].append(submission.selftext)
    
    topics_data = pd.DataFrame(topics_dict)

    #posts are now in dataframe form
    topics_filt = {}
    #topics_filt will find posts containing ticker keywords
    dupl_dict = {}
    #dupl_dict will deal with duplicate matches
    for i in tickers:
        for j in tickers[i]:
            dupl_dict[j] = i
            if len(topics_data[topics_data['title'].str.contains(j)]) == 0:
                continue
            else:
                topics_filt[j] = [topics_data[topics_data['title'].str.contains(j)].iloc[:,2].iloc[:]] 
                
    
    comms_dict = { "topic": [], "body":[],"score":[], "comm_id":[], "created":[],"dupl_key":[] }
    #scrapes comments only for posts that have ticker matches
    for keyword in topics_filt:
        temp_df = pd.DataFrame(topics_filt[keyword])
        temp_df = pd.DataFrame.transpose(temp_df)
        iteration = 1
        for topic in temp_df["id"]:
            iteration += 1
            submission = reddit.submission(id=topic)
            submission.comments.replace_more(limit=0)
            for top_level_comment in submission.comments:
                comms_dict["topic"].append(topic)
                comms_dict["body"].append(top_level_comment.body)
                comms_dict["score"].append(top_level_comment.score)
                comms_dict["comm_id"].append(top_level_comment)
                comms_dict["created"].append(top_level_comment.created)
                comms_dict["dupl_key"].append(dupl_dict[keyword])
    
    comms_data = pd.DataFrame(comms_dict)
    comms_data = comms_data.loc[comms_data['score'] >= 1]
    #data frame with comments having a positive score only, with their corresponding ticker mentioned in post
    pol_dict = {}
    #record the polarity of each comment
    cnt1 = 0
    for reddit_comment, topic, dupl_key1, score in zip(comms_data.iloc[:,1],comms_data.iloc[:,0],
                                                       comms_data.iloc[:,5],comms_data.iloc[:,2]):
        commt = TextBlob(reddit_comment)
        pol_dict[cnt1] = [reddit_comment,topic,commt.sentiment.polarity,dupl_key1,score]
        cnt1 += 1
    
    pol_df = pd.DataFrame(pol_dict)
    pol_df = pd.DataFrame.transpose(pol_df)
        
    pol_df = pol_df.drop_duplicates(keep = False)
    #dataframe with sentiment polarity
    pol_df[5] = 'NA'
    pol_df[6] = 'NA'
    #Take out the rows where sentiment polarity = 0
    pol_df.loc[pol_df[2] == 0,2] = np.nan
    pol_df.dropna(subset = [2], inplace=True)
    #Total score for comments containing the keywords
    total_score = pol_df[4].sum()
    #Weighting the score over total score. Not used in this version of the method
    cnt3 = 0
    for score1 in pol_df[4]:
        pol_df.iloc[cnt3,5] = score1/total_score
        cnt3 += 1
    #Multiply the sentiment by the score. To magnify based on the number of people who feel that sentiment.
    cnt4 = 0
    for sent, w8 in zip(pol_df[2], pol_df[4]):
        pol_df.iloc[cnt4,6] = sent * w8
        cnt4 += 1
    #Divide the sum of 'weighted' scores by sum of total score. If 100% of voters feel 100% positive sentiment, score will be 1.0    
    ticker_means = {}
    for v in tickers:
        try: ticker_means[tickers[v][0]] = [pol_df.loc[pol_df[3]== v,6].sum()/pol_df.loc[pol_df[3]== v,4].sum()]
        except ZeroDivisionError:
            ticker_means[tickers[v][0]] = [0]
    
    for t,p in zip(ticker_means,tickers):
        ticker_means[t].append(pol_df.loc[pol_df[3]== p,4].sum())
    
    cnt2 = 0
    for tick_id in pol_df[3]:
        pol_df.iloc[cnt2,3] = tickers[tick_id][0]
        cnt2 += 1
    
    return ticker_means
    


subreddit_sentiment(sub,tickers)

