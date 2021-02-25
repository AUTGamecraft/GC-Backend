from django.contrib import admin
from .models import (
    Talk,
    Workshop,
    Presenter,
    EventService,
    CompetitionMember,
    Team,
    Payment,
    Coupon
)

class PresenterTalkInline(admin.TabularInline):
    model = Talk.presenters.through
    

class PresenterWorkshopInline(admin.TabularInline):
    model = Workshop.presenters.through
    
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
                'title','capacity','cost','level','presentation_link','content'
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
                'title','capacity','cost','level','presentation_link','content'
            ),
            'classes':('wide','extrapretty'),
        })
    )
    exclude = ['presenters']
    inlines = [
        PresenterWorkshopInline
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
    list_display = ['user' , 'created_date' , 'payment_state','total_price']
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
    list_display = ['user' , 'workshop' , 'talk','payment_state','service_type']
    actions_on_top = True
    list_filter = ['payment_state','service_type']


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            "fields": (
               'name' 
            ,),
        }),
        ('feedbacks',{
            'fields': (
                'like',
                'dislike'
            )
        }),
        ('Files' ,{
            'fields':(
                'video','game','profile'
            )
        }),
        (
            'register state' , {
                'fields':(
                    'state','team_activation'
                )
            }
        )
    )
    list_display = ['name' , 'state' , 'like','dislike']
    actions_on_top = True
    list_filter = ['state']

    
@admin.register(CompetitionMember)
class CompetitionMember(admin.ModelAdmin):
    fieldsets = (
        (None, {
            "fields": (
                'user','team'
            ),
        }),
        ('state' , {
            'fields':(
                'has_team',
                'is_head'
            )
        })
    )
    list_display = ['user' , 'team' , 'has_team']
    actions_on_top = True
    
    
@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    fields = (
        'name','count','percentage'
    )
    list_display = ['name' , 'count' , 'percentage']
    
    
# admin.site.register(Talk)
# admin.site.register(Workshop)
# admin.site.register(Presenter)
# admin.site.register(CompetitionMember)
# admin.site.register(Payment)