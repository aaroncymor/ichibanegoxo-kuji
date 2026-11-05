import random
from typing import Any
from django.db.models import Count, Q
from . import models


def summarize_kuji_session(
    kuji_session: models.KujiSession
) -> dict[str, Any]:
    summary = {
        "id": str(kuji_session.id),
        "session_title": kuji_session.title,
        "cost_per_draw": kuji_session.draw_amount,
        "raffles": {},
        "total": kuji_session.raffles.count(),
        "unclaimed_total": kuji_session.raffles.filter(Q(claimed=False)).count(),
    }

    raffles = kuji_session.raffles.values('tier', 'name').annotate(
        total_count=Count('id'),
        claimed_count=Count('id', filter=Q(claimed=True)),
        unclaimed_count=Count('id', filter=Q(claimed=False)),
    ).order_by('tier', 'name')

    summary["raffles"] = list(raffles)
    print("SUMMARY", summary)
    return summary


def draw_raffles(
    kuji_session: models.KujiSession,
    draw_count: int,
    user_id: str
) -> list[models.Raffle]:
    raffles = kuji_session.raffles.filter(claimed=False).values_list('id', flat=True)
    if len(raffles) < draw_count:
        raise ValueError("Not enough unclaimed raffles to draw")
    drawn_raffle_ids = random.sample(list(raffles), draw_count)
    drawn_raffles = kuji_session.raffles.filter(id__in=drawn_raffle_ids).values('id', 'name', 'tier')
    return list(drawn_raffles), drawn_raffle_ids


def claim_raffles(
    kuji_session: models.KujiSession,
    raffle_ids: list[int],
    user_id: str
) -> tuple[bool, str]:
    try:
        kuji_session.raffles.filter(id__in=raffle_ids).update(claimed=True)
        return True, ""
    except Exception as e:
        print("ERROR: Failed to claim raffles", e)
        return False, str(e)
