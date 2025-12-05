from django.dispatch import receiver
from django.db.models.signals import post_save, m2m_changed
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.urls import reverse
from django.core.mail import send_mail
import logging

User = get_user_model()
logger = logging.getLogger("django")

@receiver(post_save, sender=User)
def send_activation_email(sender, instance, created, **kwargs):
    if created:
        logger.warning("SIGNAL: Preparing to send activation email to %s", instance.email)

        token = default_token_generator.make_token(instance)
        path = reverse('activate_user', args=[instance.id, token])
        activation_url = f"{settings.FRONTEND_URL}{path}"

        subject = "Activate Your Account"
        message = (
            f"Hi {instance.username},\n\n"
            "Please activate your account using the link below:\n"
            f"{activation_url}\n\n"
            "Thank you!"
        )

        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,    
                [instance.email],
                fail_silently=False,
            )
            logger.warning("SIGNAL: Email SENT to %s", instance.email)

        except Exception as e:
            logger.error("SIGNAL: FAILED to send email to %s — ERROR: %s", instance.email, e)


@receiver(post_save, sender=User)
def assign_role(sender, instance, created, **kwargs):
    if created:
        group, _ = Group.objects.get_or_create(name="User")
        instance.groups.add(group)


@receiver(m2m_changed)
def send_rsvp_confirmation_email(sender, instance, action, model, pk_set, **kwargs):
    if action == "post_add" and instance.__class__.__name__ == 'Event' and model == User:
        for user_id in pk_set:
            try:
                user = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                continue

            if user.email:
                event = instance

                send_mail(
                    subject=f"RSVP Confirmation — {event.name}",
                    message=(
                        f"Hi {user.get_full_name() or user.username},\n\n"
                        f"You successfully RSVP for {event.name}.\n"
                        f"Date: {event.date}\nTime: {event.time}\nLocation: {event.location}\n"
                        "Best of Luck."
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,   
                    recipient_list=[user.email],
                    fail_silently=True,
                )
