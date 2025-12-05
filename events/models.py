from django.db import models
from django.utils import timezone
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name




class Event(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="events")
    # participants = models.ManyToManyField(Participant, related_name="events", blank=True)
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="rsvp_events",
        blank=True
    )
    asset = models.ImageField(
    upload_to='events_asset/',
    default='events_asset/default_event.jpg',
    blank=True,
    null=True
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
