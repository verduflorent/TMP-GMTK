import random

from catalogue.models import MobProfile


PROFILE_WEIGHTS = {
    MobProfile.COMBATANT: 3,
    MobProfile.ASSASSIN: 4,
    MobProfile.TIREUR: 5,
    MobProfile.SOUTIEN: 2,
    MobProfile.CONTROLE: 2,
}

LIMITED_PROFILES = (MobProfile.SOUTIEN, MobProfile.CONTROLE)

# Design anchors supplied by the MJ. Intermediate levels are linearly interpolated.
TIER_ANCHORS = {
    1: (80.0, 20.0, 0.0, 0.0),
    3: (70.0, 25.0, 5.0, 0.0),
    6: (50.0, 35.0, 10.0, 5.0),
}
TIER_CAP = (30.0, 40.0, 20.0, 10.0)
TIER_CAP_LEVEL = 20


def specialist_cap(quantity: int) -> int:
    """Maximum number of each limited profile in a generated group."""
    _validate_quantity(quantity)
    if quantity <= 4:
        return 1
    if quantity <= 10:
        return 2
    return 1 + quantity // 5


def generate_profiles(quantity: int, rng=None) -> list[str]:
    """Generate profile codes using weights while enforcing S/K group caps."""
    _validate_quantity(quantity)
    rng = rng or random
    cap = specialist_cap(quantity)
    combatant_cap = 1 if quantity <= 4 else 2 if quantity <= 10 else 1 + quantity // 5
    counts = {profile: 0 for profile in PROFILE_WEIGHTS}
    generated = []

    for _ in range(quantity):
        candidates = [
            profile
            for profile in PROFILE_WEIGHTS
            if (
                (profile not in LIMITED_PROFILES or counts[profile] < cap)
                and (profile != MobProfile.COMBATANT or counts[profile] < combatant_cap)
            )
        ]
        weights = [PROFILE_WEIGHTS[profile] for profile in candidates]
        selected = rng.choices(candidates, weights=weights, k=1)[0]
        generated.append(selected)
        counts[selected] += 1

    return generated


def tier_weights(level: int) -> tuple[float, float, float, float]:
    """Return T1..T4 weights for a level, interpolating between design anchors."""
    _validate_level(level)

    if level in TIER_ANCHORS:
        return TIER_ANCHORS[level]

    if level < 3:
        # T3 is hard-locked before N3: interpolate only T1/T2.
        progress = (level - 1) / 2
        t1 = TIER_ANCHORS[1][0] + (TIER_ANCHORS[3][0] - TIER_ANCHORS[1][0]) * progress
        return (t1, 100.0 - t1, 0.0, 0.0)

    if level < 6:
        # T4 is hard-locked before N6: interpolate T1/T2/T3 only.
        progress = (level - 3) / 3
        start = TIER_ANCHORS[3]
        end = TIER_ANCHORS[6]
        first_three = tuple(
            start[index] + (end[index] - start[index]) * progress
            for index in range(3)
        )
        total = sum(first_three)
        return tuple(value * 100.0 / total for value in first_three) + (0.0,)

    if level >= TIER_CAP_LEVEL:
        return TIER_CAP

    return _interpolate(
        TIER_ANCHORS[6],
        TIER_CAP,
        (level - 6) / (TIER_CAP_LEVEL - 6),
    )


def choose_weapon_tier(level: int, rng=None) -> int:
    rng = rng or random
    weights = tier_weights(level)
    return rng.choices((1, 2, 3, 4), weights=weights, k=1)[0]


def compatible_weapons(weapons, *, profile: str, tier: int):
    """Filter a supplied weapon collection without querying the database."""
    return [
        weapon
        for weapon in weapons
        if weapon.tier == tier and weapon.supports_profile(profile)
    ]


def choose_primary_weapon(weapons, *, profile: str, level: int, rng=None):
    """Choose a compatible primary weapon. Falls back only to lower accessible tiers."""
    rng = rng or random
    requested_tier = choose_weapon_tier(level, rng)

    for tier in range(requested_tier, 0, -1):
        candidates = compatible_weapons(weapons, profile=profile, tier=tier)
        if candidates:
            return rng.choice(candidates)

    raise ValueError(f"Aucune arme compatible disponible pour le profil {profile}.")


