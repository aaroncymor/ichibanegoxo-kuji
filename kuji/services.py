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
        "session_desc": kuji_session.description,
        "is_live": kuji_session.is_live,
        "ticket_draw": kuji_session.ticket_draw,
        "draw_amount": float(kuji_session.draw_amount),
        "prizes": [],
        "last_prize": None,
        "inclusive_prizes": [],
        "sweep_amount": 0.0,
        "sweep_guarantee": "ALL prizes!",
        "stats": {
            "total_prizes": 0,
            "claimed_prizes": 0,
            "unclaimed_prizes": 0,
        }
    }

    prizes = kuji_session.prizes.exclude(tier__in=['lp', 'in', 's']).annotate(
        unclaimed=F('starting_inventory') - F('claimed')
    ).values(
        'id', 'name', 'tier', 'tier_label', 'image_url', 'description', 
        'reference_price', 'starting_inventory', 'claimed', 'unclaimed'
    ).order_by('tier', 'id')

    s_prizes = kuji_session.prizes.filter(tier__in=['s', 'ss']).annotate(
        unclaimed=F('starting_inventory') - F('claimed')
    ).values(
        'id', 'name', 'tier', 'tier_label', 'image_url', 'description',
        'starting_inventory', 'claimed', 'unclaimed'
    ).order_by('-name')

    summary["prizes"] = list(s_prizes) + list(prizes)

    last_prize = kuji_session.prizes.annotate(
        unclaimed=F('starting_inventory') - F('claimed')
    ).filter(tier='lp').first()
    if last_prize:
        summary["last_prize"] = {
            'id': str(last_prize.id),
            'name': last_prize.name,
            'tier': last_prize.tier,
            'tier_label': last_prize.tier_label,
            'image_url': last_prize.image_url,
            'description': last_prize.description,
            'reference_price': float(last_prize.reference_price) if last_prize.reference_price else None,
            'starting_inventory': last_prize.starting_inventory,
            'claimed': last_prize.claimed,
            'unclaimed': last_prize.unclaimed,
        }

    inclusive_prizes = kuji_session.prizes.filter(tier='in').annotate(
        unclaimed=F('starting_inventory') - F('claimed')
    ).values(
        'id', 'name', 'tier', 'tier_label', 'image_url', 'description',
        'starting_inventory', 'claimed', 'unclaimed'
    )
    summary["inclusive_prizes"] = list(inclusive_prizes)

    stats = {
        "total_prizes": sum([prize['starting_inventory'] for prize in summary["prizes"]]),
        "claimed_prizes": sum([prize['claimed'] for prize in summary["prizes"]]),
        "unclaimed_prizes": sum([prize['unclaimed'] for prize in summary["prizes"]]),
    }
    
    stats["drawn_pct"] = (stats["claimed_prizes"] / stats["total_prizes"]) * 100 if stats["total_prizes"] > 0 else 0
    summary["stats"] = stats

    sweep_amount = stats['unclaimed_prizes'] * kuji_session.draw_amount
    summary["sweep_amount"] = float(sweep_amount)

    if stats["claimed_prizes"] == 0:
        sweep_guarantee = "ALL prizes!"
    else:
        if summary["last_prize"]:
            sweep_guarantee = f"Last One Prize: {summary['last_prize']['name']}"
        if summary["inclusive_prizes"]:
            sweep_guarantee += f" + {len(summary['inclusive_prizes'])} Inclusive Prizes"

        for prize in summary["prizes"]:
            unclaimed = prize['unclaimed']
            sweep_guarantee += f" + {prize['name']} x {unclaimed}"

    summary["sweep_guarantee"] = sweep_guarantee

    print("SUMMARY", summary)
    return summary


def initialize_draw(
    kuji_session: models.KujiSession,
    draw_count: int,
    user_id: str
) -> dict[str, int]:
    prizes = kuji_session.prizes.filter(
        starting_inventory__gt=0, 
        claimed__lt=F('starting_inventory'),
    ).exclude(tier__in=['lp', 'in']).annotate(
        unclaimed=F('starting_inventory') - F('claimed')
    ).values('id', 'name', 'tier', 'starting_inventory', 'claimed', 'unclaimed')

    if len(prizes) < draw_count:
        raise ValueError("Not enough unclaimed prizes to draw")
    
    # Convert to list of dicts for random sampling
    prizes_list = [
        {
            'id': prize['id'],
            'name': prize['name'],
            'tier': prize['tier'],
            'unclaimed': prize['unclaimed'],
        } 
        for prize in prizes 
        for _ in range(prize['unclaimed'])
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
