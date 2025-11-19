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
    'send-event-reminders': {
        'task': 'apps.events.tasks.send_event_reminders',
        'schedule': crontab(minute='*/5'),  # Run every 5 minutes
    },
    'create-meetings': {
        'task': 'apps.events.tasks.create_meetings_for_events',
        'schedule': crontab(minute='*/1'),  # Run every minute
    },
}

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
