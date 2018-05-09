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
    DEFAULT_LANGUAGE = LANGUAGES[0][0]

    CATEGORIES_SLUGS = ['impact', 'experience', 'raw', 'creative']
    STATIC_PAGES_SLUGS = [
        'about-us',
        'contact',
        'editorial-vision',
        'terms-and-privacy',
        'faq'
    ]
    SOCIAL_NETWORKS = {
        'facebook': {
            'en': 'https://www.facebook.com/cafebabelmagazine/',
            'fr': 'https://www.facebook.com/cafebabelfrance/',
            'de': 'https://www.facebook.com/cafebabelDeutsch/',
            'it': 'https://www.facebook.com/CafebabelItalia/',
            'es': 'https://www.facebook.com/cafebabelenespanol/',
            'pl': 'https://www.facebook.com/cafebabelpolski/'
        },
        'twitter': {
            'en': 'https://twitter.com/cafebabel_ENG',
            'fr': 'https://twitter.com/cafebabel_FR',
            'de': 'https://twitter.com/cafebabel_DE',
            'it': 'https://twitter.com/cafebabel_IT',
            'es': 'https://twitter.com/cafebabel_ES',
            'pl': 'https://twitter.com/cafebabel_POL'
        },
        'instagram': {
            'en': 'https://www.instagram.com/inside.cafebabel/'
        },
        'youtube': {
            'en': 'https://www.youtube.com/channel/UCKanXxqYDt3vmz89Ig6RqBg'
        },
        'linkedin': {
            'en': 'https://www.linkedin.com/company/cafebabel-com/'
        }
    }

    SECURITY_PASSWORD_SALT = 'and pepper'
    SECURITY_CONFIRMABLE = False
    SECURITY_REGISTERABLE = True
    SECURITY_RECOVERABLE = True
    SECURITY_CHANGEABLE = True
    SECURITY_EMAIL_SENDER = '@'.join(['no-reply', 'cafebabel.com'])
    SECURITY_POST_LOGIN_VIEW = '/login_complete/'
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
    EDITOR_EMAILS = {
        'fr': '@'.join(['redaction', 'cafebabel.com']),
        'en': '@'.join(['editors', 'cafebabel.com']),
        'de': '@'.join(['redaktion', 'cafebabel.com']),
        'es': '@'.join(['redaccion', 'cafebabel.com']),
        'it': '@'.join(['redazione', 'cafebabel.com']),
    }

    UPLOADS_FOLDER = Path(__file__).parent / 'cafebabel' / 'uploads'
    RESIZE_ROOT = str(UPLOADS_FOLDER)
    RESIZE_SIZE_TAG_COVER = (2000, 1333)
    RESIZE_SIZE_ARTICLE_COVER = (1200, 467)
    RESIZE_SIZE_ARTICLE_LIST = (768, 300)
    RESIZE_SIZE_ARTICLE_SERIES = (600, 381)
    RESIZE_SIZE_PROFILE = (200, 200)
    RESIZE_SIZE_PROFILE_THUMBNAIL = (45, 45)
    ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
    MAX_CONTENT_LENGTH = 1024 * 1024 * 16  # Megabytes.
    USERS_IMAGE_MAX_CONTENT_LENGTH = 1024 * 500  # Kilobytes.
    HARD_LIMIT_PER_PAGE = 20

    GOOGLE_ANALYTICS_ID = ''


class ProdConfig(BaseConfig):
    DEBUG = False
    MEDIA_URL = 'https://media.cafebabel.com'
    RESIZE_URL = MEDIA_URL + '/'
    GOOGLE_ANALYTICS_ID = 'UA-126606-5'


class PreprodConfig(BaseConfig):
    DEBUG = True
    MEDIA_URL = 'https://media.preprod.cafebabel.com'
    RESIZE_URL = MEDIA_URL + '/'


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
    MEDIA_URL = ''
    RESIZE_URL = MEDIA_URL + '/'


class TestingConfig(BaseConfig):
    TESTING = True
    MONGODB_SETTINGS = {
        'db': 'cafebabel_test'
    }
    WTF_CSRF_ENABLED = False
    UPLOADS_FOLDER = Path(mkdtemp())
    RESIZE_ROOT = str(UPLOADS_FOLDER)
    DEBUG_TB_ENABLED = False
    MEDIA_URL = ''
    RESIZE_URL = MEDIA_URL + '/'

    GOOGLE_ANALYTICS_ID = 'testing-analytics'
