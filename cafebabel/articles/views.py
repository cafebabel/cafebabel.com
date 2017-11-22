from http import HTTPStatus

from flask import (Blueprint, abort, flash, redirect, render_template, request,
                   url_for)
from flask_login import fresh_login_required, login_required

from .. import app
from ..core.helpers import editor_required
from ..users.models import User
from .models import Article
from .translations.models import Translation


proposal_bp = Blueprint(
    'proposal', __name__, template_folder='templates/articles')
draft_bp = Blueprint(
    'draft', __name__, template_folder='templates/articles')
article_bp = Blueprint(
    'article', __name__, template_folder='templates/articles')


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


@proposal_bp.route('/')
def proposal_create_form():
    return render_template('articles/proposal.html')


@proposal_bp.route('/', methods=['post'])
def proposal_create():
    data = request.form
    msg = Message(f'Article proposal: {data["topic"]}',
                  sender=data['email'],
                  recipients=[
                      app.config['EDITOR_EMAILS'][data.get('language', 'en')]
                  ],
                  body=f'''
Language: {{data['language']}}
Name: {data['name']}
Email: {{data['email']}}
city: {{data['city']}}
topic: {data['topic']}
Media: {data['media']}
Format: {data['format']}
Section: {data['section']}
Additional infos: {data['additional']}
                  ''',
                  )
    mail.send(msg)
    flash('Your proposal was successfully send.', 'success')
    return redirect(url_for('home'))


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
    try:
        article = Article.objects.get(id=draft_id)
    except Article.DoesNotExist:
        abort(404, 'No draft found with this id.')
    authors = User.objects.all()
    return render_template('articles/edit.html', article=article,
                           authors=authors)


@draft_bp.route('/<regex("\w{24}"):draft_id>/edit/',
                methods=['post'])
def draft_edit(draft_id=None):
    try:
        article = Article.objects.get(id=draft_id)
    except Article.DoesNotExist:
        abort(404, 'No draft found with this id.')
    article = _save_article(request.form.to_dict(), article)
    flash('Your article was successfully saved.')
    if article.is_draft:
        return redirect(url_for('draft.draft_detail', draft_id=article.id))
    else:
        return redirect(url_for('article.article_detail', slug=article.slug,
                                article_id=article.id))


@draft_bp.route('/<regex("\w{24}"):draft_id>/')
def draft_detail(draft_id):
    try:
        article = Article.objects.get(id=draft_id, status='draft')
    except Article.DoesNotExist:
        abort(404, 'No draft found with this id.')
    return render_template('articles/draft_detail.html', article=article)


# Only route with the slug for SEO purpose.
@articles.route('/<slug>-<regex("\w{24}"):article_id>/')
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


@articles.route(
    '/<regex("\w{24}"):article_id>/edit/', methods=['get', 'post'])
@login_required
@editor_required
def edit(article_id):
    article = Article.objects.get_or_404(id=article_id, status='published')

    if request.method == 'POST':
        article.save_from_request(request)
        flash('Your article was successfully saved.')
        return redirect(
            url_for('.detail', article_id=article.id, slug=article.slug))

    authors = User.objects.all()
    return render_template(
        'articles/edit.html', article=article, authors=authors)


@articles.route('/<regex("\w{24}"):article_id>/delete/', methods=['post'])
@fresh_login_required
@editor_required
def delete(article_id):
    article = Article.objects.get_or_404(id=article_id)
    article.delete()
    flash('Article was deleted.', 'success')
    return redirect(url_for('home'))


@articles.route('/to-translate/')
def to_translate():
    default = app.config['LANGUAGES'][0]
    current_language = request.args.get('in', default[0])
    LANGUAGES_DICT = dict(app.config['LANGUAGES'])
    if current_language not in LANGUAGES_DICT:
        abort(HTTPStatus.BAD_REQUEST, 'You must specify a valid language.')
    articles = Article.objects.filter(language__ne=current_language)
    return render_template(
        'articles/to-translate.html', articles=articles,
        current_language=(current_language, LANGUAGES_DICT[current_language]))
