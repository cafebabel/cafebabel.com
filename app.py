import os
from flask import Flask


PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config.from_pyfile(f'{PROJECT_PATH}/settings.py')


@app.route('/')
def home():
    return '<h1>Cafebabel</h1>'


if __name__ == '__main__':
    app.run(host=app.config.get('HOST'), port=app.config.get('PORT'),
            debug=app.config.get('DEBUG'))
