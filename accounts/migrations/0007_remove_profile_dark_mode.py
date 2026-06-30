from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0006_backfill_missing_profiles'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='dark_mode',
        ),
    ]
