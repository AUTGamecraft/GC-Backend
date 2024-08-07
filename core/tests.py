from django.test import TestCase
from .models import Talk


class TalkTest(TestCase):

    def test_new_talk(self):
        db = Talk
        talk = db.objects.create(title='Test Talk', start='2023-10-11 10:10', end='2024-10-11 10:10', capacity=12)
        self.assertEqual(talk.capacity, 12)
