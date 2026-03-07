import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'talkabout.settings')

app = Celery('talkabout')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat schedule for periodic tasks
app.conf.beat_schedule = {
    'send-first-reminders': {
        'task': 'apps.events.tasks.send_first_reminders',
        'schedule': crontab(minute='*/5'),
    },
    'send-second-reminders': {
        'task': 'apps.events.tasks.send_second_reminders',
        'schedule': crontab(minute='*/5'),
    },
    'send-waiting-room-notifications': {
        'task': 'apps.events.tasks.send_waiting_room_notifications',
        'schedule': crontab(minute='*/1'),
    },
    'cleanup-old-events': {
        'task': 'apps.events.tasks.cleanup_old_events',
        'schedule': crontab(minute='*/10'),
    },
    'create-meetings': {
        'task': 'apps.events.tasks.create_meetings_for_events',
        'schedule': crontab(minute='*/1'),
    },
}

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
