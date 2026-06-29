from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0004_profile_x_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reputationhistory',
            name='action',
            field=models.CharField(
                choices=[
                    ('question_upvote', 'Question Upvote (+5)'),
                    ('question_downvote', 'Question Downvote (-2)'),
                    ('answer_upvote', 'Answer Upvote (+10)'),
                    ('answer_downvote', 'Answer Downvote (-2)'),
                    ('answer_accepted', 'Answer Accepted (+15)'),
                    ('answer_acceptance', 'Accepted an Answer (+2)'),
                ],
                max_length=50,
            ),
        ),
    ]
