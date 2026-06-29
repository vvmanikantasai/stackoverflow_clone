from .models import Notification


def create_notification(recipient, sender, notification_type, message, url=''):
    if recipient == sender:
        return
    Notification.objects.create(
        recipient=recipient,
        sender=sender,
        notification_type=notification_type,
        message=message,
        url=url
    )
