#!/usr/bin/python3

import time
from lxml import html
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from loginCredentials import loginCredentials
from bs4 import BeautifulSoup
from urllib.parse import quote
import argparse

def logInIntoMyEpisodes(username, password):
    global browser
    browser.get("https://www.myepisodes.com/login/")
    browser.implicitly_wait(3)
    time.sleep(5)
    u = browser.find_element("name", "username")
    p = browser.find_element("name", "password")
    u.send_keys(username)
    p.send_keys(password)
    p.submit()

def readTimeWasted():
    global browser
    global allShows
    browser.get("https://www.myepisodes.com/timewasted/")
    browser.implicitly_wait(3)
    time.sleep(5)
    soup = BeautifulSoup(browser.page_source, features='html.parser')
    table = soup.find('table', attrs={'class':'mylist'}).find('tbody')
    rows = table.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        if len(cols) > 0:
            allShows.append([
                    cols[1].text, # Name
                    cols[2].text, # Status
                    cols[6].text, # time wasted
                    'https://www.myepisodes.com' + quote(cols[1].find_all('a')[0]['href']) # href
                ]
            )

def readIndividualShow(href):
    global browser
    global episodes
    browser.get("{}".format(href))
    browser.implicitly_wait(3)
    time.sleep(5)
    soup = BeautifulSoup(browser.page_source, features='html.parser')
    table = soup.find('table', attrs={'class':'mylist'})
    try:
        table = table.find('tbody')
        rows = table.find_all('tr')
        for row in rows:
            if row['class'] and row['class'][0] in ['even', 'odd']:
                cols = row.find_all('td')
                if len(cols) > 0:
                    episodes.append([
                            cols[0].text, # air date
                            cols[1].text, # show name
                            cols[2].text, # season/episode number
                            cols[3].text, # episode name
                            #cols[4], # status aquired
                            'checked' in cols[5].find_all('input')[0].attrs.keys()  # status watched
                        ]
                    )
        print('Read data for: {}'.format(cols[1].text))
    except:
        print('Cannot find table with class "mylist"; href= {}'.format(href))

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

    # configure the output formats
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

    # extract all shows from time_wasted
    if args.extract in ['all', 'time_wasted']:
        readTimeWasted()

    # output the data from time_wasted if requested
    if args.extract == 'time_wasted' and len(allShows) > 0:
        for line in allShows:
            outputString = ''
            for item in line:
                outputString = '{}{}{}'.format(outputString, item, delimiter)
            if args.format == 'terminal':
                print(outputString)
            else:
                file.write(outputString + '\n')

    # extract all individual shows data
    if args.extract == "all":
        for show in allShows:
            readIndividualShow(show[3]) # read each show and append its result to episodes global var

    # output the data for all individual shows if requested
    if args.extract == 'all' and len(episodes) > 0:
        for line in episodes:
            outputString = ''
            for item in line:
                outputString = '{}{}{}'.format(outputString, item, delimiter)
            if args.format == 'terminal':
                print(outputString)
            else:
                file.write(outputString + '\n')

    # close the output file if opened
    if file:
        file.close()
    browser.quit()

