import uuid
from django.db import models
from django.conf import settings


# Create your models here.

TICKET_DRAW_CHOICES = (
    ('single', 'Single (Draw 1 ticket)'),
    ('double', 'Double (Draw 1, or 3 tickets)'),
    ('triple', 'Triple (Draw 1, 3, or 5 tickets)'),
    ('aggressive', 'Aggressive (Draw 1, 3, 5, or 10 tickets)'),
)

KUJI_STATUS_CHOICES = (
    ('draft', 'Draft'),
    ('live', 'Live'),
    ('ended', 'Ended'),
    ('paused', 'Paused'),
    ('cancelled', 'Cancelled'),
)


class KujiSession(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_live = models.BooleanField(default=False)
    ticket_draw = models.CharField(
        max_length=10, choices=TICKET_DRAW_CHOICES, default='mild'
    )
    draw_amount = models.DecimalField(max_digits=10, decimal_places=2)
    availability = models.DateField(blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="created_kujis"
    )
    status = models.CharField(
        max_length=20, choices=KUJI_STATUS_CHOICES, default='draft'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


TIER_CHOICES = (
    ('lp', 'LP'), ('in', 'IN'), ('s', 'S'), ('a', 'A'), ('b', 'B'), ('c', 'C'), 
    ('d', 'D'), ('e', 'E'),  ('f', 'F'), ('g', 'G'), ('h', 'H'), ('i', 'I'), 
    ('j', 'J')
)

class KujiPrize(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    kuji_session = models.ForeignKey(
        KujiSession, on_delete=models.CASCADE, related_name="prizes"
    )
    name = models.TextField()
    tier = models.CharField(max_length=2, choices=TIER_CHOICES)
    tier_label = models.CharField(max_length=50, blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    reference_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, blank=True, null=True
    )
    starting_inventory = models.IntegerField(default=0)
    claimed = models.IntegerField(default=0)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
        related_name="created_kuji_prizes"
    )
    claimed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
        related_name="claimed_kuji_prizes", blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        claimed = "Claimed!" if self.claimed > 0 else "Not Claimed!"
        return f"[Tier {self.tier.upper()}] {self.name} - {claimed}"

    def unclaimed(self):
        return self.starting_inventory - self.claimed


class KujiSessionLog(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    kuji_session = models.ForeignKey(
        KujiSession, on_delete=models.CASCADE, related_name="draw_logs"
    )
    participant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="draw_logs"
    )
    prizes = models.JSONField(default=list)
    tickets_drawn = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.participant} - {len(self.prizes)} prizes - {self.created_at}"
