from django.core.management.base import BaseCommand

from catalogue.models import MobImplant, MobWeapon


WEAPONS = [
    ("Arme de lancer", 2, "A", 1, "SHORT", 10, 2, "Léger", "+50 % Vitesse de Déplacement.", False),
    ("Fusil à pompe court", 2, "C", 1, "SHORT", 10, 2, "Double portée", "Puissance 10 à distance ; Puissance 20 au Contact.", False),
    ("Hardpoint", 3, "S", 1, "MEDIUM", 10, 2, "Ralliement", "+50 % Vitesse de Déplacement vers un allié.", False),
    ("Pistolet", 1, "", 1, "SHORT", 10, 2, "", "", False),
    ("Pistolet-mitrailleur", 1, "", 1, "SHORT", 10, 2, "Rafale", "Une cible touchée ne peut plus effectuer d'Attaque d'opportunité pendant 1 tour.", False),
    ("Revolver", 2, "T", 1, "MEDIUM", 10, 2, "Gros calibre", "+5 Puissance.", False),
    ("Smartgun", 2, "K", 1, "SHORT", 10, 2, "Exploitation", "+5 Dégâts × Niveau contre une cible Marquée.", False),
    ("Katana", 3, "A", 1, "CONTACT", 15, 2, "Riposte", "Après une Esquive réussie contre une attaque à distance, renvoie 5 Dégâts × Niveau à l'attaquant.", False),
    ("Powerfist", 3, "S", 1, "CONTACT", 15, 2, "Charge cinétique", "Une attaque réussie génère 5 PB × Niveau, non cumulables.", False),
    ("Arbalète", 4, "A", 2, "MEDIUM", 15, 1, "Saignée", "Une attaque réussie soigne le porteur de 5 PV × Niveau.", False),
    ("Arc", 3, "T", 2, "MEDIUM", 15, 1, "Perforation", "Ignore les Couvertures légères.", False),
    ("Carabine", 2, "T", 2, "MEDIUM", 15, 1, "Mirador", "Vigilance : + ⌊Niveau ÷ 5⌋ Visée.", False),
    ("Chakram", 4, "A", 2, "CONTACT", 15, 1, "Bond", "+5 Puissance. Permet de bondir sur la cible à partir de 4 m. Peut être lancé à Portée Moyenne.", False),
    ("Fusil d’assaut", 2, "", 2, "MEDIUM", 15, 1, "Polyvalence", "Ignore les malus de portée.", False),
    ("Med Rifle", 2, "S", 2, "MEDIUM", 15, 1, "MedBoost", "Soigne un allié de 20 PV × Niveau.", False),
    ("Railgun", 4, "T", 2, "MEDIUM", 15, 1, "Transpercement", "Traverse les cibles alignées ; les suivantes subissent 50 % des dégâts.", False),
    ("Smart Rifle", 3, "K", 2, "MEDIUM", 15, 1, "Exploitation", "+10 Dégâts × Niveau contre une cible Marquée.", False),
    ("Fusil à shrapnels", 4, "C", 2, "CONTACT", 20, 1, "Dispersion", "Les créatures dans le cône 3×3 derrière la cible subissent 50 % des dégâts.", False),
    ("Fusil de précision", 4, "T", 2, "LONG", 20, 1, "Tir ajusté", "+2 Visée.", False),
    ("Mitrailleuse", 3, "C", 2, "MEDIUM", 20, 0, "Suppression", "Ignore 1 niveau de Couverture.", False),
    ("Lame lourde", 3, "C", 2, "CONTACT", 25, 0, "Garde", "Peut effectuer une Parade contre une attaque à distance.", False),
    ("Masse de combat", 2, "C", 2, "CONTACT", 25, 0, "Dégâts", "+5 Dégâts × Niveau.", False),
    ("Lance-grenades compact", 2, "C", 1, "MEDIUM", 20, 1, "Flash", "Zone 3×3. Peut remplacer le tir normal par une grenade flash en Zone 5×5 : les créatures présentes doivent dépenser 1 Réaction ou devenir Aveuglées jusqu'à la fin de votre prochain tour. Peut tirer par-dessus les Couvertures selon les règles de la grenade flash.", False),
    ("Lance-flammes", 3, "C", 2, "SHORT", 30, -1, "Incendiaire", "Zone cône 3×3. Les cibles touchées effectuent un test de VOL ou subissent un Désavantage.", False),
    ("Lance-roquettes", 4, "C", 2, "LONG", 35, -3, "Impact explosif", "Zone 5×5. Les cibles touchées perdent 5 Armure.", False),
    ("Backpulse", 3, "K", 1, "SHORT", 0, 2, "Propulsion", "Repousse la cible de Niveau cases.", True),
    ("GridLock", 2, "K", 2, "SHORT", 0, 1, "Enchevêtrement", "Test de Résistance FOR ; échec : Enchevêtré 1 tour.", True),
    ("MagLink", 4, "K", 2, "MEDIUM", 0, 1, "Magnétisation", "Collision : test de FOR ; échec → Désavantage.", True),
    ("PolyGel", 3, "A", 2, "SHORT", 0, 0, "Mousse polymère", "Zone 5×5 : test de FOR ou Immobilisé.", True),
]

