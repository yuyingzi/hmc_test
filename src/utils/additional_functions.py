'''
This is an additional file that used to identify the missing links when using Douban_post_content_scrap.py
Also, feel free to import this file to use 'save_links_to_json' function
'''


import re
import json

def extract_links_from_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    # Use regular expression to find links
    links = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)

    return links

def save_links_to_json(links, output_file):
    with open(output_file, 'w') as json_file:
        json.dump(links, json_file, indent=2)
    
    return f"Extracted Links saved to {output_json_file}"



# 可更改参数部分-------
file_path = 'group_人机之恋output.txt'          
output_json_file = 'missed_links_group:人机之恋.json'

links = extract_links_from_file(file_path)
save_links_to_json(links, output_json_file)

print(f"Extracted Links saved to {output_json_file}")