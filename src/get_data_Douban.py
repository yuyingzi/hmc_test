'''
---------
Author: Yuyingzi Yang
Date: Nov 17, 2023
This file is used to collecting raw data from Douban's three target groups
---------
Main approach:
* Firstly using cookie request group page, and collected all the post links in target group
* Then, iternarate all the links to scrape all the data.

'''

import time
import requests
import json
import csv
from bs4 import BeautifulSoup


######################################################
##### part 1 get the postlink ########################
######################################################

pagelinks = []
postlinks = []
filename = 'Douban_Post_name(group:人机之恋).csv'  
number_of_page = 92     # manual check and fill in
    
def Get_the_link(number_of_page, filename): #首先需要人工摸索出需要访问的小组链接url及其规律，生成小组每一页的链接
    with open(filename, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Post URL', 'Title', 'Author']) 
    
    for i in range(0,number_of_page):
        page_number = i*25
        base_link = f'https://www.douban.com/group/rjzl/discussion?start={page_number}&type=new' #其他都基本类似，group/之后为小组的代号
        pagelinks.append(base_link)
        

def scrape_douban_posts(url, cookies, unique_urls_set,filename):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
    }
    res = requests.get(url, cookies=cookies, headers=headers)
    
    if res.status_code == 200:
        response = res.text
        print('sucess')
        soup = BeautifulSoup(response, 'html.parser') 
        posts = soup.find_all('tr', class_='')
        
        with open(filename, 'a', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            
            for post in posts:
                title_element = post.find('td', class_='title')
                if title_element:
                    title_a = title_element.a
                    if title_a:
                        title = title_a.get_text(strip=True)
                        link = title_a['href']
                        
                        # Check if the post URL is already in the set
                        if link not in unique_urls_set:
                            unique_urls_set.add(link)  # Add the URL to the set
                            postlinks.append(link)
                            
                            author_element = post.find('td', nowrap='nowrap')
                            if author_element:
                                author_a = author_element.a
                                author = author_a.get_text(strip=True) if author_a else "N/A"
                            else:
                                author = "N/A"
                            
                            csv_writer.writerow([link, title, author])
                    else:
                        print("Title element not found for a post.")
        
        json_filename = f'{filename}_postlink.json'
        with open(json_filename, 'w') as json_file:
            json.dump(postlinks, json_file)
            
    else:
        print(f"Failed to retrieve data from {url}. Status code: {res.status_code}")


# Set to store unique post URLs
unique_urls = set()
# List of URLs to scrape
urls_to_scrape = pagelinks

# Load cookies from the JSON file
with open("cookies.json", 'r') as json_file:
    loaded_cookies = json.load(json_file)


Get_the_link(number_of_page, filename)
# Execute the scraping function for each URL
count = 0
for url in urls_to_scrape:
    scrape_douban_posts(url, loaded_cookies, unique_urls, filename)
    count += 1
    if count % 60 == 0:  # 每运行60次
        print('Have a rest')
        time.sleep(60)  # 休息60秒（一分钟）
    else:
        continue
    
    
######################################################
##### part 2 get the content. ########################
######################################################

def get_douban_post_info(post_link):
    # Set headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
    }

    # Make request to the post link
    res = requests.get(post_link, cookies=loaded_cookies, headers=headers)
    
    if res.status_code == 200: 
        response = res.text
        soup = BeautifulSoup(response, 'html.parser') 
        article = soup.find('div', class_="topic-doc")

        # Extracting author and author link
        author_element = article.find('span', class_='from').a
        author = author_element.get_text(strip=True)
        author_link = author_element['href']

        # Extracting post time and ip
        post_time = article.find('span', class_='create-time')
        time = post_time.get_text(strip=True)[:10] 
        post_ip = article.find('span', class_='ip-location')
        ip = post_ip.get_text(strip=True)
        print(f'{author}, {time}, {ip}')

        # Extracting post content
        post_content = soup.find('div', class_= "rich-content topic-richtext")
        text = post_content.get_text(strip=True)

        # Find all image containers
        image_tags = post_content.find_all('img')
        # Extract image links
        image_links = [img['src'] for img in image_tags]

        # Extracting Likes
        like = soup.find('div', class_= "action-react")
        num_like = like.find('span', class_='react-num').get_text(strip=True)
        
        csv_writer_content.writerow([post_link, time, text, num_like, author, author_link, ip, image_links])
    else:
        print(f"Failed to retrieve data for {post_link}. Status code: {res.status_code}")



