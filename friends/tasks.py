from celery import shared_task 
from friends.models import Notification


@shared_task
def notifications_cleaner():
    Notification.clear_notifications()
    return f"cleared notifications"
