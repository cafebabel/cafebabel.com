from datetime import datetime
from http import HTTPStatus
from pathlib import Path
from urllib.parse import quote_plus

import click
from flask import Flask, g, render_template
from flask_mail import Mail
from flask_mongoengine import MongoEngine
from flask_security import MongoEngineUserDatastore, Security

mail = Mail()
db = MongoEngine()
security = Security()


def create_app(config_object):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_object)
    local_config = Path(__file__).parent.parent / 'config.local.py'
    if local_config.exists():
        app.config.from_pyfile(local_config)

    # Blueprints must be before extensions as they require <lang> url pattern.
    register_blueprints(app)
    register_extensions(app)
    register_template_filters(app)
    register_context_processors(app)
    # register_cli is only called when necessary
    return app


def register_extensions(app):
    db.init_app(app)
    mail.init_app(app)

    from .users.models import Role, User

    app.user_datastore = MongoEngineUserDatastore(db, User, Role)
    security.init_app(app, datastore=app.user_datastore)

    if app.debug:
        try:
            from flask_debugtoolbar import DebugToolbarExtension
            DebugToolbarExtension(app)
        except ImportError:
            pass

    if app.testing:
        from .core.testing import ContainsResponse
        app.response_class = ContainsResponse


def register_lang(app):
    @app.url_defaults
    def add_lang(endpoint, values):
        if 'lang' in values or not g.get('lang'):
            return
        if app.url_map.is_endpoint_expecting(endpoint, 'lang'):
            values['lang'] = g.lang

    @app.url_value_preprocessor
    def retrieve_lang(endpoint, values):
        if not (values and 'lang' in values):
            return
        g.lang = values.pop('lang', app.config['DEFAULT_LANGUAGE'])


def register_errors(app):
    @app.errorhandler(HTTPStatus.NOT_FOUND)
    def error_not_found(error):
        return render_template('404.html', error=error), HTTPStatus.NOT_FOUND

    @app.errorhandler(HTTPStatus.INTERNAL_SERVER_ERROR)
    def error_internal_server_error(error):
        return (render_template('500.html', error=error),
                HTTPStatus.INTERNAL_SERVER_ERROR)


def register_blueprints(app):
    from .core.routing import LangConverter, RegexConverter

    app.url_map.converters['regex'] = RegexConverter
    app.url_map.converters['lang'] = LangConverter

    from .archives.views import archives
    from .articles.views import articles
    from .articles.drafts.views import drafts
    from .articles.proposals.views import proposals
    from .articles.tags.views import tags
    from .articles.translations.views import translations
    from .core.views import cores
    from .users.views import users

    register_lang(app)
    app.register_blueprint(cores, url_prefix='')
    app.register_blueprint(articles, url_prefix='/<lang:lang>/article')
    app.register_blueprint(tags, url_prefix='/<lang:lang>/article/tag')
    app.register_blueprint(drafts, url_prefix='/<lang:lang>/article/draft')
    app.register_blueprint(proposals,
                           url_prefix='/<lang:lang>/article/proposal')
    app.register_blueprint(translations,
                           url_prefix='/<lang:lang>/article/translation')
    app.register_blueprint(users, url_prefix='/<lang:lang>/profile')
    # Keep that blueprint in the latest position as a fallback.
    app.register_blueprint(archives, url_prefix='')
    register_errors(app)


def register_cli(app):
    from .commands import (auth_fixtures, categories_fixtures,
                           drop_collections, static_pages_fixtures)
    from .django_migrations import migrate_articles, migrate_users
    from .users.models import User
    from .articles.models import Article
    from .articles.tags.models import Tag

    @app.cli.command(short_help='Initialize the database')
    def initdb():
        drop_collections()
        auth_fixtures(app)
        static_pages_fixtures(app)
        categories_fixtures(app)

    @app.cli.command(short_help='Load articles and tags fixtures')
    def load_fixtures():
        static_pages_fixtures(app)
        categories_fixtures(app)

    @app.cli.command(short_help='Migrate data from old to new system')
    @click.option('--limit', default=0, help='Number of items migrated.')
    @click.option('--users-filepath', help='Path to users.json file.')
    @click.option('--articles-filepath',
                  help='Path to articles35000.json file.')
    @click.option('--articles-filepath2',
                  help='Path to articles35000-70000.json file.')
    def load_migrations(limit, users_filepath, articles_filepath,
                        articles_filepath2):
        User.drop_collection()
        migrate_users(app, limit, users_filepath)
        Article.drop_collection()
        static_pages_fixtures(app)
        Tag.drop_collection()
        categories_fixtures(app)
        migrate_articles(app, limit, articles_filepath)
        migrate_articles(app, limit, articles_filepath2)

    @app.cli.command(short_help='Display list of URLs')
    def urls():
        print(app.url_map)


def register_template_filters(app):
    from .core import helpers

    app.add_template_filter(quote_plus, 'quote_plus')
    app.add_template_filter(helpers.slugify, 'slugify')
    app.add_template_filter(helpers.to_json_filter, 'to_json')
    app.add_template_filter(helpers.markdown, 'markdown')
    app.add_template_filter(helpers.obfuscate_email, 'obfuscate_email')
    app.add_template_filter(helpers.rewrite_img_src, 'rewrite_img_src')


def register_context_processors(app):

    @app.context_processor
    def add_template_helpers():
        from .core import helpers
        return dict(
            get_languages=lambda: app.config.get('LANGUAGES', tuple()),
            get_categories_slugs=(
                lambda: app.config.get('CATEGORIES_SLUGS', tuple())),
            get_year=lambda: datetime.now().year,
            current_language=helpers.current_language(),
            lang_url_for=helpers.lang_url_for,
            absolute=helpers.absolute,
            static_pages_for=helpers.static_pages_for,
            social_network_url_for=helpers.social_network_url_for
        )
