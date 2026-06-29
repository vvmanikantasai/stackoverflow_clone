from django.db import migrations, models


def keep_one_accepted_answer(apps, schema_editor):
    Answer = apps.get_model('answers', 'Answer')
    accepted_question_ids = (
        Answer.objects.filter(is_accepted=True)
        .values_list('question_id', flat=True)
        .distinct()
    )

    for question_id in accepted_question_ids.iterator():
        accepted_answers = Answer.objects.filter(
            question_id=question_id,
            is_accepted=True,
        ).order_by('-updated_at', '-pk')
        keep_id = accepted_answers.values_list('pk', flat=True).first()
        accepted_answers.exclude(pk=keep_id).update(is_accepted=False)


class Migration(migrations.Migration):
    dependencies = [
        ('answers', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            keep_one_accepted_answer,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AddConstraint(
            model_name='answer',
            constraint=models.UniqueConstraint(
                fields=('question',),
                condition=models.Q(is_accepted=True),
                name='one_accepted_answer_per_question',
            ),
        ),
    ]
