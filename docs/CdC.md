# TMP-GMTK — Cahier des charges MVP

Version du 5 octobre 2026 — Monster Builder

## 1. Objectif

TMP-GMTK est d'abord un outil de préparation et de gestion des rencontres de THE MOIRA PROTOCOL.

Le MVP doit permettre au MJ de générer rapidement plusieurs Mobs immédiatement jouables, de corriger en quelques clics les choix proposés par le générateur, de sauvegarder une rencontre puis de la jouer soit depuis le PC, soit sur papier.

Principe produit :

> Le générateur propose. Le MJ corrige.

Le Monster Builder n'a pas pour objectif de reproduire le système complet de création des PJ ni de générer tous les aspects imaginables d'un ennemi.

## 2. Périmètre MVP

Inclus :
- authentification ;
- Monster Builder ;
- édition rapide après génération ;
- Bestiaire ;
- création et sauvegarde de Rencontres ;
- Table numérique ;
- Dice Roller Mob ;
- impression A4 d'une Rencontre.

Hors MVP :
- constructeur de PJ ;
- système dédié Élite ;
- générateur de Boss ou miniboss ;
- capacités spéciales de Boss ;
- EVO pour les Mobs ;
- Mods, Accessoires et Viseurs pour les Mobs ;
- économie, loot, véhicules et patrimoine ;
- automatisation exhaustive de toutes les règles TMP.

Un ennemi exceptionnel peut être représenté par un Mob de niveau supérieur et joué plus intelligemment par le MJ. Les miniboss et Boss restent designés manuellement.

## 3. Sources d'autorité

Pour le Monster Builder, le document MONSTER est l'autorité fonctionnelle et numérique.

Le Livre des Règles TMP reste la référence générale de l'univers et des règles de combat, mais le Monster Builder utilise ses propres simplifications lorsqu'elles sont définies dans MONSTER.

Les valeurs de catalogue et de scaling doivent être stockées comme données ou règles centralisées, jamais dupliquées dans l'interface.

## 4. Modèle Mob

### 4.1 Niveau

Le niveau est le premier curseur de difficulté.

Le scaling numérique peut continuer au-delà du niveau 10.

Les caractéristiques de profil, elles, ne progressent jamais au-delà de leur ligne N10 : un Mob N15 conserve les caractéristiques N10 de son profil, tandis que ses valeurs explicitement scalées par niveau continuent d'évoluer.

### 4.2 PV

PV maximum :

    250 + 30 × (Niveau - 1)

Repères :
- N1 : 250 PV ;
- N5 : 370 PV ;
- N10 : 520 PV ;
- N20 : 820 PV ;
- N30 : 1 120 PV.

PV actuels et PV maximum sont stockés séparément sur une instance de Mob jouée.

### 4.3 Base de dégâts

Base :

    50 + 10 × (Niveau - 1)

