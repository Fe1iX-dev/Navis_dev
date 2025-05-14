import os
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re
import phonenumbers


def validate_phone(value):
    cleaned_phone = re.sub(r'[^\d+]', '', value)

    try:
        parsed = phonenumbers.parse(cleaned_phone, None)

        if not phonenumbers.is_valid_number(parsed) or parsed.country_code != 996:
            raise ValidationError("Номер должен быть в формате +996 XXX XXX XXX")

    except phonenumbers.phonenumberutil.NumberParseException:
        raise ValidationError("Неверный формат номера. Используйте +996 XXX XXX XXX")

def validate_file(value):
    max_size = 5 * 1024 * 1024  # 5 МБ
    disallowed_extensions = ('.json', '.py', '.js', '.sh', '.bat', '.cmd')

    if value.size > max_size:
        raise ValidationError(f'Размер файла не должен превышать 5 МБ! Текущий размер: {value.size / 1024 / 1024:.2f} МБ')

    file_extension = os.path.splitext(value.name.lower())[1]
    if file_extension in disallowed_extensions:
        raise ValidationError('Недопустимый тип файла! Запрещены .json, .py, .js, .sh, .bat, .cmd.')


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(null=True, blank=True)
    message = models.TextField()
    file = models.FileField(upload_to='contacts/', null=True, blank=True, validators=[validate_file])
    phone = models.CharField(max_length=20, validators=[validate_phone], null=False, blank=False)  # Увеличим max_length
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        super().clean()
        if self.phone:
            cleaned_phone = re.sub(r'[^\d+]', '', self.phone)

            if cleaned_phone.startswith('0'):
                cleaned_phone = '+996' + cleaned_phone[1:]

            elif cleaned_phone.startswith('996'):
                cleaned_phone = '+' + cleaned_phone

            elif len(cleaned_phone) == 9 and cleaned_phone.isdigit():
                cleaned_phone = '+996' + cleaned_phone

            try:
                parsed = phonenumbers.parse(cleaned_phone, None)
                if not phonenumbers.is_valid_number(parsed) or parsed.country_code != 996:
                    raise ValidationError({'phone': "Номер должен быть в формате +996 XXX XXX XXX"})

                self.phone = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)

            except phonenumbers.phonenumberutil.NumberParseException:
                raise ValidationError({'phone': "Неверный формат номера. Используйте +996 XXX XXX XXX"})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Message from {self.name}"

class YouTubeShort(models.Model):
    title = models.CharField(max_length=200)
    video_url = models.URLField()
    thumbnail = models.ImageField(upload_to='youtube_shorts/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField(null=True, blank=True)  # Разрешаем NULL
    image = models.ImageField(upload_to='events/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    gallery = models.ManyToManyField('EventImage', related_name='events')

    def __str__(self):
        return self.title

class EventImage(models.Model):
    image = models.ImageField(upload_to='event_gallery/')
    event = models.ForeignKey(Event, related_name='gallery_images', on_delete=models.CASCADE)

    def __str__(self):
        return f"Image for {self.event.title}"

class Services(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='services/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Vacancy(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    requirements = models.TextField()
    conditions = models.TextField(blank=True)  # Новое поле
    salary = models.CharField(max_length=255, blank=True)  # Новое поле
    is_active = models.BooleanField(default=True)  # Новое поле
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Project(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='projects/', null=True, blank=True)
    link = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Review(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    rating = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.author.username}"

class About(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='about/', null=True, blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class TeamMember(models.Model):
    about = models.ForeignKey(About, related_name='team_members', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='team/')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Gallery(models.Model):
    title = models.CharField(max_length=200, blank=True, null=True)
    image = models.ImageField(upload_to='gallery/', null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    related_service = models.ForeignKey(Services, on_delete=models.SET_NULL, null=True, blank=True)
    related_project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Gallery Image - {self.title or 'No Title'}"


class Direction(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    image = models.ImageField(upload_to='directions/')
    additional_content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Comment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    text = models.TextField()