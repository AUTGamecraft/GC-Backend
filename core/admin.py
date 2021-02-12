from django.contrib import admin
from .models import (
    Talk,
    Workshop,
    Presenter,
    EventService,
    CompetitionMember,
    Team,
    Payment
)


admin.site.register(Talk)
admin.site.register(Workshop)
admin.site.register(EventService)
admin.site.register(Presenter)
admin.site.register(Team)
admin.site.register(CompetitionMember)
admin.site.register(Payment)