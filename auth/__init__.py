from core import app, db
from core.models import Role, User, UserRoles
from flask_security import PeeweeUserDatastore, Security

user_datastore = PeeweeUserDatastore(db, User, Role, UserRoles)
security = Security(app, user_datastore)
