from datetime import timezone

import jdatetime
from dill import objects
from django.contrib import admin
from core.models import (
    Assistant,
    Workshop,
    Presenter,
    EventService,
    Talk,
    Payment,
    Coupon,
    PAYMENT_STATES
)
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from tasks.tasks import reminder_email_task

import tempfile
import zipfile
from django.http import HttpResponse, JsonResponse
import csv


class PresenterTalkInline(admin.TabularInline):
    model = Talk.presenters.through


class PresenterWorkshopInline(admin.TabularInline):
    model = Workshop.presenters.through


class WorkshopAssistantInline(admin.TabularInline):
    model = Workshop.assistants.through


@admin.register(Presenter)
class PresenterAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            "fields": (
                'first_name', "last_name", 'email', 'descriptions', 'linked_in', 'profile'
            ),
        }),
    )
    inlines = [
        PresenterTalkInline, PresenterWorkshopInline
    ]


@admin.register(Assistant)
class AssistantAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            "fields": (
                'first_name', "last_name", 'linked_in', 'profile', 'role'
            ),
        }),
    )
    inlines = [
        WorkshopAssistantInline,
    ]


def main_presenter(obj):
    if presenters := obj.presenters.all():
        return presenters[0]
    else:
        return "no presenters"


def send_reminder(services):
    if not services:
        return

    sample = services[0]
    presentation = sample.talk or sample.workshop
    date = presentation.start
    j_date = (jdatetime.datetime.utcfromtimestamp(date.timestamp())
              .aslocale(jdatetime.FA_LOCALE).
              strftime('%a, %d %b %Y (%H:%M)'))
    emails = [service.user.email for service in services]

    context = {
        'emails': emails,
        'title': presentation.title,
        'is_online': bool(presentation.is_online),
        'link': presentation.presentation_link,
        'date': j_date
    }
    reminder_email_task.delay(context)


@admin.register(Talk)
class TalkAdmin(admin.ModelAdmin):
    def send_reminder_emails(self, request, queryset):
        for event in queryset.all():
            services = []
            for service in EventService.objects.filter(talk_id=event.id):
                if service.payment_state == "CM":
                    services.append(service)

            send_reminder(services)

        return JsonResponse({"message": "Emails sent."})

    fieldsets = (
        ('Dates', {
            "fields": (
                ('start', 'end'),
            ),
        }),
        ('Details', {
            'fields': (
                'title', 'capacity', 'cost', 'level', 'is_online', 'presentation_link', 'content', 'files',
                'is_registration_active'
            ),
            'classes': ('wide', 'extrapretty'),

        })
    )
    inlines = [
        PresenterTalkInline
    ]

    actions = ['send_reminder_emails']
    send_reminder_emails.short_description = 'Send reminder emails'
    exclude = ['presenters']
    date_hierarchy = 'start'
    actions_on_top = True
    list_display = ('title', main_presenter, 'start', 'registered', 'capacity')
    search_fields = ['title']
    show_full_result_count = True


@admin.register(Workshop)
class WorkshopAdmin(admin.ModelAdmin):
    def send_reminder_emails(self, request, queryset):
        for event in queryset.all():
            services = []
            for service in EventService.objects.filter(workshop_id=event.id):
                if service.payment_state == "CM":
                    services.append(service)

            send_reminder(services)

        return JsonResponse({"message": "Emails sent."})

    fieldsets = (
        ('Dates', {
            "fields": (
                ('start', 'end'),
            ),
        }),
        ('Details', {
            'fields': (
                'title', 'capacity', 'cost', 'level', 'is_online', 'presentation_link', 'content', 'files',
                'is_registration_active'
            ),
            'classes': ('wide', 'extrapretty'),
        })
    )
    exclude = ['presenters']
    inlines = [
        PresenterWorkshopInline, WorkshopAssistantInline,
    ]

    actions = ['send_reminder_emails']
    send_reminder_emails.short_description = 'Send reminder emails'
    date_hierarchy = 'start'
    actions_on_top = True
    list_display = ('title', main_presenter, 'start', 'registered', 'capacity')
    show_full_result_count = True
    search_fields = ['title']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    fields = [
        'total_price'
        , 'status'
        , 'payment_id'
        , 'payment_link'
        , 'card_number'
        , 'hashed_card_number'
        , 'payment_trackID'
        , 'verify_trackID'
        , 'created_date'
        , 'finished_date'
        , 'verified_date'
        , 'original_data'
        , 'user'
        , 'coupon'
    ]
    actions = None

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        # Return nothing to make sure user can't update any data
        pass

    date_hierarchy = 'created_date'
    list_display = ['__str__', 'user', 'created_date', 'payment_state', 'total_price']
    actions_on_top = True
    list_filter = ['status']
    search_fields = ['user__email']


@admin.register(EventService)
class EventServiceAdmin(admin.ModelAdmin):
    fieldsets = (
        ('User', {
            "fields": (
                'user',
            ),
        }),
        (
            'State', {
                'fields': (
                    'payment_state',
                    'service_type'
                )
            }
        ),
        (
            'Services', {
                'fields': (
                    'workshop',
                    'talk',
                    'payment'
                )
            }
        )
    )
    readonly_fields = ['payment']
    list_display = ['user', 'workshop', 'talk', 'payment_state', 'service_type']
    actions_on_top = True
    list_filter = ['payment_state', 'service_type']
    search_fields = ['user__email']


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    fields = (
        'name', 'count', 'percentage'
    )
    list_display = ['name', 'count', 'percentage']
