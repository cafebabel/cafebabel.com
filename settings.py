DEBUG = True
SECRET_KEY = 'TODO'

DATABASE = {
    'name': 'cafebabel.db',
    'engine': 'peewee.SqliteDatabase',
}


MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_DEBUG = False
MAIL_USERNAME = 'cafebabel.dev@gmail.com'
MAIL_PASSWORD = 'cafebabeldev'
# Prevent writing clear email for avoiding robots on Github sources.
MAIL_DEFAULT_SENDER = '@'.join(['do-reply', 'cafebabel.com'])

EDITORS_EMAIL_DEFAULT = '@'.join(['editors', 'cafebabel.com'])
EDITOR_EMAILS = {
    'en': '@'.join(['en', 'cafebabel.co.uk']),
    'fr': '@'.join(['fr', 'cafebabel.fr']),
    'it': '@'.join(['it', 'cafebabel.it']),
}

SECURITY_SEND_REGISTER_EMAIL = True
SECURITY_PASSWORD_SALT = 'and pepper'
SECURITY_CONFIRMABLE = True
SECURITY_REGISTERABLE = True
SECURITY_RECOVERABLE = True
SECURITY_CHANGEABLE = True
SECURITY_EMAIL_SENDER = MAIL_DEFAULT_SENDER
SECURITY_POST_LOGIN_VIEW = '/profile/'
SECURITY_FORGOT_PASSWORD_TEMPLATE = 'forgot.html'
SECURITY_CHANGE_PASSWORD_TEMPLATE = 'change.html'
SECURITY_RESET_PASSWORD_TEMPLATE = 'reset.html'
SECURITY_LOGIN_USER_TEMPLATE = 'login.html'
SECURITY_REGISTER_USER_TEMPLATE = 'register.html'
SECURITY_SEND_CONFIRMATION_TEMPLATE = 'confirmation.html'

EXPLAIN_TEMPLATE_LOADING = True
DEBUG_TB_INTERCEPT_REDIRECTS = False
