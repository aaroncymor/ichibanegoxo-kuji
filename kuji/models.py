import uuid
from django.db import models


# Create your models here.
class KujiSession(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    title = models.CharField(max_length=255)
    is_live = models.BooleanField(default=False)
    draw_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.title


class KujiRaffle(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    kuji_session = models.ForeignKey(
        KujiSession, on_delete=models.CASCADE, related_name="raffles"
    )
    name = models.CharField(max_length=255)
    tier = models.CharField(max_length=3)
    claimed = models.BooleanField(default=False)

    def __str__(self):
        claimed = "Claimed!" if self.claimed else "Not Claimed!"
        return f"[Tier {self.tier}] {self.name} - {claimed}"
