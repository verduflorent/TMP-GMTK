from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from catalogue.models import MobImplant, MobWeapon
from rules.randomizer import (
    generate_mobs,
    rebuild_mob,
    reroll_mob_role,
    serialize_mob,
)

from .forms import BestiaryMobSaveForm, MobAbilityForm, MobAbilityLibraryForm, UserWeaponForm, UserWeaponLibraryForm, UserImplantForm, UserImplantLibraryForm, TableMobResourceForm, MobFieldOverrideForm, MobImplantForm, MobRoleForm, MobWeaponForm, MonsterBuilderForm
from .models import BestiaryMob, TableMob, UserAbility, UserWeapon, UserImplant
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
    user_weapons = list(UserWeapon.objects.filter(owner=request.user))
    user_implants = list(UserImplant.objects.filter(owner=request.user))
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
        generated_mobs = [rebuild_mob(weapons, implants, data, user_weapons, user_implants) for data in saved]

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
            "user_abilities": UserAbility.objects.filter(owner=request.user),
            "user_weapons": user_weapons,
            "user_implants": user_implants,
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
    refs = data.get("weapons")
    if refs is None:
        refs = [{"source": "catalogue", "id": item_id} for item_id in data.get("weapon_ids", [])]
    refs = list(refs)
    action = form.cleaned_data["action"]
    weapon_index = form.cleaned_data.get("weapon_index")
    weapon_id = form.cleaned_data.get("weapon_id")

    if action in ("add", "replace") and (
        weapon_id is None or not MobWeapon.objects.filter(id=weapon_id).exists()
    ):
        return _builder_redirect_editing(request, index)

    ref = {"source": "catalogue", "id": weapon_id}
    if action == "add":
        refs.append(ref)
    elif action == "replace":
        if weapon_index is None or not 0 <= weapon_index < len(refs):
            return _builder_redirect_editing(request, index)
        refs[weapon_index] = ref
    elif action == "remove":
        if weapon_index is None or not 0 <= weapon_index < len(refs) or len(refs) <= 1:
            return _builder_redirect_editing(request, index)
        refs.pop(weapon_index)

    data["weapons"] = refs
    data.pop("weapon_ids", None)
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
    field = form.cleaned_data["field"]
    value = form.cleaned_data["value"]
    if field == "level":
        if value < 1 or value > 99:
            return _builder_redirect_editing(request, index)
        data["level"] = value
    else:
        overrides = dict(data.get("overrides", {}))
        overrides[field] = value
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
    refs = data.get("implants")
    if refs is None:
        refs = [{"source": "catalogue", "id": item_id} for item_id in data.get("implant_ids", [])]
    refs = list(refs)
    action = form.cleaned_data["action"]
    implant_index = form.cleaned_data.get("implant_index")
    implant_id = form.cleaned_data.get("implant_id")
    if action in ("add", "replace") and (
        implant_id is None or not MobImplant.objects.filter(id=implant_id).exists()
    ):
        return _builder_redirect_editing(request, index)
    ref = {"source": "catalogue", "id": implant_id}
    if action == "add":
        refs.append(ref)
    elif action == "replace":
        if implant_index is None or not 0 <= implant_index < len(refs):
            return _builder_redirect_editing(request, index)
        refs[implant_index] = ref
    elif action == "remove":
        if implant_index is None or not 0 <= implant_index < len(refs):
            return _builder_redirect_editing(request, index)
        refs.pop(implant_index)

    data["implants"] = refs
    data.pop("implant_ids", None)
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
        if form.cleaned_data.get("save_to_library"):
            effect = ability.get("effect", {})
            UserAbility.objects.create(
                owner=request.user,
                name=ability["name"],
                description=ability["description"],
                effect_type=effect.get("type", ""),
                scaling=effect.get("scaling", "fixed"),
                value=effect.get("value", 0),
            )
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
    user_weapons = list(UserWeapon.objects.filter(owner=request.user))
    user_implants = list(UserImplant.objects.filter(owner=request.user))
    table = ensure_game_table(request.user)
    valid_indexes = [index for index in indexes if 0 <= index < len(saved)]

    for index in valid_indexes:
        mob = rebuild_mob(weapons, implants, saved[index], user_weapons)
        TableMob.objects.create(
            game_table=table,
            name=mob.get("name") or f"{mob['profile'].label if hasattr(mob['profile'], 'label') else mob['profile']} N{mob['level']}",
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


@login_required
def bestiary_home(request):
    mobs = BestiaryMob.objects.filter(owner=request.user).order_by("name", "id")
    return render(request, "toolkit/bestiary.html", {"bestiary_mobs": mobs})


@login_required
def monster_builder_save(request):
    if request.method != "POST":
        return redirect("monster_builder")
    form = BestiaryMobSaveForm(request.POST)
    saved = request.session.get("monster_builder_mobs", [])
    if not form.is_valid():
        return redirect("monster_builder")
    index = form.cleaned_data["index"]
    if not 0 <= index < len(saved):
        return redirect("monster_builder")

    data = dict(saved[index])
    data["name"] = form.cleaned_data["name"].strip()
    saved[index] = data
    request.session["monster_builder_mobs"] = saved
    request.session.modified = True
    BestiaryMob.objects.create(
        owner=request.user,
        name=form.cleaned_data["name"].strip(),
        profile=data["profile"],
        level=data["level"],
        draft_payload=data,
    )
    return _builder_redirect_editing(request, index)


@login_required
def bestiary_load(request, mob_id):
    if request.method != "POST":
        return redirect("bestiary")
    mob = BestiaryMob.objects.filter(id=mob_id, owner=request.user).first()
    if mob is None or not mob.draft_payload:
        return redirect("bestiary")
    saved = request.session.get("monster_builder_mobs", [])
    try:
        quantity = max(1, min(50, int(request.POST.get("quantity", "1"))))
    except ValueError:
        quantity = 1
    first_index = len(saved)
    for _ in range(quantity):
        draft = dict(mob.draft_payload)
        draft["name"] = mob.name
        saved.append(draft)
    request.session["monster_builder_mobs"] = saved
    request.session["monster_builder_editing"] = first_index
    request.session.modified = True
    return redirect("monster_builder")


@login_required
def bestiary_delete(request, mob_id):
    if request.method == "POST":
        BestiaryMob.objects.filter(id=mob_id, owner=request.user).delete()
    return redirect("bestiary")


@login_required
def bestiary_duplicate(request, mob_id):
    if request.method != "POST":
        return redirect("bestiary")
    source = BestiaryMob.objects.filter(id=mob_id, owner=request.user).first()
    if source is not None:
        source.pk = None
        source.name = f"{source.name} — Copie"
        source.save()
    return redirect("bestiary")


@login_required
def monster_builder_ability_library(request):
    if request.method != "POST":
        return redirect("monster_builder")
    form = MobAbilityLibraryForm(request.POST)
    saved = request.session.get("monster_builder_mobs", [])
    if not form.is_valid():
        return redirect("monster_builder")
    index = form.cleaned_data["index"]
    if not 0 <= index < len(saved):
        return redirect("monster_builder")
    ability = UserAbility.objects.filter(
        id=form.cleaned_data["ability_id"], owner=request.user
    ).first()
    if ability is None:
        return _builder_redirect_editing(request, index)
    data = saved[index]
    abilities = list(data.get("abilities", []))
    abilities.append(ability.as_draft())
    data["abilities"] = abilities
    saved[index] = data
    request.session["monster_builder_mobs"] = saved
    request.session.modified = True
    return _builder_redirect_editing(request, index)


@login_required
def ability_library_delete(request, ability_id):
    if request.method == "POST":
        UserAbility.objects.filter(id=ability_id, owner=request.user).delete()
    return redirect("monster_builder")


@login_required
def monster_builder_user_weapon_create(request):
    if request.method != "POST":
        return redirect("monster_builder")
    form = UserWeaponForm(request.POST)
    saved = request.session.get("monster_builder_mobs", [])
    if not form.is_valid():
        return redirect("monster_builder")
    index = form.cleaned_data["index"]
    if not 0 <= index < len(saved):
        return redirect("monster_builder")
    weapon = UserWeapon.objects.create(
        owner=request.user,
        name=form.cleaned_data["name"].strip(),
        hands=int(form.cleaned_data["hands"]),
        optimal_range=form.cleaned_data["optimal_range"],
        power=form.cleaned_data["power"],
        aim=form.cleaned_data["aim"],
        property_name=(form.cleaned_data.get("property_name") or "").strip(),
        property_text=(form.cleaned_data.get("property_text") or "").strip(),
    )
    data = saved[index]
    refs = list(data.get("weapons", []))
    refs.append({"source": "user", "id": weapon.id})
    data["weapons"] = refs
    data.pop("weapon_ids", None)
    saved[index] = data
    request.session["monster_builder_mobs"] = saved
    request.session.modified = True
    return _builder_redirect_editing(request, index)


@login_required
def monster_builder_user_weapon_add(request):
    if request.method != "POST":
        return redirect("monster_builder")
    form = UserWeaponLibraryForm(request.POST)
    saved = request.session.get("monster_builder_mobs", [])
    if not form.is_valid():
        return redirect("monster_builder")
    index = form.cleaned_data["index"]
    if not 0 <= index < len(saved):
        return redirect("monster_builder")
    weapon = UserWeapon.objects.filter(
        id=form.cleaned_data["weapon_id"], owner=request.user
    ).first()
    if weapon is None:
        return _builder_redirect_editing(request, index)
    data = saved[index]
    refs = list(data.get("weapons", []))
    refs.append({"source": "user", "id": weapon.id})
    data["weapons"] = refs
    data.pop("weapon_ids", None)
    saved[index] = data
    request.session["monster_builder_mobs"] = saved
    request.session.modified = True
    return _builder_redirect_editing(request, index)


@login_required
def monster_builder_user_implant_create(request):
    if request.method != "POST":
        return redirect("monster_builder")
    form = UserImplantForm(request.POST)
    saved = request.session.get("monster_builder_mobs", [])
    if not form.is_valid():
        return redirect("monster_builder")
    index = form.cleaned_data["index"]
    if not 0 <= index < len(saved):
        return redirect("monster_builder")
    implant = UserImplant.objects.create(
        owner=request.user, name=form.cleaned_data["name"].strip(),
        property_name=(form.cleaned_data.get("property_name") or "").strip(),
        property_text=(form.cleaned_data.get("property_text") or "").strip(),
    )
    data = saved[index]
    refs = list(data.get("implants", []))
    refs.append({"source": "user", "id": implant.id})
    data["implants"] = refs
    data.pop("implant_ids", None)
    saved[index] = data
    request.session["monster_builder_mobs"] = saved
    request.session.modified = True
    return _builder_redirect_editing(request, index)


@login_required
def monster_builder_user_implant_add(request):
    if request.method != "POST":
        return redirect("monster_builder")
    form = UserImplantLibraryForm(request.POST)
    saved = request.session.get("monster_builder_mobs", [])
    if not form.is_valid():
        return redirect("monster_builder")
    index = form.cleaned_data["index"]
    if not 0 <= index < len(saved):
        return redirect("monster_builder")
    implant = UserImplant.objects.filter(
        id=form.cleaned_data["implant_id"], owner=request.user
    ).first()
    if implant is None:
        return _builder_redirect_editing(request, index)
    data = saved[index]
    refs = list(data.get("implants", []))
    refs.append({"source": "user", "id": implant.id})
    data["implants"] = refs
    data.pop("implant_ids", None)
    saved[index] = data
    request.session["monster_builder_mobs"] = saved
    request.session.modified = True
    return _builder_redirect_editing(request, index)


@login_required
def table_mob_resource(request, mob_id):
    if request.method != "POST":
        return redirect("table")
    table = ensure_game_table(request.user)
    mob = TableMob.objects.filter(id=mob_id, game_table=table).first()
    form = TableMobResourceForm(request.POST)
    if mob is None or not form.is_valid():
        return redirect("table")

    payload = dict(mob.payload)
    resource = form.cleaned_data["resource"]
    action = form.cleaned_data["action"]
    value = form.cleaned_data.get("value") or 0
    key_map = {"hp": "current_hp", "shield": "shield", "reactions": "reactions", "vigilance": "vigilance"}
    key = key_map[resource]
    current = int(payload.get(key, 0))

    if action == "add":
        current += value
    elif action == "subtract":
        current = max(0, current - value)
    elif action == "set":
        current = value
    elif action == "reset":
        if resource == "hp":
            current = int(payload.get("max_hp", current))
        else:
            initial = payload.get("initial_resources", {})
            current = int(initial.get(key, current))

    if resource == "hp":
        current = min(current, int(payload.get("max_hp", current)))
    payload[key] = current
    mob.payload = payload
    mob.save(update_fields=["payload", "updated_at"])
    return redirect("table")
