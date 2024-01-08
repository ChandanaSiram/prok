from flask import render_template, redirect, url_for, request, session
from app import app
import uuid
from datetime import datetime, timedelta

users = {}
short_links = {}

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    # Replace this with a proper authentication mechanism (e.g., database lookup)
    if username in users and users[username] == password:
        session['username'] = username
        return redirect(url_for('dashboard'))
    else:
        return render_template('login.html', error='Invalid credentials')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        user_links = [link for link in short_links.values() if link['username'] == session['username']]
        return render_template('dashboard.html', short_links=user_links)
    else:
        return redirect(url_for('index'))

@app.route('/create_short_link', methods=['POST'])
def create_short_link():
    if 'username' in session:
        original_url = request.form.get('original_url')
        short_code = str(uuid.uuid4())[:8]
        expiration_time = datetime.now() + timedelta(hours=48)

        short_link_data = {
            'short_code': short_code,
            'original_url': original_url,
            'username': session['username'],
            'expiration_time': expiration_time,
            'creation_time': datetime.now(),
            'clicks': 0
        }

        short_links[short_code] = short_link_data

        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('index'))

@app.route('/analytics/<short_code>')
def analytics_page(short_code):
    if 'username' in session and short_code in short_links and short_links[short_code]['username'] == session['username']:
        link_data = short_links[short_code]
        return render_template('analytics.html', link_data=link_data)
    else:
        return redirect(url_for('index'))
