from datetime import datetime

import click
from flask_security.utils import hash_password

from cafebabel.users.models import Role, User, UserProfile
from cafebabel.articles.models import Article
from cafebabel.articles.tags.models import Tag
from cafebabel.articles.translations.models import Translation
from cafebabel.core.helpers import slugify


def drop_collections():
    Role.drop_collection()
    User.drop_collection()
    Article.drop_collection()
    Tag.drop_collection()
    click.echo('Roles, Users, Articles and Tags dropped.')


def editor_fixtures(ds, app):
    editor = ds.create_user(email=app.config['EDITOR_EMAILS']['en'],
                            password=hash_password('password'))
    ds.activate_user(editor)
    click.echo('Editor intialized.')
    return editor


def roles_fixtures(ds, editor):
    editor_role = Role.objects.create(name='editor')
    ds.add_role_to_user(editor, editor_role)
    click.echo('Roles intialized.')


def auth_fixtures(app):
    ds = app.user_datastore
    with app.app_context():
        editor = editor_fixtures(ds, app)
        roles_fixtures(ds, editor)
        ds.commit()
    click.echo('Auth intialized.')


def categories_fixtures(app):
    for category_slug in app.config['CATEGORIES_SLUGS']:
        for lang_code, _ in app.config['LANGUAGES']:
            if not Tag.objects.filter(slug=category_slug).count():
                Tag.objects.create(
                    name=category_slug.title(),
                    language=lang_code)
    click.echo('Categories intialized.')


def static_pages_fixtures(app):
    editor = User.objects.get(email=app.config['EDITOR_EMAILS']['en'])
    for static_page_slug in app.config['STATIC_PAGES_SLUGS']:
        if not Article.objects.filter(slug=static_page_slug).count():
            article = Article.objects.create(
                title=static_page_slug.capitalize().replace('-', ' '),
                summary='Lorem ipsum…',
                authors=[editor],
                editor=editor,
                status='published',
                language=app.config['LANGUAGES'][0][0],
                body='…dolor sit amet.',
                creation_date=datetime(1970, 1, 1),
                publication_date=datetime(1970, 1, 1))
        for lang_code, _ in app.config['LANGUAGES'][1:]:
            slug = f'{lang_code}-{static_page_slug}'
            if not Translation.objects.filter(slug=slug).count():
                Translation.objects.create(
                    title=f'[{lang_code}] {article.title}',
                    summary=f'[{lang_code}] {article.summary}',
                    body=f'[{lang_code}] {article.body}',
                    translators=[editor],
                    original_article=article.id,
                    language=lang_code,
                    status=article.status,
                    editor=article.editor,
                    authors=article.authors,
                    creation_date=article.creation_date,
                    publication_date=article.publication_date)
    click.echo('Static pages intialized.')


def migrate_users_slugs():
    for user in User.objects.all():
        if not user.profile.slug:
            user.profile.slug = slugify(user.profile.name)
            user.save()