Dégâts d'une attaque Mob :

    Base + (Puissance de l'arme × 2) + Modificateur du jet

Modificateur du jet :

    (10 - résultat du jet) × 5

Le résultat 10 est neutre. Chaque point sous 10 ajoute 5 dégâts ; chaque point au-dessus retire 5 dégâts.

Les Mobs n'appliquent aucun effet spécial de critique dans ce moteur.

### 4.4 Test d'attaque

Seuil d'attaque :

    10 + bonus de PER + Visée de l'arme + modificateurs contextuels

Le Dice Roller compare le d20 au seuil puis, sur une attaque réussie, utilise le résultat retenu du d20 dans la formule de dégâts Mob.

Les modificateurs contextuels restent modifiables manuellement par le MJ.

## 5. Profils Mob

Cinq profils existent :
- Combattant (C) ;
- Assassin (A) ;
- Tireur (T) ;
- Soutien (S) ;
- Contrôle (K).

Chaque profil possède :
- une table de caractéristiques N1 à N10 issue de MONSTER ;
- un passif simplifié ;
- un pool d'armes compatibles ;
- un pool d'implants compatibles.

Les tables de caractéristiques ne doivent pas être recalculées par une progression générique si MONSTER fournit les valeurs explicites : ces valeurs sont la référence.

### 5.1 Passifs

Le Monster Builder reprend les passifs définis dans MONSTER et intègre directement leurs valeurs permanentes à la fiche lorsque le document le demande.

Exemples actuels :
- Combattant : Blindage, +5 Armure × Niveau ;
- Assassin : Mobilité, +1 Réaction ;
- Tireur : +1 seuil de Vigilance à partir du N10 ;
- Soutien : Protection, +20 PB × Niveau ;
- Contrôle : Domination selon sa définition MONSTER.

## 6. Composition d'un groupe

Le Randomizer utilise une pondération de profils.

Soutien et Contrôle sont volontairement limités dans une escouade :
- de 1 à 4 Mobs : maximum 1 Soutien et maximum 1 Contrôle ;
- de 5 à 10 Mobs : un deuxième Soutien et/ou Contrôle peut apparaître.

Les pondérations numériques exactes seront calibrées pendant le chantier Randomizer et devront rester configurables.

Le MJ doit également pouvoir corriger manuellement le profil d'un Mob généré.

## 7. Armes Mob

### 7.1 Catalogue indépendant

Le catalogue Mob est indépendant du catalogue PJ.

Tiers :
- T1 : socle universel ;
- T2 : arme commune spécialisée ;
- T3 : arme rare spécialisée ;
- T4 : arme exceptionnelle spécialisée.

À partir du T2, une ou plusieurs compatibilités de profil peuvent limiter l'arme.

Le Tier représente d'abord rareté et spécialisation tactique, pas directement la Puissance.

### 7.2 Prise en main

Une arme possède une prise en main structurée :
- 1 main ;
- 2 mains.

Seules les armes 1 main peuvent participer à une configuration Akimbo.

### 7.3 Attribution aléatoire

Le Randomizer doit pouvoir déterminer séparément :
- Tier de l'arme principale ;
- présence éventuelle d'une arme secondaire ;
- qualité/Tier de la secondaire ;
- éventuelle configuration Akimbo.

Les probabilités exactes ne sont pas verrouillées dans ce CdC. Elles seront définies pendant le chantier Randomizer.

La distribution doit pouvoir évoluer avec le niveau : les Tiers élevés peuvent être débloqués progressivement et prendre davantage de poids sans modifier l'architecture.

Les armes secondaires doivent conserver une distribution plus simple/conservatrice afin qu'un Mob de haut niveau ne reçoive pas automatiquement plusieurs armes exceptionnelles.

### 7.4 Édition manuelle

Après génération, chaque arme est remplaçable immédiatement par le MJ via un sélecteur.

Le sélecteur peut filtrer par Tier, profil compatible et/ou afficher toutes les armes lorsque le MJ souhaite forcer un choix.

Changer une arme actualise immédiatement ses valeurs et propriétés sur la fiche.

Le Randomizer n'a pas besoin de produire une combinaison parfaite : corriger quelques armes en quelques clics fait partie du workflow normal.

### 7.5 Restrictions MVP

Les Mobs n'utilisent pas :
- EVO ;
- Ascend / Overcome ;
- Accessoires ;
- Mods ;
- Viseurs.

## 8. Implants Mob

Les implants utilisent la bibliothèque simplifiée MONSTER.

Chaque implant possède au minimum :
- nom ;
- profils compatibles ;
- description courte ;
- éventuelles valeurs directement calculables.

Les compatibilités C/A/T/S/K de MONSTER sont l'autorité.

Les probabilités d'obtention, niveaux d'apparition et éventuel nombre d'implants ne sont pas verrouillés dans ce CdC. Ils seront calibrés pendant le chantier Randomizer.

Après génération, l'implant doit pouvoir être remplacé ou retiré manuellement.

## 9. Monster Builder

### 9.1 Entrée minimale

Le MJ doit pouvoir demander rapidement :
- un nombre de Mobs ;
- un niveau.

Le générateur produit immédiatement le groupe.

Des options de profil pourront permettre de forcer ou orienter la composition sans rendre l'écran initial obligatoire ou complexe.

### 9.2 Sortie

Chaque Mob généré possède au minimum :
- profil ;
- niveau ;
- FOR, AGI, PER, TECH, CON, VOL ;
- PV max ;
- PV actuels ;
- Armure ;
- PB/Bouclier si applicable ;
- Réactions ;
- seuil(s) de Vigilance si applicable ;
- arme(s) ;
- implant éventuel ;
- passif de profil ;
- valeurs nécessaires aux jets.

### 9.3 Philosophie d'édition

Tous les champs utiles à la préparation doivent être rapidement modifiables.

Le MJ peut accepter le résultat aléatoire, changer seulement quelques éléments, ou forcer une configuration inhabituelle.

Les erreurs ou incompatibilités évitables doivent être signalées sans transformer l'outil en système rigide lorsque le forçage manuel est utile.

## 10. Bestiaire

Un Mob préparé peut être sauvegardé dans le Bestiaire.

Le Bestiaire permet au minimum :
- consulter les Mobs sauvegardés ;
- les réutiliser dans une Rencontre ;
- les modifier ;
- les dupliquer ;
- les supprimer.

Une entrée de Bestiaire représente un modèle préparé. Lorsqu'elle est ajoutée à une Rencontre, la Rencontre utilise une instance afin que les PV et ressources de combat ne modifient pas le modèle source.

## 11. Rencontres

Une Rencontre contient un ensemble d'instances de Mobs.

Le MJ peut :
- créer une Rencontre depuis le Monster Builder ;
- ajouter des Mobs du Bestiaire ;
- modifier les Mobs de la Rencontre avant le combat ;
- sauvegarder la Rencontre ;
- la lancer sur la Table numérique ;
- l'imprimer.

Les modifications propres à une Rencontre ne doivent pas altérer silencieusement le modèle du Bestiaire.

## 12. Table numérique

La Table est le mode de jeu sur PC.

Elle doit privilégier la vitesse d'utilisation :
- afficher clairement les Mobs de la Rencontre ;
- suivre PV actuels / maximum ;
- suivre PB/Boucliers utiles ;
- suivre les ressources simples nécessaires ;
- accéder aux armes, implants et passifs sans changer d'écran inutilement ;
- lancer rapidement une attaque via le Dice Roller.

Le MJ doit pouvoir appliquer directement dégâts, soins et modifications de PV.

Le suivi numérique est une option : aucune Rencontre ne doit dépendre de la Table pour être jouable sur papier.

## 13. Dice Roller Mob

Le Dice Roller doit être accessible depuis l'arme du Mob.

Il affiche au minimum :
- seuil d'attaque ;
- d20 ;
- résultat retenu ;
- réussite/échec ;
- Base de dégâts ;
- Puissance ×2 ;
- modificateur du jet ;
- dégâts finaux avant protections de la cible.

Le MJ peut ajouter les modificateurs contextuels nécessaires au seuil.

Les propriétés particulières d'une arme peuvent rester descriptives lorsqu'elles ne nécessitent pas une automatisation utile.

Le MVP privilégie un calcul fiable des attaques courantes plutôt qu'une automatisation exhaustive des effets tactiques.

## 14. Impression de Rencontre

### 14.1 Objectif

Le MJ doit pouvoir jouer une Rencontre sans rester devant le PC.

Un bouton « Imprimer la rencontre » produit une vue A4 dédiée à l'impression à partir de la même Rencontre sauvegardée que la Table numérique.

Il ne s'agit pas d'un second modèle de données.

### 14.2 Contenu

La feuille doit être compacte et lisible debout ou posée sur un calepin.

Elle contient les informations nécessaires au combat :
- profil et niveau ;
- caractéristiques ;
- PV maximum ;
- Armure ;
- PB/Bouclier ;
- Réactions/Vigilance utiles ;
- armes avec Visée, Puissance, portée et propriété courte ;
- implant et effet résumé ;
- passif utile.

Les informations identiques peuvent être regroupées lorsque plusieurs Mobs partagent le même profil/configuration, à condition que le suivi individuel reste évident.

### 14.3 Suivi manuscrit

Chaque Mob individuel possède une ligne de suivi avec au minimum :
- champ vide « Jeton : _____ » ;
- PV ;
- PB/Bouclier si applicable ;
- Réactions ou autres ressources simples si utiles ;
- espace de note court si la mise en page le permet.

Le champ Jeton reste volontairement vide à l'impression afin que le MJ puisse reporter le numéro du jeton physique choisi lors de l'installation de la scène.

## 15. Authentification et propriété des données

L'application nécessite une authentification.

Les Bestiaires et Rencontres appartiennent à leur utilisateur.

Un utilisateur ne peut consulter ou modifier les données privées d'un autre utilisateur.

Le choix d'hébergement reste hors de cette étape et pourra être décidé à la fin du développement MVP.

## 16. Données configurables

Les éléments suivants ne doivent pas être enfouis dans le code de l'interface :
- profils et tables de caractéristiques ;
- armes Mob ;
- implants Mob ;
- compatibilités ;
- Tiers ;
- probabilités du Randomizer ;
- seuils de déblocage ;
- propriétés et descriptions courtes.

Le système doit permettre d'ajuster l'équilibrage sans réécrire le moteur.

## 17. Arbitrages reportés

À définir pendant les chantiers concernés :
- pondération exacte des cinq profils ;
- courbes T1/T2/T3/T4 selon le niveau ;
- niveaux exacts de déblocage des Tiers ;
- chance et qualité d'une arme secondaire ;
- chance et règles exactes d'Akimbo ;
- probabilités, niveaux d'apparition et quantité d'implants ;
- détails finaux de la mise en page d'impression.

Ces arbitrages ne doivent pas bloquer la construction du socle.

## 18. Critères de réussite du MVP

Le MVP est réussi si le MJ peut :

1. se connecter ;
2. demander X Mobs d'un niveau donné ;
3. obtenir immédiatement des fiches cohérentes ;
4. remplacer en quelques clics les armes/implants qu'il ne souhaite pas ;
5. sauvegarder les Mobs utiles ;
6. constituer et sauvegarder une Rencontre ;
7. choisir entre jouer la Rencontre sur PC ou l'imprimer ;
8. lancer les attaques courantes sans calcul manuel répétitif ;
9. gérer les PV sur PC ou au crayon sur la feuille imprimée.

La priorité est le temps gagné en préparation et à la table, pas la simulation exhaustive du Livre des Règles.
