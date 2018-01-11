from urllib.parse import quote_plus

from flask import Flask
from flask_mail import Mail
from flask_mongoengine import MongoEngine
from flask_security import MongoEngineUserDatastore, Security


mail = Mail()
db = MongoEngine()
security = Security()


def create_app(config_object):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_object)
    app.config.from_pyfile('config.local.py')

    register_extensions(app)
    register_blueprints(app)
    register_template_filters(app)
    register_context_processors(app)
    # register_cli is only called when necessary
    return app


def register_extensions(app):
    db.init_app(app)
    mail.init_app(app)

    from cafebabel.users.models import Role, User

    app.user_datastore = MongoEngineUserDatastore(db, User, Role)
    security.init_app(app, datastore=app.user_datastore)

    if app.debug:
        try:
            from flask_debugtoolbar import DebugToolbarExtension
            DebugToolbarExtension(app)
        except ImportError:
            pass

    if app.testing:
        from cafebabel.core.testing import ContainsResponse
        app.response_class = ContainsResponse


def register_blueprints(app):
    from .core.routing import RegexConverter

    app.url_map.converters['regex'] = RegexConverter

    from .articles.views import articles
    from .articles.drafts.views import drafts
    from .articles.proposals.views import proposals
    from .articles.translations.views import translations
    from .core.views import cores
    from .users.views import users

    app.register_blueprint(cores, url_prefix='/')
    app.register_blueprint(articles, url_prefix='/article')
    app.register_blueprint(drafts, url_prefix='/article/draft')
    app.register_blueprint(proposals, url_prefix='/article/proposal')
    app.register_blueprint(translations, url_prefix='/article/translation')
    app.register_blueprint(users, url_prefix='/profile')


def register_cli(app):
    import click

    @app.cli.command(short_help='Initialize the database')
    def initdb():
        from cafebabel.users.models import Role, User
        from cafebabel.articles.models import Article
        Role.drop_collection()
        User.drop_collection()
        Article.drop_collection()
        click.echo('Roles, Users and Articles dropped.')
        Role.objects.create(name='editor')
        admin_role = Role.objects.create(name='admin')
        admin_user = app.user_datastore.create_user(
            email='admin@example.com', password='password')
        app.user_datastore.add_role_to_user(admin_user, admin_role)
        click.echo('DB intialized.')

    @app.cli.command(short_help='Display list of URLs')
    def urls():
        print(app.url_map)


def register_template_filters(app):
    from cafebabel.core import helpers

    app.add_template_filter(quote_plus, 'quote_plus')
    app.add_template_filter(helpers.slugify, 'slugify')
    app.add_template_filter(helpers.to_json_filter, 'to_json')
    app.add_template_filter(helpers.markdown, 'markdown')
    app.add_template_filter(helpers.reading_time, 'reading_time')
    app.add_template_filter(helpers.obfuscate_email, 'obfuscate_email')


def register_context_processors(app):

    @app.context_processor
    def add_template_helpers():
        return dict(
            get_languages=lambda: app.config.get('LANGUAGES', tuple()),
            get_categories=lambda: app.config.get('CATEGORIES', [])
        )
