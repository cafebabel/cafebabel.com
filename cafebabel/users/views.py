from http import HTTPStatus

from flask import (Blueprint, abort, current_app, flash, jsonify, redirect,
                   render_template, request)
from flask_login import current_user, login_required
from werkzeug import exceptions

from ..articles.models import Article
from ..articles.translations.models import Translation
from ..core.helpers import allowed_file, lang_url_for, file_exceeds
from .models import User

users = Blueprint('users', __name__)


@users.route('/suggest/')
def suggest():
    terms = request.args.get('terms')
    if len(terms) < 3:
        abort(HTTPStatus.BAD_REQUEST,
              'Suggestions are made available from 3-chars and more.')
    users = User.objects(profile__name__istartswith=terms)
    cleaned_user = [{
        'name': user.profile.name,
        'id': str(user.id)
    } for user in users]
    return jsonify(cleaned_user)


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
                return redirect(lang_url_for('users.edit', id=user.id))
            if not allowed_file(image.filename):
                # TODO: https://github.com/cafebabel/cafebabel.com/issues/187
                message = ('There was an error in your profile submission: '
                           'Unallowed extension.')
                flash(message, 'error')
                return redirect(lang_url_for('users.edit', id=user.id))
            user.profile.attach_image(image)
        user.save()
        flash('Your profile has been updated :-)')
        return redirect(user.detail_url)
    articles = Article.objects.filter(authors=user).hard_limit()
    return render_template('users/edit.html', user=user, articles=articles)


@users.route('/<id>/')
def detail(id):
    user = User.objects.get_or_404(id=id)
    is_full = 'full' in request.args
    filters = {}
    if not user.is_me():
        filters['status'] = 'published'
    articles = Article.objects(original_article=None, authors__in=[user],
                               **filters)
    # PERF: we exclude the `original_article` to avoid an extra query
    #       during the following `select_related`.
    translations = (Translation.objects(translators__in=[user], **filters)
                    .exclude('original_article'))
    if not is_full:
        articles = articles.hard_limit()
        translations = translations.hard_limit()
    # PREF: `select_related` calls must be performed at the end given
    #       they turn querysets into lists.
    return render_template(
        'users/detail.html', user=user, is_full=is_full,
        articles=articles.select_related(max_depth=1),
        translations=translations.select_related(max_depth=1))
