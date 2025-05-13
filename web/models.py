from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re


def validate_phone(value):

    cleaned_value = re.sub(r'[^0-9]', '', value)

    # Проверяем длину (должно быть 9 цифр после +996)
    if len(cleaned_value) != 9:
        raise ValidationError('Номер телефона должен содержать 9 цифр после кода страны (например, 708245676).')


    if value.startswith('0'):
        value = '+996' + cleaned_value[1:]
    elif not value.startswith('+996'):
        value = '+996' + cleaned_value

    return value

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(null=True, blank=True)
    message = models.TextField()
    file = models.FileField(upload_to='contacts/', null=True, blank=True)
    phone = models.CharField(max_length=13, validators=[validate_phone], null=False, blank=False)  # Сделали phone обязательным
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.phone:
            self.phone = validate_phone(self.phone)
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
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='events/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Services(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='services/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Vacancy(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    requirements = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='projects/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

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
    title = models.CharField()
    image = models.ImageField(upload_to='About/', null=True, blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Gallery(models.Model):
    title = models.CharField(max_length=200, blank=True, null=True)
    image = models.ImageField(upload_to='gallery/', null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    related_service = models.ForeignKey(Services, on_delete=models.SET_NULL, null=True, blank=True)
    related_project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Gallery Image - {self.title or 'No Title'}"
