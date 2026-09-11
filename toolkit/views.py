from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .services import ensure_game_table


@login_required
def table_home(request):
    game_table = ensure_game_table(request.user)
    return render(
        request,
        "toolkit/table.html",
        {
            "game_table": game_table,
            "allies": game_table.instances.filter(camp="ALLY"),
            "enemies": game_table.instances.filter(camp="ENEMY"),
        },
    )
