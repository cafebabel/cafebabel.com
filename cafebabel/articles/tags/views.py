from http import HTTPStatus

from flask import (Blueprint, abort, current_app, flash, jsonify, redirect,
                   render_template, request, url_for)

from ...core.exceptions import ValidationError
from ...core.helpers import editor_required, current_language
from ..models import Article
from .models import Tag

tags = Blueprint('tags', __name__)


@tags.route('/suggest/')
def suggest():
    terms = request.args.get('terms')
    if len(terms) < 3:
        abort(HTTPStatus.BAD_REQUEST,
              'Suggestions made available from 3-chars and more.')
    languages = dict(current_app.config['LANGUAGES'])
    language = request.args.get('language')
    if language not in languages:
        abort(HTTPStatus.BAD_REQUEST,
              f'Languages available: {list(languages.keys())}.')
    tags = Tag.objects(language=language, name__istartswith=terms)
    cleaned_tag = [{
        'name': tag.name,
        'slug': tag.slug,
        'language': tag.language,
        'summary': tag.summary or ''
    } for tag in tags]
    return jsonify(cleaned_tag)


@tags.route('/<slug>/')
def detail(slug):
    tag = Tag.objects.get_or_404(slug=slug, language=current_language())
    articles = (Article.objects(tags__in=[tag], status='published')
                .order_by('-publication_date').hard_limit())
    return render_template('articles/tags/detail.html', tag=tag,
                           articles=articles)


@tags.route('/<slug>/edit/', methods=['get', 'post'])
@editor_required
def edit(slug):
    tag = Tag.objects.get_or_404(slug=slug, language=current_language())

    if request.method == 'POST':
        try:
            tag.save_from_request(request)
        except ValidationError as e:
            # TODO: see https://github.com/cafebabel/cafebabel.com/issues/187
            message = f'There was an error in your tag submission: {e}'
            flash(message, 'error')
            return redirect(tag.edit_url)
        flash('Your tag was successfully saved.')
        return redirect(tag.detail_url)

    return render_template('articles/tags/edit.html', tag=tag)
