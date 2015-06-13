# -*- coding: utf-8 -*-

import sys
from selenium import webdriver


def search(username, password, keyword):
    driver = webdriver.Firefox()
    driver.get('https://www.facebook.com')
    driver.find_element_by_id('email').send_keys(username)
    driver.find_element_by_id('pass').send_keys(password)
    driver.find_element_by_id('login_form').submit()
    driver.implicitly_wait(30)
    # search box that is available when logged in
    search = driver.find_element_by_id('q')
    search.send_keys(keyword)
    search.submit()
    # Add code to scrape data of interest from Facebook search here
    #driver.close()
 
    
if __name__ == '__main__':
    try:
        username = sys.argv[1]
        password = sys.argv[2]
        keyword = sys.argv[3]
    except IndexError:
        print 'Usage: %s <username> <password> <keyword>' % sys.argv[0]
    else:
        search(username, password, keyword)
