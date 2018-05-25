from lxml import html,etree
from bs4 import BeautifulSoup
from time import time
from uuid import uuid4

from urlparse import urlparse, parse_qs
from uuid import uuid4

import re, os, json, requests, urllib2, pymongo, math, sys, pprint

wordlist = set()
documents = {}
tags = set()
stopwords = set()
numFiles = len(loadFiles())

def split_words_in_file(content):
    pattern=re.compile("\w+")
    soup = BeautifulSoup(content, "html.parser")
    return soup

def loadFiles():
    with open("bookkeeping.json") as data:
        webpages = json.load(data)

    return webpages

def loadStopWords():
    stopwords = set()
    swtext = open('stopwords.txt', 'r')

    for sw in swtext.readlines():
        sw = sw.strip("\n")
        stopwords.add(sw)
    return stopwords

def calculateLTF(token, directory, count):
    pass

def calculateTFIDF(token, directory):
    pass

def parsePageContent(page, pageText):
    for p in pageText:
        if len(p.contents) > 0:
            for c in p.contents:
                print c
                print "\n\n"
        else:
            print "---------- No Contents: ----------"
            print p
            print "----------------------------------"
            print "\n\n"


def updateDBDoc(documents, token, words, page):
    doc = {'location': {}, 'tag': set(), 'count': 0}

    token = token.lower()

    if token not in stopwords:
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

def not_script_or_style(item):
    return item.name != "script" and item.name != "style"


def main():
    webpages = loadFiles()
    fp = "0/2"
    p = open(fp, 'r')

    soup = split_words_in_file(p)
    stopwords = loadStopWords()

    s = soup.text.lower()
    pattern=re.compile("\w+")
    w = pattern.findall(s)
    sw=set(w)

    totalCount = 0
    for i in sw:
        doc = {'location': {}, 'totalCount': 0}
        tokenCount = w.count(i)
        totalCount += tokenCount
        if i not in stopwords and i not in wordlist:
            if i in documents:
                documents[str(i)]['totalCount'] += tokenCount
                if p in documents[str(i)]['location']:
                    documents[str(i)]['location'][fp] += 1
                else:
                    documents[str(i)]['location'][fp] = 1
            else:
                doc['totalCount'] = tokenCount
                doc['location'][fp] = 1
                wordlist.add(str(i))
                documents[str(i)] = doc


    for item in documents:
        print item, documents[item]['totalCount']






    # for s in soup.findAll(not_script_or_style):
    #     tags.add(s.name)
    #
    # print tags
    #
    # for t in tags:
    #     s = soup.findAll(re.compile(str(t)))
    #     for w in s:
    #         if w.string != None:
    #             print t
    #             print w.string


    #         string = str(w.string)
    #         string = string.split()
    #         for word in string:
    #             if word in documents:
    #                 documents[word].add(str(t))
    #             else:
    #                 documents[word] = set(str(t))
    # print documents

    # (1) get all the .name s in the file and save them somewhere
    # (2) get all the strings of each .name that was found and keep record of the .name


    # for s in soup.findAll(string=re.compile("Undergraduate")):
    #     print s.name
    # wordList = soup.findAll(recursive=False)
    # for w in soup.stripped_strings:
    #     print w
    #     for s in soup.findAll(string=re.compile(str(w))):
    #         print s.name
    #     print "\n"
    # for c in wordList.stripped_strings:
    #     print c
    #     print "\n"

    # for word in wordList:
    #     for w in word.descendants:
    #         print word
    #         print "----------------------------------"
    #         print "\n\n"

    # parsePageContent(p, wordList)


    # for w in wordList:
    #     print type(w.contents)
    #     break
    #     for t in w.contents:
        #     t = str(t.encode("utf-8"))
        #     t = t.split("\n")
        #     for q in t:
        #         print q
        #         print "\n"
        #     print "\n"
        # print "\n"

if __name__ == "__main__":
    main()
