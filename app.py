from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import requests, json, os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key'
NEWS_API_KEY = 'your_newsapi_key'
BOOKMARKS_FILE = 'bookmarks.json'

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['email'] = request.form['email']
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/news', methods=['POST'])
@login_required
def news():
    language = request.form.get('language')
    country = request.form.get('country')
    category = request.form.get('category')
    keyword = request.form.get('keyword')
    if keyword:
        url = f'https://newsapi.org/v2/everything?q={keyword}&language={language}&apiKey={NEWS_API_KEY}'
    else:
        url = f'https://newsapi.org/v2/top-headlines?country={country}&category={category}&language={language}&apiKey={NEWS_API_KEY}'
    response = requests.get(url)
    articles = response.json().get('articles', [])
    return render_template('news.html', articles=articles)

@app.route('/bookmark', methods=['POST'])
@login_required
def bookmark():
    data = request.json
    if os.path.exists(BOOKMARKS_FILE):
        with open(BOOKMARKS_FILE, 'r') as f:
            bookmarks = json.load(f)
    else:
        bookmarks = {}
    user_email = session['email']
    if user_email not in bookmarks:
        bookmarks[user_email] = []
    bookmarks[user_email].append(data)
    with open(BOOKMARKS_FILE, 'w') as f:
        json.dump(bookmarks, f)
    return jsonify({'status': 'success'})

@app.route('/bookmarks')
@login_required
def bookmarks():
    if os.path.exists(BOOKMARKS_FILE):
        with open(BOOKMARKS_FILE, 'r') as f:
            bookmarks = json.load(f)
    else:
        bookmarks = {}
    user_bookmarks = bookmarks.get(session['email'], [])
    return render_template('bookmarks.html', articles=user_bookmarks)

if __name__ == '__main__':
    app.run(debug=True)