from flask_login import LoginManager

from core import app
from core.models import User

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(session_token):
    try:
        return User.get(session_token=session_token)
    except User.DoesNotExist:
        return None
