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

from .articles.views import articles  # noqa: F402
from .articles.drafts.views import drafts  # noqa: F402
from .articles.proposals.views import proposals  # noqa: F402
from .articles.translations.views import translations  # noqa: F402
from .api import views  # noqa: F401, F801
from .core import commands, views  # noqa: F401, F811
from .users import views  # noqa: F401, F811

app.register_blueprint(articles, url_prefix='/article')
app.register_blueprint(drafts, url_prefix='/article/draft')
app.register_blueprint(proposals, url_prefix='/article/proposal')
app.register_blueprint(translations, url_prefix='/article/translation')

# Dev specific packages
try:
    from flask_debugtoolbar import DebugToolbarExtension
    toolbar = DebugToolbarExtension(app)
except ModuleNotFoundError:  # noqa: F821
    pass


if __name__ == '__main__':
    app.run(host=app.config.get('HOST'), port=app.config.get('PORT'),
            debug=app.config.get('DEBUG'))
