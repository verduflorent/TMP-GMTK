from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from catalogue.models import MobImplant, MobWeapon
from rules.randomizer import (
    generate_mobs,
    rebuild_mob,
    reroll_mob_role,
    serialize_mob,
)

from .forms import MobFieldOverrideForm, MobImplantForm, MobRoleForm, MobWeaponForm, MonsterBuilderForm
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

    for mob in generated_mobs:
        mob["editable_derived"] = (
            ("armor", "Armure", mob["armor"]),
            ("shield", "PB", mob["shield"]),
            ("reactions", "Réactions", mob["reactions"]),
            ("vigilance", "Vigilance", mob["vigilance"]),
        )

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

    implant_groups = []
    for code in ("C", "A", "T", "S", "K"):
        group = sorted(
            [implant for implant in implants if code in implant.allowed_profiles],
            key=lambda implant: implant.name,
        )
        if group:
            implant_groups.append((profile_labels[code], group))

    return render(
        request,
        "toolkit/monster_builder.html",
        {
            "form": form,
            "generated_mobs": generated_mobs,
            "weapon_groups": weapon_groups,
            "implant_groups": implant_groups,
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

    data = saved[index]
    weapon_ids = list(data.get("weapon_ids", []))
    action = form.cleaned_data["action"]
    weapon_index = form.cleaned_data.get("weapon_index")
    weapon_id = form.cleaned_data.get("weapon_id")

    if action in ("add", "replace"):
        if weapon_id is None or not MobWeapon.objects.filter(id=weapon_id).exists():
            return redirect("monster_builder")

    if action == "add":
        weapon_ids.append(weapon_id)
    elif action == "replace":
        if weapon_index is None or not 0 <= weapon_index < len(weapon_ids):
            return redirect("monster_builder")
        weapon_ids[weapon_index] = weapon_id
    elif action == "remove":
        if weapon_index is None or not 0 <= weapon_index < len(weapon_ids):
            return redirect("monster_builder")
        # Keep one weapon until the zero-weapon draft renderer is implemented.
        if len(weapon_ids) <= 1:
            return redirect("monster_builder")
        weapon_ids.pop(weapon_index)

    data["weapon_ids"] = weapon_ids
    saved[index] = data
    request.session["monster_builder_mobs"] = saved
    request.session.modified = True
    return redirect("monster_builder")


@login_required
def monster_builder_field(request):
    if request.method != "POST":
        return redirect("monster_builder")

    form = MobFieldOverrideForm(request.POST)
    saved = request.session.get("monster_builder_mobs", [])
    if not form.is_valid():
        return redirect("monster_builder")

    index = form.cleaned_data["index"]
    if not 0 <= index < len(saved):
        return redirect("monster_builder")

    data = saved[index]
    overrides = dict(data.get("overrides", {}))
    overrides[form.cleaned_data["field"]] = form.cleaned_data["value"]
    data["overrides"] = overrides
    saved[index] = data
    request.session["monster_builder_mobs"] = saved
    request.session.modified = True
    return redirect("monster_builder")


@login_required
def monster_builder_implant(request):
    if request.method != "POST":
        return redirect("monster_builder")

    form = MobImplantForm(request.POST)
    saved = request.session.get("monster_builder_mobs", [])
    if not form.is_valid():
        return redirect("monster_builder")

    index = form.cleaned_data["index"]
    if not 0 <= index < len(saved):
        return redirect("monster_builder")

    data = saved[index]
    implant_ids = list(data.get("implant_ids", []))
    action = form.cleaned_data["action"]
    implant_index = form.cleaned_data.get("implant_index")
    implant_id = form.cleaned_data.get("implant_id")

    if action in ("add", "replace"):
        if implant_id is None or not MobImplant.objects.filter(id=implant_id).exists():
            return redirect("monster_builder")

    if action == "add":
        implant_ids.append(implant_id)
    elif action == "replace":
        if implant_index is None or not 0 <= implant_index < len(implant_ids):
            return redirect("monster_builder")
        implant_ids[implant_index] = implant_id
    elif action == "remove":
        if implant_index is None or not 0 <= implant_index < len(implant_ids):
            return redirect("monster_builder")
        implant_ids.pop(implant_index)

    data["implant_ids"] = implant_ids
    saved[index] = data
    request.session["monster_builder_mobs"] = saved
    request.session.modified = True
    return redirect("monster_builder")
