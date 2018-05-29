import pymongo


dbclient = pymongo.MongoClient()
db = dbclient['test'] # Grabs the 'test' DB from MongoDB

posts = db.posts

query = raw_input("Enter a search query: ")

def multi_word_query(query, posts):
    pages = []
    totalCount = 0
    queryCount = 0
    qry = query.split()
    r1 = posts.find_one({'token': qry[0]})
    r2 = posts.find_one({'token': qry[1]})


    for l in r1['location']:
        print l
        if l['path'] in r2['location']:
            print "yes!"
            index = r2['location'].index(str(l))
            queryCount = int(str(l)['pathCount']) + int(r2['location'][index]['pathCount'])
            pages.append({'page': str(l)['path'],
                        'pageCount': queryCount,
                        'tf-idf': (float(str(l)['tf-idf']) + float(r2['location'][index]['tf-idf']))/2})

            totalCount += queryCount

    return [pages, totalCount]

if len(query.split()) == 1:
    results = posts.find_one({'token': query})
    print dict(results)

elif len(query.split()) == 2:
    results = multi_word_query(query, posts)
