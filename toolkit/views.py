from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
import random

from catalogue.models import MobImplant, MobWeapon
from rules.randomizer import (
    generate_mobs,
    rebuild_mob,
    reroll_mob_role,
    serialize_mob,
)

from .forms import BestiaryMobSaveForm, MobAbilityForm, MobAbilityLibraryForm, UserWeaponForm, UserWeaponLibraryForm, UserImplantForm, UserImplantLibraryForm, TableMobResourceForm, TableConditionForm, TableWeaponRollForm, TableUniversalRollForm, EncounterCreateForm, EncounterMobAddForm, TableEncounterSaveForm, TableEncounterLoadForm, UserFolderForm, FolderMoveForm, MobFieldOverrideForm, MobImplantForm, MobRoleForm, MobWeaponForm, MonsterBuilderForm
from .models import BestiaryMob, Encounter, EncounterDraftMob, UserFolder, TableMob, TableCondition, UserAbility, UserWeapon, UserImplant
from .services import ensure_game_table


def _builder_redirect_editing(request, index):
    request.session["monster_builder_editing"] = index
    request.session.modified = True
    return redirect("monster_builder")


def _builder_clear_editing(request):
    request.session.pop("monster_builder_editing", None)
    request.session.modified = True



@login_required
def table_home(request):
    game_table = ensure_game_table(request.user)
    builder_mobs = list(game_table.builder_mobs.all())
    for mob in builder_mobs:
        payload = mob.payload
        mob.live_resources = (
            ("hp", "PV", f"{payload.get('current_hp', 0)}/{payload.get('max_hp', 0)}"),
            ("shield", "PB", payload.get("shield", 0)),
            ("reactions", "Réactions", payload.get("reactions", 0)),
            ("vigilance", "Vigilance", payload.get("vigilance", 0)),
        )
    roll_result = request.session.pop("table_roll_result", None)
    universal_roll_result = request.session.pop("universal_roll_result", None)
    return render(request, "toolkit/table.html", {
        "game_table": game_table,
        "instances": game_table.instances.all(),
        "builder_mobs": builder_mobs,
        "roll_result": roll_result,
        "universal_roll_result": universal_roll_result,
        "encounters": Encounter.objects.filter(owner=request.user).order_by("name"),
    })


@login_required
def monster_builder(request):
    weapons = list(MobWeapon.objects.all())
    implants = list(MobImplant.objects.all())
    user_weapons = list(UserWeapon.objects.filter(owner=request.user))
    user_implants = list(UserImplant.objects.filter(owner=request.user))
    generated_mobs = []
    editing_index = request.session.get("monster_builder_editing")
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
        "initial_resources": {
            "shield": mob["shield"],
            "reactions": mob["reactions"],
            "vigilance": mob["vigilance"],
        },
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
    folders = UserFolder.objects.filter(owner=request.user)
    folder_filter = request.GET.get("folder", "all")
    mobs = BestiaryMob.objects.filter(owner=request.user).select_related("folder").order_by("name", "id")
    if folder_filter == "unclassified":
        mobs = mobs.filter(folder__isnull=True)
    elif folder_filter != "all":
        try:
            folder_id = int(folder_filter)
        except ValueError:
            folder_filter = "all"
        else:
            if folders.filter(id=folder_id).exists():
                mobs = mobs.filter(folder_id=folder_id)
            else:
                folder_filter = "all"
    return render(request, "toolkit/bestiary.html", {
        "bestiary_mobs": mobs,
        "folders": folders,
        "folder_filter": folder_filter,
    })


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


@login_required
def table_next_round(request):
    if request.method != "POST":
        return redirect("table")
    table = ensure_game_table(request.user)
    for mob in table.builder_mobs.all():
        payload = dict(mob.payload)
        initial = payload.get("initial_resources", {})
        payload["reactions"] = int(initial.get("reactions", payload.get("reactions", 0)))
        payload["vigilance"] = int(initial.get("vigilance", payload.get("vigilance", 0)))
        mob.payload = payload
        mob.save(update_fields=["payload", "updated_at"])
    return redirect("table")


@login_required
def table_condition_add(request, mob_id):
    if request.method != "POST":
        return redirect("table")
    table = ensure_game_table(request.user)
    mob = TableMob.objects.filter(id=mob_id, game_table=table).first()
    form = TableConditionForm(request.POST)
    if mob is not None and form.is_valid():
        TableCondition.objects.create(mob=mob, name=form.cleaned_data["name"].strip())
    return redirect("table")


@login_required
def table_condition_delete(request, mob_id, condition_id):
    if request.method == "POST":
        table = ensure_game_table(request.user)
        TableCondition.objects.filter(
            id=condition_id, mob_id=mob_id, mob__game_table=table
        ).delete()
    return redirect("table")


