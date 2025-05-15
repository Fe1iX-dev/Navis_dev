from rest_framework import serializers
from .models import Event, Services, Vacancy, Project, Contact, Review, YouTubeShort, About, Gallery, TeamMember, \
    Tools, EventImage, Comment


class EventImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventImage
        fields = ['id', 'image']

class EventSerializer(serializers.ModelSerializer):
    gallery = EventImageSerializer(many=True, read_only=True)
    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'date', 'image', 'gallery', 'created_at']

class ServicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Services
        fields = ['id', 'title', 'content', 'image', 'created_at']

class VacancySerializer(serializers.ModelSerializer):
    class Meta:
        model = Vacancy
        fields = ['id', 'title', 'description', 'requirements', 'conditions', 'salary', 'is_active', 'created_at']

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'image', 'link', 'created_at']

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'name', 'email', 'message', 'file', 'phone', 'created_at']

class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Review
        fields = ['id', 'author', 'avatar', 'text', 'rating', 'created_at']

class YouTubeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = YouTubeShort
        fields = ['id', 'title', 'video_url', 'thumbnail', 'created_at']

class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = ['id', 'name', 'position', 'photo', 'description', 'created_at']


class AboutSerializer(serializers.ModelSerializer):
    team_members = serializers.SerializerMethodField()

    class Meta:
        model = About
        fields = ['title', 'image', 'description', 'team_members', 'created_at']

    def get_team_members(self, obj):
        return TeamMemberSerializer(obj.team_members.all(), many=True).data


class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = ['id', 'title', 'image', 'description', 'related_service', 'related_project', 'created_at']


class ToolsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tools
        fields = ['id', 'name', 'image', 'additional_content', 'created_at']


class CommentSerializer(serializers.ModelSerializer):
    project_title = serializers.CharField(source='project.title', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'project', 'project_title', 'text', 'created_at']
        read_only_fields = ['created_at']
        extra_kwargs = {
            'project': {'write_only': True}
        }

    def validate_project(self, value):
        if not Project.objects.filter(id=value.id, is_active=True).exists():
            raise serializers.ValidationError("Проект не найден или удален")
        return value