import secrets
from django.db import migrations, models


def generate_tokens(apps, schema_editor):
    """Generate unsubscribe tokens for existing users."""
    User = apps.get_model('users', 'User')
    for user in User.objects.filter(unsubscribe_token=''):
        user.unsubscribe_token = secrets.token_urlsafe(32)
        user.save(update_fields=['unsubscribe_token'])


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='email_notifications_enabled',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='user',
            name='unsubscribe_token',
            field=models.CharField(default='', max_length=64, null=True),
        ),
        migrations.RunPython(generate_tokens, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='user',
            name='unsubscribe_token',
            field=models.CharField(max_length=64, unique=True, db_index=True),
        ),
    ]