@login_required
def table_mob_roll_weapon(request, mob_id, weapon_index):
    if request.method != "POST":
        return redirect("table")
    table = ensure_game_table(request.user)
    mob = TableMob.objects.filter(id=mob_id, game_table=table).first()
    form = TableWeaponRollForm(request.POST)
    if mob is None or not form.is_valid():
        return redirect("table")
    weapons = mob.payload.get("weapons", [])
    if not 0 <= weapon_index < len(weapons):
        return redirect("table")

    weapon = weapons[weapon_index]
    roll = random.randint(1, 20)
    modifier = form.cleaned_data.get("modifier") or 0
    threshold = 10 + int(weapon.get("aim", 0)) + modifier
    success = roll <= threshold
    roll_damage = (10 - roll) * 5
    damage = None
    if success:
        mode = form.cleaned_data.get("mode") or "default"
        if mode == "contact" and weapon.get("contact_damage") is not None:
            base = weapon["contact_damage"]
        elif mode == "distance" and weapon.get("distance_damage") is not None:
            base = weapon["distance_damage"]
        elif weapon.get("damage") is not None:
            base = weapon["damage"]
        elif weapon.get("distance_damage") is not None:
            base = weapon["distance_damage"]
        else:
            base = weapon.get("contact_damage", 0)
        damage = base + roll_damage

    request.session["table_roll_result"] = {
        "mob": mob.name, "weapon": weapon.get("name", "Arme"),
        "roll": roll, "aim": threshold, "modifier": modifier,
        "success": success, "damage": damage,
        "roll_damage": roll_damage if success else None,
    }
    request.session.modified = True
    return redirect("table")



@login_required
def table_mob_roll_stat(request, mob_id):
    if request.method != "POST":
        return redirect("table")
    table = ensure_game_table(request.user)
    mob = TableMob.objects.filter(id=mob_id, game_table=table).first()
    form = TableUniversalRollForm(request.POST)
    if mob is None or not form.is_valid():
        return redirect("table")

    stat = form.cleaned_data["stat"]
    labels = {
        "force": "FOR", "agility": "AGI", "perception": "PER",
        "technique": "TECH", "constitution": "CON", "willpower": "VOL",
    }
    value = int(mob.payload.get("stats", {}).get(stat, 10))
    modifier = form.cleaned_data.get("modifier") or 0
    threshold = value + modifier
    roll = random.randint(1, 20)

    request.session["table_roll_result"] = {
        "mob": mob.name, "weapon": labels[stat],
        "roll": roll, "aim": threshold, "modifier": modifier,
        "success": roll <= threshold, "damage": None, "roll_damage": None,
        "kind": "stat",
    }
    request.session.modified = True
    return redirect("table")


@login_required
def table_universal_roll(request):
    if request.method != "POST":
        return redirect("table")
    request.session["universal_roll_result"] = random.randint(1, 20)
    request.session.modified = True
    return redirect("table")



@login_required
def encounters_home(request):
    folders = UserFolder.objects.filter(owner=request.user)
    folder_filter = request.GET.get("folder", "all")
    encounters = Encounter.objects.filter(owner=request.user).select_related("folder").prefetch_related("draft_mobs")
    if folder_filter == "unclassified":
        encounters = encounters.filter(folder__isnull=True)
    elif folder_filter != "all":
        try:
            folder_id = int(folder_filter)
        except ValueError:
            folder_filter = "all"
        else:
            if folders.filter(id=folder_id).exists():
                encounters = encounters.filter(folder_id=folder_id)
            else:
                folder_filter = "all"
    bestiary = BestiaryMob.objects.filter(owner=request.user).order_by("name")
    return render(request, "toolkit/encounters.html", {
        "encounters": encounters, "bestiary_mobs": bestiary,
        "folders": folders, "folder_filter": folder_filter,
    })


@login_required
def encounter_create(request):
    if request.method == "POST":
        form = EncounterCreateForm(request.POST)
        if form.is_valid():
            Encounter.objects.create(owner=request.user, name=form.cleaned_data["name"].strip())
    return redirect("encounters")


@login_required
def encounter_add_mob(request, encounter_id):
    if request.method != "POST":
        return redirect("encounters")
    encounter = Encounter.objects.filter(id=encounter_id, owner=request.user).first()
    form = EncounterMobAddForm(request.POST)
    if encounter is None or not form.is_valid():
        return redirect("encounters")
    source = BestiaryMob.objects.filter(
        id=form.cleaned_data["bestiary_id"], owner=request.user
    ).first()
    if source is None or not source.draft_payload:
        return redirect("encounters")
    EncounterDraftMob.objects.create(
        encounter=encounter, name=source.name,
        quantity=form.cleaned_data["quantity"],
        payload=source.draft_payload,
        rank=encounter.draft_mobs.count(),
    )
    return redirect("encounters")


@login_required
def encounter_remove_mob(request, encounter_id, entry_id):
    if request.method == "POST":
        EncounterDraftMob.objects.filter(
            id=entry_id, encounter_id=encounter_id, encounter__owner=request.user
        ).delete()
    return redirect("encounters")


@login_required
def encounter_delete(request, encounter_id):
    if request.method == "POST":
        Encounter.objects.filter(id=encounter_id, owner=request.user).delete()
    return redirect("encounters")


