from flask_security import PeeweeUserDatastore, Security

from ..core import app, db
from .models import Role, User, UserRoles

user_datastore = PeeweeUserDatastore(db, User, Role, UserRoles)
security = Security(app, user_datastore)