def should_add_secondary(primary_weapon, rng=None) -> bool:
    """T4 and Med Rifle always get a sidearm; other weapons have a 20% chance."""
    rng = rng or random
    return (
        primary_weapon.tier == 4
        or primary_weapon.name == "Med Rifle"
        or rng.random() < 0.20
    )


def choose_secondary_weapon(weapons, *, profile: str, primary_weapon, rng=None):
    """Choose a simple T1/T2 sidearm compatible with the Mob profile."""
    rng = rng or random
    if not should_add_secondary(primary_weapon, rng):
        return None

    candidates = [
        weapon
        for weapon in weapons
        if (
            weapon.tier in (1, 2)
            and weapon.supports_profile(profile)
            and weapon.name != primary_weapon.name
        )
    ]
    if not candidates:
        return None
    return rng.choice(candidates)


def should_use_akimbo(primary_weapon, rng=None) -> bool:
    """Akimbo has a 10% chance and requires a one-handed primary weapon."""
    rng = rng or random
    return primary_weapon.hands == 1 and rng.random() < 0.10


def choose_akimbo_pair(weapons, *, profile: str, primary_weapon, level: int, rng=None):
    """Return an Akimbo pair, 80% identical and 20% mixed, or None."""
    rng = rng or random
    if not should_use_akimbo(primary_weapon, rng):
        return None

    unlocked_tiers = {
        tier
        for tier, weight in enumerate(tier_weights(level), start=1)
        if weight > 0
    }
    candidates = [
        weapon
        for weapon in weapons
        if (
            weapon.hands == 1
            and weapon.tier in unlocked_tiers
            and weapon.supports_profile(profile)
        )
    ]
    if not candidates:
        return None

    # 80%: same weapon twice.
    if rng.random() < 0.80:
        return primary_weapon, primary_weapon

    # 20%: mixed pair. The second weapon must actually differ.
    different = [weapon for weapon in candidates if weapon.name != primary_weapon.name]
    if not different:
        return primary_weapon, primary_weapon
    return primary_weapon, rng.choice(different)


def choose_weapon_loadout(weapons, *, profile: str, level: int, rng=None):
    """Generate primary + optional secondary/Akimbo without stacking both modes."""
    rng = rng or random
    primary = choose_primary_weapon(weapons, profile=profile, level=level, rng=rng)

    akimbo = choose_akimbo_pair(
        weapons, profile=profile, primary_weapon=primary, level=level, rng=rng
    )
    if akimbo is not None:
        return {"primary": akimbo[0], "secondary": akimbo[1], "akimbo": True}

    secondary = choose_secondary_weapon(
        weapons, profile=profile, primary_weapon=primary, rng=rng
    )
    return {"primary": primary, "secondary": secondary, "akimbo": False}



# Independent implant-slot chances. Values between anchors are interpolated.
# Locked slots stay at 0 until their unlock level.
IMPLANT_SLOT_ANCHORS = {
    1: (0.20, 0.00, 0.00),
    3: (0.30, 0.00, 0.00),
    4: (0.50, 0.10, 0.00),
    6: (0.70, 0.25, 0.00),
    7: (0.85, 0.50, 0.10),
    10: (1.00, 0.70, 0.25),
    15: (1.00, 1.00, 0.50),
    20: (1.00, 1.00, 0.75),
}


def implant_slot_chances(level: int) -> tuple[float, float, float]:
    """Return independent fill chances for implant slots 1..3."""
    _validate_level(level)
    levels = sorted(IMPLANT_SLOT_ANCHORS)

    if level >= levels[-1]:
        return IMPLANT_SLOT_ANCHORS[levels[-1]]
    if level in IMPLANT_SLOT_ANCHORS:
        return IMPLANT_SLOT_ANCHORS[level]

    lower = max(anchor for anchor in levels if anchor < level)
    upper = min(anchor for anchor in levels if anchor > level)
    progress = (level - lower) / (upper - lower)
    start = IMPLANT_SLOT_ANCHORS[lower]
    end = IMPLANT_SLOT_ANCHORS[upper]
    return tuple(a + (b - a) * progress for a, b in zip(start, end))


def roll_implant_slots(level: int, rng=None) -> list[int]:
    """Roll each unlocked implant slot independently and return successful slot numbers."""
    rng = rng or random
    chances = implant_slot_chances(level)
    return [
        index
        for index, chance in enumerate(chances, start=1)
        if chance > 0 and rng.random() < chance
    ]


def compatible_implants(implants, *, profile: str):
    return [implant for implant in implants if implant.supports_profile(profile)]


