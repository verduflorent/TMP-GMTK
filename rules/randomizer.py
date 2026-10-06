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
