from http import HTTPStatus

from flask import (Blueprint, abort, flash, redirect, render_template, request,
                   url_for)
from flask_login import fresh_login_required, login_required

from .. import app
from ..core.helpers import editor_required
from ..users.models import User
from .models import Article
from .translations.models import Translation

blueprint = Blueprint('article', __name__)


# Only route with the slug for SEO purpose.
@blueprint.route('/<slug>-<regex("\w{24}"):article_id>/')
def detail(slug, article_id):
    article = Article.objects.get_or_404(id=article_id, status='published')
    if article.slug != slug:
        return redirect(
            url_for('.detail', article_id=article.id, slug=article.slug),
            code=HTTPStatus.MOVED_PERMANENTLY)
    if article.is_translation:
        translations = Translation.objects(
            original_article=article.original_article.id)
    else:
        translations = Translation.objects(original_article=article.id)
    translations_langs = [translation.language for translation in translations]
    translations_drafts = [translation for translation in translations
                           if translation.is_draft]
    translations_publisheds = [translation for translation in translations
                               if translation.is_published and
                               translation.id != article.id]
    return render_template('articles/detail.html', article=article,
                           translations=translations,
                           translations_langs=translations_langs,
                           translations_drafts=translations_drafts,
                           translations_publisheds=translations_publisheds)


@blueprint.route(
    '/<regex("\w{24}"):article_id>/edit/', methods=['get', 'post'])
@login_required
@editor_required
def edit(article_id):
    article = Article.objects.get_or_404(id=article_id, status='published')

    if request.method == 'POST':
        article = Article._save_article(
            request.form.to_dict(), request.files, article)
        flash('Your article was successfully saved.')
        return redirect(
            url_for('.detail', article_id=article.id, slug=article.slug))

    authors = User.objects.all()
    return render_template(
        'articles/edit.html', article=article, authors=authors)


@blueprint.route('/<regex("\w{24}"):article_id>/delete/', methods=['post'])
@fresh_login_required
@editor_required
def delete(article_id):
    article = Article.objects.get_or_404(id=article_id)
    article.delete()
    flash('Article was deleted.', 'success')
    return redirect(url_for('home'))


@blueprint.route('/to_translate/')
def to_translate():
    english = app.config['LANGUAGES'][0]
    current_language = request.args.get('in', english[0])
    LANGUAGES_DICT = dict(app.config['LANGUAGES'])
    if current_language not in LANGUAGES_DICT:
        abort(HTTPStatus.BAD_REQUEST, 'You must specify a valid language.')
    articles = Article.objects.filter(language__ne=current_language)
    return render_template(
        'articles/to_translate.html', articles=articles,
        current_language=(current_language, LANGUAGES_DICT[current_language]))
