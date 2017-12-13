from flask import (Blueprint, flash, render_template, redirect, url_for,
                   request, abort)
from flask_login import login_required, current_user

from ..articles.models import Article
from .models import User


users = Blueprint('users', __name__)


@users.route('/')
@login_required
def me():
    return redirect(url_for('.detail', id=current_user.id))


@users.route('/<id>/edit/', methods=['get', 'post'])
def edit(id):
    user = User.objects.get_or_404(id=id)
    if not (user.is_me() or user.has_role('editor')):
        abort(401, 'You cannot edit this profile.')
    if request.method == 'POST':
        fields = ['name', 'website', 'about']
        for f in fields:
            setattr(user.profile, f, request.form.get(f))
        user.profile.socials = {k.split('-')[1]: v
                                for k, v in request.form.items()
                                if k.startswith('socials-')}
        image = request.files.get('image')
        if request.form.get('delete'):
            user.profile.delete_image()
        if image:
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
