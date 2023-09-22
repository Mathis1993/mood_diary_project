import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rules', '0003_alter_ruleclient_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='ruletriggeredlog',
            name='requested_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
