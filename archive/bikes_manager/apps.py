from django.apps import AppConfig


class BikesManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bikes_manager'
    verbose_name = "Велосипеды"
    icon = 'fa-solid fa-bicycle'
    # divider_title = "Apps" 
    # priority = 0  
    # hide = False  
