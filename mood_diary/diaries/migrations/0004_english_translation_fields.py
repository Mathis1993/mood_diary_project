from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diaries', '0003_german_translation_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='value_en',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='activitycategory',
            name='value_en',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='mood',
            name='label_en',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
