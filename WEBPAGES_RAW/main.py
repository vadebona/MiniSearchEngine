from lxml import html,etree
from bs4 import BeautifulSoup
from time import time
from uuid import uuid4

from urlparse import urlparse, parse_qs
from uuid import uuid4

import re, os, json, requests, urllib2, pymongo, math, sys, pprint


#initialize variables:
stopwords = set()
wordlist = set()
N = 37497 # Number of webpages

documents = {}
tags = ['p', 'li', 'title', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6' 'a']

''' Open stopwords.txt file and put the words into stopwords set:
'''
def loadStopWords():
    swtext = open('stopwords.txt', 'r')

    for sw in swtext.readlines():
        sw = sw.strip("\n")
        stopwords.add(sw)

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

''' Finds a tag name in a gibberish tag
'''
def getTagSubstr(tag):
    for t in tags:
        index = tag.find(t)
        if index != -1:
            if (index != 0) and (tag[index-1] == "<"):
                resultTag = t
                return resultTag
    return ""

''' Calculates the TF-IDF score of a given token
'''
def calculateTFIDF(token, documents):
    tfs = []
    idf = math.log10(N/len(documents[token]['location']))
    for l in documents[token]['location']:
        tf = 1 + math.log(documents[token]['location'][l])
        tfs.append(tf)


''' Takes in a webpage and the database dictionary, and
    updates the database dictionary with new tokens
'''
def parsePageContent(page, pageText):
    for words in pageText:
        words = str(words)
        words = words.split()
        for w in words:
            if w == "":
                continue
            w = re.sub(r'[^\w]', ' ', w).strip()#w.strip("\.!?;:(){}[]/,''\"")
            if len(w.split()) > 1:
                w = w.split()
                for x in w:
                    if x == "":
                        continue
                    x = x.strip()
                    updateDBDoc(documents, x, w, page)
            else:
                updateDBDoc(documents, w, words, page)


def updateDBDoc(documents, token, words, page):
    doc = {'location': {}, 'tag': set(), 'count': 0}

    token = token.lower()

    if token not in stopwords:
        if token not in tags:
            if re.match("^[A-Za-z']+$", token):
                if token in wordlist:
                    documents[token]['count'] += 1
                    if getTagSubstr(words[0]) != "":
                        documents[token]['tag'].add(getTagSubstr(words[0]))
                    if str(page) in documents[token]['location']:
                        documents[token]['location'][str(page)] += 1
                    else:
                        documents[token]['location'][str(page)] = 1


                else:
                    doc['count'] = 1
                    doc['location'][str(page)] = 1
                    if getTagSubstr(words[0]) != "":
                        doc['tag'].add(getTagSubstr(words[0]))
                    documents[token] = doc
                    wordlist.add(token)


# Start extracting words from files using beautiful soup: https://www.quora.com/How-can-I-extract-only-text-data-from-HTML-pages
def parseAll(webpages):
    for page in webpages:
        currPage = open(str(page), 'r')
        soup = BeautifulSoup(currPage, "lxml")
        pageText = soup.findAll(tags, text=True) # Find all tags on the webpage that include displayed text
        parsePageContent(page, pageText)

''' Opens the JSON file 'bookkeeping.json' and stores all of the data into a dictionary:
'''
def loadFiles():
    with open("bookkeeping.json") as data:
        webpages = json.load(data)

    return webpages

''' Creates a document for each item in the documents
    dictionary, and then loads it into the database.
'''
def loadDB(db, posts):


    for d in documents:
        p = {"token":   d,
            "location": [],
            "tag":      list(documents[d]["tag"]),
            "count":    documents[d]["count"]}

        for l in documents[d]["location"]:
            p["location"].append({"path": l,
                                "pathCount": documents[d]["location"][l]})

        insertID = posts.insert_one(p)


def queryDB(db, posts, token):
    results = posts.find({'token': token})
    for r in results:
        pprint.pprint(r)

def main():
    # Create Pymongo/MongoDB DB:
    dbclient = pymongo.MongoClient()
    db = dbclient['test'] # Grabs the 'test' DB from MongoDB

    posts = db.posts

    # Grab user query from input (restrict to 1 word input for now):
    token = sys.argv[1]
    queryDB(db, posts, token)

    # loadStopWords()
    # webpages = loadFiles()
    # parseAll(webpages)
    #loadDB(db)

        # print d, documents[d]
if __name__ == "__main__":
    main()
