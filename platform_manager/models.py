import os
import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db.models import JSONField
from django.urls import reverse
# from phone_field import PhoneField
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.safestring import mark_safe
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils import timezone



# ------------------------------
# USER & PROFILE
# ------------------------------

class UserManager(BaseUserManager):
    def create_user(self, email, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError("The Phone field must be set")
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, phone, password, **extra_fields)

class User(AbstractUser):
    """
    Основной пользователь системы.
    Расширяет стандартного пользователя Django (email, пароль, и т.п.)
    """
    username_validator = UnicodeUsernameValidator()

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(
        verbose_name="Имя пользователя",
        max_length=50,
        unique=True,
        help_text="Обязательное поле. До 50 символов. Буквы, цифры и @/./+/-/_ символы.",
        validators=[username_validator],
        error_messages={
            "unique": "Заданное имя пользователя уже существует.",
        },
    )
    
    email = models.EmailField(unique=True, help_text="", verbose_name="Email")
    phone = PhoneNumberField(unique=True, help_text="Номер телефона указывается в международной форме", verbose_name="Номер телефона")
    
    first_name = models.CharField(max_length=30, blank=True, help_text="", verbose_name="Имя")
    last_name = models.CharField(max_length=30, blank=True, help_text="", verbose_name="Фамилия")

    is_staff = models.BooleanField(
        "Сотрудник",
        default=False,
    )
    is_active = models.BooleanField(
        "Активен",
        default=True,
    )
    
    
    is_superuser = models.BooleanField(
        "Администратор",
        default=False,
    )
    
    date_joined = models.DateTimeField("Дата создания", default=timezone.now)
    last_login = models.DateTimeField("Последний вход", blank=True, null=True)

    objects = UserManager()

    REQUIRED_FIELDS = ["email", 'phone', 'first_name', 'last_name']

    def __str__(self):
        return '{} {} - {}'.format (self.first_name, self.last_name, self.phone)

    class Meta:
        db_table = "users"
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


def profile_id_image_upload_path(instance, filename):
    ext = filename.split('.')[-1]

    if instance.pk:
        filename = f'profile_id_photo_{instance.pk} - {uuid.uuid4().hex}.{ext}'
    else:
        filename = f'profile_id_photo_{uuid.uuid4().hex}.{ext}'

    return os.path.join('profile_id_photos', filename)

def profile_face_image_upload_path(instance, filename):
    ext = filename.split('.')[-1]

    if instance.pk:
        filename = f'profile_face_photo_{instance.pk} - {uuid.uuid4().hex}.{ext}'
    else:
        filename = f'profile_face_photo_{uuid.uuid4().hex}.{ext}'

    return os.path.join('profile_face_photos', filename)

class Profile(models.Model):
    """Персональные данные и документы пользователя"""
    GENDER_CHOICES = [
        ("MALE", "Мужской"),
        ("FEMALE", "Женский")
    ]
    
    CITY_CHOICES = [
        ("ALMATY", "Алматы")
    ]
    
    PREFERRED_LANGUAGE_CHOICES = [
        ("RUS", "Русский"),
        ("KAZ", "Казахский"),
        ("ENG", "Английский"),
        ("UZB", "Узбекский"),
        ("KRG", "Киргизкий"),
        ("OTHER", "Другой"),
    ]
    
    RELATION_CHOICES = [
        ("SPOUSE", "Супруг(а)"),
        ("SIBLING", "Брат/Сестра"),
        ("PARENT", "Родитель"),
        ("OTHER", "Другое")
    ]
    
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, help_text="", verbose_name="Идентификатор")
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name="profile", help_text="", verbose_name="Пользователь")
    first_name = models.CharField(max_length=255, help_text="", verbose_name="Имя")
    last_name = models.CharField(max_length=255, help_text="", verbose_name="Фамилия")
    third_name = models.CharField(max_length=255, null=True, blank=True, help_text="", verbose_name="Отчество")
    gender = models.CharField(blank=True, choices=GENDER_CHOICES, default="MALE", help_text="", verbose_name="Пол")
    
    email = models.EmailField(unique=True, help_text="", verbose_name="Email")
    phone = PhoneNumberField(unique=True, help_text="Номер телефона указывается в международной форме", verbose_name="Номер телефона")
    
    birthdate = models.DateField(null=True, blank=True, help_text="", verbose_name="Дата рождения")
    
    id_number = models.CharField(max_length=40, help_text="", verbose_name="Номер удостоверения личности")
    id_outstand = models.CharField(max_length=255, help_text="", verbose_name="Кем выдано удостоверение личности")

    city = models.CharField(blank=True, choices=CITY_CHOICES, default="ALMATY", help_text="", verbose_name="Город")
    registration_address = models.CharField(max_length=255, blank=True, help_text="", verbose_name="Адрес прописки")
    address = models.CharField(max_length=255, blank=True, help_text="", verbose_name="Адрес проживания")
    
    id_front_photo = models.ImageField(upload_to=profile_id_image_upload_path, null=True, blank=True, help_text="", verbose_name="Фотография удостоверения (лицевая сторона)")
    id_back_photo = models.ImageField(upload_to=profile_id_image_upload_path, null=True, blank=True, help_text="", verbose_name="Фотография удостоверения (задняя сторона)")
    
    user_face_photo = models.ImageField(upload_to=profile_face_image_upload_path, null=True, blank=True, help_text="", verbose_name="Фотография пользователя")
    
    trusted_contact_name = models.CharField(max_length=255, help_text="", verbose_name="Имя доверенного лица")
    relation = models.CharField(choices=RELATION_CHOICES, blank=True, help_text="", verbose_name="Кем приходится")

    trusted_contact_phone = PhoneNumberField(help_text="Номер телефона указывается в международной форме", verbose_name="Номер телефона доверенного лица")

    preferred_locale = models.CharField(max_length=8, blank=True, help_text="", choices=PREFERRED_LANGUAGE_CHOICES, default="RUS", verbose_name="Предпочитаемый язык")
    
    manager_comment = models.TextField(null=True, blank=True, help_text="", verbose_name="Комментарий менеджера")
    
    created_at = models.DateTimeField(auto_now_add=True, help_text="", verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, help_text="", verbose_name="Дата изменения")


    # readonly_fields = ["preview"]

    # def preview(self, obj):
    #     return mark_safe(f'<img src="{obj.user_face_photo.url}">')

    def get_absolute_url(self):
        return reverse('profile-detail', args=[str(self.id)])

    def __str__(self):
        return '%s %s' % (self.last_name, self.first_name)

    class Meta:
        db_table = "profiles"
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

