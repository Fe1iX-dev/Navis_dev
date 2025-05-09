from requests import Response
from rest_framework import generics, permissions, mixins, viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django_filters import FilterSet, filters
from .models import Event, Services, Vacancy, Project, Contact, Review, YouTubeShort
from .serializers import EventSerializer, ServicesSerializer, VacancySerializer, ProjectSerializer, ContactSerializer, ReviewSerializer, YouTubeShortSerializer
from .utils import send_telegram_notification
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from datetime import timedelta
from django.contrib.auth.models import User

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

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


class ServicesListCreateViewSet(viewsets.ModelViewSet):
    queryset = Services.objects.all().order_by('created_at')
    serializer_class = ServicesSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    @swagger_auto_schema(
        operation_description="Получить детальную информацию об услуге и список других услуг",
        responses={
            200: openapi.Response(
                description="Детали услуги и список других услуг",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'service': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            description='Текущая услуга',
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'title': openapi.Schema(type=openapi.TYPE_STRING),
                                'content': openapi.Schema(type=openapi.TYPE_STRING),
                                'image': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, nullable=True),
                                'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                            }
                        ),
                        'other_services': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            description='Список других услуг',
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'title': openapi.Schema(type=openapi.TYPE_STRING),
                                    'content': openapi.Schema(type=openapi.TYPE_STRING),
                                    'image': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, nullable=True),
                                    'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                                }
                            )
                        )
                    }
                )
            )
        }
    )
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

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


class ProjectListCreateViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by('created_at')
    serializer_class = ProjectSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


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

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

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