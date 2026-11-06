import uuid
from django.db import models

# Create your models here.

TICKET_DRAW_CHOICES = (
    ('single', 'Draw 1 ticket'),
    ('double', 'Draw 1, or 3 tickets'),
    ('mild', 'Draw 1, 3, or 5 tickets'),
    ('heavy', 'Draw 1, 3, 5, or 10 tickets'),
)

class KujiSession(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    title = models.CharField(max_length=255)
    is_live = models.BooleanField(default=False)
    ticket_draw = models.CharField(
        max_length=10, choices=TICKET_DRAW_CHOICES, default='mild'
    )
    draw_amount = models.DecimalField(max_digits=10, decimal_places=2)
    availability = models.DateField(blank=True, null=True)


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
    tier_label = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    reference_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, blank=True, null=True
    )
    starting_inventory = models.IntegerField(default=0)
    claimed = models.IntegerField(default=0)

    def __str__(self):
        claimed = "Claimed!" if self.claimed > 0 else "Not Claimed!"
        return f"[Tier {self.tier}] {self.name} - {claimed}"