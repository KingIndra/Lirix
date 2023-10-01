import os
from celery import Celery
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('backend')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

# app.conf.beat_schedule = {
#     'my_periodic_task_10s': {
#         'task': 'chat.tasks.periodic',
#         'schedule': 20,
#         'args': ('11111',)
#     },
# }
