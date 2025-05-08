import requests
from django.conf import settings
from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_telegram_notification(message, file_path=None):
    logger.info(f"Начало отправки уведомления: {message}, файл: {file_path}")
    try:
        # Отправка текстового сообщения
        send_message_url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        message_data = {
            "chat_id": settings.TELEGRAM_CHAT_ID,
            "text": message
        }
        response = requests.post(send_message_url, data=message_data)
        response.raise_for_status()
        logger.info("Текст уведомления успешно отправлен")

        # Отправка файла, если он есть
        if file_path:
            send_document_url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendDocument"
            with open(file_path, 'rb') as file:
                document_data = {
                    "chat_id": settings.TELEGRAM_CHAT_ID,
                }
                files = {"document": file}
                response = requests.post(send_document_url, data=document_data, files=files)
                response.raise_for_status()
            logger.info("Файл успешно отправлен")
    except Exception as e:
        logger.error(f"Ошибка отправки уведомления: {e}")
        raise