def choose_implants(implants, *, profile: str, level: int, rng=None):
    """Fill successful slots with compatible implants, compacted for display.

    Duplicates are avoided while enough distinct compatible implants exist.
    """
    rng = rng or random
    successful_slots = roll_implant_slots(level, rng)
    pool = compatible_implants(implants, profile=profile)
    if not pool or not successful_slots:
        return []

    selected = []
    available = list(pool)
    for _slot in successful_slots:
        if not available:
            break
        implant = rng.choice(available)
        selected.append(implant)
        available.remove(implant)

    return selected


def _assemble_mob(*, level, profile, primary, secondary, akimbo, implants):
    from rules.engine import (
        ResolvedWeapon, apply_weapon_damage_bonuses, base_damage,
        implant_armor_bonus, implant_damage_bonuses, profile_derived,
        profile_stats, resolve_implant, resolve_weapon, round_to_5,
        stat_modifier, tech_support_bonus,
    )
    stats = profile_stats(profile, level)
    derived = profile_derived(profile, level)
    primary_card = resolve_weapon(primary, level, perception=stats.perception, technique=stats.technique)
    secondary_card = (
        resolve_weapon(secondary, level, perception=stats.perception, technique=stats.technique)
        if secondary is not None else None
    )
    akimbo_identical = bool(akimbo and secondary is not None and primary.name == secondary.name)
    if akimbo_identical:
        combined_power = primary_card.effective_power + secondary_card.effective_power
        primary_card = ResolvedWeapon(
            primary, combined_power, round_to_5(base_damage(level) + combined_power * 2),
            primary_card.effective_aim, primary_card.resolved_property,
            primary_card.property_lines,
        )
    contact_bonus, distance_bonus = implant_damage_bonuses(implants, level)
    primary_card = apply_weapon_damage_bonuses(
        primary_card,
        contact_bonus=contact_bonus,
        distance_bonus=distance_bonus,
    )
    if secondary_card is not None:
        secondary_card = apply_weapon_damage_bonuses(
            secondary_card,
            contact_bonus=contact_bonus,
            distance_bonus=distance_bonus,
        )

    implant_cards = [
        resolve_implant(item, level, derived.max_hp, technique=stats.technique)
        for item in implants
    ]
    return {
        "profile": profile, "level": level, "stats": stats,
        "stat_modifiers": {
            "force": stat_modifier(stats.force), "agility": stat_modifier(stats.agility),
            "perception": stat_modifier(stats.perception), "technique": None,
            "willpower": stat_modifier(stats.willpower),
        },
        "tech_support_bonus": tech_support_bonus(stats.technique),
        "max_hp": derived.max_hp, "current_hp": derived.max_hp,
        "armor": round_to_5(derived.armor + implant_armor_bonus(implants, level)),
        "shield": round_to_5(derived.shield + (tech_support_bonus(stats.technique) if derived.shield else 0)),
        "reactions": derived.reactions, "vigilance": derived.vigilance,
        "primary": primary, "secondary": secondary,
        "primary_card": primary_card, "secondary_card": secondary_card,
        "akimbo": akimbo, "akimbo_identical": akimbo_identical,
        "implants": implants, "implant_cards": implant_cards,
    }


def assemble_draft_mob(*, level, profile, weapons, implants, abilities=None, overrides=None):
    """Build an editable draft from unrestricted equipment lists."""
    if not weapons:
        raise ValueError("Un brouillon Mob doit conserver au moins une arme pour le moment.")

    mob = _assemble_mob(
        level=level,
        profile=profile,
        primary=weapons[0],
        secondary=weapons[1] if len(weapons) > 1 else None,
        akimbo=False,
        implants=implants,
    )
    stats = mob["stats"]
    from rules.engine import resolve_weapon
    mob["weapons"] = weapons
    from rules.engine import apply_weapon_damage_bonuses, implant_damage_bonuses
    contact_bonus, distance_bonus = implant_damage_bonuses(implants, level)
    mob["weapon_cards"] = [
        apply_weapon_damage_bonuses(
            resolve_weapon(
                weapon,
                level,
                perception=stats.perception,
                technique=stats.technique,
            ),
            contact_bonus=contact_bonus,
            distance_bonus=distance_bonus,
        )
        for weapon in weapons
    ]
    mob["abilities"] = resolve_abilities(list(abilities or []), level)
    mob["overrides"] = dict(overrides or {})
    _apply_draft_overrides(mob)
    return mob


