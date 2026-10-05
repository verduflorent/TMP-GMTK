# TMP-GMTK — Roadmap MVP Monster Builder

Version du 6 octobre 2026

## 1. Stratégie

TMP-GMTK est recentré sur un seul objectif : préparer et jouer rapidement des rencontres de Mobs pour THE MOIRA PROTOCOL.

Chaîne principale :

> Générer → Corriger → Sauvegarder → Composer une Rencontre → Jouer sur PC ou Imprimer

Le projet ne cherche plus à reproduire la création complète des PJ. Le document MONSTER est l'autorité du Monster Builder ; le CdC MVP décrit le produit.

L'architecture reste volontairement simple : Django classique, templates et formulaires Django, JavaScript limité aux interactions qui gagnent réellement du temps à la table, règles de calcul isolées du HTTP et de l'ORM.

Le développement se fait avec tests locaux avant commit/merge. La CI GitHub ne doit pas être utilisée comme boucle de test ordinaire.

## 2. État hérité

Le socle déjà produit reste utile :
- projet Django ;
- authentification et User personnalisé ;
- isolation des données par utilisateur ;
- premières relations de persistance ;
- documentation versionnée.

La branche PR2 contient également du travail issu de l'ancien système de règles. Ce code n'est pas une autorité : il doit être supprimé, simplifié ou remplacé lorsqu'il contredit le nouveau CdC Monster Builder.

Aucune compatibilité artificielle avec l'ancien Character Editor ne doit alourdir le MVP.

## 3. Découpage cible

Le nouveau MVP tient en cinq chantiers fonctionnels, puis une passe de déploiement.

### PR 2 — Recentrage du domaine et moteur Mob

Objectif : disposer d'un socle métier propre correspondant à MONSTER.

Travaux :
- retirer ou neutraliser les modèles/règles devenus inutiles pour le MVP ;
- modéliser les cinq profils Mob ;
- intégrer les tables de caractéristiques N1–N10 ;
- implémenter le scaling PV ;
- implémenter la Base de dégâts et la formule de dégâts Mob ;
- implémenter le seuil d'attaque Mob ;
- plafonner les caractéristiques au profil N10 pour les niveaux supérieurs ;
- intégrer les passifs permanents directement calculables ;
- structurer le catalogue d'armes Mob ;
- structurer les implants Mob et leurs compatibilités de profils ;
- préparer les probabilités comme données configurables sans inventer leur calibration.

Tests minimum :
- PV à plusieurs niveaux, y compris >N10 ;
- caractéristiques exactes des cinq profils aux niveaux représentatifs ;
- caractéristiques identiques N10/N15 ;
- passifs de profils ;
- calcul d'attaque et dégâts ;
- catalogue armes/implants et compatibilités ;
- absence de dépendance aux EVO/Mods/Accessoires/Viseurs PJ.

Livrable : moteur Mob déterministe et référentiel prêt à alimenter l'interface.

### PR 3 — Monster Builder, Randomizer et Bestiaire

Objectif : obtenir le premier outil réellement utile de préparation.

Travaux :
- écran minimal « nombre de Mobs + niveau » ;
- génération pondérée des profils ;
- quotas Soutien/Contrôle ;
- attribution aléatoire des armes ;
- secondaire/Akimbo lorsque leur calibration sera définie ;
- attribution des implants lorsque leur calibration sera définie ;
- prévisualisation immédiate du groupe ;
- édition rapide de chaque Mob ;
- remplacement d'une arme par sélecteur filtrable ;
- remplacement/retrait d'un implant ;
- modification manuelle des champs utiles ;
- sauvegarde d'un Mob dans le Bestiaire ;
- liste, édition, duplication et suppression des entrées du Bestiaire.

Règle de conception :

> Le Randomizer doit produire rapidement un résultat suffisamment bon, pas garantir une composition parfaite.

Les probabilités T1–T4, secondaire, Akimbo et implants sont calibrées dans cette PR. Elles restent configurables et ne doivent pas être dispersées dans les vues.

Tests minimum :
- génération de lots à plusieurs niveaux ;
- respect des quotas Soutien/Contrôle ;
- respect des compatibilités de profils ;
- impossibilité d'Akimbo avec une arme 2 mains ;
- édition d'une génération sans régénérer le reste ;
- changement d'arme recalculant la fiche ;
- sauvegarde/duplication Bestiaire ;
- isolation entre utilisateurs.

Livrable : le MJ peut demander X Mobs de niveau N, corriger quelques choix et conserver les fiches utiles.

### PR 4 — Rencontres et Table numérique

Objectif : passer de Mobs préparés à une rencontre jouable sur PC.

Travaux :
- créer une Rencontre ;
- ajouter des Mobs générés et/ou du Bestiaire ;
- quantités et instances indépendantes ;
- modifier une instance sans modifier silencieusement le Bestiaire ;
- sauvegarder/recharger une Rencontre ;
- lancer une Rencontre sur la Table ;
- suivi PV actuels/max ;
- suivi PB/Bouclier et ressources simples utiles ;
- dégâts et soins rapides ;
- accès compact aux armes, implants et passifs ;
- ordre d'affichage pratique et persistant si nécessaire.

Tests minimum :
- plusieurs instances d'un même modèle gardent leurs PV indépendants ;
- modifications locales d'une Rencontre n'altèrent pas la source ;
- sauvegarde/rechargement ;
- dégâts/soins ;
- isolation des Rencontres entre comptes.

Livrable : une rencontre complète peut être gérée sans papier.

