from django.apps import AppConfig


class RentManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rent_manager'
    verbose_name = "Аренды и оплаты"
    icon = 'fa-solid fa-comments-dollar'
