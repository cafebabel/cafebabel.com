from flask import (Blueprint, flash, render_template, redirect, url_for,
                   request, abort, current_app)
from flask_login import login_required, current_user
from werkzeug import exceptions

from ..core.helpers import allowed_file, file_exceeds
from ..articles.models import Article
from .models import User


users = Blueprint('users', __name__)


@users.route('/<id>/edit/', methods=['get', 'post'])
@login_required
def edit(id):
    user = User.objects.get_or_404(id=id)
    if not (user.is_me() or current_user.has_role('editor')):
        abort(401, 'You cannot edit this profile.')
    if request.method == 'POST':
        fields = ['name', 'website', 'about']
        for f in fields:
            setattr(user.profile, f, request.form.get(f))
        user.profile.socials = {k.split('-')[1]: v
                                for k, v in request.form.items()
                                if k.startswith('socials-')}
        # Editor role
        if current_user.has_role('editor'):
            if request.form.get('editor'):
                current_app.user_datastore.add_role_to_user(user, 'editor')
            else:
                current_app.user_datastore.remove_role_from_user(user,
                                                                 'editor')
        # Image upload
        image = request.files.get('image')
        if request.form.get('delete'):
            user.profile.delete_image()
        if image:
            maximum = current_app.config['USERS_IMAGE_MAX_CONTENT_LENGTH']
            if file_exceeds(image, maximum):
                raise exceptions.RequestEntityTooLarge()
            if image.filename == '':
                message = ('There was an error in your profile submission: '
                           'No selected file.')
                flash(message, 'error')
                return redirect(url_for('users.edit', id=user.id))
            if not allowed_file(image.filename):
                # TODO: https://github.com/cafebabel/cafebabel.com/issues/187
                message = ('There was an error in your profile submission: '
                           'Unallowed extension.')
                flash(message, 'error')
                return redirect(url_for('users.edit', id=user.id))
            user.profile.attach_image(image)
        user.save()
        flash('Your profile was successfully saved.')
        return redirect(url_for('users.detail', id=user.id))
    articles = Article.objects.filter(author=user)
    return render_template('users/edit.html', user=user, articles=articles)


@users.route('/<id>/')
def detail(id):
    user = User.objects.get_or_404(id=id)
    filters = {'author': user}
    if not user.is_me():
        filters['status'] = 'published'
    articles = Article.objects(**filters)
    return render_template('users/detail.html', user=user, articles=articles)
