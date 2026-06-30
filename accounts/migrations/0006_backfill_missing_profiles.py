from django.db import migrations


def create_missing_profiles(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Profile = apps.get_model('accounts', 'Profile')

    users_with_profiles = Profile.objects.values_list('user_id', flat=True)
    missing_profiles = [
        Profile(user_id=user_id)
        for user_id in User.objects.exclude(pk__in=users_with_profiles)
        .values_list('pk', flat=True)
    ]
    Profile.objects.bulk_create(missing_profiles)


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0005_alter_reputationhistory_action'),
    ]

    operations = [
        migrations.RunPython(
            create_missing_profiles,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
