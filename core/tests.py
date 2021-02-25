from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from .models import (
    Talk
)


class TalkTest(TestCase):

    def test_new_talk(self):
        db  = Talk
        talk = db.objects.create(date='2020' , content='asdasdasd' , capacity=12)
        self.assertEqual(talk.capacity , 12)