IMPLANTS = [
    ("MEDUSA", "K", "Résistance au Contrôle", "Avantage aux tests de Résistance contre les Contrôles."),
    ("AMBROSIA", "S", "Ambroisie", "Lorsqu'il soigne un allié, peut également soigner un second allié."),
    ("ENCELADE", "C", "Bond", "Réaction : Bond de 8 m ; à l’atterrissage, les ennemis dans un rayon de 1 m subissent Déséquilibré."),
    ("AEGIS", "CSK", "Blindage", "+5 Armure × Niveau."),
    ("ANCHOR", "CSK", "Ancrage", "+2 Armure × Niveau ; résistance aux Poussées."),
    ("COLOSSUS", "CK", "Colosse", "+2 Armure × Niveau ; Propulsion : +5 % PV max en dégâts + test FOR → Étourdi."),
    ("VELOS", "A", "Réaction", "Déplacement +8 m, sans déclencher Vigilance."),
    ("APATE", "AT", "Réaction", "Déplacement + Reflet ; 50 % de chance que l’attaque cible le Reflet."),
    ("SKIA", "A", "Dissimulation", "Action : devient Dissimulé."),
    ("MINOS", "AC", "Approche", "+50 % Vitesse de Déplacement vers un ennemi ; attaques au Contact : +5 Dégâts × Niveau."),
    ("ARGUS", "TS", "Observation", "Ignore la Dissimulation et peut cibler les créatures Dissimulées."),
    ("ZEPHYR", "AT", "Portée optimale", "Attaques à distance : +5 Dégâts tous les 2 Niveaux."),
    ("METIS", "T", "Ricochet", "Les attaques à distance peuvent effectuer 1 Ricochet sur une surface solide avant d'atteindre leur cible."),
    ("PHALANX", "CS", "Barrière", "Réaction : déploie une barrière à 10 PV × Niveau."),
    ("ECLIPSE", "KS", "Portail", "Action : ouvre un portail vers un point visible à Portée Courte."),
    ("PHOIBOS", "CT", "Marquage", "Ignore 1 niveau de Couverture contre une cible Marquée."),
]


class Command(BaseCommand):
    help = "Crée ou actualise le référentiel officiel Monster Builder."

    def handle(self, *args, **options):
        weapon_names = set()
        for name, tier, profiles, hands, optimal_range, power, aim, prop_name, prop_text, is_control in WEAPONS:
            weapon_names.add(name)
            MobWeapon.objects.update_or_create(
                name=name,
                defaults={
                    "tier": tier,
                    "allowed_profiles": profiles,
                    "hands": hands,
                    "optimal_range": optimal_range,
                    "power": power,
                    "aim": aim,
                    "property_name": prop_name,
                    "property_text": prop_text,
                    "is_control": is_control,
                },
            )

        implant_names = set()
        for name, profiles, prop_name, prop_text in IMPLANTS:
            implant_names.add(name)
            MobImplant.objects.update_or_create(
                name=name,
                defaults={
                    "allowed_profiles": profiles,
                    "property_name": prop_name,
                    "property_text": prop_text,
                },
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Référentiel Monster synchronisé : {len(weapon_names)} armes, {len(implant_names)} implants."
            )
        )
