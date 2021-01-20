from django.db import models

from django.core.validators import RegexValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import(
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
    User
)

import logging
logger = logging.getLogger(__name__)



from core.models import (
    EventService
)

class PhoneValidator(RegexValidator):
    regex = r'^(\+98|0)?9\d{9}$'
    message = "Phone number must be entered in the format: '+98----------' or '09---------'."



class CustomAccountManager(BaseUserManager):

    def create_user(self, email , user_name , first_name , password, phone_number , **other_fieds):
        if not email:
            raise ValueError(_('you must provide an email address'))

        if not phone_number:
            raise ValueError(_('you must provide a phone number'))

        if not first_name:
            raise ValueError(_('you must provide a first name'))

        if not user_name:
            raise ValueError(_('you must provide a user name'))

        print(f'\nuser phone number is {phone_number}\n')
        email = self.normalize_email(email)
        user = self.model(email=email , user_name=user_name,first_name=first_name , phone_number=phone_number , **other_fieds)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email , user_name , first_name , password,phone_number , **other_fieds):
        other_fieds.setdefault('is_staff' , True)
        other_fieds.setdefault('is_superuser' , True)
        other_fieds.setdefault('is_active' , True)


        if other_fieds.get('is_staff') is not True:
            raise ValueError(_('Superuser must be assigned to is_staff=True.'))


        if other_fieds.get('is_superuser') is not True:
            raise ValueError(_('Superuser must be assigned to is_superuser=True.'))

        return self.create_user(email , user_name , first_name , password, phone_number, **other_fieds)





class SiteUser(AbstractBaseUser, PermissionsMixin):

    # default fields of user model
    email = models.EmailField(_("email address"), unique=True)
    user_name = models.CharField(_("user name") ,max_length=150, unique=True)
    first_name = models.CharField(_('first name'),max_length=150)
    start_date = models.DateTimeField(default=timezone.now)
    about = models.TextField(_('about'), max_length=500, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    
    # event informations
    phone_number = models.CharField(_("phone number"),validators=[PhoneValidator()], max_length=32 , blank=False,null=False)
    services = models.ForeignKey(EventService, on_delete=models.PROTECT , blank=True , null=True)

    objects = CustomAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('phone_number','first_name' , 'user_name')

    def __str__(self):
        return self.user_name


