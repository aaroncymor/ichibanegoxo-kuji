import random
from typing import Any
from django.db.models import Count, Q, Sum, F
from . import models


def summarize_kuji_session(
    kuji_session: models.KujiSession
) -> dict[str, Any]:
    summary = {
        "id": str(kuji_session.id),
        "session_title": kuji_session.title,
        "draw_amount": float(kuji_session.draw_amount),
        "prizes": {},
    }

    prizes = kuji_session.prizes.values('tier', 'name').annotate(
        total_count=Sum('starting_inventory'),
        claimed_count=Sum('claimed'),
        unclaimed_count=Sum('starting_inventory') - Sum('claimed'),
    ).order_by('tier', 'name')

    summary["prizes"] = list(prizes)
    print("SUMMARY", summary)
    return summary


def draw_prizes(
    kuji_session: models.KujiSession,
    draw_count: int,
    user_id: str
) -> dict[str, int]:
    prizes = kuji_session.prizes.filter(
        starting_inventory__gt=0, 
        claimed__lt=F('starting_inventory'),
        tier__ne__in=['lp', 'in']
    ).values('id', 'name', 'tier', 'starting_inventory', 'claimed')

    if len(prizes) < draw_count:
        raise ValueError("Not enough unclaimed prizes to draw")
    
    # Convert to list of dicts for random sampling
    prizes_list = [
        {
            'id': prize['id'],
            'name': prize['name'],
            'tier': prize['tier'],
        } 
        for prize in prizes 
        for _ in range(prize['starting_inventory'] - prize['claimed'])
    ]
    drawn_prizes = random.sample(prizes_list, draw_count)
    
    results = {}
    for prize in drawn_prizes:
        results[prize['id']] = results.get(prize['id'], 0) + 1
    
    return results


def claim_prizes(
    drawn_prizes: dict[str, int],
    user_id: str
) -> tuple[bool, str]:
    try:
        prizes = models.KujiPrize.objects.filter(id__in=drawn_prizes.keys())
        for prize in prizes:
            prize.claimed += drawn_prizes[prize.id]
            prize.save()
        return True, ""
    except Exception as e:
        print("ERROR: Failed to claim prizes", e)
        return False, str(e)
