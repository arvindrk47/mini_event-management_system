from django.db import models

# Create your models here.
from django.core.exceptions import ValidationError
from django.utils import timezone


class Event(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=300)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    max_capacity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start_time']

    def __str__(self):
        return f"{self.name} - {self.start_time}"

    def clean(self):
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError("Start time must be before end time")

    @property
    def current_attendees_count(self):
        return self.registrations.count()

    @property
    def is_full(self):
        return self.current_attendees_count >= self.max_capacity

    @property
    def available_spots(self):
        return self.max_capacity - self.current_attendees_count


class Registration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'email')
        ordering = ['registered_at']

    def __str__(self):
        return f"{self.name} - {self.event.name}"