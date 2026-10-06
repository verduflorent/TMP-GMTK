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


def specialist_cap(quantity: int) -> int:
    """Maximum number of each limited profile in a generated group."""
    _validate_quantity(quantity)
    if quantity <= 4:
        return 1
    if quantity <= 10:
        return 2
    # Keep the same rhythm for larger batches without adding a hard group-size limit.
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


def _validate_quantity(quantity: int) -> None:
    if quantity < 1:
        raise ValueError("La quantité de Mobs doit être supérieure ou égale à 1.")
