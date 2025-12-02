from django.db import models
from django.urls import reverse #Used to generate URLs by reversing the URL patterns
from django.db.models import JSONField
from django.core.files.storage import FileSystemStorage

import uuid

# ------------------------------
# BICYCLES
# ------------------------------

class BicycleModel(models.Model):
    """Модель электровелосипеда"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    model_code = models.CharField(max_length=64, unique=True, help_text="", verbose_name="Код модели")
    name = models.CharField(max_length=255, help_text="", verbose_name="Название модели")
    manufacturer = models.CharField(max_length=255, help_text="", verbose_name="Производитель")
    
    weight_kg = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True, help_text="", verbose_name="Вес велосипеда (кг)")
    battery_wh = models.IntegerField(null=True, blank=True, help_text="", verbose_name="Мощность батареи (Вт/ч)")
    motor_w = models.IntegerField(null=True, blank=True, help_text="", verbose_name="Мощность велосипеда (Вт)")
    range_km_estimated = models.IntegerField(null=True, blank=True, help_text="", verbose_name="Запас хода (км)")
    created_at = models.DateTimeField(auto_now_add=True, help_text="", verbose_name="Дата создания")
    
    updated_at = models.DateTimeField(auto_now=True, help_text="", verbose_name="Дата обновления")

    class Meta:
        db_table = "bicycle_models"
        verbose_name = "Модель велосипеда"
        verbose_name_plural = "Модели велосипедов"
        

    def __str__(self):
        return self.name


class Bicycle(models.Model):
    """Конкретный велосипед"""
    STATUS_CHOICES = [
        ("AVAILABLE", "Доступен"),
        ("RESERVED", "Забронирован"),
        ("RENTED", "Арендован"),
        ("IN_REPAIR", "В ремонте"),
        ("DECOMMISSIONED", "Выведен из эксплуатации"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, help_text="", verbose_name="Идентификатор")
    model = models.ForeignKey(BicycleModel, on_delete=models.CASCADE, related_name="bicycles", help_text="", verbose_name="Модель")
    gps_tracker_id = models.CharField(max_length=64, default="", unique=True, help_text="", verbose_name="ID-трекера GPS")
    serial_number = models.CharField(max_length=128, null=True, blank=True, help_text="", verbose_name="Серийный номер")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="AVAILABLE", help_text="", verbose_name="Статус")
    production_year = models.SmallIntegerField(help_text="", null=True, blank=True, verbose_name="Год производства")
    current_battery_pct = models.SmallIntegerField(default=100, help_text="", null=True, blank=True, verbose_name="Износ батареи (%)") # TODO: validate 0-100
    last_maintenance_at = models.DateField(null=True, blank=True, help_text="", verbose_name="Дата последней ТО")
    last_status_change = models.DateTimeField(auto_now=True, help_text="", verbose_name="Последнее изменение статуса")
    created_at = models.DateTimeField(auto_now_add=True, help_text="", verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, help_text="", verbose_name="Дата изменения")

    class Meta:
        db_table = "bicycles"
        verbose_name = "Велосипед"
        verbose_name_plural = "Велосипеды"
        
    def __str__(self):
        return self.model.name + " - " + self.serial_number
    
    
    
class BicycleModelPhoto(models.Model):
   
    model = models.ForeignKey(BicycleModel, on_delete=models.CASCADE, related_name="bicycles_model_photos", help_text="", verbose_name="Модель")
   
    photo = models.ImageField(upload_to="bikes_model_photos", null=True, blank=True, help_text="", verbose_name="Фотография велосипеда")
   
    created_at = models.DateTimeField(auto_now_add=True, help_text="", verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, help_text="", verbose_name="Дата изменения")

    class Meta:
        db_table = "bicycles_model_photos"
        verbose_name = "Фотография велосипеда"
        verbose_name_plural = "Фотографии велосипеда"
        
    def __str__(self):
        return self.model.name
