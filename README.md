# MiniSearchEngine
CS 121 Project 3 + 4 -- Creating a minature search engine

### To get the front-end working, you'll need to install a few dependencies in the command line:

- Flask:
`pip install flask`

- Flask WTForms:
`pip install WTForms`

- Pymongo (MongoDB library for Python):
`pip install pymongo` or
`pip install pymongo='version'` for a specific version of Pymongo


### Running the application:
- (1) Start MongoDB from the command line. If you're on a mac, make sure you brew installed MongoDB, and then run
`brew services start mongodb`

- (2) Open the mongodb command line interface:
`mongo`

- (3) Type in `use [insert DB name here]`

- (4) In a command line window, navigate to the repository and type in
`python app.py`
to run the entire web application. This starts up Flask

- (5) Happy searching!
