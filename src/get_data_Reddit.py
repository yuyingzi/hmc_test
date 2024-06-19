'''
---------
Author: Yuyingzi Yang
Date: Nov 17, 2023
This file is used to collecting raw data from Reddit's two target subreddit: CharacterAI & Replika
---------
What needs to fix: 
* Can I collect all the posts without limitation?
* ✅ How to colleted all the image links from the post content? This file only scrape one image link.
* ✅ Nov 24: all the images collected in 'pic_Reddit/' named by submission's id; len(postslink_all) = 2215
* ✅ csv files updated, post_id and post_link were saved as json file

'''
import praw
import csv
import requests
import os
from datetime import datetime
import pandas as pd

posts_id = []           # new list is used to avoid collect repeated posts
postslink_all = []

def download_image(url, folder, submission_id, index=None):
    response = requests.get(url)
    if response.status_code == 200:
        # Extract the file extension from the URL
        file_extension = url.split('.')[-1].split('?')[0]
        
        # Construct the file name based on submission.id and optional index
        file_name = f"{submission_id}"
        if index is not None:
            file_name += f"_{index}"
        file_name += f".{file_extension}"

        file_path = os.path.join(folder, file_name)
        with open(file_path, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded: {file_path}")
    else:
        print(f"Failed to download image from {url}")
        

def reddit_collect(subname, keywords, sorttype):
    # 设置Reddit API的访问信息
    reddit = praw.Reddit(client_id='tSZqlD1rlMXnkdYxw2_T7Q',
                        client_secret='DqZcsG-Y35DZGfh2SVS5qVg2eCji4A',
                        user_agent='EvlBread') # my API keys and account

    # 指定要访问的subreddit名称和搜索关键词
    subreddit_name = subname
    keywords = keywords
    subreddit = reddit.subreddit(subreddit_name) # 获取subreddit对象

    # 创建CSV文件写入表头
    csv_file_path = f'output_data/{subname}_{keywords}_{sorttype}.csv'
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['id', 'Post URL', 'Title', 'Timestamp', 'Content', 'Author','Score','Comments', 'Image'])
        
        # 使用Reddit API的search方法进行搜索, 并获取帖子列表
        for submission in subreddit.search(query= keywords, sort= sorttype, limit=None): #limit = None, the maximum output posts is 25
            if submission.id not in posts_id:   # 去重
                postid = submission.id
                post_url = f'https://www.reddit.com{submission.permalink}'
                postslink_all.append(post_url)
                title = submission.title
                timestamp = datetime.utcfromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M:%S')
                content = submission.selftext  # This includes the post's text content
                author = str(submission.author)
                num_comments = submission.num_comments # the number of comments: just in case I need collect comments itf
                score = submission.score # The number of upvotes for the submission.
                
                piclink = submission.url
                if piclink:                                                     # condition1: single image
                    if piclink.endswith(('.png', '.jpg', '.jpeg', '.gif')):
                        # Download the image to a folder
                        download_folder = 'pic_Reddit'
                        download_image(piclink, download_folder, postid)
                        # write the information 
                        csv_writer.writerow([postid, post_url, title, timestamp, content, author, score, num_comments, piclink])
                    else:                                                       # condition2: multiple image (gallery)
                        piclinks = []
                        # Check if the submission has gallery data
                        if hasattr(submission, 'gallery_data') and submission.gallery_data:
                            for index, item in enumerate(sorted(submission.gallery_data['items'], key=lambda x: x['id'])):
                                media_id = item['media_id']
                                meta = submission.media_metadata[media_id]
                                if meta['e'] == 'Image':
                                    source = meta['s']
                                    direct_image_url = source['u']
                                    piclinks.append(direct_image_url)
                                    # Download the image to a folder
                                    download_folder = 'pic_Reddit'
                                    download_image(direct_image_url, download_folder, postid, index+1)
                            csv_writer.writerow([postid, post_url, title, timestamp, content, author, score, num_comments, piclinks])
                        else:
                            csv_writer.writerow([postid, post_url, title, timestamp, content, author, score, num_comments, "NA"])
                else:                                                           # condition3: no image
                    csv_writer.writerow([postid, post_url, title, timestamp, content, author, score, num_comments, "NA"])
                    
                posts_id.append(postid)
            else:
                print('ops, repeat post')
                
    return len(postslink_all)


# Example usage:
subreddit_name = "your_subreddit"
keywords = "your_keywords"
sorttype = "your_sort_type"
reddit_collect(subreddit_name, keywords, sorttype)


# parameters part --- already executed in Nov 24 --------
'''
reddit_collect('CharacterAI','creepy', 'relevance')
reddit_collect('CharacterAI','fear', 'relevance')
reddit_collect('CharacterAI','freak out', 'relevance')
reddit_collect('CharacterAI','horrible', 'relevance')
reddit_collect('CharacterAI','scary', 'relevance')

reddit_collect('replika','creepy', 'relevance')
reddit_collect('replika','fear', 'relevance')
reddit_collect('replika','freak out', 'relevance')
reddit_collect('replika','horrible', 'relevance')
reddit_collect('replika','scary', 'relevance')
'''

### merge the parent-post data of Reddit
dfreddit1 = pd.read_csv('output_data/CharacterAI_creepy_relevance.csv')
dfreddit2 = pd.read_csv('output_data/CharacterAI_fear_relevance.csv')
dfreddit3 = pd.read_csv('output_data/CharacterAI_freak out_relevance.csv')
dfreddit4 = pd.read_csv('output_data/CharacterAI_horrible_relevance.csv')
dfreddit5 = pd.read_csv('output_data/CharacterAI_scary_relevance.csv')

dfreddit6 = pd.read_csv('output_data/replika_creepy_relevance.csv')
dfreddit7 = pd.read_csv('output_data/replika_fear_relevance.csv')
dfreddit8 = pd.read_csv('output_data/replika_freak out_relevance.csv')
dfreddit9 = pd.read_csv('output_data/replika_horrible_relevance.csv')
dfreddit10 = pd.read_csv('output_data/replika_scary_relevance.csv')

# Concatenate DataFrames with keys
result_df = pd.concat([dfreddit1, dfreddit2, dfreddit3, \
                        dfreddit4, dfreddit5, dfreddit6, \
                        dfreddit7, dfreddit8, dfreddit9, \
                        dfreddit10])


# Reset index to make the keys and original index regular columns
result_df = result_df.reset_index(level=0).reset_index(drop=True)

result_df['Text_all'] = result_df['Title'] + ' ' + result_df['Content']

# save to file
result_df.to_csv('data/raw/Reddit_allpost.csv',index=None)
