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

import json
import tempfile
import zipfile
from django.http import HttpResponse
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
                'first_name',"last_name",'email','descriptions','linked_in','profile'
            ),
        }),
    )
    inlines = [
        PresenterTalkInline ,PresenterWorkshopInline
    ]

@admin.register(Assistant)
class AssistantAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            "fields": (
                'first_name',"last_name",'linked_in','profile','role'
            ),
        }),
    )
    inlines = [
        WorkshopAssistantInline,
    ]
    


@admin.register(Talk)
class TalkAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Dates', {
            "fields": (
                ('start' , 'end'),
            ),
        }),
        ('Details' , {
            'fields': (
                'title','capacity','cost','level','is_online','presentation_link','content','files','is_registration_active'
            ),
            'classes':('wide','extrapretty'),
            
        })
    )
    inlines = [
        PresenterTalkInline
    ]
    exclude = ['presenters']
    date_hierarchy = 'start'
    actions_on_top = True
    list_display = ('title','start' , 'end','registered','capacity')
    search_fields = ['title']
    show_full_result_count = True
    
@admin.register(Workshop)
class WorkshopAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Dates', {
            "fields": (
                ('start' , 'end'),
            ),
        }),
        ('Details' , {
            'fields': (
                'title','capacity','cost','level','is_online','presentation_link','content','files','is_registration_active'
            ),
            'classes':('wide','extrapretty'),
        })
    )
    exclude = ['presenters']
    inlines = [
        PresenterWorkshopInline, WorkshopAssistantInline,
    ]
    date_hierarchy = 'start'
    actions_on_top = True
    list_display = ('title','start' , 'end','registered','capacity')
    show_full_result_count = True
    search_fields = ['title']
    

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    fields = [
        'total_price'
        ,'status'
        ,'payment_id'
        ,'payment_link'
        ,'card_number'
        ,'hashed_card_number'
        ,'payment_trackID'
        ,'verify_trackID'
        ,'created_date'
        ,'finished_date'
        ,'verified_date'
        ,'original_data'
        ,'user'
        ,'coupon'
    ]
    actions = None

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        #Return nothing to make sure user can't update any data
        pass
    date_hierarchy = 'created_date'
    list_display = ['__str__','user' , 'created_date' , 'payment_state','total_price']
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
            'Services' ,{
                'fields' : (
                    'workshop',
                    'talk',
                    'payment'
                )
            }
        )
    )
    actions = ['download_talk_export_csv', 'download_workshops_export_csv']
    readonly_fields = ['payment']
    list_display = ['user' , 'workshop' , 'talk','payment_state','service_type']
    actions_on_top = True
    list_filter = ['payment_state','service_type']
    search_fields = ['user__email']
    
    
    def changelist_view(self, request, extra_context=None):
        if 'action' in request.POST and (request.POST['action'] == 'download_talk_export_csv' or request.POST['action'] == 'download_workshops_export_csv'):
            if not request.POST.getlist(ACTION_CHECKBOX_NAME):
                post = request.POST.copy()
                es =  EventService.objects.all()[0]
                post.update({ACTION_CHECKBOX_NAME: str(es.id)})
                
                request._set_post(post)
        return super(EventServiceAdmin, self).changelist_view(request, extra_context)
    
    def download_talk_export_csv(modeladmin, request, queryset):
        events = Talk.objects.all()
        
        with tempfile.SpooledTemporaryFile() as zip_tmp:
            with zipfile.ZipFile(zip_tmp, 'w', zipfile.ZIP_DEFLATED) as archive:
                register_records = None
                for event in events:
                    
                    register_records = EventService.objects.filter(talk=event, payment_state=PAYMENT_STATES[0][0])
                        
                    data = [
                        {
                            'full_name':record.user.first_name,
                            'email':record.user.email,
                            'phone_number': record.user.phone_number
                        }
                        for record in register_records
                    ]

                    fileNameInZip = f'event_export_{event.title}.csv'
                    
                    keys = data[0].keys()
                    with tempfile.NamedTemporaryFile(mode="w+") as temp_csv:
                        dict_writer = csv.DictWriter(temp_csv, keys)
                        dict_writer.writeheader()
                        dict_writer.writerows(data)
                        temp_csv.flush()
                        temp_csv.seek(0)
                        
                        archive.writestr(fileNameInZip, temp_csv.read())

                archive.close()
                
                zip_tmp.seek(0)
                response = HttpResponse(zip_tmp.read(), content_type='application/x-zip-compressed')
                response['Content-Disposition'] = 'attachment; filename="talk_exports.zip"'
                return response
            

    def download_workshops_export_csv(modeladmin, request, queryset):
        events = Workshop.objects.all()
        
        with tempfile.SpooledTemporaryFile() as zip_tmp:
            with zipfile.ZipFile(zip_tmp, 'w', zipfile.ZIP_DEFLATED) as archive:
                register_records = None
                for event in events:
                    
                    register_records = EventService.objects.filter(workshop=event, payment_state=PAYMENT_STATES[0][0])
                        
                    data = [
                        {
                            'full_name':record.user.first_name,
                            'email':record.user.email,
                            'phone_number': record.user.phone_number
                        }
                        for record in register_records
                    ]

                    fileNameInZip = f'event_export_{event.title}.csv'
                    
                    keys = data[0].keys()
                    with tempfile.NamedTemporaryFile(mode="w+") as temp_csv:
                        dict_writer = csv.DictWriter(temp_csv, keys)
                        dict_writer.writeheader()
                        dict_writer.writerows(data)
                        temp_csv.flush()
                        temp_csv.seek(0)
                        
                        archive.writestr(fileNameInZip, temp_csv.read())

                archive.close()
                
                zip_tmp.seek(0)
                response = HttpResponse(zip_tmp.read(), content_type='application/x-zip-compressed')
                response['Content-Disposition'] = 'attachment; filename="workshop_exports.zip"'
                return response


    
@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    fields = (
        'name','count','percentage'
    )
    list_display = ['name' , 'count' , 'percentage']
    
    
    