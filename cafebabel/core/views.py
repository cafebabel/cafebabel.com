from flask import Blueprint, current_app, render_template, send_from_directory

cores = Blueprint('cores', __name__)


@cores.route('/')
def home():
    return render_template('home.html')


@cores.route('/uploads/<filename>')
def uploads(filename):
    return send_from_directory(current_app.config['UPLOADS_FOLDER'], filename)
