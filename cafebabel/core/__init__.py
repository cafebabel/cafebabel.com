from pathlib import Path

from flask import Flask
from flask_mail import Mail

from .database import Database


app = Flask(__name__)
ROOT_PATH = Path(__file__).parent.parent.parent
app.root_path = str(ROOT_PATH)
app.config.from_pyfile(str(ROOT_PATH / 'settings.py'))
if Path.exists(ROOT_PATH / 'settings.local.py'):
    app.config.from_pyfile(str(ROOT_PATH / 'settings.local.py'))
db = Database(app)
mail = Mail(app)

from cafebabel.core import views  # noqa: F401, F801
from cafebabel.api import views  # noqa: F401
from cafebabel.articles import views  # noqa: F401, F801

# Dev specific packages
try:
    from flask_debugtoolbar import DebugToolbarExtension
    toolbar = DebugToolbarExtension(app)
except ModuleNotFoundError:
    pass
