from pathlib import Path

from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from .database import Database
from flask_mail import Mail


app = Flask(__name__)
ROOT_PATH = Path(__file__).parent.parent.parent
app.root_path = str(ROOT_PATH)
app.config.from_pyfile(str(ROOT_PATH / 'settings.py'))
db = Database(app)
mail = Mail(app)
toolbar = DebugToolbarExtension(app)
