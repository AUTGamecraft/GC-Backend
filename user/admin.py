from django.contrib import admin
from .models import SiteUser , Team
from django.contrib.auth.admin import UserAdmin


class UserAdminConfig(UserAdmin):
    
    # search by fields
    search_fields = (
        'email',
        'user_name',
        'first_name'
    )
    
    # order of fields
    ordering  = ('-start_date',)
    
    
    # list disply of user 
    list_display = (
        'email',
        'user_name',
        'first_name',
        'is_active',
        'is_staff'
    )


    # filter by
    list_filter = (
        'is_active',
        'is_staff'
    )


    # field set 
    fieldsets = (
        (None , {'fields' : ('email','user_name','first_name','password')}),
        ('permissions' , {'fields' : ('is_staff','is_active')}),
        ('personal',{'fields':('phone_number','about','profile')}),
        ('team' , {'fields':('team' , 'team_role')})
    )
    add_fieldsets = (
        (None , {'fields' : ('email','user_name','first_name','password')}),
        ('permissions' , {'fields' : ('is_staff','is_active')}),
        ('personal',{'fields':('phone_number','about','profile')}),
        ('team' , {'fields':('team' , 'team_role')})
        
    )

class UserTeamInline(admin.TabularInline):
    model = SiteUser
    fields = ['email','first_name' , 'team_role']

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
    list_display = ['name' , 'state' , 'member_count' ,'like','dislike']
    actions_on_top = True
    list_filter = ['state']
    inlines = [
        UserTeamInline,
    ]



admin.site.register(SiteUser , UserAdminConfig)
