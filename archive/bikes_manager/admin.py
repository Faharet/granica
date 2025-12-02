from django.contrib import admin
from django.utils.html import format_html

from .models import Bicycle, BicycleModel, BicycleModelPhoto

class BicycleModelPhotoInline(admin.TabularInline):
    model = BicycleModelPhoto
    fields = ('photo',)   # Добавляем превью в форму
    extra = 1  # Количество пустых строк для добавления

class BicycleModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'preview_photo', 'model_code', 'manufacturer')
    list_filter = ('model_code', 'name', 'manufacturer')
    search_fields = ('model_code', 'name', 'manufacturer')
    
    inlines = [BicycleModelPhotoInline]
    
    def preview_photo(self, obj):
        """Превью первой фотографии в списке моделей"""
        try:
            photo = obj.bicycles_model_photos.first()
            if photo and photo.photo:
                return format_html(
                    '<img src="{}" style="max-height: 100px; max-width: 100px;"/>',
                    photo.photo.url
                )
        except Exception:
            pass
        return "Нет фото"
    preview_photo.short_description = "Фотография"
    preview_photo.allow_tags = True
    
    fieldsets = (
        (None, {
            'fields': ('model_code', 'name', 'manufacturer')
        }),
        ('Характеристики', {
            'fields': (('weight_kg', 'battery_wh'),
                       ('range_km_estimated', 'motor_w'))
        }),
    )

class BicycleAdmin(admin.ModelAdmin):
    list_display = ('model', 'gps_tracker_id', 'status', "last_status_change",'production_year')
    list_filter = ('model', 'status')
    search_fields = ('model', 'gps_tracker_id', 'status', 'production_year')


admin.site.register(BicycleModel, BicycleModelAdmin)
admin.site.register(Bicycle, BicycleAdmin)
