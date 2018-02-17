from pathlib import Path
from tempfile import mkdtemp
from cafebabel.users.forms import MultipleHashLoginForm


class BaseConfig:
    DEBUG = False
    SECRET_KEY = 'TODO'

    MONGODB_SETTINGS = {
        'db': 'cafebabel',
        'host': '127.0.0.1',
        'port': 27017,
        'username': '',
        'password': '',
    }

    LANGUAGES = (
        ('en', 'English'),
        ('fr', 'Français'),
        ('es', 'Español'),
        ('it', 'Italiano'),
        ('de', 'Deutsch'),
        ('pl', 'Polszczyzna'),
    )

    CATEGORIES = ['society', 'lifestyle', 'politics', 'culture']

    SECURITY_PASSWORD_SALT = 'and pepper'
    SECURITY_CONFIRMABLE = False
    SECURITY_REGISTERABLE = True
    SECURITY_RECOVERABLE = True
    SECURITY_CHANGEABLE = True
    SECURITY_EMAIL_SENDER = '@'.join(['no-reply', 'cafebabel.com'])
    SECURITY_POST_LOGIN_VIEW = '/profile/'
    SECURITY_PASSWORD_SCHEMES = ['bcrypt', 'django_pbkdf2_sha256']
    SECURITY_LOGIN_FORM = MultipleHashLoginForm
    SECURITY_URL_PREFIX = '/<lang:lang>'

    SECURITY_SEND_REGISTER_EMAIL = True

    SECURITY_FORGOT_PASSWORD_TEMPLATE = 'auth/forgot.html'
    SECURITY_CHANGE_PASSWORD_TEMPLATE = 'auth/change.html'
    SECURITY_RESET_PASSWORD_TEMPLATE = 'auth/reset.html'
    SECURITY_LOGIN_USER_TEMPLATE = 'auth/login.html'
    SECURITY_REGISTER_USER_TEMPLATE = 'auth/register.html'
    SECURITY_SEND_CONFIRMATION_TEMPLATE = 'auth/confirmation.html'

    MAIL_SERVER = 'localhost'
    MAIL_PORT = 25
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False
    MAIL_DEBUG = DEBUG
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    MAIL_DEFAULT_SENDER = None

    # Prevent writing clear email for avoiding robots on Github sources.
    EDITORS_EMAIL_DEFAULT = '@'.join(['editors', 'cafebabel.com'])
    EDITOR_EMAILS = {
        'fr': '@'.join(['redaction', 'cafebabel.com']),
        'en': '@'.join(['editors', 'cafebabel.com']),
        'de': '@'.join(['redaktion', 'cafebabel.com']),
        'es': '@'.join(['redaccion', 'cafebabel.com']),
        'it': '@'.join(['redazione', 'cafebabel.com']),
    }
    UPLOADS_FOLDER = Path(__file__).parent / 'cafebabel' / 'uploads'
    ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
    MAX_CONTENT_LENGTH = 1024 * 1024 * 16  # Megabytes.
    USERS_IMAGE_MAX_CONTENT_LENGTH = 1024 * 500  # Kilobytes.

    DEFAULT_LANGUAGE = LANGUAGES[0][0]


class DevelopmentConfig(BaseConfig):
    DEBUG = True

    SECURITY_SEND_REGISTER_EMAIL = False

    DEBUG_TB_INTERCEPT_REDIRECTS = False
    DEBUG_TB_PANELS = [
        'flask_debugtoolbar.panels.request_vars.RequestVarsDebugPanel',
        'flask_debugtoolbar.panels.config_vars.ConfigVarsDebugPanel',
        'flask_debugtoolbar.panels.template.TemplateDebugPanel',
        'flask_debugtoolbar.panels.route_list.RouteListDebugPanel',
        'flask_mongoengine.panels.MongoDebugPanel'
    ]
    EXPLAIN_TEMPLATE_LOADING = False


class TestingConfig(BaseConfig):
    TESTING = True
    MONGODB_SETTINGS = {
        'db': 'cafebabel_test'
    }
    WTF_CSRF_ENABLED = False
    UPLOADS_FOLDER = Path(mkdtemp()) / 'cafebabel' / 'uploads'
    DEBUG_TB_ENABLED = False

    MONGODB_SETTINGS = {
        'host': 'mongomock://localhost'
    }
