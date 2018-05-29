from flask import Flask, render_template, flash, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from main import *
import pymongo

app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = 'oooh-secret'

# @app.route('/')
# def hello_world():
#     return render_template('index.html')

# SOURCE: https://pythonspot.com/flask-web-forms/
class ReusableForm(Form):
    query = TextField('Query:', validators=[validators.required()])


class queryObj():
    def __init__(self, query):
        self.token = str(query['token'])
        self.count = int(query['count'])
        self.location = list(query['location'])


def getTitle(webpage):
    page = open(str(webpage), 'r')
    soup = BeautifulSoup(page, "lxml")
    title = soup.find('title')
    return title

def multi_word_query(query, posts):
    qry = query.split()
    r1 = posts.find_one({'token': qry[0]})
    r2 = posts.find_one({'token': qry[1]})

    r1loc = []
    r2loc = []
    # pages = multi_word_query(query, posts)
    for item in r1['location']:
        r1loc.append(item)
    for item in r2['location']:
        r1loc.append(item)

    pages = [r1loc, (int(r1['count']) + int(r2['count']))]

    return pages

@app.route("/", methods=['GET', 'POST'])
def searchQuery():
    form = ReusableForm(request.form)

    print form.errors
    if request.method == 'POST':
        query = request.form['query'].lower()

        if form.validate():
            json = loadFiles()
            dbclient = pymongo.MongoClient()
            db = dbclient['test'] # Grabs the 'test' DB from MongoDB

            posts = db.posts

            if len(query.split()) == 1:
                results = posts.find_one({'token': query})
                pages = [results['location'], results['count']]

            elif len(query.split()) == 2:
                pages = multi_word_query(query, posts)


            pages[0] = sorted(pages[0], key = lambda x: (-x['tf-idf'], -x['pathCount']))
            # else:
            #     qo = queryObj(results)
            #     qo.location = sorted(qo.location, key = lambda x: (-x['tf-idf'], -x['pathCount']))

            return render_template('results.html',
                                    query=query,
                                    json=json,
                                    form=form,
                                    pages=pages)
        else:
            flash('Error: Please enter a search query.')

    return render_template('index.html', form=form)

if __name__ == '__main__':
    app.run()