ABILITY_EFFECT_LABELS = {
    "damage_contact": "Dégâts Contact", "damage_distance": "Dégâts Distance",
    "aim": "Visée", "armor": "Armure", "shield": "PB", "healing": "Soin",
    "max_hp": "PV", "reactions": "Réactions", "vigilance": "Vigilance",
}

def resolve_abilities(abilities, level):
    result = []
    for source in abilities:
        item = dict(source)
        effect = item.get("effect")
        if effect:
            value = effect.get("value", 0)
            if effect.get("scaling") == "level":
                value *= level
            item["resolved_effect"] = {
                "label": ABILITY_EFFECT_LABELS.get(effect.get("type"), effect.get("type", "")),
                "value": value,
            }
        else:
            item["resolved_effect"] = None
        result.append(item)
    return result


def _apply_draft_overrides(mob):
    """Apply MJ sources and custom ability effects, then recalculate the draft."""
    from dataclasses import replace
    from rules.engine import (
        ResolvedWeapon, apply_weapon_damage_bonuses, implant_damage_bonuses,
        max_hp, resolve_implant, resolve_weapon, round_to_5,
        stat_modifier, tech_support_bonus,
    )

    overrides = mob.get("overrides", {})
    stats = mob["stats"]
    stat_fields = {
        "force": stats.force, "agility": stats.agility,
        "perception": stats.perception, "technique": stats.technique,
        "constitution": stats.constitution, "willpower": stats.willpower,
    }
    for field in stat_fields:
        if field in overrides:
            stat_fields[field] = overrides[field]
    stats = replace(stats, **stat_fields)
    mob["stats"] = stats
    mob["stat_modifiers"] = {
        "force": stat_modifier(stats.force), "agility": stat_modifier(stats.agility),
        "perception": stat_modifier(stats.perception), "technique": None,
        "willpower": stat_modifier(stats.willpower),
    }
    mob["tech_support_bonus"] = tech_support_bonus(stats.technique)

    effects = {}
    for ability in mob.get("abilities", []):
        resolved = ability.get("resolved_effect")
        effect = ability.get("effect")
        if resolved and effect:
            effects[effect["type"]] = effects.get(effect["type"], 0) + resolved["value"]

    calculated_hp = max_hp(mob["level"], stats.constitution)
    mob["max_hp"] = overrides.get("max_hp", calculated_hp) + effects.get("max_hp", 0)
    mob["current_hp"] = overrides.get("current_hp", mob["max_hp"])
    mob["armor"] = overrides.get("armor", mob["armor"]) + effects.get("armor", 0)
    mob["shield"] = overrides.get("shield", mob["shield"]) + effects.get("shield", 0)
    mob["reactions"] = overrides.get("reactions", mob["reactions"]) + effects.get("reactions", 0)
    mob["vigilance"] = overrides.get("vigilance", mob["vigilance"]) + effects.get("vigilance", 0)
    mob["ability_healing_bonus"] = effects.get("healing", 0)

    contact_bonus, distance_bonus = implant_damage_bonuses(mob["implants"], mob["level"])
    contact_bonus += effects.get("damage_contact", 0)
    distance_bonus += effects.get("damage_distance", 0)
    aim_bonus = effects.get("aim", 0)

    cards = []
    for weapon in mob["weapons"]:
        card = resolve_weapon(
            weapon, mob["level"],
            perception=stats.perception,
            technique=stats.technique,
        )
        card = apply_weapon_damage_bonuses(
            card, contact_bonus=contact_bonus, distance_bonus=distance_bonus,
        )
        if aim_bonus:
            card = ResolvedWeapon(
                card.weapon, card.effective_power, card.neutral_damage,
                card.effective_aim + aim_bonus, card.resolved_property,
                card.property_lines, card.contact_damage, card.distance_damage,
            )
        cards.append(card)
    mob["weapon_cards"] = cards

    mob["implant_cards"] = [
        resolve_implant(implant, mob["level"], mob["max_hp"], technique=stats.technique)
        for implant in mob["implants"]
    ]


def _weapon_ref(weapon):
    return {
        "source": "user" if weapon.__class__.__name__ == "UserWeapon" else "catalogue",
        "id": weapon.id,
    }


