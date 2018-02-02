import json
from datetime import datetime, timedelta, timezone

import click
from cafebabel.articles.models import Article
from cafebabel.articles.tags.models import Tag
from cafebabel.articles.translations.models import Translation
from cafebabel.users.models import Role, User
from mongoengine import errors as mongo_errors
from progressist import ProgressBar

PROGRESSIST_TEMPLATE = ('{prefix} {animation} {percent} ({done}/{total}) '
                        'ETA: {eta:%H:%M} {elapsed}')
NOW = datetime.now()


def load_json_file(filename):
    with open(filename) as json_file:
        return json.loads(json_file.read())


def timestamp_to_datetime(timestamp):
    datetime_ = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S')
    datetime_.replace(tzinfo=timezone.utc)
    return datetime_


def migrate_users(app, limit, users_filepath):
    click.echo('Starting users migration.')
    ds = app.user_datastore
    old_users = load_json_file(users_filepath)
    if limit:
        old_users = old_users[:limit]
    bar = ProgressBar(total=len(old_users), template=PROGRESSIST_TEMPLATE,
                      done_char='👤')
    editor_role = Role.objects.get(name='editor')
    with app.app_context():
        for old_user in bar.iter(old_users):
            create_user(ds, old_user, editor_role)
    click.echo('Users migrated.')


def create_user(ds, old_user, editor_role):
    fields = old_user['fields']
    creation_date = timestamp_to_datetime(fields['date_joined'])
    user = ds.create_user(email=fields['email'],
                          password=fields['password'],
                          creation_date=creation_date)
    user.profile.name = f'{fields["first_name"]} {fields["last_name"]}'
    avatar = fields['avatar']
    if avatar:
        user.profile.image_filename = avatar[len('avatars/'):]
    user.profile.old_pk = old_user['pk']
    user.save()
    if fields['is_superuser'] or fields['is_staff']:
        ds.add_role_to_user(user, editor_role)


def migrate_articles(app, limit, article_filepath):
    click.echo('Starting article migration.')
    old_articles = load_json_file(article_filepath)
    if limit:
        old_articles = old_articles[:limit]
    bar = ProgressBar(total=len(old_articles), template=PROGRESSIST_TEMPLATE,
                      done_char='📃')
    with app.app_context():
        for old_article in bar.iter(old_articles):
            create_article(old_article)
        bar.done = 0  # Reset.
        for old_article in bar.iter(old_articles):
            create_article(old_article)
    click.echo('Articles migrated.')


def normalize_status(status):
    normalized_status = 'draft'
    if status == 'PUBLISHED':
        normalized_status = 'published'
    return normalized_status


def normalize_language(language):
    normalized_language = language[:2]
    if normalized_language == 'ge':
        normalized_language = 'de'
    elif normalized_language == 'sp':
        normalized_language = 'es'
    return normalized_language


def normalize_image(image):
    return image and image[len('editorials/'):] or ''


def normalize_author(author_pk):
    try:
        if author_pk is not None:
            return User.objects.get(profile__old_pk=author_pk)
    except User.DoesNotExist:
        print(author_pk, 'user does not exist (outdated input file?)')


def handle_groups(groups):
    tags = []
    old_category_slug = ''
    if groups:
        for group in groups:
            group_fields = group['fields']
            data = {
                'name': group_fields['name'],
                'language': normalize_language(group_fields['language']),
                'summary': group_fields['about'],
            }
            try:
                tag = Tag.objects.get_or_create(**data)
            except mongo_errors.NotUniqueError:
                # We fallback on the old slug in that particular case.
                data['slug'] = group_fields['slug']
                tag = Tag.objects.get_or_create(**data)
            tags.append(tag)
            if group_fields['feature'] == 'MAGAZINE':
                old_category_slug = group_fields['slug']
    return tags, old_category_slug


def create_article(old_article):
    fields = old_article['fields']
    status = normalize_status(fields['status'])
    creation_date = timestamp_to_datetime(fields['created_at'])
    # Get rid of drafts older than 3 months.
    if status == 'draft' and creation_date + timedelta(days=90) < NOW:
        return
    try:
        Article.objects.get(old_pk=old_article['pk'])
        return
    except Article.DoesNotExist:
        pass
    article_fields = old_article['article']['fields']
    tags, old_category_slug = handle_groups(old_article['groups'])
    data = {
        'title': fields['title'],
        'summary': article_fields['original_header'] or 'TODO',
        'body': article_fields['body'] or 'TODO',
        'language': normalize_language(fields['language']),
        'old_pk': old_article['pk'],
        'old_slug': fields['slug'],
        'creation_date': creation_date,
        'publication_date': timestamp_to_datetime(fields['publication_date']),
        'author': normalize_author(fields['created_by']),
        'image_filename': normalize_image(fields['image']),
        'status': status,
        'old_category_slug': old_category_slug,
        'tags': tags or None
    }
    translation_from = fields['translation_from']
    if translation_from:
        try:
            original_article = Article.objects.get(
                old_pk=translation_from)
        except Article.DoesNotExist:
            # print(old_pk, 'article does not exist')
            return
        translator = data['author']
        data['author'] = original_article.author
        try:
            Translation.objects.create(
                translator=translator,
                original_article=original_article,
                **data
            )
        except mongo_errors.ValidationError:
            print(f'Translator not found for {data["old_pk"]} (skipping)')
    else:
        Article.objects.create(**data)
