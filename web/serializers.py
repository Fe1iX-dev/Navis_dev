from rest_framework import serializers
from .models import (
    Event, Services, Vacancy, Project, Contact,
    Review, YouTubeShort, About, Gallery, Tools
)


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'


class ServicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Services
        fields = '__all__'


class VacancySerializer(serializers.ModelSerializer):
    class Meta:
        model = Vacancy
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'


class YouTubeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = YouTubeShort
        fields = '__all__'


class AboutSerializer(serializers.ModelSerializer):
    class Meta:
        model = About
        fields = '__all__'


class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = '__all__'


class ToolsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tools
        fields = '__all__'


