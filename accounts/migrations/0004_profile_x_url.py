from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0003_profile_github_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='x_url',
            field=models.URLField(blank=True),
        ),
    ]
