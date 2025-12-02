from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from .models import User, Profile, AdminUser, NotificationTemplate, EventLog, FormResponse
from django.utils.safestring import mark_safe

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['email', 'phone', 'first_name', 'last_name', 'is_staff']
    search_fields = ['email', 'phone', 'first_name', 'last_name']
    
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Персональная информация", {"fields": (("first_name", "last_name",),( "email", "phone"))}),
        (
            "Права и группы",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Даты", {"fields": (("last_login", "date_joined"), ())}),
    )


class ProfileAdmin(admin.ModelAdmin):
    list_display = ["full_name", "face_preview", 'gender', 'birthdate', "phone", "city"]
    search_fields = ['first_name', "last_name", 'gender', 'birthdate', "phone", "id_number", "city",  ]
    list_filter = ('gender', "city")

    readonly_fields = ["face_preview", "full_name"]

    def face_preview(self, obj):
        return mark_safe(f'<img src="{obj.user_face_photo.url}" style="max-width: auto; max-height: 100px;">')

    face_preview.short_description = "Фотография пользователя"
    face_preview.allow_tags = True

    # def id_front_preview(self, obj):
    #     return mark_safe(f'<img src="{obj.id_front_photo.url}" style="max-width: auto">')

    # id_front_preview.short_description = "Фотография удостоверения личности (лицевая сторона)"
    # id_front_preview.allow_tags = True

    # def id_back_preview(self, obj):
    #     return mark_safe(f'<img src="{obj.id_back_photo.url}" style="max-width: auto">')

    # id_back_preview.short_description = "Фотография удостоверения личности (задняя сторона)"
    # id_back_preview.allow_tags = True


    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    full_name.short_description = "Полное имя"
    full_name.allow_tags = True

    fieldsets = (
        (None, {
            'fields': (("user_face_photo"), ('first_name', 'last_name', 'third_name'), ('gender', 'birthdate'), ('email', 'phone'))
        }),
        ('Адреса', {
            'fields': (('city'),
                       ('registration_address'),
                       ('address'),)
        }),
        ('Удостоверение личности', {
            'fields': (('id_number', 'id_outstand'),
                       ('id_front_photo','id_back_photo'),)
        }),
        ('Доверенный контакт', {
            'fields': (('trusted_contact_name', 'relation'),
                       ('trusted_contact_phone'))
        }),
        ('Дополнительная информация', {
            'fields': ('preferred_locale', 'manager_comment')
        }),
    )

# class UserAdmin(User):
#     """Administration object for Book models.
#     Defines:
#      - fields to be displayed in list view (list_display)
#      - adds inline addition of book instances in book view (inlines)
#     """
#     list_display = ('first_name', 'last_name', 'phone', 'email', 'is_staff', 'is_active')

admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(AdminUser)
admin.site.register(NotificationTemplate)  
admin.site.register(EventLog)  
admin.site.register(FormResponse)


# Allow adding/removing users directly from Group admin page
try:
    UserModel = get_user_model()

    class UserInline(admin.TabularInline):
        model = UserModel.groups.through
        extra = 1

    class CustomGroupAdmin(admin.ModelAdmin):
        inlines = [UserInline]

    # Unregister default Group admin and register our custom one
    admin.site.unregister(Group)
    admin.site.register(Group, CustomGroupAdmin)
except Exception:
    # If anything goes wrong (e.g., migrations not applied), ignore — groups can still be assigned via User admin
    pass

