from rest_framework import generics, mixins
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Event, Services, Vacancy, Project, Contact, Review, YouTubeShort, About, Gallery, Tools
from .serializers import ServicesSerializer, VacancySerializer, ProjectSerializer, ContactSerializer, ReviewSerializer, YouTubeShortSerializer, AboutSerializer, GallerySerializer, ToolsSerializer
from .utils import send_telegram_notification
from rest_framework_simplejwt.tokens import AccessToken
from datetime import timedelta, timezone
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.shortcuts import get_object_or_404
from .models import Event
from .serializers import EventSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.pagination import PageNumberPagination
import logging


logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class EventDetailAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, pk):
        logger.info(f"Получен GET-запрос на /api/events/{pk}/")
        event = get_object_or_404(Event, pk=pk)
        serializer = EventSerializer(event)
        return Response(serializer.data)

class EventListAPIView(generics.ListAPIView):
    queryset = Event.objects.all().order_by('created_at')
    serializer_class = EventSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]


class ServicesDetailAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        logger.info(f"Получен GET-запрос на /api/services/{pk}/")
        service = get_object_or_404(Services, pk=pk)
        serializer = ServicesSerializer(service)
        return Response(serializer.data)


class ServicesListAPIView(generics.ListAPIView):
    queryset = Services.objects.all().order_by('created_at')
    serializer_class = ServicesSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]


class VacancyDetailAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        logger.info(f"Получен GET-запрос на /api/vacancies/{pk}/")
        vacancy = get_object_or_404(Vacancy, pk=pk)
        serializer = VacancySerializer(vacancy)
        return Response(serializer.data)


class VacancyListAPIView(generics.ListAPIView):
    queryset = Vacancy.objects.all().order_by('created_at')
    serializer_class = VacancySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]


class ProjectDetailAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        serializer = ProjectSerializer(project)
        return Response(serializer.data)


class ProjectListAPIView(generics.ListAPIView):
    queryset = Project.objects.all().order_by('created_at')
    serializer_class = ProjectSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]


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

class YouTubeShortListAPIView(generics.ListAPIView):
    queryset = YouTubeShort.objects.all().order_by('created_at')
    serializer_class = YouTubeShortSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]


class ReviewListCreateView(generics.ListCreateAPIView):
    queryset = Review.objects.all().order_by('created_at')
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class GalleryListAPIView(generics.ListAPIView):
    queryset = Gallery.objects.all().order_by('created_at')
    serializer_class = GallerySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]

class ToolsDetailAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, slug):
        logger.info(f"Получен GET-запрос на /api/directions/{slug}/")
        tool = get_object_or_404(Tools, slug=slug)
        serializer = ToolsSerializer(tool)
        return Response(serializer.data)

class ToolsListAPIView(generics.ListAPIView):
    queryset = Tools.objects.all().order_by('created_at')
    serializer_class = ToolsSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]


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


class AboutListAPIView(generics.ListAPIView):
    queryset = About.objects.all().order_by('created_at')
    serializer_class = AboutSerializer
    permission_classes = [permissions.AllowAny]

