'''
This file aims to do the LDA
ATTENTION: As the LDA result may not be perfect, plz adjust and reset all the parameters if needed
Dec 1, 2023
Author: Yuyingzi 
'''

path = '/Users/yinterested/github-classroom/Fall23-DSCI-510/final-project-yuyingzi/'

import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import pyLDAvis.lda_model   
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
import en_core_web_lg
import string
from tqdm._tqdm_notebook import tqdm_notebook
import matplotlib.pyplot as plt
tqdm_notebook.pandas()

punctuations = string.punctuation
stopwords = list(STOP_WORDS)
# Parser
parser = en_core_web_lg.load()
parser.max_length = 21000

def spacy_tokenizer(sentence):
    mytokens = parser(sentence)
    mytokens = [ word.lemma_.lower().strip() if word.lemma_ != "-PRON-" else word.lower_ for word in mytokens ]
    mytokens = [ word for word in mytokens if word not in stopwords and word not in punctuations]
    mytokens = " ".join([i for i in mytokens])
    return mytokens
    

def save_lda_topics(filename, lda_topics, previews_df):
    # Save the distribution of doc-topics in previews dataframe
    topics_columns = [f"topic{i+1}" for i in range(lda_topics.shape[1])]
    previews_df[topics_columns] = lda_topics
    
    result_file_path = f"{path}data/processed/{filename}_{n_topics}topics.csv"
    previews_df.to_csv(result_file_path, index=False)
    
    return previews_df


def topic_top_words(model, tf_feature_names, n_top_words):
    # calculate the distribution of topic-keywords 
    for topic_idx, topic in enumerate(model.components_):  # lda.component相当于model.topic_word_
        print('Topic #%d:' % topic_idx)
        print(' '.join([tf_feature_names[i] for i in topic.argsort()[:-n_top_words - 1:-1]]))
        print("")
         
         
def parse_eg(df, text_col_name):
    # parse text for English words
    df[text_col_name] = df[text_col_name].fillna(df['Title']) # if Text_all is NA, filling with title
    df[text_col_name] = df[text_col_name].progress_apply(spacy_tokenizer)
    return df
      
      
def parse_ch(df, text_col_name):
    # parse text for Chinese words
    df[text_col_name] = df[text_col_name].fillna(df['Title']) # if Content is NA, filling with title
    import jieba
    dic_file = f"{path}src/utils/dic_douban.txt"
    # define the custom dictionary
    jieba.load_userdict(dic_file)
    jieba.initialize()
    def chinese_word_cut(mytext):
        return ' '.join(jieba.cut(mytext))
    df[text_col_name] = df[text_col_name].apply(chinese_word_cut)
    return df

def topic_n_calculator(filename, tf, min_n, max_n):
    ## If the number of topics is not determined, this function calculate the perplexity to test the best n
    from sklearn.decomposition import LatentDirichletAllocation
    n_topics = range(min_n, max_n)
    perplexityLst = [1.0] * len(n_topics)

    # training LDA and print the result
    lda_models = []
    for idx, n_topic in enumerate(n_topics):
        lda = LatentDirichletAllocation(n_components=n_topic,
                                        max_iter=50,
                                        learning_method='online',
                                        evaluate_every=200,
                                        #                                    perp_tol=0.1, #default
                                        #                                    doc_topic_prior=1/n_topic, #default
                                        #                                    topic_word_prior=1/n_topic, #default
                                        verbose=0)
        # t0 = time()
        lda.fit(tf)
        perplexityLst[idx] = lda.perplexity(tf)
        lda_models.append(lda)
    
    # return the best n_topic
    best_index = perplexityLst.index(min(perplexityLst))
    best_n_topic = n_topics[best_index]
    best_model = lda_models[best_index]
    print("Best number of Topic: ", best_n_topic)

    # report the perplexity & n_topic pic
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(n_topics, perplexityLst)
    ax.set_xlabel(f"{filename} of topics")
    ax.set_ylabel("Approximate Perplexity")
    plt.grid(True)
    plt.savefig(f'{path}results/perplexity_{min_n}-{max_n}.png', bbox_inches='tight')
    
    return f"Best number of Topic:{best_n_topic} " 


def LDA_operation_prepare(path, filename, text_col_name, n_features):
    ### loading the data
    file = f'{path}data/processed/{filename}_sensitive.csv'
    df = pd.read_csv(file)
    
    ### words preparation
    #   as we have both Chinese and English texts, set different parse methods
    if filename == 'Reddit':
        parse_eg(df, text_col_name)
        ## Vectorization for English text
        tf_vectorizer = TfidfVectorizer(strip_accents='unicode',
                                        max_features=n_features,
                                        max_df=0.9,
                                        min_df=0.02)  
    else:
        parse_ch(df, text_col_name)
        stop_file = f'{path}src/utils/stopwords.txt'
        stopword_list = open(stop_file, encoding='utf-8')
        stop_list = []
        flag_list = ['n', 'nz', 'vn','v']
        for line in stopword_list:
            line = re.sub(u'\n|\\r', '', line)
            stop_list.append(line)
        ## Vectorization for Chinese text
        tf_vectorizer = TfidfVectorizer(strip_accents='unicode',
                                        max_features=n_features,
                                        stop_words=stop_list,
                                        max_df=0.9,
                                        min_df=0.02)  
    
    tf = tf_vectorizer.fit_transform(df[text_col_name])
    
    ## if needed, calculator the sutable n_topics, here need to manul set min/max n
    # topic_n_calculator(filename, tf, min_n, max_n)
    
    return tf, tf_vectorizer


def LDA_operation(path, filename, text_col_name, n_features, n_topics):
    #### LDA
    file = f'{path}data/processed/{filename}_sensitive.csv'
    df = pd.read_csv(file)
    
    tf, tf_vectorizer = LDA_operation_prepare(path, filename, text_col_name, n_features)
    
    lda = LatentDirichletAllocation(n_components=n_topics,
                                    max_iter=50,
                                    learning_method='online',
                                    learning_offset=50,
                                    random_state=0)
    lda.fit(tf)
    
    # fit_transform: calculate distribution of doc-topics and save
    lda_topics = lda.fit_transform(tf) 
    save_lda_topics(filename, lda_topics, df) 
    
    # calculate and print each topic's keywords
    tf_feature_names = tf_vectorizer.get_feature_names_out()
    topic_top_words(lda, tf_feature_names, n_top_words) 

    # output visualization result
    pic = pyLDAvis.lda_model.prepare(lda, tf, tf_vectorizer)
    pyLDAvis.save_html(pic, f'{path}results/{filename}_{n_topics}topics.html')
    
    return f'success for {filename}'


#### here's an example for Reddit
## when analyze Douban, plz reset all parameters

filename = 'Reddit'
text_col_name = 'Text_all'

n_features = 1000        # set the maximun feature, the longer your text is, the larger feature number should be
n_topics = 13            # set the number of topics
n_top_words = 20         # set the output amount of keywords in each topic 
LDA_operation(path, filename, text_col_name, n_features, n_topics)



filename = 'Douban'
text_col_name = 'text'
n_features = 500         # Douban posts' text are shorter than Red
n_topics = 13
n_top_words = 20 
LDA_operation(path, filename, text_col_name, n_features, n_topics)


