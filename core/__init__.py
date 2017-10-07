from pathlib import Path

from flask import Flask
from flask_peewee.db import Database


app = Flask(__name__)
app.root_path = Path(__file__).parent.parent
app.config.from_pyfile(app.root_path / 'settings.py')

db = Database(app)
