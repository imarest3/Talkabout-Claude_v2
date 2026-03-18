from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0003_alter_activityfile_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='max_participants',
            field=models.PositiveIntegerField(
                blank=True,
                null=True,
                help_text='Maximum total enrollments per event. Leave blank for unlimited.'
            ),
        ),
    ]
