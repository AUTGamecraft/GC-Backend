from django.db import models
from django.core.validators import RegexValidator


PAYMENT_STATES = [
    ('CM' , 'COMPLETED'),
    ('PN' , 'PENDING'),
    ('RJ' , 'REJECTED')
]

SERVICE_TYPE = [
    ('WS' , 'WORKSHOP'),
    ('TK'  , 'TALK')
]


class Presenter(models.Model):
    first_name = models.CharField(max_length=30,blank=False)
    last_name = models.CharField(max_length=30 , blank=False)
    email = models.EmailField(blank=True , null=True)
    descriptions = models.TextField()
    linked_in = models.URLField(blank=True)


    class Meta:
        unique_together = ('first_name' , 'last_name')

    def __str__(self):
        return f'{self.last_name} {self.first_name}'

class Talk(models.Model):
    title = models.CharField(max_length=100 , blank=False)
    date = models.DateTimeField(blank=False)
    content = models.TextField(blank=False)
    capacity = models.IntegerField(blank=False)
    participant_count = models.IntegerField()
    presenters = models.ForeignKey(Presenter, on_delete=models.PROTECT , null=True)
    presentation_link = models.URLField(blank=True)

    def __str__(self):
        return self.title


class Workshop(models.Model):
    title = models.CharField(max_length=100 , blank=False) 
    date = models.DateTimeField(blank=False)
    content = models.TextField(blank=False)
    capacity = models.IntegerField(blank=False)
    participant_count = models.IntegerField()
    presenters = models.ForeignKey(Presenter , on_delete=models.PROTECT , null=True)
    presentation_link = models.URLField(blank=True)

    def __str__(self):
        return self.title


class EventService(models.Model):
    payment_state = models.CharField(
        max_length=2,
        choices=PAYMENT_STATES,
        default='PN'
    )
    service = models.CharField(
        max_length=2,
        choices=SERVICE_TYPE,
        blank=False
    )
    talk = models.ForeignKey(Talk , blank=True , on_delete=models.CASCADE)
    Workshop = models.ForeignKey(Workshop , blank=True , on_delete=models.CASCADE)


