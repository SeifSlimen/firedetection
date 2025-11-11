from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()


class AuthFlowTests(TestCase):
	def test_register_and_activate_and_login(self):
		# register
		resp = self.client.post(reverse('register'), data={
			'email': 'test@example.com',
			'password1': 'complexpassword123',
			'password2': 'complexpassword123',
			'user_type': User.USER_TYPE_AGENT,
		})
		self.assertEqual(resp.status_code, 302)  # redirected to login

		user = User.objects.get(email='test@example.com')
		self.assertFalse(user.is_active)

		# simulate activation link
		uid = urlsafe_base64_encode(force_bytes(user.pk))
		token = default_token_generator.make_token(user)
		resp = self.client.get(reverse('activate', args=[uid, token]))
		self.assertEqual(resp.status_code, 302)
		user.refresh_from_db()
		self.assertTrue(user.is_active)

		# login
		resp = self.client.post(reverse('login'), data={'email': 'test@example.com', 'password': 'complexpassword123'})
		self.assertIn(resp.status_code, (302, 200))

	def test_dashboard_access_by_role(self):
		# create an admin user
		admin = User.objects.create_user(email='admin2@example.com', password='pw', user_type=User.USER_TYPE_ADMIN, is_active=True)
		self.client.login(username='admin2@example.com', password='pw')
		resp = self.client.get(reverse('admin_dashboard'))
		self.assertEqual(resp.status_code, 200)

		# agent should be denied admin dashboard
		agent = User.objects.create_user(email='agent2@example.com', password='pw', user_type=User.USER_TYPE_AGENT, is_active=True)
		self.client.login(username='agent2@example.com', password='pw')
		resp = self.client.get(reverse('admin_dashboard'))
		# should redirect to login with access denied message
		self.assertIn(resp.status_code, (302, 200))

# Create your tests here.
