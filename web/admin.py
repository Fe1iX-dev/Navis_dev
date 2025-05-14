from django.contrib import admin
from .models import Event, Services, Vacancy, Project, Contact, Review, YouTubeShort, About, Gallery, TeamMember, Direction, EventImage

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'created_at')
    list_filter = ('date', 'created_at')
    search_fields = ('title', 'description')

@admin.register(Services)
class ServicesAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'content')

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'description', 'requirements')

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'description')

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'email', 'message')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('author', 'rating', 'created_at')
    list_filter = ('created_at', 'rating')
    search_fields = ('text', 'author__username')

@admin.register(YouTubeShort)
class YouTubeShortAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'video_url')

@admin.register(About)
class AboutAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'description')

@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'description')

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'position', 'description')

@admin.register(Direction)
class DirectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description')

@admin.register(EventImage)
class EventImageAdmin(admin.ModelAdmin):
    list_display = ('event', 'get_created_at')
    list_filter = ('event',)
    search_fields = ('event__title',)

    def get_created_at(self, obj):
        return obj.created_at
    get_created_at.short_description = 'Created At'