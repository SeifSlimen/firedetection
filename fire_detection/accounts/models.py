from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class CustomUserManager(BaseUserManager):
	"""Custom user manager where email is the unique identifiers
	for authentication instead of usernames.

	We implement _create_user, create_user and create_superuser so
	Django's createsuperuser and other utilities work correctly.
	"""

	use_in_migrations = True

	def _create_user(self, email, password, **extra_fields):
		if not email:
			raise ValueError('The given email must be set')
		email = self.normalize_email(email)
		user = self.model(email=email, **extra_fields)
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_user(self, email, password=None, **extra_fields):
		extra_fields.setdefault('is_staff', False)
		extra_fields.setdefault('is_superuser', False)
		return self._create_user(email, password, **extra_fields)

	def create_superuser(self, email, password, **extra_fields):
		extra_fields.setdefault('is_staff', True)
		extra_fields.setdefault('is_superuser', True)

		if extra_fields.get('is_staff') is not True:
			raise ValueError('Superuser must have is_staff=True.')
		if extra_fields.get('is_superuser') is not True:
			raise ValueError('Superuser must have is_superuser=True.')

		return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
	"""A custom user model that uses email instead of username and
	includes a `user_type` field for role-based redirects/permissions.

	Notes:
	- We remove the default `username` field (set to None) and make
	  `email` the `USERNAME_FIELD`.
	- `user_type` is a simple CharField with choices. For more complex
	  authorization you can replace it with a separate Role model or
	  Django groups/permissions.
	"""

	username = None
	email = models.EmailField('email address', unique=True)

	USER_TYPE_ADMIN = 'admin'
	USER_TYPE_SUPERVISOR = 'supervisor'
	USER_TYPE_AGENT = 'agent'
	USER_TYPE_CHOICES = [
		(USER_TYPE_ADMIN, 'Admin'),
		(USER_TYPE_SUPERVISOR, 'Supervisor'),
		(USER_TYPE_AGENT, 'Agent'),
	]

	user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default=USER_TYPE_AGENT)

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = []  # email is required by USERNAME_FIELD

	objects = CustomUserManager()

	def __str__(self):
		return f"{self.email} ({self.user_type})"
