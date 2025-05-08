from django.urls import path, include
from .views import (
    EventListCreateViewSet,
    NewsListCreateViewSet,
    VacancyListCreateViewSet,
    ProjectListCreateViewSet,
    ContactCreateView,
    ReviewListCreateView,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from rest_framework.routers import DefaultRouter

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

router = DefaultRouter()
router.register(r'events', EventListCreateViewSet, basename='events')
router.register(r'news', NewsListCreateViewSet, basename='news')
router.register(r'vacancies', VacancyListCreateViewSet, basename='vacancies')
router.register(r'projects', ProjectListCreateViewSet, basename='projects')



urlpatterns = [
    path('', include(router.urls)),
    path('contacts/', ContactCreateView.as_view(), name='contact_create'),
    path('reviews/', ReviewListCreateView.as_view(), name='review_list'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

]