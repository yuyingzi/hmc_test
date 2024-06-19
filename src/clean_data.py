'''
This file aims to do the data clean and sentiment analysis
Nov 29, 2023
Author: Yuyingzi Yang (Yoko)
'''

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
plt.style.use('ggplot')
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from tqdm.notebook import tqdm
from transformers import AutoTokenizer # transformers is in the hugging face website
from transformers import AutoModelForSequenceClassification 
from scipy.special import softmax
import emoji
import re

MODEL = f"cardiffnlp/twitter-roberta-base-sentiment" # this is providing by hugging face that already trained
tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForSequenceClassification.from_pretrained(MODEL) 
sia = SentimentIntensityAnalyzer()

path = '/Users/yinterested/github-classroom/final-project-yuyingzi/'

def clean_text(text):
    # Remove unwanted characters (e.g., '&#x200B;\n\n')
    text = re.sub(r'&#[a-zA-Z0-9]+;|\n', ' ', text)
    # Remove URLs
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'https\S+', '', text)
    # Remove special characters like '&#x200B;' and '\n'
    text = re.sub(r'&#\w+;', ' ', text)
    text = re.sub(r'\\n', ' ', text)
    # Remove emojis
    text = ''.join(char for char in text if char not in emoji.EMOJI_DATA)
    # Additional cleanup for specific patterns
    text = re.sub(r'\s+', ' ', text).strip()  # Remove extra spaces
    
    return text

def polarity_scores_roberta(example):
    encoded_text = tokenizer(example, return_tensors='pt')
    output = model(**encoded_text)
    scores = output[0][0].detach().numpy()
    scores = softmax(scores)
    scores_dict = {
        'roberta_neg' : scores[0],
        'roberta_neu' : scores[1],
        'roberta_pos' : scores[2]
    }
    return scores_dict


def sentiment_analysis_eg(filename, text_col_name, index_col_name):
    # set a dic named 'res' to store the result
    df = pd.read_csv(filename)
    res = {}
    for i, row in tqdm(df.iterrows(), total=len(df)):
        try:
            text = row[text_col_name] # Here we use "title text" as analitical basement
            myid = row[index_col_name]
            vader_result = sia.polarity_scores(text)
            vader_result_rename = {}
            for key, value in vader_result.items():
                vader_result_rename[f"vader_{key}"] = value
            roberta_result = polarity_scores_roberta(text)
            both = {**vader_result_rename, **roberta_result}
            res[myid] = both
        # there may be certain reviews that too big for the model to handle
        # so we will skip those by using try & expept block
        except RuntimeError: 
            print(f'Broke for id {myid}')

    # convert dic to dataframe and merge with the original
    results_df = pd.DataFrame(res).T
    results_df = results_df.reset_index().rename(columns={'index': index_col_name})
    results_df = results_df.merge(df, how='left')
    
    return results_df


def sentiment_analysis_ch(filename, text_col_name, index_col_name):
    from cnsenti import Sentiment
    senti = Sentiment()
    df = pd.read_csv(filename)
    # Run the polarity score on the entire dataset
    res = {}
    for i, row in tqdm(df.iterrows(), total=len(df)):
        text = row[text_col_name]
        myid = row[index_col_name]
        res[myid] = senti.sentiment_calculate(text)
        
    # store the res dataframe into our old dataframe
    results_df = pd.DataFrame(res).T
    results_df = results_df.reset_index().rename(columns={'index': index_col_name}) 
    # rename the data with ID index so that we could merge the dataframe by index 
    results_df = df.merge(results_df, how='left') # left merge 
    
    return results_df


def clean_red(path, text_name_red, index_name_red):
    # for Reddit 
    filename_reddit = f'{path}data/raw/Reddit_allpost.csv'
    Reddit_df = sentiment_analysis_eg(filename_reddit, text_name_red, index_name_red)

    # spectial dataclean process: generate variable: score_new
    Reddit_df['Score_new'] = pd.cut(Reddit_df['Score'], bins=[0, 1, 3, 6, 10, 100, 500, 1000, 2000, float('inf')], labels=[1, 2, 3, 4, 5, 6, 7, 8, 9], right=False)
    # Convert 'Score_new' to numeric
    Reddit_df['Score_new'] = pd.to_numeric(Reddit_df['Score_new'], errors='coerce')
    
    Reddit_df.to_csv(f'{path}data/processed/Reddit_sensitive.csv', index = None)
    
    return f'success cleaned reddit, data lenth: {len(Reddit_df)}'
    

def clean_dou(path, text_name_dou, index_name_dou):
    # for Douban 
    filename_Dou = f'{path}data/raw/Douban_allpost.csv'
    # spectial dataclean process: clean all the advertise and interview hiring info (not related to the project)
    Dou_df = sentiment_analysis_ch(filename_Dou, text_name_dou, index_name_dou)
    
    # Remove unwanted rows based on title content
    # here are the chinese words about advertising which not related to our project
    titles_to_remove = ['已报备', 'ChatGPT写作大揭秘']
    for word in titles_to_remove:
        mask_title = Dou_df['Title'].str.contains(word)
        Dou_df = Dou_df[~mask_title]
        
    # Define keywords for content filtering
    # here are the chinese words about advertising which not related to our project
    keywords = ['招募', '访谈', '论文', '问卷', '招聘', '组规',
                '受访者', '调研报告', '费用免费', '市场营销', '直播创业', '发展主题沙龙',
                '产品经理', '邀请码', '调研', '量表',
                '国家互联网信息办公室关于《生成式人工智能服务管理办法（征求意见稿）》']

    # Filter rows based on content keywords
    mask_content = Dou_df['Content'].str.contains('|'.join(keywords), na=False)
    Dou_df = Dou_df[~mask_content]

    # generate text for next analysis
    Dou_df['text'] = Dou_df['Title'].astype(str) + ' ' + Dou_df['Content'].astype(str)
    Dou_df['text'] = Dou_df['text'].apply(clean_text) # clean the text 
    Dou_df['Like'] = Dou_df['Like'].fillna(0)
    Dou_df.to_csv(f'{path}data/processed/Douban_sensitive.csv', index = None)
    
    return f'success cleaned Douban, data lenth: {len(Dou_df)}'

    

# Read in data, clean and calculate the sentiment 
text_name_red = 'Title'
index_name_red = 'id'
clean_red(path, text_name_red, index_name_red)

text_name_dou = 'Title'
index_name_dou = 'Post URL'
clean_dou(path, text_name_dou, index_name_dou)

