from pathlib import Path
from tempfile import mkdtemp


MONGODB_SETTINGS = {'db': 'cafebabel_test'}
WTF_CSRF_ENABLED = False
ARTICLES_IMAGES_PATH = Path(mkdtemp())
DEBUG_TB_ENABLED = False
