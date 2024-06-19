[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-24ddc0f5d75046c5622901739e7c5dd533143b0c8e959d652212380cedb1ea36.svg)](https://classroom.github.com/a/Z1npak42)

# Sentiment Analysis & LDA of User Discussion on Emotional Chatbots

Note: This program is still ongoing. Please contact author if you need to use the data or scripts. 

Welcome to all discussion :)

## Abstract

This project collected and analyzed people’s discussions on their experience with emotional chatbots from social media platforms. Based on web scraping, sentiment analysis, and topic modeling, this project showed how emotional chatbots have become more popular since the rapid development of AIGC and discussed the potential pessimistic side of human-chatbot communication.

## Data source and collection

To encompass a more extensive dataset, the project collected internet forum data from both the international internet and the Simplified Chinese internet, specifically from Reddit and Douban (Chinese).

As the project may want to conduct _cultural comparison_ in the future, and language's cultural cues may get lose during translation, I keeped the database as its original language. I designed following NLP analysis process for both En and Cn formats.

### Reddit
* [Replika.ai](https://www.reddit.com/r/replika/)
* [Character.AI](https://www.reddit.com/r/CharacterAI/)
* collect script: **get_data_Reddit.py**, API request

### Douban (Chinese forum)
* [Love between Human & Machine](https://www.douban.com/group/rjzl/)
* [Did you interact with AI today?](https://www.douban.com/group/735729/)
* [My Replika Takes on Human-like Qualities](https://www.douban.com/group/690305/) 
* collect script: **get_data_Douban.py**, html parse & beautifulsoup (use login cookie)


_Recommend do not rerun the two py. as it may take some time and raw data already saved in data/raw folder._
_Douban has constrain in group page. If rerun too much, cookie may get invalid and need relogin_

## Data clean and Sentiment Analysis

See python script **clean_data.py**, which could clean both datasets

* For En text:  Roberta Pretrained Model, reference [Python Sentiment Analysis Project with NLTK and 🤗 Transformers](https://www.youtube.com/watch?v=QpzMWQvxXWk)

* For Cn text: Tranditional word count (calculates the modifier of strength adverbs before emotional words, and the potential emotional semantic reversal effect), reference [Cntext](https://github.com/hiDaDeng/cnsenti)

## LDA 

See python script **run_analysis**. 

As the LDA result is not good enough, future may adjust and reset all parameters

Note: 
* function topic_n_calculator(filename, tf, min_n, max_n) is default not run. Previous run result shows n_topic = 13 appear elbow point, then I set topic number == 13.
* run_analysis already contains LDA result visualization. Later **visualiza_results.ipynb** file only did the general visualzation and embeded LDA visual html made from this script.


## Things you should know...

All the codes could be executed successfully on Python 3.10.11
