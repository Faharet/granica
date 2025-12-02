"""
Original rent_manager.models moved to archive/rent_manager/models.py
"""

# file archived; see archive/rent_manager/models.py
from django.db import models

import uuid

from bikes_manager.models import Bicycle, BicycleModel
from platform_manager.models import AdminUser, User
from django.db.models import JSONField

# ------------------------------
# CONTRACTS
# ------------------------------

class Contract(models.Model):
    STATUS_CHOICES = [
        ("DRAFT", "Не подписан"),
        ("ACTIVE", "Подписан"),
        ("CANCELLED", "Расторгнут"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, help_text="", verbose_name="Идентификатор")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="contracts", help_text="", verbose_name="Пользователь")
    contract_number = models.CharField(max_length=64, unique=True, help_text="", verbose_name="Номер договора")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="DRAFT", help_text="", verbose_name="Статус")
    start_date = models.DateField(help_text="", verbose_name="Дата вступления в силу")
    created_at = models.DateTimeField(auto_now_add=True, help_text="", verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, help_text="", verbose_name="Дата изменения")

    class Meta:
        db_table = "contracts"
        constraints = []
        verbose_name = "Договор"
        verbose_name_plural = "Договоры"

class Booking(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Ожидание"),
        ("CONFIRMED", "Обработано"),
        ("CANCELLED", "Отменено"),
        ("EXPIRED", "Истекло"),
        ("CLOSED", "Закрыто")
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, help_text="", verbose_name="Идентификатор")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings", help_text="", verbose_name="Пользователь")
    bicycle_model = models.ForeignKey(BicycleModel, null=True, blank=True, on_delete=models.SET_NULL, help_text="", verbose_name="Модель велосипеда")
    bicycle = models.ForeignKey(Bicycle, null=True, blank=True, on_delete=models.SET_NULL, help_text="", verbose_name="Велосипед")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="PENDING", help_text="", verbose_name="Статус")
    requested_start = models.DateTimeField(help_text="", verbose_name="Дата начала брони")
    requested_end = models.DateTimeField(help_text="", verbose_name="Дата окончания брони")

    user_comment_text = models.TextField(blank=True, editable=False, help_text="", verbose_name="Комментарий пользователя")
    manager_comment_text = models.TextField(blank=True, help_text="", verbose_name="Комментарий")

    created_at = models.DateTimeField(auto_now_add=True, help_text="", verbose_name="Дата создания")

    class Meta:
        db_table = "bookings"
        indexes = [models.Index(fields=["status"])]
        verbose_name = "Бронь"
        verbose_name_plural = "Бронирование"


class Rental(models.Model):
    STATUS_CHOICES = [
        ("INITIATED", "Создана"),
        ("ACTIVE", "Активно"),
        ("COMPLETED", "Завершено"),
        ("OVERDUE", "Просрочено"),
        ("CANCELLED", "Отменено"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, help_text="", verbose_name="Идентификатор")

    user = models.ForeignKey(User, on_delete=models.CASCADE, help_text="", verbose_name="Пользователь")
    contract = models.ForeignKey(Contract, null=True, blank=True, on_delete=models.SET_NULL, help_text="", verbose_name="Договор")
    bicycle = models.ForeignKey(Bicycle, on_delete=models.CASCADE, help_text="", verbose_name="Велосипед")
    booking = models.ForeignKey(Booking, null=True, blank=True, on_delete=models.SET_NULL, help_text="", verbose_name="Бронирование")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="INITIATED", help_text="", verbose_name="Статус")
    start_at = models.DateTimeField(help_text="", verbose_name="Дата начала аренды")
    scheduled_end_at = models.DateTimeField(help_text="", verbose_name="Дата запланированного окончания аренды")
    actual_end_at = models.DateTimeField(null=True, blank=True, help_text="", verbose_name="Фактическая дата окончания аренды")
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="", verbose_name="Сумма депозита")

    penalty_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="", verbose_name="Сумма удержания")
    overdue_notified_at = models.DateTimeField(null=True, blank=True, help_text="", verbose_name="Дата уведомления о просрочке")
    overdue_reason = models.TextField(blank=True, help_text="", verbose_name="Причина просрочки")
    created_at = models.DateTimeField(auto_now_add=True, help_text="", verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, help_text="", verbose_name="Дата изменения")

    class Meta:
        db_table = "rentals"
        verbose_name = "Аренда"
        verbose_name_plural = "Аренды"


