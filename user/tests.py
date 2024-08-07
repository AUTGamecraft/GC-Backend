from django.test import TestCase
from django.contrib.auth import get_user_model


class UserAccountTest(TestCase):

    def test_new_superuser(self):
        db = get_user_model()
        super_user = db.objects.create_superuser(
            email='testuser@super.com',
            user_name='username',
            first_name='firstname',
            password='password',
            phone_number='09001112222'
        )

        self.assertEqual(super_user.email, 'testuser@super.com')
        self.assertTrue(super_user.is_superuser)
        self.assertTrue(super_user.is_active)
        self.assertTrue(super_user.is_staff)