### PR 5 — Dice Roller Mob et impression de Rencontre

Objectif : couvrir les deux manières réelles de mener : PC ou feuille sur calepin.

Dice Roller :
- lancement depuis une arme ;
- seuil d'attaque affiché ;
- modificateur contextuel manuel ;
- résultat du d20 ;
- réussite/échec ;
- détail Base + Puissance ×2 + modificateur du jet ;
- dégâts finaux ;
- propriétés tactiques non automatisées laissées lisibles sur la carte.

Impression :
- vue A4 dédiée ;
- aucun second modèle de données ;
- mêmes données que la Rencontre ;
- regroupement compact lorsque pertinent ;
- informations de combat immédiatement lisibles ;
- suivi individuel obligatoire ;
- champ manuscrit « Jeton : _____ » pour chaque Mob ;
- PV ;
- PB/Bouclier si applicable ;
- Réactions/ressources simples si utiles ;
- espace de note court si la mise en page le permet.

Tests minimum :
- calculs du Dice Roller ;
- modificateurs contextuels ;
- rendu d'impression d'une Rencontre simple et d'une Rencontre dense ;
- présence d'une ligne individuelle et d'un champ Jeton pour chaque Mob ;
- aucune dépendance à la Table numérique pour imprimer.

Livrable : le MJ choisit librement de gérer la même Rencontre depuis son PC ou sur papier.

### PR 6 — Passe UX et stabilisation MVP

Objectif : transformer les fonctionnalités en outil rapide à utiliser pendant une vraie partie.

Travaux :
- hiérarchie visuelle des fiches ;
- densité adaptée à la Table ;
- édition d'arme/implant en peu de clics ;
- génération de groupe rapide ;
- contrôles PV utilisables debout ;
- responsive raisonnable ;
- confirmations uniquement pour les actions destructrices ;
- états vides et erreurs lisibles ;
- optimisation de la feuille A4 ;
- nettoyage du code hérité devenu inutile ;
- revue complète du CdC MVP.

Parcours de recette :
1. connexion ;
2. générer plusieurs Mobs ;
3. changer quelques armes ;
4. sauvegarder les Mobs utiles ;
5. créer une Rencontre ;
6. jouer sur Table et lancer des attaques ;
7. recharger la Rencontre ;
8. imprimer la même Rencontre ;
9. vérifier qu'elle est jouable uniquement avec la feuille imprimée.

Livrable : MVP fonctionnel et confortable en conditions de partie.

### PR 7 — Déploiement

Objectif : rendre l'outil accessible depuis les appareils souhaités.

Le choix d'hébergement est volontairement différé. Il pourra tenir compte de l'hébergement déjà disponible pour EzRp.

Travaux :
- choisir le fournisseur au moment du déploiement ;
- configuration production ;
- secrets hors dépôt ;
- HTTPS ;
- base persistante ;
- fichiers statiques ;
- migrations ;
- sauvegarde/restauration ;
- procédure de mise à jour ;
- vérification depuis plusieurs appareils.

Aucune règle métier ne doit être modifiée pour s'adapter à un fournisseur évitable.

## 4. Dépendances

    PR1 Socle existant
        ↓
    PR2 Domaine + moteur Mob
        ↓
    PR3 Monster Builder + Bestiaire
        ↓
    PR4 Rencontres + Table
        ↓
    PR5 Dice Roller + Impression
        ↓
    PR6 UX + Stabilisation
        ↓
    PR7 Déploiement

Chaque PR doit produire une amélioration utilisable et testable. On évite les micro-PR artificielles.

## 5. Arbitrages volontairement différés

Ils sont décidés dans la PR3, au moment où ils deviennent observables :
- poids exacts des cinq profils ;
- courbe T1/T2/T3/T4 ;
- niveaux de déblocage exacts ;
- chance de secondaire ;
- distribution de qualité de la secondaire ;
- chance et règles finales d'Akimbo ;
- chance d'implant ;
- nombre d'implants et éventuels paliers de niveau.

Le modèle PR2 doit permettre ces réglages sans en imposer les valeurs.

Les détails graphiques de la feuille imprimée sont affinés en PR5/PR6 à partir de vrais exemples de Rencontres.

## 6. Principes techniques

### Règles

Les formules Mob sont centralisées dans un module Python pur et testable.

Les vues ne contiennent pas de formules métier.

Le hasard du Randomizer est injectable afin de tester les invariants sans rendre les tests probabilistes.

### Données

Profils, armes, implants, compatibilités, Tiers et réglages du Randomizer sont structurés.

MONSTER reste la source humaine ; l'application n'interprète pas le DOCX à runtime.

### Persistance

Un modèle du Bestiaire et une instance de Rencontre sont distincts.

Les PV actuels appartiennent à l'instance jouée.

Une modification locale ne remonte jamais silencieusement vers le Bestiaire.

### Simplicité

Ne pas construire avant le besoin :
- système Élite ;
- Boss Builder ;
- Character Editor PJ ;
- moteur universel d'effets ;
- EVO/Mods/Accessoires/Viseurs Mob ;
- économie/loot ;
- IA tactique ;
- API publique ;
- SPA ;
- temps réel multiutilisateur.

## 7. Définition du MVP terminé

TMP-GMTK V1 est terminé lorsque le MJ peut, sans consulter le code ni refaire de calcul répétitif :

> se connecter → générer X Mobs N → corriger rapidement → sauvegarder → créer une Rencontre → jouer sur PC ou imprimer.

Le critère principal est le temps réellement gagné avant et pendant une partie.
