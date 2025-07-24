from flask import Flask, request, jsonify, render_template, redirect
import sqlite3, random, string
import validators

app = Flask(__name__)
DB_FILE = 'urls.db'

def generate_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_unique_code():
    while True:
        code = generate_code()
        with sqlite3.connect(DB_FILE) as conn:
            cur = conn.execute("SELECT 1 FROM urls WHERE code = ?", (code,))
            if not cur.fetchone():
                return code

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/shorten', methods=['POST'])
def shorten_url():
    long_url = request.form['url'].strip()

    if not long_url:
        return jsonify({'error': 'URL cannot be empty'}), 400

    if not validators.url(long_url):
        return jsonify({'error': 'Invalid URL format'}), 400

    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.execute("SELECT code FROM urls WHERE long_url = ?", (long_url,))
        row = cur.fetchone()
        if row:
            code = row[0]
        else:
            code = generate_unique_code()
            conn.execute("INSERT INTO urls (code, long_url) VALUES (?, ?)", (code, long_url))

    short_url = request.host_url + code
    return jsonify({'short_url': short_url})

@app.route('/<code>')
def redirect_to_url(code):
    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.execute("SELECT long_url FROM urls WHERE code = ?", (code,))
        row = cur.fetchone()
        if row:
            return redirect(row[0])
        return "Invalid URL", 404

if __name__ == '__main__':
    # Create table if not exists
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS urls (code TEXT PRIMARY KEY, long_url TEXT)')
    app.run(debug=True)
