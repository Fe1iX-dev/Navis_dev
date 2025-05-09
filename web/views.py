from rest_framework import generics, permissions, mixins, viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django_filters import FilterSet, filters
from .models import Event, Services, Vacancy, Project, Contact, Review, YouTubeShort
from .serializers import EventSerializer, ServicesSerializer, VacancySerializer, ProjectSerializer, ContactSerializer, ReviewSerializer, YouTubeShortSerializer
from .utils import send_telegram_notification
import logging

logger = logging.getLogger(__name__)

class EventFilter(FilterSet):
    date = filters.DateTimeFilter(field_name='date', lookup_expr='gte')
    class Meta:
        model = Event
        fields = ['date']

class EventListCreateViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by('created_at')
    serializer_class = EventSerializer
    filterset_class = EventFilter

class ServicesListCreateViewSet(viewsets.ModelViewSet):
    queryset = Services.objects.all().order_by('created_at')
    serializer_class = ServicesSerializer

class VacancyListCreateViewSet(viewsets.ModelViewSet):
    queryset = Vacancy.objects.all().order_by('created_at')
    serializer_class = VacancySerializer

class ProjectListCreateViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by('created_at')
    serializer_class = ProjectSerializer

class ContactCreateView(mixins.ListModelMixin, generics.CreateAPIView):
    queryset = Contact.objects.all().order_by('created_at')
    serializer_class = ContactSerializer
    parser_classes = [MultiPartParser, FormParser]

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
            openapi.Parameter('email', openapi.IN_FORM, type=openapi.TYPE_STRING, description='Email', required=True),
            openapi.Parameter('message', openapi.IN_FORM, type=openapi.TYPE_STRING, description='Сообщение', required=True),
            openapi.Parameter('file', openapi.IN_FORM, type=openapi.TYPE_FILE, description='Прикрепленный файл (опционально)', required=False),
            openapi.Parameter('phone', openapi.IN_FORM, type=openapi.TYPE_STRING, description='Номер телефона (начинается с +996)', required=False),
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
        message = f"Новая заявка!\nИмя: {contact.name}\nEmail: {contact.email}\nСообщение: {contact.message}\nТелефон: {contact.phone or 'Не указан'}\nДата: {contact.created_at}"
        file_path = contact.file.path if contact.file else None
        logger.info(f"Отправка уведомления с файлом: {file_path}")
        send_telegram_notification.delay(message, file_path)


class YouTubeShortListCreateViewSet(viewsets.ModelViewSet):
    queryset = YouTubeShort.objects.all().order_by('created_at')
    serializer_class = YouTubeShortSerializer
    parser_classes = [MultiPartParser, FormParser]

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

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)