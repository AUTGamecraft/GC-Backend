from django.db import models
from django.core.validators import RegexValidator
from user.models import CustomUser

class PhoneValidator(RegexValidator):
    regex = r'^(\+98|0)?9\d{9}$'
    message = "Phone number must be entered in the format: '+9999'. Up to 30 digits allowed."


class Talk(models.Model):
    date = models.DateTimeField(blank=False)
    content = models.TextField(blank=False)
    capacity = models.IntegerField(blank=False)
    participant_count = models.IntegerField()


class Competition(models.Model):
    date = models.DateTimeField(blank=False)
    content = models.TextField(blank=False)
    capacity = models.IntegerField(blank=False)
    participant_count = models.IntegerField()


class Workshop(models.Model):
    date = models.DateTimeField(blank=False)
    content = models.TextField(blank=False)
    capacity = models.IntegerField(blank=False)
    participant_count = models.IntegerField()





class GDUser(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    phone_number = models.CharField(
        validators=[PhoneValidator()], max_length=32, blank=False)
    talks = models.ManyToManyField(Talk)
    competitions = models.ManyToManyField(Competition)
    workshops = models.ManyToManyField(Workshop)

    # def __str__(self):
    #     return self.user.user_name
