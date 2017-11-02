import re
import unicodedata

import markdown as markdownlib
from flask import Markup

from .. import app


@app.template_filter()
def slugify(value):
    value = (unicodedata.normalize('NFKD', str(value))
             .encode('ascii', 'ignore').decode('ascii'))
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    return re.sub('[-\s]+', '-', value)


@app.template_filter()
def markdown(value):
    return Markup(markdownlib.markdown(value))


@app.context_processor
def add_template_helpers():
    return dict(
        get_languages=lambda: app.config.get('LANGUAGES', tuple()),
        get_categories=lambda: app.config.get('CATEGORIES', []),
        article_image_url=(lambda a:
            f'{app.config.get("ARTICLES_IMAGES_URL")}/{a.id}'),
    )
