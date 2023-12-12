from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('diaries', '0005_alter_activity_options'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mooddiaryentry',
            old_name='mood_and_emotion_info',
            new_name='details',
        ),
    ]
