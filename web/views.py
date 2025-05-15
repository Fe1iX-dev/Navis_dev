from django_filters import FilterSet, filters
from rest_framework import generics, permissions, mixins, viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from .models import Event, Services, Vacancy, Project, Contact, Review, YouTubeShort, About, Gallery, TeamMember, Tools, EventImage
from .serializers import EventSerializer, ServicesSerializer, VacancySerializer, ProjectSerializer, ContactSerializer, ReviewSerializer, YouTubeShortSerializer, AboutSerializer, GallerySerializer, TeamMemberSerializer, ToolsSerializer, EventImageSerializer
from .utils import send_telegram_notification
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from datetime import timedelta, timezone
from django.contrib.auth.models import User
from django.core.cache import cache

logger = logging.getLogger(__name__)

class EventFilter(FilterSet):
    date = filters.DateTimeFilter(field_name='date', lookup_expr='gte')
    class Meta:
        model = Event
        fields = ['date']

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class EventListCreateViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by('created_at')
    serializer_class = EventSerializer
    filterset_class = EventFilter
    parser_classes = (MultiPartParser, FormParser)
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def retrieve(self, request, *args, **kwargs):
        logger.info(f"Получен GET-запрос на /api/events/{kwargs['pk']}/")
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        other_events = Event.objects.exclude(id=instance.id).order_by('created_at')
        other_serializer = self.get_serializer(other_events, many=True)
        return Response({
            'event': serializer.data,
            'other_events': other_serializer.data
        })

class ServicesListCreateViewSet(viewsets.ModelViewSet):
    queryset = Services.objects.all().order_by('created_at')
    serializer_class = ServicesSerializer
    parser_classes = [MultiPartParser, FormParser]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def retrieve(self, request, *args, **kwargs):
        logger.info(f"Получен GET-запрос на /api/services/{kwargs['pk']}/")
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        other_services = Services.objects.exclude(id=instance.id).order_by('created_at')
        other_serializer = self.get_serializer(other_services, many=True)
        return Response({
            'service': serializer.data,
            'other_services': other_serializer.data
        })

class VacancyListCreateViewSet(viewsets.ModelViewSet):
    queryset = Vacancy.objects.all().order_by('created_at')
    serializer_class = VacancySerializer
    parser_classes = [MultiPartParser, FormParser]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def retrieve(self, request, *args, **kwargs):
        logger.info(f"Получен GET-запрос на /api/vacancies/{kwargs['pk']}/")
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        other_vacancies = Vacancy.objects.exclude(id=instance.id).order_by('created_at')
        other_serializer = self.get_serializer(other_vacancies, many=True)
        return Response({
            'vacancy': serializer.data,
            'other_vacancies': other_serializer.data
        })

class ActiveVacancyListView(generics.ListAPIView):
    queryset = Vacancy.objects.filter(is_active=True)
    serializer_class = VacancySerializer


class ProjectListCreateViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by('created_at')
    serializer_class = ProjectSerializer
    parser_classes = [MultiPartParser, FormParser]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

class ProjectFilterView(generics.ListAPIView):
    serializer_class = ProjectSerializer
    filterset_fields = ['category', 'is_featured']

    def get_queryset(self):
        return Project.objects.all()


class ProjectSearchView(generics.ListAPIView):
    serializer_class = ProjectSerializer

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        return Project.objects.filter(title__icontains=query)