class NotificationTemplate(models.Model):
    CHANNEL_CHOICES = [
        ("EMAIL", "Email"),
        ("WHATSAPP", "WhatsApp"),
        ("PUSH", "Push"),
        ("SMS", "SMS"),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, help_text="", verbose_name="Идентификатор")
    name = models.CharField(max_length=255, help_text="", verbose_name="Имя шаблона")
    channel = models.CharField(max_length=16, choices=CHANNEL_CHOICES, help_text="", verbose_name="Канал связи")
    body_template = models.TextField(help_text="", verbose_name="Шаблон сообщения")
    placeholders = JSONField(default=dict, help_text="", verbose_name="Заголовок сообщения")
    is_active = models.BooleanField(default=True, help_text="", verbose_name="Активно")
    created_at = models.DateTimeField(auto_now_add=True, help_text="", verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, help_text="", verbose_name="Дата редактирования")

    class Meta:
        db_table = "notification_templates"
        verbose_name = "Шаблон уведомлений"
        verbose_name_plural = "Шаблоны уведомлений"

class AdminUser(models.Model):
    ROLE_CHOICES = [
        ("SUPERADMIN", "Superadmin"),
        ("OPERATOR", "Operator"),
        ("SUPPORT", "Support"),
        ("MAINTENANCE", "Maintenance"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, help_text="", verbose_name="Идентификатор")
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, help_text="", verbose_name="Пользователь")
    role = models.CharField(max_length=32, choices=ROLE_CHOICES, help_text="", verbose_name="Роль")
    permissions = JSONField(default=dict, blank=True, help_text="", verbose_name="Права доступа")
    last_login = models.DateTimeField(null=True, blank=True, help_text="", verbose_name="Последний вход")
    created_at = models.DateTimeField(auto_now_add=True, help_text="", verbose_name="Создано")

    class Meta:
        db_table = "admin_users"
        verbose_name = "Администратор"
        verbose_name_plural = "Администраторы"
        

class EventLog(models.Model):
    EVENT_TYPES = [
        ("NOTIFICATION", "Отправка уведомления"),
        ("AUDIT", "Аудит"),
        ("SYSTEM", "Система"),
        ("PAYMENT", "оплата"),
        ("GEOZONE", "Гео Зона"),
        ("OTHER", "Другое"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, help_text="", verbose_name="Идентификатор")
    event_type = models.CharField(max_length=64, choices=EVENT_TYPES, help_text="", verbose_name="Тип события")
    severity = models.CharField(max_length=16, default="INFO", help_text="", verbose_name="Уровень")
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, help_text="", verbose_name="Пользователь")
    admin_user = models.ForeignKey(AdminUser, null=True, blank=True, on_delete=models.SET_NULL, help_text="", verbose_name="Адмнинистратор")
    payload = JSONField(default=dict, blank=True, help_text="", verbose_name="Данные")
    occurred_at = models.DateTimeField(auto_now_add=True, help_text="", verbose_name="Дата-время")

    class Meta:
        db_table = "event_logs"
        indexes = [models.Index(fields=["event_type", "-occurred_at"])]
        verbose_name = "Событие"
        verbose_name_plural = "События"


