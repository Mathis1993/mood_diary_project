from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='push_notifications_granted',
            field=models.BooleanField(blank=True, default=None, null=True),
        ),
    ]
