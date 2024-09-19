from excel_response import ExcelResponse
from django.contrib import admin
from .models import SiteUser, Team
from django.contrib.auth.admin import UserAdmin


class UserAdminConfig(UserAdmin):
    def export_selected_users(self, request, queryset):
        data = []
        headers = ['Name', 'Email', 'Phone Number', 'Date Joined']
        data.append(headers)

        # Add user data to the worksheet
        for user in queryset:
            data.append([user.first_name, user.email, user.phone_number, user.start_date])

        return ExcelResponse(data=data, worksheet_name="Users", output_filename="users")

    def export_selected_services(self, request, queryset):
        data = []
        headers = ['Username / Email', 'Phone Number', 'Name', 'Talk / workshop']

        for user in queryset:
            for service in user.services.all():
                if service.payment_state == "CM":
                    event = service.talk or service.workshop
                    data.append([service.user.email, service.user.phone_number, service.user.first_name, event.title])

        data.sort(key=lambda x: x[3])
        data.insert(0, headers)
        return ExcelResponse(data=data, worksheet_name="Services", output_filename="services")

    def export_selected_online_participants(self, request, queryset):
        data = []
        headers = ['Username / Email', 'Phone Number', 'Name', 'Classes', 'Access']
        data.append(headers)

        for user in queryset:
            classes = ""
            for service in user.services.all():
                if service.payment_state == "CM" and service.service_type == "TK":
                    talk = service.talk
                    if talk and talk.is_online and talk.presentation_link:
                        classes += ',' + talk.presentation_link.split('/')[-1]

            if classes:
                data.append([user.email, user.phone_number, user.first_name, classes[1:], "normal"])

        return ExcelResponse(data=data, worksheet_name="Participants", output_filename="participants")

    actions = ['export_selected_users', 'export_selected_services', 'export_selected_online_participants']
    export_selected_users.short_description = 'Export selected site users'
    export_selected_services.short_description = "Export selected site users' services"
    export_selected_online_participants.short_description = "Export selected site users' online classes"

    # search by fields
    search_fields = (
        'email',
        'user_name',
        'first_name'
    )

    # order of fields
    ordering = ('-start_date',)

    # list display of user
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

    exclude = None
    fields = None

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("user_name", "password1", "password2"),
            },
        ),
    )

    # field set
    fieldsets = (
        (None, {'fields': ('email', 'user_name', 'first_name', 'password')}),
        ('permissions', {'fields': ('is_staff', 'is_active')}),
        ('personal', {'fields': ('phone_number', 'about', 'profile', 'favorite_game_title')}),
        ('team', {'fields': ('team', 'team_role')})
    )


class UserTeamInline(admin.TabularInline):
    model = SiteUser
    fields = ['email', 'first_name', 'team_role']


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            "fields": (
                'name'
                ,),
        }),
        (
            'register state', {
                'fields': (
                    'state', 'team_activation'
                )
            }
        )
    )
    list_display = ['id', 'name', 'state', 'member_count']
    actions_on_top = True
    list_filter = ['state']
    inlines = [
        UserTeamInline,
    ]


admin.site.register(SiteUser, UserAdminConfig)
