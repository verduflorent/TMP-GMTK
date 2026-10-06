from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from catalogue.models import MobImplant, MobWeapon
from rules.randomizer import generate_mobs

from .forms import MonsterBuilderForm
from .services import ensure_game_table


@login_required
def table_home(request):
    game_table = ensure_game_table(request.user)
    return render(
        request,
        "toolkit/table.html",
        {"game_table": game_table, "instances": game_table.instances.all()},
    )


@login_required
def monster_builder(request):
    generated_mobs = []
    form = MonsterBuilderForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        generated_mobs = generate_mobs(
            list(MobWeapon.objects.all()),
            list(MobImplant.objects.all()),
            quantity=form.cleaned_data["quantity"],
            level=form.cleaned_data["level"],
        )

    return render(
        request,
        "toolkit/monster_builder.html",
        {"form": form, "generated_mobs": generated_mobs},
    )
