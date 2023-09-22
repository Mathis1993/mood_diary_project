from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0003_german_translation_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='message_en',
            field=models.TextField(null=True),
        ),
    ]
