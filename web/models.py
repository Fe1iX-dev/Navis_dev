from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re
import os
import phonenumbers
from ckeditor.fields import RichTextField
from django.utils.translation import gettext_lazy as _


def validate_phone(value):
    pattern = r'^\+996\d{9}$'
    if not re.fullmatch(pattern, value):
        raise ValidationError("Номер должен быть в формате +996XXXXXXXXX (9 цифр после +996)")


def validate_file(value):
    max_size = 5 * 1024 * 1024  # 5 МБ
    disallowed_extensions = ('.json', '.py', '.js', '.sh', '.bat', '.cmd')

    if value.size > max_size:
        raise ValidationError(f'Размер файла не должен превышать 5 МБ! Текущий размер: {value.size / 1024 / 1024:.2f} МБ')

    file_extension = os.path.splitext(value.name.lower())[1]
    if file_extension in disallowed_extensions:
        raise ValidationError('Недопустимый тип файла! Запрещены .json, .py, .js, .sh, .bat, .cmd.')


def normalize_kg_phone(phone: str) -> str:
    cleaned = re.sub(r'[^\d+]', '', phone)

    if cleaned.startswith('+996'):
        return cleaned
    elif cleaned.startswith('996'):
        return '+' + cleaned
    elif cleaned.startswith('0') and len(cleaned) >= 10:
        return '+996' + cleaned[1:]
    elif cleaned.startswith('7') and len(cleaned) == 9:
        return '+996' + cleaned
    else:
        raise ValidationError("Неверный формат номера. Используйте +996 XXX XXX XXX")


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(null=False, blank=False)
    message = models.TextField()
    file = models.FileField(upload_to='contacts/', null=True, blank=True, validators=[validate_file])
    phone = models.CharField(max_length=20, validators=[], null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Заявка")
        verbose_name_plural = _("Заявки")

    def clean(self):
        super().clean()
        if self.phone:
            try:
                normalized_phone = normalize_kg_phone(self.phone)

                parsed = phonenumbers.parse(normalized_phone, None)
                if not phonenumbers.is_valid_number(parsed) or parsed.country_code != 996:
                    raise ValidationError({'phone': "Неверный кыргызский номер. Ожидается +996 XXX XXX XXX"})

                self.phone = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)

            except phonenumbers.NumberParseException:
                raise ValidationError({'phone': "Неверный формат номера. Используйте +996 XXX XXX XXX"})
            except ValidationError as e:
                raise e

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Message from {self.name}"

class YouTubeShort(models.Model):
    video_url = models.URLField()
    thumbnail = models.ImageField(upload_to='youtube_shorts/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Ютуб-Шортс")
        verbose_name_plural = _("Ютуб-Шортсы")

    def __str__(self):
        return self.title

class Event(models.Model):
    content = RichTextField(default='', blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField(null=True, blank=True)  # Разрешаем NULL
    image = models.ImageField(upload_to='events/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    gallery = models.ManyToManyField('EventImage', related_name='events')

    class Meta:
        verbose_name = _("Мероприятие")
        verbose_name_plural = _("Мероприятия")

    def __str__(self):
        return self.title

class EventImage(models.Model):
    content = RichTextField(default='', blank=True)
    image = models.ImageField(upload_to='event_gallery/')
    event = models.ForeignKey(Event, related_name='gallery_images', on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Фото мероприятия")
        verbose_name_plural = _("Фото мероприятий")

    def __str__(self):
        return f"Image for {self.event.title}"

class Services(models.Model):
    content = RichTextField(default='', blank=True)
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='services/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Услуга")
        verbose_name_plural = _("Услуги")

    def __str__(self):
        return self.title

class Vacancy(models.Model):
    content = RichTextField(default='', blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    requirements = models.TextField()
    conditions = models.TextField(blank=True)
    salary = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Вакансия")
        verbose_name_plural = _("Вакансии")

    def __str__(self):
        return self.title

class Project(models.Model):
    content = RichTextField(default='', blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='projects/', null=True, blank=True)
    link = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_featured = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Проект")
        verbose_name_plural = _("Проекты")

    def __str__(self):
        return self.title


class Review(models.Model):
    content = RichTextField(default='', blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    avatar = models.ImageField(upload_to='reviews/avatars/', null=True, blank=True)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Отзыв")
        verbose_name_plural = _("Отзывы")

    def __str__(self):
        return f"Review by {self.author.username if self.author else 'Anonymous'}"


class About(models.Model):
    content = RichTextField(default='', blank=True)
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='about/', null=True, blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("О нас")
        verbose_name_plural = _("О нас")

    def __str__(self):
        return self.title

class Gallery(models.Model):
    content = RichTextField(default='', blank=True)
    title = models.CharField(max_length=200, blank=True, null=True)
    image = models.ImageField(upload_to='gallery/', null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    related_service = models.ForeignKey(Services, on_delete=models.SET_NULL, null=True, blank=True)
    related_project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Галерея")
        verbose_name_plural = _("Галерея")

    def __str__(self):
        return f"Gallery Image - {self.title or 'No Title'}"

class Tools(models.Model):
    content = RichTextField(default='', blank=True)
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='tools/')
    additional_content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Инструменты")
        verbose_name_plural = _("Инструменты")

    def __str__(self):
        return self.name

class ToolImage(models.Model):
    content = RichTextField(default='', blank=True)
    tool = models.ForeignKey(Tools, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='tool_images/')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Фото инструментов")
        verbose_name_plural = _("Фото инструментов")

    def __str__(self):
        return f"Image for {self.tool.name}"


class ContactVacancy(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(null=False, blank=False)
    phone = models.CharField(max_length=20, validators=[], null=False, blank=False)
    link = models.URLField(null=False, blank=False)
    file = models.FileField(upload_to='contacts/vacancy/', null=True, blank=True, validators=[validate_file])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Заявка вакансии")
        verbose_name_plural = _("Заявки вакансий")

    def clean(self):
        super().clean()
        if self.phone:
            try:
                normalized_phone = normalize_kg_phone(self.phone)

                parsed = phonenumbers.parse(normalized_phone, None)
                if not phonenumbers.is_valid_number(parsed) or parsed.country_code != 996:
                    raise ValidationError({'phone': "Неверный кыргызский номер. Ожидается +996 XXX XXX XXX"})

                self.phone = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)

            except phonenumbers.NumberParseException:
                raise ValidationError({'phone': "Неверный формат номера. Используйте +996 XXX XXX XXX"})
            except ValidationError as e:
                raise e

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Message from {self.name}"

