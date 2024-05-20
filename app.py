import sqlite3
from hashids import Hashids
from flask import Flask, render_template, request, flash, redirect, url_for

app = Flask(__name__)
app.config['SECRET_KEY'] = 'this should be a secret random string'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS urls(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            original_url TEXT NOT NULL,
            clicks INTEGER NOT NULL DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

create_tables()

hashids = Hashids(min_length=4, salt=app.config['SECRET_KEY'])

@app.route('/', methods=('GET', 'POST'))
def index():
    conn = get_db_connection()

    if request.method == 'POST':
        url = request.form['url']

        if not url:
            flash('The URL is required!')
            return redirect(url_for('index'))

        conn.execute('INSERT INTO urls (original_url) VALUES (?)', (url,))
        conn.commit()
        url_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
        conn.close()

        hashid = hashids.encode(url_id)
        short_url = request.host_url + hashid

        return render_template('index.html', short_url=short_url)

    return render_template('index.html')

@app.route('/<id>')
def url_redirect(id):
    conn = get_db_connection()

    original_id = hashids.decode(id)
    if original_id:
        original_id = original_id[0]
        url_data = conn.execute('SELECT original_url, clicks FROM urls WHERE id = (?)', (original_id,)).fetchone()
        if url_data:
            original_url = url_data['original_url']
            clicks = url_data['clicks']

            conn.execute('UPDATE urls SET clicks = ? WHERE id = ?', (clicks+1, original_id))
            conn.commit()
            conn.close()
            return redirect(original_url)
        else:
            conn.close()
            flash('Invalid URL')
            return redirect(url_for('index'))
    else:
        flash('Invalid URL')
        return redirect(url_for('index'))

@app.route('/stats')
def stats():
    conn = get_db_connection()
    db_urls = conn.execute('SELECT id, created, original_url, clicks FROM urls').fetchall()
    conn.close()

    urls = []
    for url in db_urls:
        url = dict(url)
        url['short_url'] = request.host_url + hashids.encode(url['id'])
        urls.append(url)

    return render_template('stats.html', urls=urls)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
