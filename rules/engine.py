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


def round_to_5(value: int | float) -> int:
    """Round a final scaled/gained value to the nearest 5, halves upward."""
    return int((value + 2.5) // 5 * 5)


def max_hp(level: int, constitution: int = 10) -> int:
    _validate_level(level)
    return 250 + 30 * (level - 1) + (constitution - 10) * 10


def base_damage(level: int) -> int:
    _validate_level(level)
    return 50 + 10 * (level - 1)


def profile_derived(profile: str, level: int) -> MobDerived:
    _validate_level(level)
    if profile not in PROFILE_STATS:
        raise ValueError(f"Profil Mob inconnu : {profile}")
    return MobDerived(
        max_hp=max_hp(level, profile_stats(profile, level).constitution),
        armor=5 * level if profile == "C" else 0,
        shield=20 * level if profile == "S" else 0,
        reactions=2 if profile == "A" else 1,
        vigilance=2 if profile == "T" and level >= 10 else 1,
    )



@dataclass(frozen=True)
class ResolvedWeapon:
    weapon: object
    effective_power: int
    neutral_damage: int
    effective_aim: int
    resolved_property: str
    property_lines: tuple[str, ...] = ()


@dataclass(frozen=True)
class ResolvedImplant:
    implant: object
    resolved_property: str
    property_lines: tuple[str, ...] = ()


def stat_modifier(value: int) -> int:
    """FOR/AGI/PER/VOL/TECH modifier: +1 per 2 points above 10."""
    return max(0, (value - 10) // 2)


def tech_support_bonus(technique: int) -> int:
    """TECH has no modifier: every point above 10 grants +10 support."""
    return max(0, technique - 10) * 10


def split_property_lines(text: str) -> tuple[str, ...]:
    """Split distinct resolved effects into readable card lines."""
    if not text:
        return ()
    return tuple(part.strip() for part in text.split(";") if part.strip())


def effective_weapon_power(weapon) -> int:
    if weapon.name in ("Revolver", "Chakram"):
        return weapon.power + 5
    return weapon.power


def neutral_weapon_damage(level: int, weapon) -> int:
    return round_to_5(base_damage(level) + effective_weapon_power(weapon) * 2)


def resolve_weapon(
    weapon,
    level: int,
    *,
    perception: int = 10,
    technique: int = 10,
) -> ResolvedWeapon:
    _validate_level(level)
    power = effective_weapon_power(weapon)
    per_bonus = stat_modifier(perception)
    tech_bonus = tech_support_bonus(technique)
    text = weapon.property_text
    if weapon.name == "Revolver":
        text = "Puissance +5 intégrée."
    elif weapon.name == "Chakram":
        text = "Permet de bondir sur la cible à partir de 4 m. ; Lancer : peut être lancé à Portée Moyenne."
    elif weapon.name == "Fusil à pompe court":
        text = f"Au Contact : +{round_to_5(5 * level)} Dégâts."
    elif weapon.name == "Smartgun":
        text = f"+{round_to_5(5 * level)} Dégâts contre une cible Marquée."
    elif weapon.name == "Katana":
        text = f"Après une Esquive réussie contre une attaque à distance, renvoie {round_to_5(5 * level)} Dégâts à l'attaquant."
    elif weapon.name == "Powerfist":
        text = f"Une attaque réussie génère {round_to_5(5 * level + tech_bonus)} PB, non cumulables."
    elif weapon.name == "Arbalète":
        text = f"Une attaque réussie soigne le porteur de {round_to_5(5 * level + tech_bonus)} PV."
    elif weapon.name == "Carabine":
        text = f"Vigilance : +{level // 5} Visée."
    elif weapon.name == "Med Rifle":
        text = f"Soigne un allié de {round_to_5(20 * level + tech_bonus)} PV."
    elif weapon.name == "Smart Rifle":
        text = f"+{round_to_5(10 * level)} Dégâts contre une cible Marquée."
    elif weapon.name == "Masse de combat":
        text = ""
    neutral_damage = base_damage(level) + power * 2
    if weapon.name == "Masse de combat":
        neutral_damage += 5 * level
    return ResolvedWeapon(
        weapon,
        power,
        round_to_5(neutral_damage),
        weapon.aim + per_bonus,
        text,
        split_property_lines(text),
    )


def resolve_implant(
    implant,
    level: int,
    max_hp_value: int,
    *,
    technique: int = 10,
) -> ResolvedImplant:
    _validate_level(level)
    tech_bonus = tech_support_bonus(technique)
    text = implant.property_text
    if implant.name == "AEGIS":
        text = f"+{round_to_5(5 * level)} Armure."
    elif implant.name == "ANCHOR":
        text = f"+{round_to_5(2 * level)} Armure ; résistance aux Poussées."
    elif implant.name == "COLOSSUS":
        text = f"+{round_to_5(2 * level)} Armure ; Propulsion : +{round_to_5(max_hp_value * 0.05)} dégâts + test FOR → Étourdi."
    elif implant.name == "MINOS":
        text = f"+50 % Vitesse de Déplacement vers un ennemi ; attaques au Contact : +{round_to_5(5 * level)} Dégâts."
    elif implant.name == "ZEPHYR":
        text = f"Attaques à distance : +{round_to_5((level // 2) * 5)} Dégâts."
    elif implant.name == "PHALANX":
        text = f"Réaction : déploie une barrière à {round_to_5(10 * level + tech_bonus)} PV."
    return ResolvedImplant(implant, text, split_property_lines(text))


def implant_armor_bonus(implants, level: int) -> int:
    bonuses = {"AEGIS": 5, "ANCHOR": 2, "COLOSSUS": 2}
    return sum(bonuses.get(implant.name, 0) * level for implant in implants)

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
