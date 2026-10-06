from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from catalogue.models import MobImplant, MobWeapon
from rules.randomizer import (
    generate_mobs,
    rebuild_mob,
    reroll_mob_role,
    serialize_mob,
)

from .forms import MobRoleForm, MobWeaponForm, MonsterBuilderForm
from .services import ensure_game_table


@login_required
def table_home(request):
    game_table = ensure_game_table(request.user)
    return render(request, "toolkit/table.html", {"game_table": game_table, "instances": game_table.instances.all()})


@login_required
def monster_builder(request):
    weapons = list(MobWeapon.objects.all())
    implants = list(MobImplant.objects.all())
    generated_mobs = []
    form = MonsterBuilderForm(request.POST or None)

    if request.method == "POST" and request.POST.get("action") == "generate" and form.is_valid():
        generated_mobs = generate_mobs(
            weapons, implants,
            quantity=form.cleaned_data["quantity"],
            level=form.cleaned_data["level"],
        )
        request.session["monster_builder_mobs"] = [serialize_mob(mob) for mob in generated_mobs]
    else:
        saved = request.session.get("monster_builder_mobs", [])
        generated_mobs = [rebuild_mob(weapons, implants, data) for data in saved]

    profile_labels = {
        "": "Commun", "C": "Combattant", "A": "Assassin",
        "T": "Tireur", "S": "Soutien", "K": "Contrôle",
    }
    weapon_groups = []
    for code in ("", "C", "A", "T", "S", "K"):
        group = sorted(
            [weapon for weapon in weapons if weapon.allowed_profiles == code],
            key=lambda weapon: (weapon.tier, weapon.name),
        )
        if group:
            weapon_groups.append((profile_labels[code], group))

    return render(
        request,
        "toolkit/monster_builder.html",
        {
            "form": form,
            "generated_mobs": generated_mobs,
            "weapon_groups": weapon_groups,
        },
    )


@login_required
def monster_builder_role(request):
    if request.method != "POST":
        return redirect("monster_builder")

    form = MobRoleForm(request.POST)
    saved = request.session.get("monster_builder_mobs", [])
    if not form.is_valid():
        return redirect("monster_builder")

    index = form.cleaned_data["index"]
    if not 0 <= index < len(saved):
        return redirect("monster_builder")

    weapons = list(MobWeapon.objects.all())
    implants = list(MobImplant.objects.all())
    current = saved[index]
    rerolled = reroll_mob_role(
        weapons, implants,
        level=current["level"],
        profile=form.cleaned_data["profile"],
    )
    saved[index] = serialize_mob(rerolled)
    request.session["monster_builder_mobs"] = saved
    request.session.modified = True
    return redirect("monster_builder")


@login_required
def monster_builder_weapon(request):
    if request.method != "POST":
        return redirect("monster_builder")

    form = MobWeaponForm(request.POST)
    saved = request.session.get("monster_builder_mobs", [])
    if not form.is_valid():
        return redirect("monster_builder")

    index = form.cleaned_data["index"]
    if not 0 <= index < len(saved):
        return redirect("monster_builder")

    weapons = list(MobWeapon.objects.all())
    weapon_by_id = {weapon.id: weapon for weapon in weapons}
    selected = weapon_by_id.get(form.cleaned_data["weapon_id"])
    if selected is None:
        return redirect("monster_builder")

    data = saved[index]
    weapon_ids = list(data.get("weapon_ids", []))
    if not weapon_ids:
        return redirect("monster_builder")

    slot = form.cleaned_data["slot"]
    if slot == "primary":
        weapon_ids[0] = selected.id
    else:
        if len(weapon_ids) >= 2:
            weapon_ids[1] = selected.id
        else:
            weapon_ids.append(selected.id)

    data["weapon_ids"] = weapon_ids
    saved[index] = data
    request.session["monster_builder_mobs"] = saved
    request.session.modified = True
    return redirect("monster_builder")
