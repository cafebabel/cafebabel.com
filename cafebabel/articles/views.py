from http import HTTPStatus

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, fresh_login_required, login_required

from ..core.helpers import editor_required
from ..users.models import User
from .models import Article
from .translations.models import Translation

draft_bp = Blueprint('draft', __name__)
article_bp = Blueprint('article', __name__)


def _save_article(data, article):
    if current_user.has_role('editor'):
        if not article.editor:
            data['editor'] = current_user.id
        if data.get('author'):
            data['author'] = User.objects.get(id=data.get('author'))
    else:
        if data.get('author'):
            del data['author']
        if data.get('editor'):
            del data['editor']
    for field, value in data.items():
        setattr(article, field, value)
    if data.get('delete-image'):
        article.delete_image()
    image = request.files.get('image')
    if image:
        article.attach_image(image)
    return article.save()


@draft_bp.route('/')
@editor_required
@login_required
def draft_create_form():
    article = Article()
    authors = User.objects.all()
    return render_template('articles/edit.html', article=article,
                           authors=authors)


@draft_bp.route('/', methods=['post'])
@editor_required
@login_required
def draft_create():
    article = _save_article(request.form.to_dict(), Article())
    flash('Your article was successfully saved.')
    if article.is_draft:
        return redirect(url_for('draft.draft_detail', draft_id=article.id))
    else:
        return redirect(url_for('article.article_detail', slug=article.slug,
                                article_id=article.id))


@draft_bp.route('/<regex("\w{24}"):draft_id>/edit/')
def draft_edit_form(draft_id):
    article = Article.objects.get_or_404(id=draft_id)
    authors = User.objects.all()
    return render_template('articles/edit.html', article=article,
                           authors=authors)


@draft_bp.route('/<regex("\w{24}"):draft_id>/edit/', methods=['post'])
def draft_edit(draft_id):
    article = Article.objects.get_or_404(id=draft_id)
    article = _save_article(request.form.to_dict(), article)
    flash('Your article was successfully saved.')
    if article.is_draft:
        return redirect(url_for('draft.draft_detail', draft_id=article.id))
    else:
        return redirect(url_for('article.article_detail', slug=article.slug,
                                article_id=article.id))


@draft_bp.route('/<regex("\w{24}"):draft_id>/')
def draft_detail(draft_id):
    article = Article.objects.get_or_404(id=draft_id, status='draft')
    return render_template('articles/draft_detail.html', article=article)


# Only route with the slug for SEO purpose.
@article_bp.route('/<slug>-<regex("\w{24}"):article_id>/')
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


@article_bp.route('/<regex("\w{24}"):article_id>/', methods=['post'])
@login_required
@editor_required
def article_edit(article_id):
    article = Article.objects.get_or_404(id=article_id, status='published')
    article = _save_article(request.form.to_dict(), article)
    flash('Your article was successfully saved.')
    return redirect(
        url_for('.article_detail', article_id=article.id, slug=article.slug))


@article_bp.route('/<regex("\w{24}"):article_id>/form/')
@login_required
@editor_required
def article_edit_form(article_id):
    article = Article.objects.get_or_404(id=article_id, status='published')
    authors = User.objects.all()
    return render_template(
        'articles/edit.html', article=article, authors=authors)


@article_bp.route('/<regex("\w{24}"):article_id>/delete/', methods=['post'])
@fresh_login_required
@editor_required
def article_delete(article_id):
    article = Article.objects.get_or_404(id=article_id)
    article.delete()
    flash('Article was deleted.', 'success')
    return redirect(url_for('home'))
