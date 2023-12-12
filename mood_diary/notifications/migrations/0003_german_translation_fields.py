from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0002_alter_notification_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='message_de',
            field=models.TextField(null=True),
        ),
    ]
