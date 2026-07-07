from django.db import migrations


def upgrade_legacy_notification_table(apps, schema_editor):
    """
    Upgrade the notification table created by the project's older notification
    implementation. Fresh databases already have the new columns, so every
    operation is conditional.
    """
    connection = schema_editor.connection
    table_name = 'notifications'
    if table_name not in connection.introspection.table_names():
        return

    with connection.cursor() as cursor:
        columns = {
            column.name
            for column in connection.introspection.get_table_description(
                cursor,
                table_name,
            )
        }

    renames = (
        ('notification_type', 'kind'),
        ('url', 'target_url'),
        ('sender_id', 'actor_id'),
    )
    for old_name, new_name in renames:
        if old_name in columns and new_name not in columns:
            schema_editor.execute(
                f'ALTER TABLE {table_name} '
                f'RENAME COLUMN {old_name} TO {new_name}'
            )
            columns.remove(old_name)
            columns.add(new_name)

    if 'read_at' not in columns:
        schema_editor.execute(
            f'ALTER TABLE {table_name} ADD COLUMN read_at timestamp NULL'
        )

    if 'kind' in columns:
        schema_editor.execute(
            f"UPDATE {table_name} SET kind = 'answer' "
            "WHERE kind = 'new_answer'"
        )
        schema_editor.execute(
            f"UPDATE {table_name} SET kind = 'comment' "
            "WHERE kind = 'new_comment'"
        )

    with connection.cursor() as cursor:
        constraints = connection.introspection.get_constraints(
            cursor,
            table_name,
        )
    if 'notif_recipient_read_idx' not in constraints:
        schema_editor.execute(
            f'CREATE INDEX notif_recipient_read_idx ON {table_name} '
            '(recipient_id, is_read, created_at DESC)'
        )


class Migration(migrations.Migration):
    dependencies = [
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            upgrade_legacy_notification_table,
            reverse_code=migrations.RunPython.noop,
        ),
    ]

