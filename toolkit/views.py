from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from catalogue.models import MobImplant, MobWeapon
from rules.randomizer import (
    generate_mobs,
    rebuild_mob,
    reroll_mob_role,
    serialize_mob,
)

from .forms import MobAbilityForm, MobFieldOverrideForm, MobImplantForm, MobRoleForm, MobWeaponForm, MonsterBuilderForm
from .models import TableMob
from .services import ensure_game_table


def _builder_redirect_editing(request, index):
    request.session["monster_builder_editing"] = index
    request.session.modified = True
    return redirect("monster_builder")



@login_required
def table_home(request):
    game_table = ensure_game_table(request.user)
    return render(request, "toolkit/table.html", {
        "game_table": game_table,
        "instances": game_table.instances.all(),
        "builder_mobs": game_table.builder_mobs.all(),
    })


@login_required
def monster_builder(request):
    weapons = list(MobWeapon.objects.all())
    implants = list(MobImplant.objects.all())
    generated_mobs = []
    editing_index = request.session.pop("monster_builder_editing", None)
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
            "editing_index": editing_index,
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
    return _builder_redirect_editing(request, index)


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
    return _builder_redirect_editing(request, index)


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
    return _builder_redirect_editing(request, index)


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
    return _builder_redirect_editing(request, index)


@login_required
def monster_builder_ability(request):
    if request.method != "POST":
        return redirect("monster_builder")

    form = MobAbilityForm(request.POST)
    saved = request.session.get("monster_builder_mobs", [])
    if not form.is_valid():
        return redirect("monster_builder")

    index = form.cleaned_data["index"]
    if not 0 <= index < len(saved):
        return redirect("monster_builder")

    data = saved[index]
    abilities = list(data.get("abilities", []))
    action = form.cleaned_data["action"]

    if action == "add":
        name = (form.cleaned_data.get("name") or "").strip()
        if not name:
            return _builder_redirect_editing(request, index)
        ability = {
            "name": name,
            "description": (form.cleaned_data.get("description") or "").strip(),
        }
        effect_type = form.cleaned_data.get("effect_type")
        value = form.cleaned_data.get("value")
        if effect_type and value is not None:
            ability["effect"] = {
                "type": effect_type,
                "scaling": form.cleaned_data.get("scaling") or "fixed",
                "value": value,
            }
        abilities.append(ability)
    elif action == "remove":
        ability_index = form.cleaned_data.get("ability_index")
        if ability_index is None or not 0 <= ability_index < len(abilities):
            return _builder_redirect_editing(request, index)
        abilities.pop(ability_index)

    data["abilities"] = abilities
    saved[index] = data
    request.session["monster_builder_mobs"] = saved
    request.session.modified = True
    return _builder_redirect_editing(request, index)


def _table_payload(mob):
    return {
        "max_hp": mob["max_hp"],
        "current_hp": mob["current_hp"],
        "armor": mob["armor"],
        "shield": mob["shield"],
        "reactions": mob["reactions"],
        "vigilance": mob["vigilance"],
        "stats": {
            "force": mob["stats"].force, "agility": mob["stats"].agility,
            "perception": mob["stats"].perception, "technique": mob["stats"].technique,
            "constitution": mob["stats"].constitution, "willpower": mob["stats"].willpower,
        },
        "stat_modifiers": mob["stat_modifiers"],
        "weapons": [
            {
                "name": card.weapon.name, "power": card.effective_power,
                "aim": card.effective_aim, "damage": card.neutral_damage,
                "contact_damage": card.contact_damage, "distance_damage": card.distance_damage,
                "property_name": card.weapon.property_name,
                "property_lines": list(card.property_lines),
            }
            for card in mob["weapon_cards"]
        ],
        "implants": [
            {
                "name": card.implant.name, "property_name": card.implant.property_name,
                "property_lines": list(card.property_lines),
            }
            for card in mob["implant_cards"]
        ],
        "abilities": mob["abilities"],
        "draft": serialize_mob(mob),
    }


@login_required
def monster_builder_validate(request):
    if request.method != "POST":
        return redirect("monster_builder")

    saved = request.session.get("monster_builder_mobs", [])
    action = request.POST.get("action")
    if action == "all":
        indexes = list(range(len(saved)))
    else:
        try:
            indexes = [int(request.POST.get("index", "-1"))]
        except ValueError:
            return redirect("monster_builder")

    weapons = list(MobWeapon.objects.all())
    implants = list(MobImplant.objects.all())
    table = ensure_game_table(request.user)
    valid_indexes = [index for index in indexes if 0 <= index < len(saved)]

    for index in valid_indexes:
        mob = rebuild_mob(weapons, implants, saved[index])
        TableMob.objects.create(
            game_table=table,
            name=f"{mob['profile'].label if hasattr(mob['profile'], 'label') else mob['profile']} N{mob['level']}",
            profile=str(mob["profile"]),
            level=mob["level"],
            payload=_table_payload(mob),
            rank=table.builder_mobs.count(),
        )

    for index in sorted(valid_indexes, reverse=True):
        saved.pop(index)
    request.session["monster_builder_mobs"] = saved
    request.session.modified = True
    return redirect("monster_builder")


@login_required
def table_mob_edit(request, mob_id):
    if request.method != "POST":
        return redirect("table")
    table = ensure_game_table(request.user)
    mob = TableMob.objects.filter(id=mob_id, game_table=table).first()
    if mob is None:
        return redirect("table")

    saved = request.session.get("monster_builder_mobs", [])
    saved.append(mob.payload["draft"])
    request.session["monster_builder_mobs"] = saved
    request.session["monster_builder_editing"] = len(saved) - 1
    request.session.modified = True
    mob.delete()
    return redirect("monster_builder")


@login_required
def table_mob_delete(request, mob_id):
    if request.method != "POST":
        return redirect("table")
    table = ensure_game_table(request.user)
    TableMob.objects.filter(id=mob_id, game_table=table).delete()
    return redirect("table")
