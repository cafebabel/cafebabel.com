from unittest import TestCase

from api import views  # noqa: 401
from articles import views  # noqa: 401
from core import views  # noqa: 401
from core import app


class ArticlesTest(TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_proposal_sends_email_to_editor(self):
        response = self.client.get('/article/proposal/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('action=/article/proposal/', response.get_data().decode())
