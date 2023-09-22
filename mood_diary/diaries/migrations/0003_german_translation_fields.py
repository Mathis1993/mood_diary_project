from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diaries', '0002_alter_activity_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='value_de',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='activitycategory',
            name='value_de',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='mood',
            name='label_de',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
