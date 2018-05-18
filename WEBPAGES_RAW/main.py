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

#initialize variables:
stopwords = set()
wordlist = set()

documents = {}
tags = ['p', 'li', 'title', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6' 'a']

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
    if ('http://' not in link) or ('https://' not in link):
        link='http://'+link

    status=bool(urlparse(link).netloc)
    return (status,link)


''' Takes in a webpage and the database dictionary, and
    updates the database dictionary with new tokens
'''
def parsePageContent(page, pageText):
    for words in pageText:
        words = str(words)
        words = words.split()
        for w in words:
            w = re.sub(r'[^\w]', ' ', w).strip()#w.strip("\.!?;:(){}[]/,''\"")
            if len(w.split()) > 1:
                w = w.split()
                for x in w:
                    x = x.strip()
                    updateDBDoc(documents, x, w, page)
            else:
                updateDBDoc(documents, w, words, page)


def updateDBDoc(documents, token, words, page):
    doc = {'location': set(), 'tag': set(), 'count': 0}

    token = token.lower()

    if token not in stopwords:
        if token not in tags:

            if token in wordlist:
                documents[token]['count'] += 1
                documents[token]['location'].add(str(page))
                documents[token]['tag'].add(words[0].strip("< >"))
            else:
                doc['count'] = 1
                doc['location'].add(str(page))
                doc['tag'].add(words[0].strip("< >"))
                documents[token] = doc
                wordlist.add(token)


# Start extracting words from files using beautiful soup: https://www.quora.com/How-can-I-extract-only-text-data-from-HTML-pages
def parseAll(webpages):
    for page in webpages:
        currPage = open(str(page), 'r')
        soup = BeautifulSoup(currPage, "lxml")
        pageText = soup.findAll(tags, text=True) # Find all tags on the webpage that include displayed text
        parsePageContent(page, pageText)

def main():

    # Create Pymongo/MongoDB DB:

    dbclient = pymongo.MongoClient()
    db = dbclient['test'] # Grabs the 'test' DB from MongoDB

    # Open stopwords.txt file and put the words into stopwords set:
    swtext = open('stopwords.txt', 'r')

    for sw in swtext.readlines():
        sw = sw.strip("\n")
        stopwords.add(sw)

    # Opens the JSON file 'bookkeeping.json' and stores all of the data into a dictionary:
    with open("bookkeeping.json") as data:
        webpages = json.load(data)

    parseAll(webpages)

    posts = db.posts

    for d in documents:
        p = {"token":   d,
            "location": list(documents[d]["location"]),
            "tag":      list(documents[d]["tag"]),
            "count":    documents[d]["count"]}

        insertID = posts.insert_one(p)

        print d, documents[d]
if __name__ == "__main__":
    main()
