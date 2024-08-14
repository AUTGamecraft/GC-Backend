from django.test import TestCase
from tasks import emails


class TasksTestCase(TestCase):
    def setUp(self):
        self.data = {
            "email": "javadakbari623@gmail.com",
            "subject": "test",
            "body": "testing",
        }

    def test_send_email(self):
        res = emails.send_simple_email(self.data)
        self.assertTrue('success' in res['message'])
