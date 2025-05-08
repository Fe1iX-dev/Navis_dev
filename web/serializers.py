from rest_framework import serializers
from .models import Event, Services, Vacancy, Project, Contact, Review
import os

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'date', 'image', 'created_at']

class ServicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Services
        fields = ['id', 'title', 'content', 'image', 'created_at']

class VacancySerializer(serializers.ModelSerializer):
    class Meta:
        model = Vacancy
        fields = ['id', 'title', 'description', 'requirements', 'created_at']

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'image', 'created_at']

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'name', 'email', 'message', 'file', 'created_at']

    def validate_file(self, value):
        if value:
            ext = os.path.splitext(value.name)[1].lower()
            forbidden_extensions = ['.json', '.py', '.sh']
            if ext in forbidden_extensions:
                raise serializers.ValidationError("Files with .json, .py, or .sh extensions are not allowed.")
        return value

    file = serializers.FileField(required=False, allow_empty_file=False)

class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Review
        fields = ['id', 'author', 'text', 'rating', 'created_at']