def serialize_mob(mob):
    weapons = mob.get("weapons")
    if weapons is None:
        weapons = [mob["primary"]]
        if mob["secondary"] is not None:
            weapons.append(mob["secondary"])
    return {
        "level": mob["level"],
        "profile": str(mob["profile"]),
        "name": mob.get("name", ""),
        "weapons": [_weapon_ref(weapon) for weapon in weapons],
        "implant_ids": [item.id for item in mob["implants"]],
        "abilities": list(mob.get("abilities", [])),
        "overrides": dict(mob.get("overrides", {})),
    }


def rebuild_mob(weapons, implants, data, user_weapons=None):
    weapon_by_id = {item.id: item for item in weapons}
    user_weapon_by_id = {item.id: item for item in (user_weapons or [])}
    implant_by_id = {item.id: item for item in implants}

    refs = data.get("weapons")
    if refs is None:
        # Compatibility with drafts produced before structured equipment refs.
        refs = []
        legacy_ids = data.get("weapon_ids")
        if legacy_ids is None and "primary_id" in data:
            legacy_ids = [data["primary_id"]]
            if data.get("secondary_id") is not None:
                legacy_ids.append(data["secondary_id"])
        for item_id in legacy_ids or []:
            if isinstance(item_id, str) and item_id.startswith("u:"):
                refs.append({"source": "user", "id": int(item_id[2:])})
            else:
                refs.append({"source": "catalogue", "id": item_id})

    selected_weapons = []
    for ref in refs:
        source, item_id = ref.get("source"), ref.get("id")
        if source == "user" and item_id in user_weapon_by_id:
            selected_weapons.append(user_weapon_by_id[item_id])
        elif source == "catalogue" and item_id in weapon_by_id:
            selected_weapons.append(weapon_by_id[item_id])

    mob = assemble_draft_mob(
        level=data["level"], profile=data["profile"], weapons=selected_weapons,
        implants=[
            implant_by_id[item_id] for item_id in data.get("implant_ids", [])
            if item_id in implant_by_id
        ],
        abilities=data.get("abilities", []), overrides=data.get("overrides", {}),
    )
    mob["name"] = data.get("name", "")
    return mob

def generate_mob(weapons, implants, *, level: int, profile: str | None = None, rng=None):
    _validate_level(level)
    rng = rng or random
    selected_profile = profile or generate_profiles(1, rng)[0]
    if selected_profile not in PROFILE_WEIGHTS:
        raise ValueError(f"Profil Mob inconnu : {selected_profile}")
    loadout = choose_weapon_loadout(weapons, profile=selected_profile, level=level, rng=rng)
    selected_implants = choose_implants(implants, profile=selected_profile, level=level, rng=rng)
    mob = _assemble_mob(
        level=level, profile=selected_profile,
        primary=loadout["primary"], secondary=loadout["secondary"],
        akimbo=loadout["akimbo"], implants=selected_implants,
    )
    mob["weapons"] = [loadout["primary"]] + (
        [loadout["secondary"]] if loadout["secondary"] is not None else []
    )
    mob["weapon_cards"] = [mob["primary_card"]] + (
        [mob["secondary_card"]] if mob["secondary_card"] is not None else []
    )
    mob["abilities"] = []
    mob["overrides"] = {}
    return mob

def generate_mobs(weapons, implants, *, quantity: int, level: int, rng=None):
    """Generate a group while applying profile quotas once for the whole batch."""
    _validate_quantity(quantity)
    _validate_level(level)
    rng = rng or random
    profiles = generate_profiles(quantity, rng)
    return [
        generate_mob(
            weapons,
            implants,
            level=level,
            profile=profile,
            rng=rng,
        )
        for profile in profiles
    ]


def reroll_mob_role(weapons, implants, *, level: int, profile: str, rng=None):
    """Regenerate one Mob at the same level while forcing its new role."""
    return generate_mob(
        weapons,
        implants,
        level=level,
        profile=profile,
        rng=rng,
    )

def _interpolate(start, end, progress):
    values = tuple(a + (b - a) * progress for a, b in zip(start, end))
    # Floating arithmetic can drift microscopically from 100; normalize defensively.
    total = sum(values)
    return tuple(value * 100.0 / total for value in values)


def _validate_quantity(quantity: int) -> None:
    if quantity < 1:
        raise ValueError("La quantité de Mobs doit être supérieure ou égale à 1.")


def _validate_level(level: int) -> None:
    if level < 1:
        raise ValueError("Le niveau Mob doit être supérieur ou égal à 1.")
