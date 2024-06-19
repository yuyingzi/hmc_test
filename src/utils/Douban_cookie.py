'''
This file aims to use selenium login in Douban and save the cookies as json file
Next step is use cookies to request page and get further information: 'Douban_postlinkscrap.py'

Author: Yoko
Date: Nov21 2023
'''

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
 

 
def login(username, password):
    # 通过selenium模拟登录豆瓣
    brower.get(url)
    time.sleep(3)
    brower.switch_to.frame(brower.find_element(By.TAG_NAME,"iframe"))  # 切换到iframe中去
    login_ele = brower.find_element(By.XPATH,"//li[@class='account-tab-account']")
    login_ele.click()
 
    # 找到 用户名和密码的节点
    username_ele = brower.find_element(By.XPATH,"//input[@id='username']")
    password_ele = brower.find_element(By.XPATH,"//input[@id='password']")
 
    # 填写用户名和密码
    username_ele.send_keys(username)
    password_ele.send_keys(password)
    submit_btn = brower.find_element(By.XPATH,"//a[@class='btn btn-account btn-active']")
    submit_btn.click()
    time.sleep(30) #滑块验证
    
    # 获取cookies
    cookies = brower.get_cookies()  # list
    cookie_dict = {}
    for item in cookies:
        cookie_dict[item['name']] = item['value']
        
    # 保存cookie在该路径，方便下次调用
    json_filename = "cookies.json"
    with open(json_filename, 'w') as json_file:
        json.dump(cookie_dict, json_file)
        
    # Close the browser
    brower.quit()
    print(f"Cookies saved to {json_filename}")


brower = webdriver.Chrome()     # 此文件已配置完毕，本行请勿动！

# 可修改参数部分：
url = ""  # 需要登陆的网页界面，理论上可以修改，但不同网页源代码不同，需要定制cookie获取方式
username = ''        # 自定义填写用户名与密码。默认勿动。如果账户被完全封锁，需要重新设置。
password = ''

login(username, password)
