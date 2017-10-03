from core import app
from api import views  # noqa: 401
from core import views  # noqa: 401


if __name__ == '__main__':
    app.run(host=app.config.get('HOST'), port=app.config.get('PORT'),
            debug=app.config.get('DEBUG'))
