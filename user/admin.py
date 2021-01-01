from django.contrib import admin
from .models import CustomUser
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
        'email',
        'user_name',
        'first_name',
        'is_active',
        'is_staff'
    )


    # field set 
    fieldsets = (
        (None , {'fields' : ('email','user_name','first_name')}),
        ('permissions' , {'fields' : ('is_staff','is_active')}),
        ('personal',{'fields':('about',)})
    )


admin.site.register(CustomUser , UserAdminConfig)
