from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from .models import User, Profile, AdminUser, NotificationTemplate, EventLog, FormResponse, BorderOfficerAssessment
from django.utils.safestring import mark_safe
from django.utils.html import format_html

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


class BorderOfficerAssessmentInline(admin.StackedInline):
    model = BorderOfficerAssessment
    extra = 0
    can_delete = True
    readonly_fields = ['assessed_by', 'assessed_at', 'total_score']
    fieldsets = (
        ('Оценка пограничника', {
            'fields': (
                'question_14', 'question_15', 'question_16', 'question_17',
                'question_18', 'question_19', 'question_20', 'question_21',
                'question_22', 'question_23', 'total_score', 'assessed_by', 'assessed_at'
            )
        }),
    )


@admin.register(FormResponse)
class FormResponseAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'get_country_display', 'threat_level_badge', 'total_score', 'created_by', 'created_at']
    list_filter = ['threat_level', 'created_at', 'birth_place']
    search_fields = ['last_name', 'first_name', 'patronymic', 'full_name_and_birth', 'id']
    readonly_fields = ['id', 'created_at', 'total_score', 'threat_level']
    date_hierarchy = 'created_at'
    inlines = [BorderOfficerAssessmentInline]
    actions = ['delete_selected_responses']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('id', 'last_name', 'first_name', 'patronymic', 'birth_date', 'birth_place')
        }),
        ('Фотографии', {
            'fields': ('full_name_photo', 'name_changed_documents')
        }),
        ('Вопросы 2-13', {
            'fields': (
                'name_changed', 'military_service', 'criminal_record', 'detained_abroad',
                'relatives_in_countries', 'radical_internet_content', 'radical_internet_sheikhs',
                'radical_religious_signs', 'document_issues', 'document_issues_types',
                'religious_deviations', 'religious_deviations_types', 'suspicious_mobile',
                'suspicious_mobile_types', 'suspicious_behavior', 'suspicious_behavior_types',
                'psychological_issues', 'psychological_types', 'relatives_mto',
                'relatives_mto_types', 'criminal_element', 'criminal_element_types',
                'violence_traces', 'violence_traces_types'
            ),
            'classes': ('collapse',)
        }),
        ('Оценка и метаданные', {
            'fields': ('total_score', 'threat_level', 'created_by', 'created_at')
        }),
    )
    
    def get_full_name(self, obj):
        if obj.last_name or obj.first_name:
            return f"{obj.last_name} {obj.first_name} {obj.patronymic}".strip()
        return obj.full_name_and_birth[:50] if obj.full_name_and_birth else "—"
    get_full_name.short_description = 'ФИО'
    
    def get_country_display(self, obj):
        if obj.birth_place and '|' in obj.birth_place:
            country_name, country_code = obj.birth_place.split('|')
            return format_html(
                '<img src="https://flagcdn.com/w40/{}.png" style="width: 20px; height: auto; border-radius: 2px; vertical-align: middle; margin-right: 5px;"> {}',
                country_code.lower(), country_name
            )
        return obj.birth_place or "—"
    get_country_display.short_description = 'Страна'
    
    def threat_level_badge(self, obj):
        colors = {
            'Низкий': '#36d399',
            'Средний': '#fbbd23', 
            'Высокий': '#f87272'
        }
        color = colors.get(obj.threat_level, '#gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color, obj.threat_level
        )
    threat_level_badge.short_description = 'Уровень угрозы'
    
    def delete_selected_responses(self, request, queryset):
        """Custom action for deleting selected responses with confirmation"""
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'Удалено записей: {count}')
    delete_selected_responses.short_description = 'Удалить выбранные ответы'
    
    def has_delete_permission(self, request, obj=None):
        """Only superusers and staff can delete"""
        return request.user.is_superuser or request.user.is_staff


admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(AdminUser)
admin.site.register(NotificationTemplate)  
admin.site.register(EventLog)


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

