from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('diaries', '0004_english_translation_fields'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='activity',
            options={'ordering': ['category__value_de', 'value_de']},
        ),
    ]
