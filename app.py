from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import URL, DataRequired
import uuid
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a secure secret key

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Sample user data (replace with a database in a real-world scenario)
users = {'user1': {'password': 'pass123', 'links': []}}

# Dictionary to store custom short IDs and their corresponding original links
custom_short_ids = {}

class User(UserMixin):
    pass


@login_manager.user_loader
def load_user(user_id):
    user = User()
    user.id = user_id
    return user


class ShortLinkForm(FlaskForm):
    link = StringField('Link', validators=[DataRequired(), URL()])
    custom_short_id = StringField('Custom Short ID (optional)')
    submit = SubmitField('Shorten')


@app.route('/')
@login_required
def home():
    return f'Hello {current_user.id}! <a href="/logout">Logout</a>'


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            user = User()
            user.id = username
            login_user(user)
            return redirect(url_for('shorten'))
        flash('Invalid login credentials', 'error')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/shorten', methods=['GET', 'POST'])
@login_required
def shorten():
    form = ShortLinkForm()
    if form.validate_on_submit():
        link = form.link.data
        custom_short_id = form.custom_short_id.data.strip()

        if custom_short_id and custom_short_id in custom_short_ids:
            flash(f'Custom short ID "{custom_short_id}" is already taken. Please choose another.', 'error')
            return render_template('shorten.html', form=form)

        if custom_short_id:
            short_link = custom_short_id
        else:
            short_link = str(uuid.uuid4())[:8]

        expiration_time = datetime.now() + timedelta(hours=48)

        users[current_user.id]['links'].append({
            'original_link': link,
            'short_link': short_link,
            'expiration_time': expiration_time
        })

        # Store the custom short ID and its corresponding original link
        custom_short_ids[short_link] = link

        flash(f'Short link created: {short_link}', 'success')
        return render_template('shorten_success.html', short_link=short_link)

    return render_template('shorten.html', form=form)


@app.route('/<short_id>')
def redirect_to_original(short_id):
    original_link = custom_short_ids.get(short_id)
    if original_link:
        return redirect(original_link)
    else:
        flash(f'Custom short ID "{short_id}" not found.', 'error')
        return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
