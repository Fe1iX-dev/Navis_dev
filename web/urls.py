from django.urls import path
from .views import EventListCreateView, NewsListCreateView, VacancyListCreateView, ProjectListCreateView, ContactCreateView, ReviewListCreateView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

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
    path('events/', EventListCreateView.as_view(), name='event-list'),
    path('news/', NewsListCreateView.as_view(), name='news-list'),
    path('vacancies/', VacancyListCreateView.as_view(), name='vacancy-list'),
    path('projects/', ProjectListCreateView.as_view(), name='project-list'),
    path('contacts/', ContactCreateView.as_view(), name='contact-create'),  # Обновлено
    path('reviews/', ReviewListCreateView.as_view(), name='review-list'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]