#!/usr/bin/python3

import time
from lxml import html
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from loginCredentials import loginCredentials
from bs4 import BeautifulSoup
import argparse
import urllib.parse

def logInIntoMyEpisodes(username, password):
    global browser
    browser.get("https://www.myepisodes.com/login/")
    browser.implicitly_wait(3)
    u = browser.find_element("name", "username")
    p = browser.find_element("name", "password")
    u.send_keys(username)
    p.send_keys(password)
    p.submit()

def readTimeWasted(delimiter='\t'):
    global browser
    global allShows
    browser.get("https://www.myepisodes.com/timewasted/")
    browser.implicitly_wait(3)
    soup = BeautifulSoup(browser.page_source, features='html.parser')
    table = soup.find('table', attrs={'class':'mylist'}).find('tbody')
    rows = table.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        if len(cols) > 0:
            allShows.append("{}{}{}{}{}{}{}".format(
                cols[1].text, # Name
                delimiter,
                cols[2].text, # Status
                delimiter,
                cols[6].text, # time wasted
                delimiter,
                'https://www.myepisodes.com' + cols[1].find_all('a')[0]['href'].replace(' ', '%20') # href
                )
            )

def readIndividualShow(show):
    return True

if __name__ == "__main__":
    # setup the argument parser
    parser = argparse.ArgumentParser(description='Script to extract data from myepisodes.com')
    parser.add_argument('-e', '--extract',  dest='extract', default='time_wasted',  choices=['all', 'time_wasted'])
    parser.add_argument('-f', '--format',   dest='format',  default='terminal',     choices=['terminal', 'csv', 'tsv'])

    args = parser.parse_args()

    # define the global data var
    global allShows
    global episodes
    allShows = []
    episodes = []

    # setup the browser
    global browser
    service = Service("/usr/bin/chromedriver")
    options = Options()
    options.add_argument('--headless=new')
    browser = webdriver.Chrome(service=service, options=options) # open a webdriver
    browser.set_window_size(1920, 1080) # set window size to 1080p

    if args.format in ['csv', 'tsv']:
        file=open('myepisodes_{}_export.{}'.format(args.extract, args.format), 'w')
        delimiter = ','
        if args.format == 'tsv':
            delimiter = '\t'
    else:
        file=False
        delimiter = '\t'
    # log in
    logInIntoMyEpisodes(username = loginCredentials['username'], password = loginCredentials['password'])
    if args.extract in ['all', 'time_wasted']:
        readTimeWasted(delimiter)

    if args.extract == 'time_wasted' and len(allShows) > 0: # output for time_wasted
        if args.format == 'terminal':
            for line in allShows:
                print(line)
        else:
            for line in allShows:
                file.write("{}\n".format(line))

    if args.extract == "all":
        for show in allShows:
            readIndividualShow(show) # read each show and append its result to episodes global var

    if args.format == 'csv':
        file.close()
    browser.quit()

