from django.test import TestCase
from django.contrib.auth import get_user_model

# Create your tests here.

class UserModelTestCase(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass123', mobile='1234567890'
        )

    def test_user_str(self):
        self.assertEqual(str(self.user), 'testuser')

    def test_user_uuid(self):
        self.assertIsNotNone(self.user.id)
        self.assertEqual(len(str(self.user.id)), 36)
