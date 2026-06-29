from django.core.management.base import BaseCommand
from badges.models import Badge


class Command(BaseCommand):
    help = 'Create default badges'

    def handle(self, *args, **options):
        badges_data = [
            # Bronze
            ('First Question', 'Asked your first question', 'bronze', ''),
            ('First Answer', 'Posted your first answer', 'bronze', ''),
            ('Curious', 'Asked a well-received question', 'bronze', ''),
            ('Teacher', 'Answered a question positively', 'bronze', ''),
            # Silver
            ('100 Reputation', 'Reached 100 reputation points', 'silver', ''),
            ('Prolific Questioner', 'Asked 10 or more questions', 'silver', ''),
            ('Top Answerer', 'Posted 10 or more answers', 'silver', ''),
            ('Good Question', 'Question with 5+ upvotes', 'silver', ''),
            # Gold
            ('1000 Reputation', 'Reached 1000 reputation points', 'gold', ''),
            ('Great Answer', 'Answer with 10+ upvotes', 'gold', ''),
            ('Legend', 'Reached 5000 reputation points', 'gold', ''),
        ]
        created = 0
        for name, desc, tier, icon in badges_data:
            _, made = Badge.objects.update_or_create(
                name=name,
                defaults={'description': desc, 'tier': tier, 'icon': icon}
            )
            if made:
                created += 1
        self.stdout.write(self.style.SUCCESS(f'Created {created} badge(s). Total: {Badge.objects.count()}'))
