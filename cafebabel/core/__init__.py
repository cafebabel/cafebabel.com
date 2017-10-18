import os
from pathlib import Path

from flask import Flask
from flask_mail import Mail

from .database import Database


app = Flask(__name__)
ROOT_PATH = Path(__file__).parent.parent.parent
app.root_path = str(ROOT_PATH)
SETTINGS_PATH = (os.environ.get('SETTINGS_PATH') or
                 str(ROOT_PATH / 'settings.py'))
app.config.from_pyfile(SETTINGS_PATH)
db = Database(app)
mail = Mail(app)

from . import views  # noqa: F401, F801
from cafebabel.api import views  # noqa: F401, F801
from cafebabel.articles import views  # noqa: F401, F801

# Dev specific packages
try:
    from flask_debugtoolbar import DebugToolbarExtension
    toolbar = DebugToolbarExtension(app)
except ModuleNotFoundError:
    pass