def get_douban_comment_info(post_link):
    # Set headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
    }

    # Make request to the post link
    res = requests.get(post_link, cookies=loaded_cookies, headers=headers)
    if res.status_code == 200: 
        print(post_link)
        response = res.text
        soup = BeautifulSoup(response, 'html.parser') 
        parentpost = soup.find('h1').get_text(strip=True)
        comments = soup.findAll('li', class_="clearfix comment-item reply-item")
        for comment in comments:
            text = comment.find('p', class_="reply-content").get_text(strip=True) # scrape the comment text
            print(text)
            author_element = comment.find('div', class_="bg-img-green").a         
            author = author_element.get_text(strip=True)                          # scrape the author name
            timestamp = comment.find('span', class_="pubtime").get_text(strip=True)[:10] # scrape the public time
            
            # Find all image containers
            image_tag = comment.find('div', class_='cmt-img-wrapper')
            # Check if image_tag is not None before trying to extract image link
            if image_tag:
                # Extract the image link
                image_link = image_tag.find('img')['src']
            else:
                image_link = ''
            
            try:
                replyinfo = comment.find('span', class_="all ref-content").get_text(strip=True) # whether this's a reply
                csv_writer_comment.writerow([author, text, timestamp, replyinfo, image_link, parentpost, post_link])
            except:
                replyinfo = None
                csv_writer_comment.writerow([author, text, timestamp, replyinfo, image_link, parentpost, post_link])
            
    else:
        print(f"Failed to retrieve data for {post_link}. Status code: {res.status_code}")
        


# parameters part --- already executed in Nov 24 --------

filename = '今天和AI互动了吗' # enter the group name
cookies_path = '/Users/yinterested/github-classroom/Fall23-DSCI-510/final-project-yuyingzi/src/utils/cookies.json' # my cookies json file
count = 0 
linkfile = f'Douban_Post_name(group:{filename}).csv_postlink.json' 

with open(linkfile, 'r') as json_file:          # Load links from the JSON file
        postlinks = json.load(json_file)

with open(cookies_path, 'r') as json_file:      # Load cookies from the JSON file
        loaded_cookies = json.load(json_file)



### scrape post content
contentfile = f'Douban_content(group:{filename}).csv'
     
with open(contentfile, 'w', newline='', encoding='utf-8') as csv_file:
    csv_writer_content = csv.writer(csv_file)
    csv_writer_content.writerow(['Post URL', 'Timestamp', 'Content', 'Like' ,'Author','Author_link', 'location', 'Imagelinks'])
    for link in postlinks[:]:
        get_douban_post_info(link)
        count += 1
        if count % 59 == 0:  # short rest after each 59
            print('Have a rest')
            time.sleep(60)  # 休息60秒（一分钟）
        else:
            continue
        
        if count % 300 == 0:  # long rest after 300 
            print('Have a long rest')
            time.sleep(180)  # 休息3分钟
        else:
            continue

'''
### scrape post comment
commentfile = f'Douban_comment(group:{filename})0.csv'
with open(commentfile, 'w', newline='', encoding='utf-8') as csv_file:
    csv_writer_comment = csv.writer(csv_file)
    csv_writer_comment.writerow(['Author', 'Comment', 'Time', 'Reply to' ,'Imagelinks', 'parent post', 'parent link'])
    for link in postlinks[:]: 
        get_douban_comment_info(link)
        count += 1
        if count % 59 == 0:  # short rest after each 59
            print('Have a rest')
            time.sleep(60)  # 休息60秒（一分钟）
        else:
            continue
        
        if count % 300 == 0:  # long rest after 300 
            print('Have a long rest')
            time.sleep(180)  # 休息3分钟
        else:
            continue
'''
