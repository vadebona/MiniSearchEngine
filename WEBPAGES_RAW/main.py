from lxml import html,etree
from bs4 import BeautifulSoup
from time import time
from uuid import uuid4

from urlparse import urlparse, parse_qs
from uuid import uuid4

import re, os, json, requests, urllib2, pymongo, math, sys, pprint

wordlist = set()
totalWordCount = 0
documents = {}

''' Open stopwords.txt file and put the words into stopwords set:
'''
def loadStopWords():
    stopwords = set()
    swtext = open('stopwords.txt', 'r')

    for sw in swtext.readlines():
        sw = sw.strip("\n")
        stopwords.add(sw)

    return stopwords

stopwords = loadStopWords()

''' Opens the JSON file 'bookkeeping.json' and stores all of the data into a dictionary:
'''
def loadFiles():
    with open("bookkeeping.json") as data:
        webpages = json.load(data)

    return webpages

numFiles = len(loadFiles())

def getSoup(directory):
    content = open(str(directory), 'r')
    pattern=re.compile("\w+")
    soup = BeautifulSoup(content, "html.parser")
    return soup

def parsePageContent(pageText):
    pattern=re.compile("\w+")
    allWords = pattern.findall(pageText)
    uniqueWords = set(allWords)

    return (allWords, uniqueWords)

def calculateIDF(token):
    return math.log10(numFiles/len(documents[token]['location']))

def updateDocuments(page, parseTuple):
    global totalWordCount
    for i in parseTuple[1]:
        doc = {'location': {}, 'totalCount': 0}
        tokenCount = parseTuple[0].count(i)
        totalWordCount += tokenCount
        if i not in stopwords and i not in wordlist:
            if i in documents:
                documents[str(i)]['totalCount'] += tokenCount
                if page in documents[str(i)]['location']:
                    documents[str(i)]['location'][page] += 1
                else:
                    documents[str(i)]['location'][page] = 1
            else:
                doc['totalCount'] = tokenCount
                doc['location'][page] = 1
                wordlist.add(str(i))
                documents[str(i)] = doc

def parseAll(webpages):
    for page in webpages:
        pageText = getSoup(page).text.lower()
        pt = parsePageContent(pageText)
        updateDocuments(page, pt)

def loadDB(db, posts):
    for d in documents:
        p = {"token":   d,
            "location": [],
            "count":    documents[d]["totalCount"]}

        for l in documents[d]["location"]:
            p['location'].append({"path":    l,
                                "pathCount": documents[d]["location"][l],
                                "tf-idf":    (documents[d]["location"][l]) * calculateIDF(d)})

        insertID = posts.insert_one(p)

def main():
    # Create Pymongo/MongoDB DB:
    dbclient = pymongo.MongoClient()
    db = dbclient['test'] # Grabs the 'test' DB from MongoDB

    posts = db.posts

    print "loading JSON of webpages..."
    webpages = loadFiles()

    print "Parsing webpages..."
    parseAll(webpages)

    print "Loading tokens to DB..."
    loadDB(db, posts)


if __name__ == "__main__":
    main()
