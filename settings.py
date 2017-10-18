DEBUG = True
SECRET_KEY = 'TODO'

DATABASE = {
    'name': 'cafebabel.db',
    'engine': 'peewee.SqliteDatabase',
}

SECURITY_PASSWORD_SALT = 'and pepper'
SECURITY_CONFIRMABLE = False
SECURITY_REGISTERABLE = True
SECURITY_RECOVERABLE = True
SECURITY_CHANGEABLE = True
SECURITY_EMAIL_SENDER = '@'.join(['no-reply', 'cafebabel.com'])
SECURITY_POST_LOGIN_VIEW = '/profile/'

SECURITY_SEND_REGISTER_EMAIL = not DEBUG

SECURITY_FORGOT_PASSWORD_TEMPLATE = 'forgot.html'
SECURITY_CHANGE_PASSWORD_TEMPLATE = 'change.html'
SECURITY_RESET_PASSWORD_TEMPLATE = 'reset.html'
SECURITY_LOGIN_USER_TEMPLATE = 'login.html'
SECURITY_REGISTER_USER_TEMPLATE = 'register.html'
SECURITY_SEND_CONFIRMATION_TEMPLATE = 'confirmation.html'
EXPLAIN_TEMPLATE_LOADING = True
DEBUG_TB_INTERCEPT_REDIRECTS = False

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
    'en': '@'.join(['en', 'cafebabel.co.uk']),
    'fr': '@'.join(['fr', 'cafebabel.fr']),
    'it': '@'.join(['it', 'cafebabel.it']),
}
