from django.contrib import admin
from .models import (
    Talk,
    Workshop
)


admin.site.register(Talk)
admin.site.register(Workshop)
