from core.models import *
from django.db import models

from django.core.validators import RegexValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from random import choice
import logging

logger = logging.getLogger(__name__)

DEFAULT_AVATARS = [
    'default/avatar-1.png',
    'default/avatar-2.png',
    'default/avatar-3.png',
]

TEAM_STATE = [
    ('AC', 'ACTIVATED'),
    ('RE', 'REQUESTED'),
    ('RJ', 'REJECTED'),
]

TEAM_MEMBER_ROLE = [
    ('HE', 'HEAD'),
    ('ME', 'MEMBER'),
    ('NO', 'NOTEAM')
]


class PhoneValidator(RegexValidator):
    regex = r'^(\+98|0)?9\d{9}$'
    message = "Phone number must be entered in the format: '+98----------' or '09---------'."


class Team(models.Model):
    name = models.CharField(max_length=30, blank=False,
                            null=False, unique=True)
    state = models.CharField(
        max_length=2,
        choices=TEAM_STATE,
        default='RE'
    )
    profile = models.ImageField(
        verbose_name='team_profile', null=True, blank=True)
    team_activation = models.CharField(max_length=40, null=True, blank=True, unique=True)

    def get_payment_state(self):
        for member in self.members.all():
            args = {'user': member, 'competition': SingletonCompetition.get_solo(),
                    'service_type': 'CP', 'payment_state': 'CM'}
            query = EventService.objects.filter(**args)
            if query.exists():
                return "COMPLETED"
            else:
                return "PENDING"

    def member_count(self):
        return self.members.count()

    def __str__(self):
        return self.name


class CustomAccountManager(BaseUserManager):

    def create_user(self, email, user_name, first_name, password, phone_number, **other_fieds):
        if not email:
            raise ValueError(_('you must provide an email address'))

        if not phone_number:
            raise ValueError(_('you must provide a phone number'))

        if not first_name:
            raise ValueError(_('you must provide a first name'))

        if not user_name:
            raise ValueError(_('you must provide a user name'))

        email = self.normalize_email(email)
        user = self.model(email=email, user_name=user_name, first_name=first_name, phone_number=phone_number,
                          **other_fieds)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, user_name, first_name, password, phone_number, **other_fieds):
        other_fieds.setdefault('is_staff', True)
        other_fieds.setdefault('is_superuser', True)
        other_fieds.setdefault('is_active', True)

        if other_fieds.get('is_staff') is not True:
            raise ValueError(_('Superuser must be assigned to is_staff=True.'))

        if other_fieds.get('is_superuser') is not True:
            raise ValueError(_('Superuser must be assigned to is_superuser=True.'))

        return self.create_user(email, user_name, first_name, password, phone_number, **other_fieds)


class SiteUser(AbstractBaseUser, PermissionsMixin):
    # default fields of user model
    email = models.EmailField(_("email address"), unique=True)
    user_name = models.CharField(_("user name"), max_length=150, unique=True)
    first_name = models.CharField(_('first name'), max_length=150)
    start_date = models.DateTimeField(default=timezone.now)
    about = models.TextField(_('about'), max_length=500, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    profile = models.ImageField(verbose_name='user_profile', null=True, blank=True)
    activation_code = models.CharField(max_length=64, blank=True)
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
    team_role = models.CharField(choices=TEAM_MEMBER_ROLE, default='NO', max_length=2)
    favorite_game_title = models.CharField(max_length=50, blank=True)
    # event information
    phone_number = models.CharField(_("phone number"), validators=[PhoneValidator()], max_length=32, blank=False,
                                    null=False)

    objects = CustomAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('phone_number', 'first_name', 'user_name')

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if not self.profile:
            self.profile = choice(DEFAULT_AVATARS)
        if self.email:
            self.email = self.email.lower()
        super(SiteUser, self).save(*args, **kwargs)
