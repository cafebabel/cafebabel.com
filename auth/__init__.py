from flask_login import LoginManager

from core import app
from core.models import User

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    try:
        return User.get(id=user_id)
    except User.DoesNotExist:
        return None
