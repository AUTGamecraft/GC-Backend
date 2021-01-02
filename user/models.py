from django.db import models


from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import(
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
    User
)

class CustomAccountManager(BaseUserManager):

    def create_user(self, email , user_name , first_name , password,  **other_fieds):
        if not email:
            raise ValueError(_('you must provide an email address'))
        
        email = self.normalize_email(email)
        user = self.model(email=email , user_name=user_name,
            first_name=first_name , **other_fieds)
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, email , user_name , first_name , password,  **other_fieds):
        other_fieds.setdefault('is_staff' , True)
        other_fieds.setdefault('is_superuser' , True)
        other_fieds.setdefault('is_active' , True)

        if other_fieds.get('is_staff') is not True:
            raise ValueError(_('Superuser must be assigned to is_staff=True.'))


        if other_fieds.get('is_superuser') is not True:
            raise ValueError(_('Superuser must be assigned to is_superuser=True.'))

        return self.create_user(email , user_name , first_name , password,  **other_fieds)





class SiteUser(AbstractBaseUser, PermissionsMixin):

    # default fields of user model
    email = models.EmailField(_("email address"), unique=True)
    user_name = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150)
    start_date = models.DateTimeField(default=timezone.now)
    about = models.TextField(_('about'), max_length=500, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    objects = CustomAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['user_name','first_name']

    def __str__(self):
        return self.user_name


