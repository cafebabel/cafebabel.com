from http import HTTPStatus

from flask import Blueprint, abort, flash, redirect, render_template, request
from flask_login import login_required
from mongoengine import errors

from ..models import Article
from .models import Translation

translations = Blueprint('translations', __name__)


@translations.route('/new/', methods=['get', 'post'])
@login_required
def create():
    if request.method == 'POST':
        try:
            translation = Translation().save_from_request(request)
        except errors.ValidationError as e:
            abort(HTTPStatus.BAD_REQUEST, str(e))
        except errors.NotUniqueError as e:
            abort(HTTPStatus.BAD_REQUEST, str(e))
        flash('Thanks! Your translation has been sent to your editor')
        return redirect(translation.detail_url)

    original_article = request.args.get('original')
    if not original_article:
        abort(HTTPStatus.BAD_REQUEST, 'You must specify a valid article.')
    article = Article.objects.get_or_404(id=original_article)
    return render_template('articles/translations/create.html',
                           article=article)


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
        try:
            translation = translation.save_from_request(request)
        except errors.ValidationError as e:
            abort(HTTPStatus.BAD_REQUEST, str(e))
        except errors.NotUniqueError as e:
            abort(HTTPStatus.BAD_REQUEST, str(e))
        flash('Your translation was successfully updated.')
        return redirect(translation.detail_url)

    return render_template('articles/translations/edit.html',
                           translation=translation)
