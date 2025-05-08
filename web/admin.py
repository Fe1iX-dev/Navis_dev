from django.contrib import admin
from .models import (
    Contact,
    Event,
    Services,
    Vacancy,
    Project,
    Review
)
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('id' ,'name', 'email', 'message', 'file', 'created_at')
#
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('id' , 'title', 'description', 'date', 'image', 'created_at')

@admin.register(Services)
class ServicesAdmin(admin.ModelAdmin):
    list_display = ('id' , 'title', 'content', 'image', 'created_at')

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('id' , 'title', 'description', 'requirements', 'created_at')

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id' , 'title', 'description', 'image', 'created_at')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id' , 'author', 'text', 'rating', 'created_at')
