from pathlib import Path

from flask import Flask
from flask_mail import Mail
from flask_security import Security

from .database import Database


app = Flask(__name__)
ROOT_PATH = Path(__file__).parent.parent
app.root_path = str(ROOT_PATH)
app.config.from_pyfile(str(ROOT_PATH / 'settings.py'))
db = Database(app)
mail = Mail(app)
security = Security(app)

# Dev specific packages
try:
    from flask_debugtoolbar import DebugToolbarExtension
    toolbar = DebugToolbarExtension(app)
except ModuleNotFoundError:
    pass
