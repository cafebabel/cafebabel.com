from http import HTTPStatus

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import fresh_login_required, login_required

from ..core.helpers import editor_required
from ..users.models import User
from .models import Article
from .translations.models import Translation

blueprint = Blueprint('article', __name__)


# Only route with the slug for SEO purpose.
@blueprint.route('/<slug>-<regex("\w{24}"):article_id>/')
def article_detail(slug, article_id):
    article = Article.objects.get_or_404(id=article_id, status='published')
    if article.slug != slug:
        return redirect(
            url_for('.article_detail', article_id=article.id,
                    slug=article.slug),
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


@blueprint.route('/<regex("\w{24}"):article_id>/', methods=['post'])
@login_required
@editor_required
def article_edit(article_id):
    article = Article.objects.get_or_404(id=article_id, status='published')
    article = Article._save_article(
        request.form.to_dict(), request.files, article)
    flash('Your article was successfully saved.')
    return redirect(
        url_for('.article_detail', article_id=article.id, slug=article.slug))


@blueprint.route('/<regex("\w{24}"):article_id>/form/')
@login_required
@editor_required
def article_edit_form(article_id):
    article = Article.objects.get_or_404(id=article_id, status='published')
    authors = User.objects.all()
    return render_template(
        'articles/edit.html', article=article, authors=authors)


@blueprint.route('/<regex("\w{24}"):article_id>/delete/', methods=['post'])
@fresh_login_required
@editor_required
def article_delete(article_id):
    article = Article.objects.get_or_404(id=article_id)
    article.delete()
    flash('Article was deleted.', 'success')
    return redirect(url_for('home'))
