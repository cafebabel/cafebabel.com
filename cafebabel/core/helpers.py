import json
import re
import unicodedata
from functools import wraps
from http import HTTPStatus
from math import ceil

import markdown as markdownlib
from flask import Markup, abort
from flask_login import current_user
from jinja2.filters import do_wordcount


def slugify(value):
    value = (unicodedata.normalize('NFKD', str(value))
             .encode('ascii', 'ignore').decode('ascii'))
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    return re.sub('[-\s]+', '-', value)


def to_json_filter(value):
    return Markup(json.dumps(value))


def markdown(value):
    return Markup(markdownlib.markdown(value))


def reading_time(text):
    words = do_wordcount(text)
    return ceil(words / 250)


def editor_required(func):
    """Decorator which ensure that the current user's has an editor role.

    If you decorate a view with this, it must be used in conjunction with the
    `(fresh_)login_required` decorator.
    """
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.has_role('editor'):
            abort(HTTPStatus.FORBIDDEN,
                  'An editor is required to perform this action.')
        return func(*args, **kwargs)
    return decorated_view
