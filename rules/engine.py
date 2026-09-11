from dataclasses import dataclass
from math import floor


OFFENSIVE_STATS = ("force", "agility", "perception", "technique")


class RuleCalculationError(ValueError):
    """Raised when an explicit override makes a TMP calculation impossible."""


@dataclass(frozen=True)
class BuildStats:
    force: int
    agility: int
    perception: int
    technique: int
    constitution: int
    willpower: int


@dataclass(frozen=True)
class BuildDerived:
    max_hp: int
    max_reactions: int
    main_slots: int
    secondary_slots: int
    gadget_slots: int
    implant_slots: int


@dataclass(frozen=True)
class AttackResult:
    threshold: int
    roll: int
    verdict: str
    delta_coefficient: int
    delta_bonus: int | None
    damage: int | None


def offensive_budget(level: int) -> int:
    _validate_level(level)
    return 36 + 2 * (level - 1)


def defensive_budget(level: int) -> int:
    _validate_level(level)
    return 21 + (level - 1)


def is_legal_level_one(stats: BuildStats) -> bool:
    offensive = sorted((stats.force, stats.agility, stats.perception, stats.technique))
    defensive = (stats.constitution, stats.willpower)
    return offensive == [5, 8, 10, 13] and sum(defensive) == 21 and all(8 <= value <= 13 for value in defensive)


def delta_coefficient(stat_value: int, explicit_modifier: int = 0) -> int:
    if stat_value >= 18:
        native = 3
    elif stat_value >= 12:
        native = 4
    else:
        native = 5
    effective = native + explicit_modifier
    if effective <= 0:
        raise RuleCalculationError(f"Coefficient Delta invalide ({effective}).")
    return effective


def critical_upper_bound(critical_bonus: int = 0) -> int:
    return max(1, 1 + critical_bonus)


def max_hp(constitution: int, permanent_bonus: int = 0) -> int:
    bonus = (5 if constitution >= 12 else 0) + (5 if constitution >= 16 else 0)
    return constitution + bonus + permanent_bonus


def max_reactions(agility: int, permanent_bonus: int = 0) -> int:
    return 1 + (1 if agility >= 16 else 0) + permanent_bonus


def main_slots(force: int, permanent_bonus: int = 0) -> int:
    return 1 + (1 if force >= 18 else 0) + permanent_bonus


def secondary_slots(permanent_bonus: int = 0) -> int:
    return 1 + permanent_bonus


def gadget_slots(technique: int, permanent_bonus: int = 0) -> int:
    return 1 + (2 if technique >= 16 else 0) + permanent_bonus


def implant_slots(willpower: int, permanent_bonus: int = 0) -> int:
    native = 2 if willpower >= 16 else 1 if willpower >= 12 else 0
    return native + permanent_bonus


def derive_build(stats: BuildStats) -> BuildDerived:
    return BuildDerived(
        max_hp=max_hp(stats.constitution),
        max_reactions=max_reactions(stats.agility),
        main_slots=main_slots(stats.force),
        secondary_slots=secondary_slots(),
        gadget_slots=gadget_slots(stats.technique),
        implant_slots=implant_slots(stats.willpower),
    )


def force_shortfall_penalty(force: int, minimum_force: int | None) -> int:
    if minimum_force is None:
        return 0
    return -max(0, minimum_force - force)


def resolve_attack(
    *,
    stat_value: int,
    roll: int,
    power: int,
    test_modifier: int = 0,
    delta_modifier: int = 0,
    critical_bonus: int = 0,
    annihilation: bool = False,
) -> AttackResult:
    threshold = stat_value + test_modifier
    coefficient = delta_coefficient(stat_value, delta_modifier)
    critical_max = critical_upper_bound(critical_bonus)

    if roll == 20:
        return AttackResult(threshold, roll, "critical_failure", coefficient, None, None)

    critical = 1 <= roll <= critical_max
    success = critical or roll <= threshold
    if not success:
        return AttackResult(threshold, roll, "failure", coefficient, None, None)

    margin = threshold - roll
    delta = max(0, floor(margin / coefficient))
    if critical:
        multiplier = 3 if annihilation else 2
        damage = power * multiplier + delta
        verdict = "critical_success"
    else:
        damage = power + delta
        verdict = "success"

    return AttackResult(threshold, roll, verdict, coefficient, delta, damage)


def fulgurance_damage(strike_damage: int, mode: str) -> tuple[int, ...]:
    if mode == "concentrated":
        return strike_damage, strike_damage
    if mode == "split":
        return strike_damage, strike_damage
    raise ValueError("Mode Fulgurance inconnu.")


def apply_armor(damage: int, armor: int) -> int:
    return max(0, damage - armor)


def apply_concentrated_fulgurance(strike_damage: int, armor: int) -> int:
    first, second = fulgurance_damage(strike_damage, "concentrated")
    return apply_armor(first, armor) + apply_armor(second, armor)


def _validate_level(level: int) -> None:
    if not 1 <= level <= 10:
        raise ValueError("Le niveau doit être compris entre 1 et 10.")
