from django.contrib import admin
from .models import (
    Contact, YouTubeShort, Event, EventImage, Services, Vacancy,
    Project, Review, About, Gallery, Tools, ToolImage, ContactVacancy
)


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'created_at')
    search_fields = ('name', 'email', 'phone')


@admin.register(YouTubeShort)
class YouTubeShortAdmin(admin.ModelAdmin):
    list_display = ('video_url', 'created_at')
    search_fields = ('created_at',)


class EventImageInline(admin.TabularInline):
    model = Event.gallery.through
    extra = 1


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'created_at')
    inlines = [EventImageInline]
    search_fields = ('title',)


@admin.register(EventImage)
class EventImageAdmin(admin.ModelAdmin):
    list_display = ('event',)
    search_fields = ('event__title',)


@admin.register(Services)
class ServicesAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title',)


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'created_at')
    search_fields = ('title',)
    list_filter = ('is_active',)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_featured', 'created_at')
    search_fields = ('title',)
    list_filter = ('is_featured',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('author', 'created_at')
    search_fields = ('author__username', 'text')


@admin.register(About)
class AboutAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title',)


@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ('title', 'related_service', 'related_project', 'created_at')
    search_fields = ('title',)


@admin.register(Tools)
class ToolsAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)


@admin.register(ToolImage)
class ToolImageAdmin(admin.ModelAdmin):
    list_display = ('tool', 'created_at')
    search_fields = ('tool__name',)


@admin.register(ContactVacancy)
class ContactVacancyAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone','link' ,'created_at')
    search_fields = ('name', 'email', 'phone')
