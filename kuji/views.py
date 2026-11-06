from django.shortcuts import render
from .models import KujiSession
from .services import summarize_kuji_session


# Create your views here.
def kuji_list(request, *args, **kwargs):
    # TODO: to be paginated
    kuji_sessions = KujiSession.objects.all()
    ctx = {
        "kuji_sessions": kuji_sessions
    }
    return render(request, "kuji/index.html", ctx)


def kuji_detail(request, pk,  *args, **kwargs):
    # TODO: to be paginated
    kuji_session = KujiSession.objects.filter(pk=pk).first()
    claimed_raffles = kuji_session.raffles.filter(claimed=True).values('id', 'name', 'tier')
    summary = summarize_kuji_session(kuji_session)
    ctx = {
        "summary": summary,
        "claimed_raffles": claimed_raffles
    }
    return render(request, "kuji/detail_old.html", ctx)


def kuji_detail_new(request, pk, *args, **kwargs):
    kuji_session = KujiSession.objects.filter(pk=pk).first()
    claimed_raffles = kuji_session.raffles.filter(claimed=True).values('id', 'name', 'tier')
    summary = summarize_kuji_session(kuji_session)
    ctx = {
        "summary": summary,
        "claimed_raffles": claimed_raffles
    }
    return render(request, "kuji/arena.html", ctx)


def marketplace(request, *args, **kwargs):
    return render(request, "kuji/marketplace.html", {})
