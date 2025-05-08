from rest_framework import generics, permissions, mixins
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django_filters import FilterSet, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Event, News, Vacancy, Project, Contact, Review
from .serializers import EventSerializer, NewsSerializer, VacancySerializer, ProjectSerializer, ContactSerializer, ReviewSerializer
from .utils import send_telegram_notification
import logging

logger = logging.getLogger(__name__)

class EventFilter(FilterSet):
    date = filters.DateTimeFilter(field_name='date', lookup_expr='gte')

    class Meta:
        model = Event
        fields = ['date']

class EventListCreateView(generics.ListCreateAPIView):
    queryset = Event.objects.all().order_by('created_at')
    serializer_class = EventSerializer
    filterset_class = EventFilter

class NewsListCreateView(generics.ListCreateAPIView):
    queryset = News.objects.all().order_by('created_at')
    serializer_class = NewsSerializer

class VacancyListCreateView(generics.ListCreateAPIView):
    queryset = Vacancy.objects.all().order_by('created_at')
    serializer_class = VacancySerializer

class ProjectListCreateView(generics.ListCreateAPIView):
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
        message = f"Новая заявка!\nИмя: {contact.name}\nEmail: {contact.email}\nСообщение: {contact.message}\nДата: {contact.created_at}"
        file_path = contact.file.path if contact.file else None
        logger.info(f"Отправка уведомления с файлом: {file_path}")
        send_telegram_notification.delay(message, file_path)

class ReviewListCreateView(generics.ListCreateAPIView):
    queryset = Review.objects.all().order_by('created_at')
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)