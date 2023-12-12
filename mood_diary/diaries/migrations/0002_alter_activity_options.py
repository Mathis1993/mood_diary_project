from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('diaries', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='activity',
            options={'ordering': ['category__value', 'value']},
        ),
    ]
