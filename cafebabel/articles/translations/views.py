from http import HTTPStatus

from flask import Blueprint, abort, flash, redirect, render_template, request
from flask_login import current_user, login_required
from mongoengine import errors

from ... import app
from ..models import Article
from .models import Translation

translations = Blueprint('translations', __name__)


@translations.route('/new/', methods=['get', 'post'])
@login_required
def create():
    original_article = request.args.get('original')
    language = request.args.get('lang')
    if not original_article:
        abort(HTTPStatus.BAD_REQUEST, 'You must specify a valid article.')
    if not language or language not in dict(app.config['LANGUAGES']):
        abort(HTTPStatus.BAD_REQUEST, 'You must specify a valid language.')
    article = Article.objects.get_or_404(id=original_article)

    if request.method == 'POST':
        data = request.form.to_dict()
        try:
            translation = Translation.objects.create(
                translator=current_user.id,
                original_article=article.id,
                status='draft',
                editor=article.editor,
                author=article.author,
                has_image=article.has_image,
                category=article.category,
                language=language,
                **data
            )
        except errors.ValidationError as e:
            abort(HTTPStatus.BAD_REQUEST, str(e))
        flash('Your translation was successfully created.')
        return redirect(translation.detail_url)

    return render_template('articles/translations/create.html',
                           article=article, language=language)


@translations.route('/<regex("\w{24}"):id>/')
def detail(id):
    translation = Translation.objects.get_or_404(id=id, status='draft')
    return render_template('articles/translations/detail.html',
                           translation=translation)


@translations.route('/<regex("\w{24}"):id>/edit/', methods=['get', 'post'])
@login_required
def edit(id):
    translation = Translation.objects.get_or_404(id=id, status='draft')

    if request.method == 'POST':
        translation.modify(**request.form.to_dict())
        flash('Your translation was successfully updated.')
        return redirect(translation.detail_url)

    return render_template('articles/translations/update.html',
                           translation=translation)