class FormResponse(models.Model):
    """Form response storing the questionnaire requested by the user.

    Fields correspond to the numbered questions in the questionnaire. Many
    answers are stored as free-text so complex multi-part answers can be
    captured. Boolean flags indicate yes/no questions for conditional parts.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, help_text="", verbose_name="Идентификатор")

    # 1. Biographical: full name, date and place of birth
    full_name_and_birth = models.TextField(blank=True, verbose_name="ФИО, дата и место рождения")

    # 2. Name changes
    name_changed = models.BooleanField(default=False, verbose_name="Изменяли ли имя/фамилию/отчество")
    name_change_reason = models.TextField(blank=True, verbose_name="Причина изменения имени")

    # 3. Phones and emails
    phones_emails = models.TextField(blank=True, verbose_name="Номера телефонов и email")

    # 4. Military service
    military_service = models.BooleanField(default=False, verbose_name="Проходили ли службу в ВС")
    military_details = models.TextField(blank=True, verbose_name="Детали службы (страна/войска)")

    # 5. Criminal record
    criminal_record = models.BooleanField(default=False, verbose_name="Имеете ли судимость")
    criminal_period_where = models.TextField(blank=True, verbose_name="Период и место отбытия наказания")
    criminal_offenses = models.TextField(blank=True, verbose_name="За какие преступления")

    # 6. Detained by foreign law enforcement
    detained_abroad = models.BooleanField(default=False, verbose_name="Задерживались ли правоохранительными органами иностранного государства")
    detained_when_why = models.TextField(blank=True, verbose_name="Когда и по какой причине задерживали")
    detained_where = models.TextField(blank=True, verbose_name="Где содержали")

    # 7. Relatives/friends in specific countries
    relatives_in_countries = models.BooleanField(default=False, verbose_name="Есть ли родственники/знакомые в указанных странах")
    relatives_details = models.TextField(blank=True, verbose_name="Детали (ФИО, когда выехали, чем занимаются)")

    # 8. Relatives wanted by authorities
    relatives_wanted = models.BooleanField(default=False, verbose_name="Разыскивается ли кто-нибудь из родственников")
    relatives_wanted_reason = models.TextField(blank=True, verbose_name="Причина розыска")

    # 9. Religion
    religious = models.BooleanField(default=False, verbose_name="Религиозны ли вы")
    denomination = models.CharField(max_length=255, blank=True, verbose_name="Мазхаб/религиозные взгляды")

    # 10. Visits to listed countries
    visited_countries = models.BooleanField(default=False, verbose_name="Посещали ли указанные страны")
    visited_countries_details = models.TextField(blank=True, verbose_name="Детали визитов (когда, цель, срок)")

    # 11. Deportation
    deported = models.BooleanField(default=False, verbose_name="Депортировали/выдворяли ли вас")
    deportation_details = models.TextField(blank=True, verbose_name="Когда и причины депортации")

    # 12. Not admitted to destination country
    not_allowed_reason = models.TextField(blank=True, verbose_name="Причина не пропуска в пункт назначения")

    # 13. Last time in homeland
    last_time_in_homeland = models.CharField(max_length=255, blank=True, verbose_name="Когда в последний раз были на родине")

    # Basic metadata
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='form_responses', verbose_name="Пользователь")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    # Scoring system
    total_score = models.IntegerField(default=0, verbose_name="Общий балл")
    threat_level = models.CharField(max_length=20, blank=True, verbose_name="Уровень опасности")

    class Meta:
        db_table = "form_responses"
        verbose_name = "Ответ на форму"
        verbose_name_plural = "Ответы на форму"

    def calculate_score(self):
        """Calculate threat score based on questionnaire responses."""
        score = 0
        
        # Criteria based on provided scoring table
        # Note: Some criteria need manual review by border officer
        
        if self.criminal_record:
            score += 10  # Criterion 9: Criminal element
            
        if self.detained_abroad:
            score += 20  # Criterion 3: Issues in documents/history
            
        if self.deported:
            score += 20  # Criterion 3: Deportation
            
        if self.visited_countries:
            score += 20  # Criterion 3: Travel to listed countries
            
        if self.relatives_wanted:
            score += 10  # Criterion 8: Relatives with MTO connections
            
        if self.religious:
            score += 15  # Criterion 4: Religious inclinations
            
        # Update total score
        self.total_score = score
        
        # Determine threat level
        if score >= 60:
            self.threat_level = "Высокий"
        elif score >= 30:
            self.threat_level = "Средний"
        else:
            self.threat_level = "Низкий"
            
        return score

    def __str__(self):
        name = self.full_name_and_birth.split(',')[0] if self.full_name_and_birth else "Неизвестно"
        return f"{name} ({self.created_at:%Y-%m-%d %H:%M}) - {self.threat_level} ({self.total_score} баллов)"


class BorderOfficerAssessment(models.Model):
    """Border officer's assessment based on scoring criteria"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form_response = models.OneToOneField(FormResponse, on_delete=models.CASCADE, related_name='officer_assessment', verbose_name="Ответ на форму")
    
    # 1. Радикальные интернет-сообщества (65 баллов)
    radical_internet = models.BooleanField(default=False, verbose_name="1. Состоит в радикальных интернет-сообществах")
    radical_internet_details = models.TextField(blank=True, verbose_name="Детали")
    
    # 2. Религиозная идеология - сторонник радикальных течений (45 баллов)
    radical_religious_ideology = models.BooleanField(default=False, verbose_name="2. Является сторонником радикальных религиозных течений")
    radical_religious_details = models.TextField(blank=True, verbose_name="Детали")
    
    # 3. Признаки в документах (20 баллов)
    document_issues = models.BooleanField(default=False, verbose_name="3. Признаки в документах (депортация, запрет въезда)")
    document_issues_details = models.TextField(blank=True, verbose_name="Детали")
    
    # 4. Религия - отклонения (15 баллов)
    religious_deviations = models.BooleanField(default=False, verbose_name="4. Религиозные отклонения/неопределенность")
    religious_deviations_details = models.TextField(blank=True, verbose_name="Детали")
    
    # 5. Мобильные устройства - сомнительный контент (15 баллов)
    suspicious_mobile_content = models.BooleanField(default=False, verbose_name="5. Сомнительный контент на мобильных устройствах")
    suspicious_mobile_details = models.TextField(blank=True, verbose_name="Детали")
    
    # 6. Поведение - религиозные термины, агрессия (15 баллов)
    suspicious_behavior = models.BooleanField(default=False, verbose_name="6. Подозрительное поведение (религиозные термины, агрессия)")
    suspicious_behavior_details = models.TextField(blank=True, verbose_name="Детали")
    
    # 7. Психологические отклонения (15 баллов)
    psychological_issues = models.BooleanField(default=False, verbose_name="7. Психологические отклонения")
    psychological_details = models.TextField(blank=True, verbose_name="Детали")
    
    # 8. Родственники с МТО связями (10 баллов)
    relatives_mto = models.BooleanField(default=False, verbose_name="8. Родственники с близкими связями с МТО")
    relatives_mto_details = models.TextField(blank=True, verbose_name="Детали")
    
    # 9. Криминально-ориентированный элемент (10 баллов)
    criminal_element = models.BooleanField(default=False, verbose_name="9. Криминально-ориентированный элемент")
    criminal_element_details = models.TextField(blank=True, verbose_name="Детали")
    
    # 10. Следы насильственных действий на теле (10 баллов)
    violence_traces = models.BooleanField(default=False, verbose_name="10. Следы насильственных действий на теле")
    violence_traces_details = models.TextField(blank=True, verbose_name="Детали")
    
    # Scoring
    total_score = models.IntegerField(default=0, verbose_name="Общий балл")
    threat_level = models.CharField(max_length=20, blank=True, verbose_name="Уровень опасности")
    
    # Metadata
    assessed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assessments', verbose_name="Оценил")
    assessed_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата оценки")
    notes = models.TextField(blank=True, verbose_name="Дополнительные заметки")
    
    class Meta:
        db_table = "border_officer_assessments"
        verbose_name = "Оценка пограничника"
        verbose_name_plural = "Оценки пограничника"
    
    def calculate_score(self):
        """Calculate threat score based on officer's assessment"""
        score = 0
        
        if self.radical_internet:
            score += 65
        if self.radical_religious_ideology:
            score += 45
        if self.document_issues:
            score += 20
        if self.religious_deviations:
            score += 15
        if self.suspicious_mobile_content:
            score += 15
        if self.suspicious_behavior:
            score += 15
        if self.psychological_issues:
            score += 15
        if self.relatives_mto:
            score += 10
        if self.criminal_element:
            score += 10
        if self.violence_traces:
            score += 10
        
        self.total_score = score
        
        # Determine threat level
        if score >= 60:
            self.threat_level = "Высокий"
        elif score >= 30:
            self.threat_level = "Средний"
        else:
            self.threat_level = "Низкий"
        
        return score
    
    def __str__(self):
        return f"Оценка для {self.form_response} - {self.threat_level} ({self.total_score} баллов)"