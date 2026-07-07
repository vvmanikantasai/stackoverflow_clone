from django.db import migrations


def normalize_legacy_column_types(apps, schema_editor):
    """Match legacy PostgreSQL column types to the current Django model."""
    connection = schema_editor.connection
    if connection.vendor != 'postgresql':
        return

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT column_name, data_type, character_maximum_length
            FROM information_schema.columns
            WHERE table_name = 'notifications'
            """
        )
        columns = {
            name: (data_type, max_length)
            for name, data_type, max_length in cursor.fetchall()
        }

    if columns.get('read_at', (None,))[0] == 'timestamp without time zone':
        schema_editor.execute(
            'ALTER TABLE notifications '
            'ALTER COLUMN read_at TYPE timestamp with time zone '
            "USING read_at AT TIME ZONE 'UTC'"
        )
    if columns.get('kind') != ('character varying', 20):
        schema_editor.execute(
            'ALTER TABLE notifications '
            'ALTER COLUMN kind TYPE varchar(20)'
        )
    if columns.get('message') != ('character varying', 255):
        schema_editor.execute(
            'ALTER TABLE notifications '
            'ALTER COLUMN message TYPE varchar(255)'
        )


class Migration(migrations.Migration):
    dependencies = [
        ('notifications', '0002_upgrade_legacy_notification_table'),
    ]

    operations = [
        migrations.RunPython(
            normalize_legacy_column_types,
            reverse_code=migrations.RunPython.noop,
        ),
    ]

