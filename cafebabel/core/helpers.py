import re
import unicodedata

from . import app


@app.template_filter()
def slugify(value):
    value = (unicodedata.normalize('NFKD', str(value))
             .encode('ascii', 'ignore').decode('ascii'))
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    return re.sub('[-\s]+', '-', value)
