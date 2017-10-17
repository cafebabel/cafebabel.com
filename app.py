import cli  # noqa: import commands.
from cafebabel.api import views  # noqa: 401
from cafebabel.articles import views  # noqa: 401
from cafebabel.core import views  # noqa: 401
from cafebabel.core import app

if __name__ == '__main__':
    app.run(host=app.config.get('HOST'), port=app.config.get('PORT'),
            debug=app.config.get('DEBUG'))
