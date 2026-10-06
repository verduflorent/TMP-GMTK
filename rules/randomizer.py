import random

from catalogue.models import MobProfile


PROFILE_WEIGHTS = {
    MobProfile.COMBATANT: 5,
    MobProfile.ASSASSIN: 3,
    MobProfile.TIREUR: 5,
    MobProfile.SOUTIEN: 2,
    MobProfile.CONTROLE: 1,
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
    counts = {profile: 0 for profile in PROFILE_WEIGHTS}
    generated = []

    for _ in range(quantity):
        candidates = [
            profile
            for profile in PROFILE_WEIGHTS
            if profile not in LIMITED_PROFILES or counts[profile] < cap
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
    """T4 always gets a sidearm; other tiers have a 20% chance."""
    rng = rng or random
    return primary_weapon.tier == 4 or rng.random() < 0.20


def choose_secondary_weapon(weapons, *, profile: str, primary_weapon, rng=None):
    """Choose a simple T1/T2 sidearm compatible with the Mob profile."""
    rng = rng or random
    if not should_add_secondary(primary_weapon, rng):
        return None

    candidates = [
        weapon
        for weapon in weapons
        if weapon.tier in (1, 2) and weapon.supports_profile(profile)
    ]
    if not candidates:
        return None
    return rng.choice(candidates)


def should_use_akimbo(primary_weapon, rng=None) -> bool:
    """Akimbo has a 10% chance and requires a one-handed primary weapon."""
    rng = rng or random
    return primary_weapon.hands == 1 and rng.random() < 0.10


def choose_akimbo_pair(weapons, *, profile: str, primary_weapon, rng=None):
    """Return an Akimbo pair, 80% identical and 20% mixed, or None."""
    rng = rng or random
    if not should_use_akimbo(primary_weapon, rng):
        return None

    candidates = [
        weapon
        for weapon in weapons
        if weapon.hands == 1 and weapon.supports_profile(profile)
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
        weapons, profile=profile, primary_weapon=primary, rng=rng
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


def generate_mob(weapons, implants, *, level: int, profile: str | None = None, rng=None):
    """Assemble one complete transient Mob proposal without persistence."""
    from rules.engine import profile_derived, profile_stats

    _validate_level(level)
    rng = rng or random
    selected_profile = profile or generate_profiles(1, rng)[0]
    if selected_profile not in PROFILE_WEIGHTS:
        raise ValueError(f"Profil Mob inconnu : {selected_profile}")

    stats = profile_stats(selected_profile, level)
    derived = profile_derived(selected_profile, level)
    loadout = choose_weapon_loadout(
        weapons, profile=selected_profile, level=level, rng=rng
    )
    selected_implants = choose_implants(
        implants, profile=selected_profile, level=level, rng=rng
    )

    return {
        "profile": selected_profile,
        "level": level,
        "stats": stats,
        "max_hp": derived.max_hp,
        "current_hp": derived.max_hp,
        "armor": derived.armor,
        "shield": derived.shield,
        "reactions": derived.reactions,
        "vigilance": derived.vigilance,
        "primary": loadout["primary"],
        "secondary": loadout["secondary"],
        "akimbo": loadout["akimbo"],
        "implants": selected_implants,
    }


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
