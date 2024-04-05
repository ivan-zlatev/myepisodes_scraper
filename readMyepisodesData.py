#!/usr/bin/python3

import time
from lxml import html
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from loginCredentials import loginCredentials
from bs4 import BeautifulSoup

def logInIntoMyEpisodes(username, password):
    global browser
    browser.get("https://www.myepisodes.com/login/")
    browser.implicitly_wait(3)
    u = browser.find_element("name", "username")
    p = browser.find_element("name", "password")
    u.send_keys(username)
    p.send_keys(password)
    p.submit()

def readTimeWasted():
    global browser
    browser.get("https://www.myepisodes.com/timewasted/")
    browser.implicitly_wait(3)
    soup = BeautifulSoup(browser.page_source, features='html.parser')
    table = soup.find('table', attrs={'class':'mylist'}).find('tbody')
    rows = table.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        if len(cols) > 0:
            print("Name: {}, Status: {}, href={}".format(cols[1].text, cols[2].text, cols[1].find_all('a')[0]['href']))

if __name__ == "__main__":
    global browser
    service = Service("/usr/bin/chromedriver")
    options = Options()
    options.add_argument('--headless=new')
    browser = webdriver.Chrome(service=service, options=options) # open a webdriver
    browser.set_window_size(1920, 1080) # set window size to 1080p

    logInIntoMyEpisodes(username = loginCredentials['username'], password = loginCredentials['password'])
    readTimeWasted()

    browser.quit()
