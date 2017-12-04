from flask import Blueprint, render_template

cores = Blueprint('cores', __name__)


@cores.route('/')
def home():
    return render_template('home.html')
