DEBUG = True
SECRET_KEY = 'TODO'

DATABASE = {
    'name': 'cafebabel.db',
    'engine': 'peewee.SqliteDatabase',
}

SECURITY_PASSWORD_SALT = 'and pepper'
SECURITY_CONFIRMABLE = True
SECURITY_REGISTERABLE = True
SECURITY_RECOVERABLE = True
SECURITY_CHANGEABLE = True
