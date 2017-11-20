from pathlib import Path

from flask import Flask
from flask_mail import Mail
from flask_mongoengine import MongoEngine


app = Flask(__name__)
ROOT_PATH = Path(__file__).parent.parent
app.root_path = str(ROOT_PATH)
app.config.from_pyfile(str(ROOT_PATH / 'settings.py'))
if Path.exists(ROOT_PATH / 'settings.local.py'):
    app.config.from_pyfile(str(ROOT_PATH / 'settings.local.py'))
db = MongoEngine(app)
mail = Mail(app)

from .core.routing import RegexConverter  # noqa: E402

app.url_map.converters['regex'] = RegexConverter

from .articles import views as articles_views  # noqa: F401, F801
from .articles.drafts import views as drafts_views  # noqa: F401, F801
from .articles.proposals import views as proposals_views  # noqa: F401, F801
from .articles.translations import views as translations_views  # noqa: F401, F801
from .api import views  # noqa: F401, F801
from .core import commands, views  # noqa: F401, F801
from .users import views  # noqa: F401, F801

app.register_blueprint(drafts_views.blueprint, url_prefix='/article/draft')
app.register_blueprint(articles_views.blueprint, url_prefix='/article')
app.register_blueprint(
    proposals_views.blueprint, url_prefix='/article/proposal')
app.register_blueprint(
    translations_views.blueprint, url_prefix='/article/translation')

# Dev specific packages
try:
    from flask_debugtoolbar import DebugToolbarExtension
    toolbar = DebugToolbarExtension(app)
except ModuleNotFoundError:
    pass


if __name__ == '__main__':
    app.run(host=app.config.get('HOST'), port=app.config.get('PORT'),
            debug=app.config.get('DEBUG'))
