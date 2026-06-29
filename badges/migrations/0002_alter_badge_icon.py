from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('badges', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='badge',
            name='icon',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
    ]