# ------------------------------
# PAYMENTS
# ------------------------------

class Transaction(models.Model):
    TYPE_CHOICES = [
        ("PAYMENT", "Payment"),
        ("REFUND", "Refund"),
        ("DEPOSIT", "Deposit"),
        ("PENALTY", "Penalty"),
    ]
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
        ("REVERSED", "Reversed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, help_text="", verbose_name="Идентификатор")
    user = models.ForeignKey(User, on_delete=models.CASCADE, help_text="", verbose_name="Пользователь")
    rental = models.ForeignKey(Rental, null=True, blank=True, on_delete=models.SET_NULL, help_text="", verbose_name="Аренда")
    booking = models.ForeignKey(Booking, null=True, blank=True, on_delete=models.SET_NULL, help_text="", verbose_name="Бронирование")
    amount = models.DecimalField(max_digits=12, decimal_places=2, help_text="", verbose_name="Сумма транзакции")
    currency = models.CharField(max_length=8, default="KZT", editable=False, help_text="", verbose_name="Валюта")
    type = models.CharField(max_length=16, choices=TYPE_CHOICES, editable=False, help_text="", verbose_name="Тип транзакции")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, editable=False, default="PENDING", help_text="", verbose_name="Статус")

    metadata = JSONField(default=dict, blank=True, verbose_name="Метаданные")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата изменения")

    class Meta:
        db_table = "transactions"
        constraints = []
        verbose_name = "Транзакция"
        verbose_name_plural = "Транзакции"

class Invoice(models.Model):
    """Чек об оплате"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name="Идентификатор")
    transaction = models.OneToOneField(Transaction, editable=False, on_delete=models.CASCADE, verbose_name="Транзакция")
    invoice_number = models.CharField(max_length=64, editable=False, unique=True, verbose_name="номер чека")
    issued_at = models.DateTimeField(auto_now_add=True, editable=False, verbose_name="Выдано")
    pdf_url = models.TextField(blank=True, help_text="", verbose_name="Ссылка на чек")
    data_json = JSONField(default=dict, help_text="", verbose_name="Данные чека")

    class Meta:
        db_table = "invoices"
        verbose_name = "Чек об оплате"
        verbose_name_plural = "Чеки об оплатах"



class RentalEndReport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, help_text="", verbose_name="Идентификатор")
    rental = models.OneToOneField(Rental, on_delete=models.CASCADE, related_name="end_report", help_text="", verbose_name="Аренда")
    created_by_admin = models.ForeignKey(AdminUser, null=True, blank=True, on_delete=models.SET_NULL, help_text="", verbose_name="Ответственный менеджер")
    condition_notes = models.TextField(blank=True, help_text="", verbose_name="Комментарий")
    rating = models.SmallIntegerField(default=5, help_text="", verbose_name="Рейтинг состояния велосипеда (1-5)")

    resolved = models.BooleanField(default=True, help_text="", verbose_name="Завершено")

    created_at = models.DateTimeField(auto_now_add=True, help_text="", verbose_name="Дата создания")

    class Meta:
        db_table = "rental_end_reports"
        verbose_name = "Отчёт об окончании аренды"
        verbose_name_plural = "Отчёты окончания аренды"

class PenaltyReason(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, help_text="", verbose_name="Идентификатор")

    title = models.CharField(max_length=255, help_text="", verbose_name="Заголовок")
    description = models.TextField(blank=True, help_text="", verbose_name="Описание")
    default_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="", verbose_name="Сумма штрафа")
    requires_photo = models.BooleanField(default=False, help_text="", verbose_name="Завершено")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "penalty_reasons"
        verbose_name = "Причина штрафа"
        verbose_name_plural = "Причины штрафов"

class ReportPenalty(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(RentalEndReport, on_delete=models.CASCADE, related_name="penalties")
    penalty_reason = models.ForeignKey(PenaltyReason, on_delete=models.CASCADE)
    amount_applied = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "report_penalties"
        verbose_name = "Отчёт штрафа"
        verbose_name_plural = "Отчёты штрафов"

class ReportPenaltyPhoto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report_penalty = models.ForeignKey(ReportPenalty, on_delete=models.CASCADE, related_name="photos")
    photo_url = models.TextField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "report_penalty_photos"
        verbose_name = "Фото штрафа"
        verbose_name_plural = "Фотографии штрафов"