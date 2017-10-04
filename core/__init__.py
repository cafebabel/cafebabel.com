import os

from flask import Flask
from peewee import SqliteDatabase


ROOT_PATH = f'{os.path.abspath(os.path.dirname(__file__))}/..'

app = Flask(__name__)
app.root_path = ROOT_PATH
app.config.from_pyfile(f'{ROOT_PATH}/settings.py')

db = SqliteDatabase(f'{ROOT_PATH}/cafebabel.db')
db.connect()