@login_required
def encounter_duplicate(request, encounter_id):
    if request.method != "POST":
        return redirect("encounters")
    source = Encounter.objects.filter(id=encounter_id, owner=request.user).first()
    if source is None:
        return redirect("encounters")
    duplicate = Encounter.objects.create(owner=request.user, name=f"{source.name} — Copie")
    for entry in source.draft_mobs.all():
        EncounterDraftMob.objects.create(
            encounter=duplicate, name=entry.name, quantity=entry.quantity,
            payload=entry.payload, rank=entry.rank,
        )
    return redirect("encounters")


@login_required
def encounter_load_table(request, encounter_id):
    if request.method != "POST":
        return redirect("encounters")
    encounter = Encounter.objects.filter(id=encounter_id, owner=request.user).first()
    if encounter is None:
        return redirect("encounters")
    table = ensure_game_table(request.user)
    weapons = list(MobWeapon.objects.all())
    implants = list(MobImplant.objects.all())
    user_weapons = list(UserWeapon.objects.filter(owner=request.user))
    user_implants = list(UserImplant.objects.filter(owner=request.user))
    for entry in encounter.draft_mobs.all():
        for _ in range(entry.quantity):
            mob = rebuild_mob(weapons, implants, entry.payload, user_weapons, user_implants)
            TableMob.objects.create(
                game_table=table, name=entry.name, profile=str(mob["profile"]),
                level=mob["level"], payload=_table_payload(mob),
                rank=table.builder_mobs.count(),
            )
    return redirect("table")


@login_required
def table_save_encounter(request):
    if request.method != "POST":
        return redirect("table")
    form = TableEncounterSaveForm(request.POST)
    if not form.is_valid():
        return redirect("table")
    table = ensure_game_table(request.user)
    encounter = Encounter.objects.create(
        owner=request.user, name=form.cleaned_data["name"].strip()
    )
    for rank, table_mob in enumerate(table.builder_mobs.all()):
        draft = table_mob.payload.get("draft")
        if not draft:
            continue
        EncounterDraftMob.objects.create(
            encounter=encounter, name=table_mob.name,
            quantity=1, payload=draft, rank=rank,
        )
    return redirect("table")


@login_required
def table_load_encounter(request):
    if request.method != "POST":
        return redirect("table")
    form = TableEncounterLoadForm(request.POST)
    if not form.is_valid():
        return redirect("table")
    encounter = Encounter.objects.filter(
        id=form.cleaned_data["encounter_id"], owner=request.user
    ).first()
    if encounter is None:
        return redirect("table")
    table = ensure_game_table(request.user)
    weapons = list(MobWeapon.objects.all())
    implants = list(MobImplant.objects.all())
    user_weapons = list(UserWeapon.objects.filter(owner=request.user))
    user_implants = list(UserImplant.objects.filter(owner=request.user))
    for entry in encounter.draft_mobs.all():
        for _ in range(entry.quantity):
            mob = rebuild_mob(
                weapons, implants, entry.payload, user_weapons, user_implants
            )
            TableMob.objects.create(
                game_table=table, name=entry.name, profile=str(mob["profile"]),
                level=mob["level"], payload=_table_payload(mob),
                rank=table.builder_mobs.count(),
            )
    return redirect("table")


@login_required
def table_clear(request):
    if request.method != "POST":
        return redirect("table")
    table = ensure_game_table(request.user)
    table.builder_mobs.all().delete()
    table.instances.all().delete()
    request.session.pop("table_roll_result", None)
    request.session.pop("universal_roll_result", None)
    request.session.modified = True
    return redirect("table")


@login_required
def folder_create(request):
    if request.method == "POST":
        form = UserFolderForm(request.POST)
        if form.is_valid():
            UserFolder.objects.get_or_create(owner=request.user, name=form.cleaned_data["name"].strip())
    return redirect(request.POST.get("next") or "bestiary")


@login_required
def folder_delete(request, folder_id):
    if request.method == "POST":
        UserFolder.objects.filter(id=folder_id, owner=request.user).delete()
    return redirect(request.POST.get("next") or "bestiary")


def _move_to_folder(request, obj):
    raw = request.POST.get("folder_id", "")
    folder = None
    if raw:
        try:
            folder = UserFolder.objects.filter(id=int(raw), owner=request.user).first()
        except ValueError:
            return False
        if folder is None:
            return False
    obj.folder = folder
    obj.save(update_fields=["folder"])
    return True


@login_required
def bestiary_move_folder(request, mob_id):
    if request.method == "POST":
        mob = BestiaryMob.objects.filter(id=mob_id, owner=request.user).first()
        if mob is not None:
            _move_to_folder(request, mob)
    return redirect("bestiary")


@login_required
def encounter_move_folder(request, encounter_id):
    if request.method == "POST":
        encounter = Encounter.objects.filter(id=encounter_id, owner=request.user).first()
        if encounter is not None:
            _move_to_folder(request, encounter)
    return redirect("encounters")
