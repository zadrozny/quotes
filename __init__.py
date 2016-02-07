import os, random, sqlite3
from flask import Flask, jsonify, render_template, request, url_for
from random import choice
from paths import sk

app = Flask(__name__)

# Below is needed to mount app at something other than root; 
# however, for local development this gets in the way.
# Figure out how to make this work on either without constanty changing!
class WebFactionMiddleware(object):
    def __init__(self, app):
        self.app = app
    def __call__(self, environ, start_response):
        environ['SCRIPT_NAME'] = '/quotes' # '/' for local
        return self.app(environ, start_response)

#app.wsgi_app = WebFactionMiddleware(app.wsgi_app)



DATABASE = 'quotations.db'
app.config.from_object(__name__)
app.secret_key = sk



def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


@app.route('/')
def home():
    '''Generate a default random quote, plus the theme and author index'''
    d = connect_db()
    # Select a random quote from the database to present as default on opening
    rows = list(d.execute('''SELECT COUNT(*) FROM quotes'''))[0][0]
    n = choice(range(1, rows+1)) 
    randomquote = d.execute('''SELECT quote, author 
                               FROM quotes 
                               WHERE id=?''', (n,)).fetchone() 
    randomquote = dict(zip(('quote', 'author'), randomquote))
    # Construct index of themes, removing redundancies ('DISTINCT'):
    cur = d.execute('''SELECT DISTINCT tags FROM topics ORDER BY tags ASC''') 
    tags = [dict(tag=row[0]) for row in cur.fetchall()]
    # Construct index of authors, removing redundancies:
    cur = d.execute('''SELECT DISTINCT author_full, author_url 
                       FROM authors ORDER BY author_full ASC''') 
    authors = [dict(author=row[0], url=row[1]) for row in cur.fetchall()]
    d.close()
    return render_template('index.html', randomquote=randomquote, tags=tags, authors=authors) 


@app.route('/_gen_quote')
def generate_quote():
    '''Generate a random quote for ajax refresh (ie, next button)'''
    d = connect_db()
    cur = d.execute('SELECT quote, author, tags FROM quotes')
    #Rewrite below as a named tuple, more space efficient, in collections module
    quotes = [dict(quote=row[0], author=row[1]) for row in cur.fetchall()]
    randomquote = [choice(quotes)]
    d.close()
    return jsonify(randomquote=randomquote)


@app.route('/_gen_topic/')
@app.route('/_gen_topic/<name>')
def generate_topic(name):
    '''Show the quotes for a given topic'''
    d = connect_db()
    cur = d.execute("""SELECT quotes.quote, quotes.author 
                       FROM quotes 
                       INNER JOIN topics 
                       ON quotes.Id=topics.Id 
                       WHERE topics.tags=(?)""", (name,))
    quotes = [dict(quote=row[0], author=row[1]) for row in cur.fetchall()]
    d.close()
    return jsonify(quotes=quotes)


@app.route('/_gen_author/')
@app.route('/_gen_author/<name>')
def generate_author(name):
    '''Show quotes from a given author'''
    d = connect_db()
    cur = d.execute("""SELECT quotes.quote, quotes.author 
                       FROM quotes 
                       INNER JOIN authors 
                       ON quotes.Id=authors.Id 
                       WHERE authors.author_url=(?)""", (name,)) 
    # Data structure of below should prob be changed
    quotes = [dict(quote=row[0], author=row[1]) for row in cur.fetchall()] 
    d.close()
    return jsonify(quotes=quotes)


# @app.route('/_gen_author_list/')
# def generate_author_list():
#     '''Generate the index of authors'''
#     g = connect_db()

#     cur = d.execute('''SELECT DISTINCT author_full, author_url 
#                        FROM authors 
#                        ORDER BY author_full ASC''') 
#     authors = [dict(author=row[0], url=row[1]) for row in cur.fetchall()]
#     d.close()
#     return jsonify(authors=authors)


if __name__ == '__main__':
    app.run(debug=False)
