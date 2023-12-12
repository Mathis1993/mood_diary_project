from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rules', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ruleclient',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
