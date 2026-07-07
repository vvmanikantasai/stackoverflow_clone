from .models import Notification


def create_notification(*, recipient, actor, kind, message, target_url=''):
    """Create one notification, unless the actor would notify themselves."""
    if actor is not None and recipient.pk == actor.pk:
        return None

    return Notification.objects.create(
        recipient=recipient,
        actor=actor,
        kind=kind,
        message=message[:255],
        target_url=target_url,
    )


def create_notifications(*, recipients, actor, kind, message, target_url=''):
    """Notify each unique recipient while excluding the actor."""
    seen = set()
    notifications = []
    for recipient in recipients:
        if recipient.pk in seen:
            continue
        seen.add(recipient.pk)
        if actor is not None and recipient.pk == actor.pk:
            continue
        notifications.append(Notification(
            recipient=recipient,
            actor=actor,
            kind=kind,
            message=message[:255],
            target_url=target_url,
        ))
    return Notification.objects.bulk_create(notifications)
