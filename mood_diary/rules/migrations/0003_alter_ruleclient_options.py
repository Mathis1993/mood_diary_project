from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rules', '0002_ruleclient_active'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ruleclient',
            options={'ordering': ['-active', 'rule__title']},
        ),
    ]
