from .models import Notification


def create_notification(*, recipient, actor, message, target_url=''):
    if not recipient or recipient == actor:
        return None
    return Notification.objects.create(
        recipient=recipient,
        actor=actor,
        message=message,
        target_url=target_url,
    )
