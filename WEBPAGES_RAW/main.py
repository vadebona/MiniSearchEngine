import json
from lxml import html,etree
from bs4 import BeautifulSoup
import re, os
from time import time
from uuid import uuid4

from urlparse import urlparse, parse_qs
from uuid import uuid4
import requests, urllib2
import re

import pymongo

'''
    Checks to see which words in the given webpage (after calling findall with BeautifulSoup)
    actually gives you text displayed on the webpage
'''
def getText(textData):
    if textData.parent.name not in ['style', 'script', 'meta' 'a', '[document]', 'head']:
        return False
    if re.match("<!-- *-->", textData):
        return False
    return True

''' Figures out if a link is absolute or not,
    and makes absolute links out of non-absolute ones
'''
def is_absolute(link):
    if link[0:4]=='www.':
        link='http://'+link
    status=bool(urlparse(link).netloc)
    return (status,link)

#initialize variables:
stopwords = set()
wordlist = set()

# Open stopwords.txt file and put the words into stopwords set:
swtext = open('stopwords.txt', 'r')

for sw in swtext.readlines():
    sw = sw.strip("\n")
    stopwords.add(sw)

# Opens the JSON file 'bookkeeping.json' and stores all of the data into a dictionary:
with open("bookkeeping.json") as data:
    webpages = json.load(data)

# Start extracting words from files using beautiful soup: https://www.quora.com/How-can-I-extract-only-text-data-from-HTML-pages
for page in webpages:
    link = is_absolute(str(webpages[page]))[1]
    print link
    url = urllib2.urlopen(link, "lxml")
    #currPage = open(str(page), 'r')
    soup = BeautifulSoup(url)

    pageText = soup.findAll(text=True) # Find all tags on the webpage that include displayed text

    filteredText = filter(getText, pageText)

    for word in filteredText:
        word = word.split()
        for w in word:
            if re.match("([a-z])*([A-Z])*", w): #try to find a regular expression that matches all valid words
                w = str(w)
                print w
                if w not in stopwords:
                    wordlist.add(w)

for w in wordlist:
    print w
# # Create Pymongo/MongoDB DB:
# dbclient = pymongo.MongoClient()
# db = dbclient['INDEXED_WORDS'] # Grabs the INDEXED_WORDS DB from MongoDB
