from django.db import models
from rest_framework.exceptions import ValidationError
from datetime import datetime
from GD.settings.base import AUTH_USER_MODEL, PAYWALL
from .validators import validate_file_extension
from tinymce.models import HTMLField

IDPAY_STATUS = [
    (1, 'payment_not_made'),
    (2, 'payment_failed'),
    (3, 'error'),
    (4, 'blocked'),
    (5, 'return_to_payer'),
    (6, 'system_reversal'),
    (7, 'cancel_payment'),
    (8, 'moved_to_payment_gateway'),
    (10, 'awaiting_payment_verification'),
    (100, 'payment_is_approved'),
    (101, 'payment_is_approved'),
    (200, 'was_deposited'),
    (201, 'payment_created'),
    (405, "error")

]
PAYPING_CODES = [
    (200, "OK"),
    (201, "NOT_VERIFIED"),
    (202, "VERIFICATION_NOT_DONE"),
    (400, "Client Error"),
    (500, "Server Error"),
    (503, "503 Service Unavailable"),
    (401, "Authentication Error"),
    (403, "403 Forbidden"),
    (404, "404 Not Found"),
]

PAYMENT_STATES = [
    ('CM', 'COMPLETED'),
    ('PN', 'PENDING'),
    ('RJ', 'REJECTED')
]

SERVICE_TYPE = [
    ('WS', 'WORKSHOP'),
    ('TK', 'TALK'),
]

LEVEL = [
    ('BG', 'BEGINNER'),
    ('IM', 'INTERMEDIATE'),
    ('EX', 'EXPERT')
]

MAX_FILE_SIZE = 1024 * 1024 * 400  # 400MB


class Presenter(models.Model):
    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=30, blank=False)
    email = models.EmailField(blank=True, null=True)
    descriptions = HTMLField(null=True, blank=True)
    linked_in = models.URLField(blank=True, null=True)
    profile = models.ImageField(
        verbose_name='presenter_profile', null=True, blank=True)

    class Meta:
        unique_together = ('first_name', 'last_name')

    def __str__(self):
        return f'{self.last_name} {self.first_name}'


class Assistant(models.Model):
    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=30, blank=False)
    role = models.TextField(null=False, blank=False)
    linked_in = models.URLField(blank=True, null=True)
    profile = models.ImageField(
        verbose_name='assistant_profile', null=True, blank=True)

    def __str__(self):
        return f'{self.last_name} {self.first_name} - id={self.pk}'


class Talk(models.Model):
    title = models.CharField(max_length=100, blank=False)
    start = models.DateTimeField(blank=False)
    end = models.DateTimeField(blank=False)
    content = HTMLField(blank=False)
    capacity = models.IntegerField(blank=False)
    is_online = models.BooleanField(default=True)
    presentation_link = models.URLField(blank=True)
    level = models.CharField(choices=LEVEL, default='BG', max_length=2)
    cost = models.FloatField(blank=False, default=0)
    presenters = models.ManyToManyField(Presenter, related_name='talks')
    files = models.URLField(default=None, blank=True, null=True)

    def clean(self):
        if self.cost < 0:
            raise ValidationError("cost cann't be a negative number.")
        if self.start > self.end:
            raise ValidationError("end of the service can not be before beginning")

    def get_total_services(self):
        return self.services.count()

    def get_services(self):
        return self.services.all()

    def get_remain_capacity(self):
        registered_user = self.services.filter(payment_state='CM').count()
        return self.capacity - int(registered_user)

    def registered(self):
        return int(self.services.filter(payment_state='CM').count())

    def __str__(self):
        return self.title


class Workshop(models.Model):
    title = models.CharField(max_length=100, blank=False)
    start = models.DateTimeField(blank=False)
    end = models.DateTimeField(blank=False)
    content = HTMLField(blank=False)
    capacity = models.IntegerField(blank=False)
    is_online = models.BooleanField(default=True)
    presentation_link = models.URLField(blank=True)
    level = models.CharField(choices=LEVEL, default='BG', max_length=2)
    cost = models.FloatField(blank=False, default=0)
    presenters = models.ManyToManyField(Presenter, related_name='workshops')
    assistants = models.ManyToManyField(Assistant, related_name='workshops')
    files = models.URLField(default=None, blank=True, null=True)

    def clean(self):
        if self.cost < 0:
            raise ValidationError("cost cann't be a negative number.")
        if self.start > self.end:
            raise ValidationError("end of the service can not be before beginning")

    def get_total_services(self):
        return self.services.count()

    def get_services(self):
        return self.services.all()

    def get_remain_capacity(self):
        registered_user = self.services.filter(payment_state='CM').count()
        return self.capacity - int(registered_user)

    def registered(self):
        return int(self.services.filter(payment_state='CM').count())

    def __str__(self):
        return self.title


class Coupon(models.Model):
    name = models.CharField(max_length=50, primary_key=True, help_text="don't use / in the name!!!")
    count = models.PositiveIntegerField(null=False, blank=False)
    percentage = models.FloatField(default=0.0, help_text='Enter a number between 0 to 100 !!!')

    def __str__(self):
        return self.name

    def clean(self):
        if self.percentage < 0 or self.percentage > 100:
            raise ValidationError("i said between 0 to 100 !!!")


class Payment(models.Model):
    total_price = models.PositiveIntegerField()
    status = models.IntegerField(choices=IDPAY_STATUS if PAYWALL == 'idapy' else PAYPING_CODES, default=201)
    payment_id = models.CharField(null=True, max_length=42)
    payment_link = models.TextField(null=True)
    card_number = models.CharField(null=True, max_length=16)
    hashed_card_number = models.TextField(null=True)
    payment_trackID = models.CharField(null=True, max_length=20)
    verify_trackID = models.CharField(null=True, max_length=20)
    created_date = models.DateTimeField(null=True)
    finished_date = models.DateTimeField(null=True)
    verified_date = models.DateTimeField(null=True)
    original_data = models.TextField(null=True)
    user = models.ForeignKey(
        AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    coupon = models.ForeignKey(
        Coupon, on_delete=models.SET_NULL, default=None, null=True
    )

    def payment_state(self):
        return self.get_status_display()

    def __str__(self):
        return f"{self.pk}"


class EventService(models.Model):
    payment_state = models.CharField(
        max_length=2,
        choices=PAYMENT_STATES,
        default='PN'
    )
    service_type = models.CharField(
        max_length=2,
        choices=SERVICE_TYPE,
        blank=False
    )

    payment = models.ForeignKey(
        Payment, null=True, blank=True, on_delete=models.SET_NULL, related_name='services')

    talk = models.ForeignKey(
        Talk, blank=True, on_delete=models.CASCADE, related_name='services', null=True)
    workshop = models.ForeignKey(
        Workshop, blank=True, on_delete=models.CASCADE, related_name='services', null=True)
    user = models.ForeignKey(
        AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, related_name='services', null=True)

    def clean(self):
        if self.service_type == 'WS':
            if self.workshop == None or self.talk != None:
                raise ValidationError(
                    'service type must match with selected service!!!')
        if self.service_type == 'TK':
            if self.talk == None or self.workshop != None:
                raise ValidationError(
                    'service type must match with selected service!!!')

    def __str__(self):
        return str(self.user.user_name) + '__' + str(self.service_type) + '__' + str(self.pk)