class ContactCreateView(mixins.ListModelMixin, generics.CreateAPIView):
    queryset = Contact.objects.all().order_by('created_at')
    serializer_class = ContactSerializer
    parser_classes = [MultiPartParser, FormParser]
    pagination_class = StandardResultsSetPagination

    @swagger_auto_schema(
        operation_description="Получить список всех заявок",
        responses={200: ContactSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        logger.info("Получен GET-запрос на /api/contacts/")
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Создать новую заявку с возможностью прикрепить файл",
        manual_parameters=[
            openapi.Parameter('name', openapi.IN_FORM, type=openapi.TYPE_STRING, description='Имя', required=True),
            openapi.Parameter('email', openapi.IN_FORM, type=openapi.TYPE_STRING, description='Email (опционально)', required=False),
            openapi.Parameter('message', openapi.IN_FORM, type=openapi.TYPE_STRING, description='Сообщение', required=True),
            openapi.Parameter('file', openapi.IN_FORM, type=openapi.TYPE_FILE, description='Прикрепленный файл (опционально)', required=False),
            openapi.Parameter('phone', openapi.IN_FORM, type=openapi.TYPE_STRING, description='Номер телефона (начинается с +996, обязателен)', required=True),
        ],
        responses={
            201: ContactSerializer,
            400: 'Ошибка валидации'
        }
    )
    def post(self, request, *args, **kwargs):
        logger.info(f"Получен POST-запрос на /api/contacts/ с данными: {request.data}")
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        contact = serializer.save()
        logger.info(f"Создана новая заявка: {contact}")
        message = f"Новая заявка!\nИмя: {contact.name}\nEmail: {contact.email or 'Не указан'}\nСообщение: {contact.message}\nТелефон: {contact.phone}\nДата: {contact.created_at}"
        file_path = contact.file.path if contact.file else None
        logger.info(f"Отправка уведомления с файлом: {file_path}")
        send_telegram_notification.delay(message, file_path)

class YouTubeShortListCreateViewSet(viewsets.ModelViewSet):
    queryset = YouTubeShort.objects.all().order_by('created_at')
    serializer_class = YouTubeShortSerializer
    parser_classes = [MultiPartParser, FormParser]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    @swagger_auto_schema(
        operation_description="Создать новый YouTube Short с миниатюрой",
        manual_parameters=[
            openapi.Parameter('title', openapi.IN_FORM, type=openapi.TYPE_STRING, description='Название', required=True),
            openapi.Parameter('video_url', openapi.IN_FORM, type=openapi.TYPE_STRING, description='URL видео', required=True),
            openapi.Parameter('thumbnail', openapi.IN_FORM, type=openapi.TYPE_FILE, description='Миниатюра (опционально)', required=False),
        ],
        responses={
            201: YouTubeShortSerializer,
            400: 'Ошибка валидации'
        }
    )
    def create(self, request, *args, **kwargs):
        logger.info(f"Получен POST-запрос на /api/youtube-shorts/ с данными: {request.data}")
        return super().create(request, *args, **kwargs)

class ReviewListCreateView(generics.ListCreateAPIView):
    queryset = Review.objects.all().order_by('created_at')
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class GalleryListCreateViewSet(viewsets.ModelViewSet):
    queryset = Gallery.objects.all().order_by('created_at')
    serializer_class = GallerySerializer
    parser_classes = [MultiPartParser, FormParser]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    @swagger_auto_schema(
        operation_description="Создать новое изображение в галерее",
        manual_parameters=[
            openapi.Parameter('title', openapi.IN_FORM, type=openapi.TYPE_STRING, description='Название изображения (опционально)', required=False),
            openapi.Parameter('image', openapi.IN_FORM, type=openapi.TYPE_FILE, description='Изображение', required=True),
            openapi.Parameter('description', openapi.IN_FORM, type=openapi.TYPE_STRING, description='Описание (опционально)', required=False),
            openapi.Parameter('related_service', openapi.IN_FORM, type=openapi.TYPE_INTEGER, description='ID услуги (опционально)', required=False),
            openapi.Parameter('related_project', openapi.IN_FORM, type=openapi.TYPE_INTEGER, description='ID проекта (опционально)', required=False),
        ],
        responses={
            201: GallerySerializer,
            400: 'Ошибка валидации'
        }
    )
    def create(self, request, *args, **kwargs):
        logger.info(f"Получен POST-запрос на /api/gallery/ с данными: {request.data}")
        return super().create(request, *args, **kwargs)


class ToolsCreateViewSet(viewsets.ModelViewSet):
    queryset = Tools.objects.all().order_by('created_at')
    serializer_class = ToolsSerializer
    parser_classes = [MultiPartParser, FormParser]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def retrieve(self, request, *args, **kwargs):
        logger.info(f"Получен GET-запрос на /api/directions/{kwargs['slug']}/")
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class CustomTokenObtainView(APIView):
    @swagger_auto_schema(
        operation_description="Получить Access-токен с настраиваемым временем жизни",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Имя пользователя'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Пароль'),
                'lifetime_hours': openapi.Schema(type=openapi.TYPE_INTEGER, description='Время жизни токена в часах', default=24),
            },
            required=['username', 'password']
        ),
        responses={200: openapi.Schema(type=openapi.TYPE_OBJECT, properties={'access': openapi.Schema(type=openapi.TYPE_STRING)})}
    )
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        lifetime_hours = int(request.data.get('lifetime_hours', 24))

        user = User.objects.filter(username=username).first()
        if user and user.check_password(password):
            token = AccessToken.for_user(user)
            token.set_exp(lifetime=timedelta(hours=lifetime_hours))
            return Response({'access': str(token)})
        return Response({'error': 'Invalid credentials'}, status=400)


class AboutViewSet(viewsets.ModelViewSet):
    queryset = About.objects.all().order_by('created_at')
    serializer_class = AboutSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

class HomeAPIView(APIView):
    @swagger_auto_schema(
        operation_description="Данные для главной страницы",
        responses={200: openapi.Response("Главная страница", schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "projects": ProjectSerializer(many=True),
                "events": EventSerializer(many=True),
                "reviews": ReviewSerializer(many=True),
                "youtube_short": YouTubeShortSerializer()
            }
        ))}
    )
    def get(self, request):
        data = {
            "projects": ProjectSerializer(
                Project.objects.filter(is_featured=True)[:3],
                many=True,
                context={'request': request}  # Для полных URL изображений
            ).data,

            "events": EventSerializer(
                Event.objects.filter(date__gte=timezone.now()).order_by('date')[:2],
                many=True
            ).data,

            "reviews": ReviewSerializer(
                Review.objects.select_related('author').order_by('-created_at')[:3],
                many=True
            ).data,

            "youtube_short": YouTubeShortSerializer(
                YouTubeShort.objects.last()
            ).data if YouTubeShort.objects.exists() else None
        }

        return Response(data)
