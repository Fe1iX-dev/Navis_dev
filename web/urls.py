from django.urls import path, include
from .views import (
    EventListAPIView, EventDetailAPIView,
    ServicesListAPIView, ServicesDetailAPIView,
    VacancyListAPIView, VacancyDetailAPIView,
    ProjectListAPIView, ProjectDetailAPIView, ProjectFilterView, ProjectSearchView,
    ContactCreateView, ReviewListCreateView,
    YouTubeShortListAPIView, GalleryListAPIView,
    ToolsListAPIView, ToolsDetailAPIView,
    AboutListAPIView, CustomTokenObtainView
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from django.conf import settings
from django.conf.urls.static import static

schema_view = get_schema_view(
    openapi.Info(
        title="NavisDevs API",
        default_version='v1',
        description="API documentation for NavisDevs",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@navisdevs.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [

    path('events/', EventListAPIView.as_view(), name='event_list'),
    path('events/<int:pk>/', EventDetailAPIView.as_view(), name='event_detail'),

    path('services/', ServicesListAPIView.as_view(), name='service_list'),
    path('services/<int:pk>/', ServicesDetailAPIView.as_view(), name='service_detail'),

    path('vacancies/', VacancyListAPIView.as_view(), name='vacancy_list'),
    path('vacancies/<int:pk>/', VacancyDetailAPIView.as_view(), name='vacancy_detail'),

    path('projects/', ProjectListAPIView.as_view(), name='project_list'),
    path('projects/<int:pk>/', ProjectDetailAPIView.as_view(), name='project_detail'),
    path('projects/filter/', ProjectFilterView.as_view(), name='project_filter'),
    path('projects/search/', ProjectSearchView.as_view(), name='project_search'),

    path('contacts/', ContactCreateView.as_view(), name='contact_create'),

    path('reviews/', ReviewListCreateView.as_view(), name='review_list_create'),

    path('youtube-shorts/', YouTubeShortListAPIView.as_view(), name='youtube_shorts'),

    path('gallery/', GalleryListAPIView.as_view(), name='gallery_list'),

    path('tools/', ToolsListAPIView.as_view(), name='tools_list'),
    path('tools/<slug:slug>/', ToolsDetailAPIView.as_view(), name='tools_detail'),

    path('about/', AboutListAPIView.as_view(), name='about_list'),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('custom-token/', CustomTokenObtainView.as_view(), name='custom_token'),

    path('ckeditor/', include('ckeditor_uploader.urls')),

    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
