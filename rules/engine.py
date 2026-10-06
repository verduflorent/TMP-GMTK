from dataclasses import dataclass


PROFILE_STATS = {
    "C": (
        (11, 10, 10, 10, 11, 10), (12, 10, 10, 10, 12, 10),
        (13, 11, 10, 10, 12, 10), (14, 12, 10, 10, 12, 10),
        (14, 12, 12, 10, 12, 10), (15, 12, 12, 10, 13, 10),
        (16, 12, 12, 10, 14, 10), (16, 13, 12, 10, 15, 10),
        (16, 14, 12, 10, 16, 10), (16, 14, 14, 10, 16, 10),
    ),
    "A": (
        (10, 11, 11, 10, 10, 10), (10, 12, 12, 10, 10, 10),
        (10, 13, 12, 10, 10, 11), (10, 14, 12, 10, 10, 12),
        (10, 15, 13, 10, 10, 12), (10, 16, 14, 10, 10, 12),
        (11, 16, 14, 10, 10, 13), (12, 16, 14, 10, 10, 14),
        (12, 16, 16, 10, 10, 14), (14, 16, 16, 10, 10, 14),
    ),
    "T": (
        (10, 10, 12, 10, 10, 10), (10, 11, 12, 10, 11, 10),
        (10, 12, 12, 10, 12, 10), (10, 12, 14, 10, 12, 10),
        (11, 12, 14, 10, 12, 11), (12, 12, 14, 10, 12, 12),
        (12, 12, 16, 10, 12, 12), (12, 12, 18, 10, 12, 12),
        (12, 12, 20, 10, 12, 12), (12, 12, 20, 10, 12, 14),
    ),
    "S": (
        (11, 10, 10, 11, 10, 10), (12, 10, 10, 12, 10, 10),
        (12, 10, 11, 13, 10, 10), (12, 10, 12, 14, 10, 10),
        (12, 10, 12, 14, 12, 10), (13, 10, 12, 15, 12, 10),
        (14, 10, 12, 16, 12, 10), (15, 10, 12, 16, 13, 10),
        (16, 10, 13, 16, 13, 10), (16, 10, 14, 16, 14, 10),
    ),
    "K": (
        (11, 10, 10, 10, 10, 11), (12, 10, 10, 10, 10, 12),
        (13, 10, 10, 10, 10, 13), (14, 10, 10, 10, 10, 14),
        (14, 10, 11, 10, 11, 14), (14, 10, 12, 10, 12, 14),
        (15, 10, 12, 10, 12, 15), (16, 10, 12, 10, 12, 16),
        (16, 10, 13, 10, 13, 16), (18, 10, 14, 10, 14, 18),
    ),
}


@dataclass(frozen=True)
class MobStats:
    force: int
    agility: int
    perception: int
    technique: int
    constitution: int
    willpower: int


@dataclass(frozen=True)
class MobDerived:
    max_hp: int
    armor: int
    shield: int
    reactions: int
    vigilance: int


@dataclass(frozen=True)
class MobAttackResult:
    threshold: int
    roll: int
    success: bool
    base_damage: int
    weapon_damage: int
    roll_modifier: int
    damage: int | None


def profile_stats(profile: str, level: int) -> MobStats:
    _validate_level(level)
    try:
        values = PROFILE_STATS[profile][min(level, 10) - 1]
    except KeyError as exc:
        raise ValueError(f"Profil Mob inconnu : {profile}") from exc
    return MobStats(*values)


def max_hp(level: int) -> int:
    _validate_level(level)
    return 250 + 30 * (level - 1)


def base_damage(level: int) -> int:
    _validate_level(level)
    return 50 + 10 * (level - 1)


def profile_derived(profile: str, level: int) -> MobDerived:
    _validate_level(level)
    if profile not in PROFILE_STATS:
        raise ValueError(f"Profil Mob inconnu : {profile}")
    return MobDerived(
        max_hp=max_hp(level),
        armor=5 * level if profile == "C" else 0,
        shield=20 * level if profile == "S" else 0,
        reactions=2 if profile == "A" else 1,
        vigilance=2 if profile == "T" and level >= 10 else 1,
    )


def attack_threshold(perception: int, weapon_aim: int, context_modifier: int = 0) -> int:
    return 10 + (perception - 10) + weapon_aim + context_modifier


def roll_damage_modifier(roll: int) -> int:
    _validate_roll(roll)
    return (10 - roll) * 5


def resolve_attack(
    *,
    level: int,
    perception: int,
    weapon_power: int,
    weapon_aim: int,
    roll: int,
    context_modifier: int = 0,
) -> MobAttackResult:
    _validate_level(level)
    _validate_roll(roll)
    threshold = attack_threshold(perception, weapon_aim, context_modifier)
    base = base_damage(level)
    weapon = weapon_power * 2
    modifier = roll_damage_modifier(roll)
    success = roll <= threshold
    return MobAttackResult(
        threshold=threshold,
        roll=roll,
        success=success,
        base_damage=base,
        weapon_damage=weapon,
        roll_modifier=modifier,
        damage=base + weapon + modifier if success else None,
    )


def _validate_level(level: int) -> None:
    if level < 1:
        raise ValueError("Le niveau Mob doit être supérieur ou égal à 1.")


def _validate_roll(roll: int) -> None:
    if not 1 <= roll <= 20:
        raise ValueError("Le résultat du d20 doit être compris entre 1 et 20.")
