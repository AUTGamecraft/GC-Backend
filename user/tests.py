# from django.test import TestCase
# from django.contrib.auth import get_user_model


# class UserAcountTest(TestCase):

#     def test_new_superuser(self):
#         db  = get_user_model()
#         super_user = db.objects.create_superuser(
#             'testuser@super.com',
#             'username',
#             'firstname',
#             'password'
#         )

#         self.assertEqual(super_user.email , 'testuser@super.com')
#         self.assertTrue(super_user.is_superuser)
#         self.assertTrue(super_user.is_active)
#         self.assertTrue(super_user.is_staff)

#         with self.assertRaises(ValueError):
#             db.objects.create_superuser(
#                 email='testuser1@super.com',
#                 user_name='username1',
#                 first_name='firstname1',
#                 password='password1',
#                 is_superuser = False
#             )
