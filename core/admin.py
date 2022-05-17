from django.contrib import admin
from .models import (
    Assistant,
    Workshop,
    Presenter,
    EventService,
    Talk,
    Payment,
    Coupon
)

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
                'first_name',"last_name",'linked_in','profile'
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
                'title','capacity','cost','level','presentation_link','content','files'
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
                'title','capacity','cost','level','presentation_link','content','files'
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
    readonly_fields = ['payment']
    list_display = ['user' , 'workshop' , 'talk','payment_state','service_type']
    actions_on_top = True
    list_filter = ['payment_state','service_type']
    search_fields = ['user__email']



    
@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    fields = (
        'name','count','percentage'
    )
    list_display = ['name' , 'count' , 'percentage']
    
    