from flask import Flask

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure secret key in a production environment

from app import routes
