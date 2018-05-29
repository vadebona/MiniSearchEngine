import lxml 
from lxml import html,etree
from bs4 import BeautifulSoup
import bs4 as bs
from time import time
from uuid import uuid4
import codecs
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

_webpages_=loadFiles()
numFiles = len(_webpages_)

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

def xml_format(filename):
    file=codecs.open(filename,'r',"utf-8")
    content=file.read()
    file.close()
    return bs.BeautifulSoup(content,"lxml")

def builf_flag_table(page,xml_page,token):
    #flag_list=[inURL,inTitle,inHeading]
    flag_list=[False,False,False]
    if not xml_page.title.string==None:
        flag_list[0]=token in xml_page.title.string
    if token in str(_webpages_[page]):
        flag_list[1]=True
    for h in xml_page.find_all(re.compile('^h[1-6]$')):
        if not h.string == None:
            if token in h.string:
                flag_list[2]=True
                continue
    return flag_list
            
                
def updateDocuments(page, parseTuple):
    global totalWordCount
    xml_page=xml_format(page)
    for i in parseTuple[1]:
        doc = {'location': {}, 'totalCount': 0}
        tokenCount = parseTuple[0].count(i)
        totalWordCount += tokenCount
        if (str(i) not in stopwords):
            if str(i) in documents:
                documents[str(i)]['totalCount'] += tokenCount
                if page in documents[str(i)]['location']:
                    documents[str(i)]['location'][page] += tokenCount
                else:
                    documents[str(i)]['location'][page] = tokenCount
            if str(i) not in documents:
                doc['totalCount'] = tokenCount
                doc['location'][page] = tokenCount
                wordlist.add(str(i))
                documents[str(i)] = doc

def parseAll(webpages):
    for page in webpages:
        if str(page) not in ["39/373", "55/433", "35/269", "0/438"]:
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
