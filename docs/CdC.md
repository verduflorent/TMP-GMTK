Cahier des charges fonctionnel final
TMP Character Editor et GM Toolkit
Version consolidée du 19 septembre 2026 — Référence fonctionnelle réconciliée avec le Livre des Règles TMP V4.
Ce document fixe le périmètre V1, les comportements attendus, les règles nécessaires aux calculs et le modèle conceptuel de l’application. Les points de recette encore indéterminés sont regroupés en section 18 ; aucune réponse implicite ne leur est attribuée.
L’ordre d’autorité appliqué est : réponses ARB-001 à ARB-031 et décisions complémentaires validées ; décisions du brouillon non remplacées ; règles certaines du Livre des Règles TMP V4 ; modèle conceptuel validé à l’issue de l’audit DATA. Les décisions récentes remplacent leurs formulations antérieures. Le Livre des Règles source n’est pas modifié par l’application.
Sources de référence : 00.8 Livre des règles — édition V4 ; Brouillon TMP Editor ; audit fonctionnel et mécanique ; arbitrages post-audit ; audit du modèle de données ; décisions d’authentification et consigne de consolidation finale. Les mentions ARB dans ce document identifient des décisions acquises, pas des questions à rouvrir.
1. Objet et vision
Le TMP Character Editor / GM Toolkit est un outil personnel de Maître du Jeu pour THE MOIRA PROTOCOL. Il facilite la préparation de personnages et de rencontres, puis leur utilisation pendant une partie sans fiches papier pour les PNJ.
Le parcours principal est : créer ou générer une fiche, conserver explicitement les profils utiles dans le Bestiaire, préparer des rencontres, charger des instances sur la Table, lancer les dés et gérer les PV.
L’application privilégie la lisibilité, la rapidité et les actions directes. Une opération courante doit idéalement demander un ou deux clics. Les fiches montrent les informations utiles immédiatement et rendent les descriptions détaillées accessibles au hover ou au clic.
L’application calcule les jets et les dégâts. Le MJ gère le combat.
2. Périmètre V1 et hors périmètre
2.1 Fonctions incluses
    • Éditeur manuel pour Mob, Élite, PNJ, Antagoniste et héros/opérateur, avec identité minimale et données mécaniques.
    • Randomizer de nouvelles fiches Mob/Élite, individuellement ou par composition.
    • Bestiaire privé, profils standards et évolutifs N1→N10.
    • Catalogue d’armes, accessoires, implants, gadgets et Perks, natifs modifiables et éléments personnalisés.
    • Dossiers et sous-dossiers libres pour le Bestiaire et les scénarios/rencontres.
    • Rencontres sauvegardées référençant les versions de personnages du Bestiaire.
    • Table persistante Alliés/Ennemis, fiches indépendantes, PV, Armure et jets.
    • Historique des jets persistant et propre au compte.
    • Authentification obligatoire et isolation des données par utilisateur.
2.2 Fonctions exclues
La V1 ne comporte ni battlemap, ni VTT, ni IA tactique, ni simulation automatique ou équilibrage mathématique complet des combats. Elle ne gère pas automatiquement l’initiative, les tours, déplacements, distances, lignes de vue, couvertures, zones, états, effets temporels ou consommation des Réactions.
Les propriétés telles que Suppression, Impact et Vigilance, les résistances secondaires, le drone et son Ultimate, l’Overdrive, la stabilisation, le sursis, la mort et Dernier souffle restent sous responsabilité du MJ. Les informations correspondantes demeurent consultables.
Métier, loisir, motivation, défaut et autres informations narratives détaillées sont hors V1. L’application ne remplace pas les documents d’écriture de personnages ou de scénarios. Aucun système de loot, économie, XP ou achat d’équipement n’est ajouté au randomizer.
Aucune inscription publique, collaboration entre comptes, gestion avancée de rôles ou plateforme publique n’est requise.
3. Principes fonctionnels
3.1 Autorité du MJ
Le système informe. Le MJ tranche.
L’application calcule la conformité des fiches aux règles applicables. Une anomalie mécanique produit un avertissement visible : budget dépassé ou non dépensé, répartition initiale incorrecte, prérequis insuffisant, équipement incompatible ou occupation excessive d’emplacements.
Le MJ peut modifier et sauvegarder une fiche non conforme, conformément aux décisions de forçage. Les valeurs automatiques forcées deviennent des overrides persistantes, prioritaires jusqu’à l’action Revenir au calcul automatique.
Cette liberté ne permet pas de créer des références inexistantes, de casser les appartenances entre objets ou d’accéder aux données d’un autre utilisateur. Les protections d’intégrité et d’accès restent obligatoires. Le randomizer applique ses règles de génération et ne bénéficie pas implicitement du forçage manuel.
3.2 Calcul, choix et description
Une conséquence automatique ne doit pas être demandée comme choix au MJ. Un choix réellement requis, comme le Perk offensif18 ou la spécialisation Technique, doit être conservé explicitement.
Un champ mécanique structuré est exploité automatiquement selon sa portée. Une description libre est affichée et appliquée manuellement par le MJ. Le texte libre ne constitue pas un programme de règles.
3.3 Réutilisation et indépendance
Le Bestiaire conserve les profils de référence ; les rencontres conservent des compositions préparées ; la Table contient les instances de travail.
Les modifications de la Table ne remontent jamais automatiquement au Bestiaire ou aux rencontres. Les définitions d’équipement restent en revanche vivantes dans le catalogue privé : leur modification affecte leurs utilisations actuelles, sous réserve des overrides explicites. L’historique des jets ne change jamais rétroactivement.
4. Concepts et modèle de données
4.1 Nature des informations
Catégorie	Définition	Exemples
STOCKÉ	Donnée propre à l’objet et nécessaire à son état courant.	Caractéristiques, Armure de base, PV actuels d’instance, quantité, camp, ordre sur Table.
RÉFÉRENCÉ	Relation vers une identité vivante.	Arme équipée vers catalogue ; entrée de rencontre vers CharacterVersion ; profil vers son propriétaire.
DÉRIVÉ	Valeur recalculable depuis les données et règles applicables.	Budget restant, PVmax théoriques, Armure totale théorique, Réactions, coefficient Delta, slots, conformité.
OVERRIDE	Valeur calculable remplacée explicitement par le MJ.	PVmax forcés à32, Armure totale forcée, Puissance d’une occurrence d’arme forcée.
SNAPSHOT	Valeur figée pour préserver une référence ou un résultat historique.	Référence native restaurable ; Puissance, seuil et dégâts réellement utilisés dans un ancien jet.

Une même notion change de catégorie selon son contexte : la Puissance native d’une arme appartient à sa définition ; la Puissance effective équipée est dérivée ; une Puissance forcée est une override ; celle utilisée dans un ancien jet est un snapshot.
La construction copiée à la création d’une instance devient son état courant éditable. Ce n’est pas un snapshot historique immuable. Les définitions d’équipements ne sont pas copiées dans cette construction.
4.2 Entités et responsabilités
Les noms ci-dessous décrivent le domaine, sans imposer un choix ORM, un héritage ou une organisation physique de tables.
Concept	Responsabilité et données essentielles	Relations et contraintes
User / Account	Identité de connexion et propriété de l’espace privé.	Possède profils, dossiers, rencontres, Table, journal et catalogue privé. Aucun partage implicite.
CharacterProfile	Identité réutilisable : nom, type, faction éventuelle, mode standard/évolutif.	Propriétaire et dossier éventuel ; regroupe les versions. Ne porte pas une seconde copie de leur construction.
CharacterVersion	Construction à un niveau : six caractéristiques, Armure de base, niveau, validation.	Appartient à un profil ; affectations, choix et overrides propres. Une version unique pour un standard ; au plus une version par niveau pour un évolutif.
CatalogueEntry / EquipmentDefinition	Identité stable dans le catalogue privé et définition active d’un élément.	Nature arme/accessoire/implant/gadget/Perk ; référence native si applicable ; utilisations vivantes du même compte.
Référence native TMP	Valeurs restaurables et provenance LdR/arbitrages validés.	Référence commune protégée, distincte des personnalisations privées.
EquipmentAssignment	Occurrence effectivement portée, emplacement et place occupée.	Appartient à une version ou à une instance ; référence une définition. Un accessoire est monté sur une occurrence d’arme précise.
Choix et exceptions de capacités	Perk18 offensif choisi, spécialisation Technique, capacités ajoutées ou retirées explicitement.	Références actives ; attributions automatiques dérivées séparément des exceptions MJ.
Override	Cible calculée précise et valeur finale forcée.	Propre à une version, une instance ou une occurrence équipée. Une seule override effective par cible et propriétaire.
Folder	Nom, domaine Bestiaire/Scénarios, parent éventuel.	Propriétaire unique, parent du même compte et du même domaine, absence de cycle.
Encounter	Composition préparée nommée.	Propriétaire, dossier Scénarios éventuel et entrées de composition.
EncounterEntry	Quantité, camp et éventuel ordre préparatoire.	Référence la CharacterVersion choisie ; le profil est accessible par cette version. Pas de copie de fiche.
GameTable	Espace courant persistant.	Une Table courante par utilisateur ; contient ses instances.
TableInstance	Fiche locale : identité minimale, type, niveau, caractéristiques, Armure de base, PV actuels, camp et ordre.	Affectations et overrides propres ; source CharacterVersion facultative ; équipements toujours référencés au catalogue du compte.
RollHistoryEntry	Contexte et résultat historiques figés, date/heure et ordre.	Propre au compte ; aucun lien vivant obligatoire vers la fiche ou le catalogue pour relire un jet.
Paramètres du Randomizer	Distributions, poids et règles de remplissage.	Séparés des caractéristiques effectivement générées ; aucune graine ou fonction de rejeu exact imposée.

Le référentiel de spécialisations Technique conserve leurs noms et descriptions. Il ne constitue pas un simulateur de drone ni un nouveau type d’arme.
4.3 Versions et références
Un profil standard possède une CharacterVersion unique, au niveau choisi. Un profil évolutif regroupe les versions progressivement construites. Les fiches du Bestiaire partagent ainsi le même fonctionnement d’équipement, d’override, de filtrage et d’ajout à une rencontre.
Une entrée de rencontre référence une version, ce qui identifie à la fois le profil et le niveau voulu. Les modifications de cette version sont prises en compte au prochain chargement. La construction d’une instance déjà chargée n’est pas synchronisée avec la version source.
Chaque occurrence d’équipement possède son identité. Deux pistolets identiques peuvent donc avoir des accessoires et des overrides différents. Les limites de slots sont calculées ; une occupation forcée non conforme reste représentable et signalée.
4.4 Calcul et overrides
Pour une cible calculable, la valeur effective est l’override si elle existe, sinon la valeur calculée. La valeur théorique demeure consultable et recalculable. Une override égale à zéro n’est pas une absence d’override.
Les overrides de version et celles de Table sont conceptuellement distinctes. À la création d’une instance, les overrides reprises avec la construction deviennent ses données propres. Un changement ultérieur du profil ne les remplace pas.
Modifier une caractéristique ou l’Armure de base modifie une donnée stockée. Modifier les PV actuels modifie l’état de l’instance. Ces opérations ne doivent pas être confondues avec une override de PVmax ou d’Armure totale.
5. Référentiel mécanique nécessaire
Cette section intègre les règles nécessaires à la création, à l’équipement et aux calculs de l’application. Les propriétés tactiques consultables gardent leur description de référence ; leur résolution demeure manuelle selon la section 2.
5.1 Caractéristiques et création N1
Les caractéristiques offensives sont Force, Agilité, Perception et Technique. Les caractéristiques défensives sont Constitution et Volonté. CON et VOL ne possèdent pas de coefficient Delta offensif.
Au niveau1, chaque offensive commence à5. Les bonus +8, +5, +3 et +0 sont attribués une seule fois chacun : les valeurs forment une permutation de 13/10/8/5. Une simple répartition libre de16 points ne remplace pas cette règle.
CON et VOL commencent chacune à8 ; sept points sont répartis entre elles, sans dépasser13 à la création. Leur somme au N1 est23.
5.2 Progression et budgets
Chaque montée de niveau ajoute deux points offensifs et un point à CON ou VOL. Le plafond normal de chaque caractéristique est18. Mob et Élite emploient exactement le budget de leur niveau.
Niveau	Points offensifs ajoutés depuis N1	Points défensifs ajoutés depuis N1	Somme offensive	Somme défensive
N1	0	0	36	23
N2	2	1	38	24
N3	4	2	40	25
N4	6	3	42	26
N5	8	4	44	27
N6	10	5	46	28
N7	12	6	48	29
N8	14	7	50	30
N9	16	8	52	31
N10	18	9	54	32

Un profil standard créé directement à un niveau donné doit être compatible avec un départ N1 légal puis les ajouts autorisés. La conformité ne se limite pas aux sommes. Pour un évolutif, l’application vérifie en plus les progressions entre les versions enregistrées.
5.3 Seuils et capacités
Condition normale	Capacité ou récompense	Conséquence exploitable par l’application
FOR16	Adaptation	Autorise une principale dans le slot secondaire ; description du changement d’arme gratuit une fois/tour.
AGI16	Dextérité	Deux armes légères possibles dans un même slot principal ; +1 Réaction ; Avantage uniquement avec deux armes identiques à leur portée optimale.
PER16	Verrouillage	+1 Critique ; Avantage conditionnel contre la cible verrouillée, dont le suivi reste au MJ.
TEC16	Prévoyance	+2 slots gadgets.
FOR18 et choix du Perk	Momentum	+1 slot principal ; effet de tour supplémentaire consultable, appliqué manuellement.
AGI18 et choix du Perk	Fulgurance	Résolution spécifique en section 13 ; applicable aux armes légères ou moyennes.
PER18 et choix du Perk	Annihilation	Critique avec Puissance×3.
TEC18 et choix du Perk	Mise à jour	Firmware avancé/Ultimate de spécialisation accessibles ; résolution du drone manuelle.
CON12	Bonus défensif	+5 PV.
CON16	Bonus défensif supplémentaire	+5 PV supplémentaires, soit +10 au total.
CON18	Dernier souffle	Capacité présente ; application manuelle.
VOL12	Déblocage	Premier slot implant.
VOL16	Déblocage supplémentaire	Deuxième slot implant.
VOL18	Détermination	Capacité présente ; application manuelle.
TEC12	Spécialisation Technique	Choix MJ dans l’éditeur, choix aléatoire dans le randomizer.

Les Perks16 offensifs et les récompenses défensives sont automatiques aux seuils concernés. Ils ne font pas l’objet d’un tirage de remplissage ou d’une attribution facultative propre aux Mobs.
Un personnage possède normalement un seul Perk18 offensif parmi FOR/AGI/PER/TEC. Si plusieurs caractéristiques sont à18, l’éditeur demande le choix au MJ ; le randomizer choisit parmi les éligibles. Ce choix ne détermine ni la dominante ni la famille de l’arme principale. Les récompenses CON18/VOL18 sont indépendantes ; aucune exclusivité supplémentaire n’est créée entre elles.
Les spécialisations Technique sont Invasion, Renfort, Bastion et Étau. Leur nom/capacité est identifiable sur la fiche et leur descriptif accessible. Leur choix ne limite pas les équipements. L’Ultimate dépend de Mise à jour, pas du seul fait d’avoir une spécialisation.
5.4 Valeurs dérivées et emplacements
PVmax théoriques = CON +5 si CON≥12 +5 si CON≥16 + bonus permanents de PV applicables + bonus du GPB porté. Le GPB léger ajoute +5 PV ; le moyen +5 PV et +1 Armure ; le lourd +10 PV et +2 Armure. Les catégories de GPB ne se cumulent pas. Les soins ordinaires ne dépassent pas les PVmax effectifs, sauf règle particulière ou correction explicite du MJ.
Armure totale théorique = Armure de base stockée + bonus permanents d’Armure + Armure du GPB porté. Les sources permanentes sont cumulatives. Les bonus temporaires, dont le cumul progressif d’AEGIS, ne sont pas suivis automatiquement.
Réactions maximales théoriques = une Réaction de base + effets permanents applicables, notamment +1 Dextérité. Aucune consommation n’est suivie.
Capacité native	Valeur
Armement	Un slot principal et un slot secondaire.
Momentum possédé	Un slot principal supplémentaire.
Adaptation possédée	Une principale peut occuper le slot secondaire.
Dextérité possédée	Deux légères peuvent partager un même slot principal.
Gadgets	Un slot ; trois avec Prévoyance.
Implants	Zéro sous VOL12 ; un de VOL12 à15 ; deux dès VOL16.
Accessoires	Un par arme, sauf indication contraire.

Les capacités structurées personnalisées peuvent modifier les valeurs et emplacements qu’elles visent. Une capacité disponible ne garantit pas son remplissage par le randomizer.
5.4 bis GPB, Biopuce et Résistance critique
Le GPB et la Biopuce sont des choix d’équipement explicites dans l’éditeur manuel : Aucun, léger, moyen ou lourd. Un prérequis CON/VOL insuffisant produit un avertissement mais n’empêche pas le forçage et la sauvegarde par le MJ.
Dans le Randomizer, GPB et Biopuce sont tirés par une distribution pondérée comprenant « aucun » et les catégories auxquelles le personnage est éligible. Plus CON/VOL sont élevés et plus le profil est qualitatif (Élite plutôt que Mob), plus les catégories hautes sont probables et moins « aucun » est probable. Les pourcentages exacts sont calibrés pendant l’implémentation.
La Biopuce légère (VOL14) ajoute +1 Puissance aux armes ; la moyenne (VOL16) ajoute +1 Puissance et +1 Critique ; la lourde (VOL18) ajoute +2 Puissance et +2 Critique. Ces bonus remplacent ceux des catégories inférieures et s’appliquent aussi aux armes de Puissance 0. Une Puissance positive ne signifie pas à elle seule qu’une propriété de contrôle inflige des dégâts ; le Répulseur exploite notamment sa Puissance dans la formule de dégâts de poussée en cas d’impact.
La Résistance critique est une valeur de combat affichée, de base 0, dérivée des effets permanents et overridable par le MJ. RHODOS apporte +5 Résistance critique. Ses autres déclenchements, son renvoi de dégâts et son Overdrive restent gérés manuellement.

5.5 Delta, Critique et minimum de Force
Le coefficient Delta natif d’une offensive est 5, puis 4 à12, puis 3 à18. Un Stabilisateur le réduit de1 : les coefficients natifs équipés deviennent donc4,3,2. Atteindre16 ne réduit pas le coefficient.
La Visée n’est pas une caractéristique indépendante. Un bonus/malus de Visée modifie le seuil du test d’attaque utilisant la caractéristique de l’arme. Ce modificateur change le seuil effectif et donc la marge du jet, mais ne change jamais le palier du coefficient Delta. Le coefficient Delta dépend de la caractéristique réelle et des seuls effets qui modifient explicitement ce coefficient, comme le Stabilisateur. Les formules complètes de résolution figurent en section 13.
La plage critique native commence à1 ; chaque point de Critique augmente son seuil supérieur de1. Le20 naturel reste un échec critique. Les armes lourdes ne bénéficient pas de Fulgurance ; les autres propriétés de vitesse restent décrites sans extrapolation automatique à des sous-systèmes non gérés.
Pour les armes ayant un minimum de Force, chaque point manquant impose −1 au test d’attaque dans l’usage manuel. Le randomizer exclut ces armes si le minimum n’est pas satisfait.
5.5 bis Variantes Ascend / Overcome
Une arme légendaire reste la même occurrence d’arme et possède une configuration Ascend ou Overcome. Le recalibrage change cette configuration ; il ne crée pas une nouvelle arme indépendante. Une variante peut remplacer des champs structurés du profil actif : caractéristique, Puissance, portée, poids, emplacement, minimum FOR ou propriétés.
La compatibilité des accessoires est évaluée contre le profil mécanique actif après recalibrage. Une incompatibilité nouvelle est signalée mais n’entraîne aucune suppression automatique ; le MJ peut conserver la configuration forcée.
Les valeurs natives et les variantes sont des données de référentiel, pas des constantes dispersées dans le moteur.

5.6 Armes natives
Poids, emplacement, caractéristique et profil sont des informations distinctes. « Spécialisé » n’est pas une autorisation réservée aux Élites. Les propriétés détaillées du LdR IV restent consultables ; seules leurs incidences sur le calcul générique et les effets structurés retenus sont automatisées.
Arme	Stat	Poids / emplacement	Puissance	Portée / profil	Minimum FOR et éléments de calcul particuliers
Fusil d’assaut	FOR	Moyenne / principale	6	Moyenne / polyvalent	Propriété de portée consultable, contexte géré par MJ.
Fusil à pompe court	FOR	Légère / secondaire	8	Courte / spécialisé	Déstabilisation et résistance secondaire manuelles.
Mitrailleuse	FOR	Lourde / principale	5	Moyenne / polyvalent	FOR15 ; Suppression manuelle.
Lance-roquettes	FOR	Lourde / principale	7	Longue / spécialisé	FOR18 ; zone3×3 et récupération manuelles.
Mêlée à deux mains	FOR	Moyenne / principale	7	Contact / spécialisé	FOR12 ; Impact manuel.
Lance-flammes	FOR	Lourde / principale	5	Courte / spécialisé	FOR15 ; cône, fuite, Brûlure et résistances manuels.
Pistolet	AGI	Légère / secondaire	4	Courte / polyvalent	Dégainage consultable.
Pistolet-mitrailleur	AGI	Légère / principale	5	Courte / polyvalent	Fluidité consultable.
Mêlée à une main	AGI	Légère / principale	6	Contact / polyvalent	Riposte manuelle.
Arme de lancer	AGI	Légère / principale	3	Courte / polyvalent	+1 Critique si attaque sans détection ; condition gérée explicitement, sans détection automatique de la scène.
Revolver	PER	Légère / secondaire	5	Moyenne / polyvalent	Sang-froid consultable.
Carabine	PER	Moyenne / principale	5	Moyenne / polyvalent	Mirador/Vigilance manuels.
Fusil de précision	PER	Moyenne / principale	9	Longue / spécialisé	+1 Critique ; Désavantages contextuels du profil à appliquer selon le contexte MJ.
Arc	PER	Moyenne / principale	5	Longue / polyvalent	Trajectoire/couverture manuelles.
GridLock	TEC	Moyenne / principale	0	Courte / polyvalent	Enchevêtrement manuel.
PolyGel	TEC	Moyenne / principale	0	Courte / polyvalent	Zone5×5, résistance et Immobilisation manuelles.
Med Rifle	TEC	Moyenne / principale	3	Moyenne / polyvalent	Protocoles consultables ; leur interprétation dégâts/soin/Avantage reste au MJ lorsque sans différence utile au calcul demandé.
Pistolet IEM	TEC	Légère / secondaire	2	Courte / polyvalent	+2 Puissance contre robots ; zone2×2 manuelle.
Fusil IEM	TEC	Moyenne / principale	4	Moyenne / polyvalent	+2 Puissance robots et +2 cibles Marquées, cumulables.

Le calcul générique d’une arme n’est pas présenté comme la résolution automatique de toutes ses propriétés. Une propriété spéciale ne reçoit pas une formule inventée à partir de sa seule Puissance.
5.7 Accessoires natifs
Accessoire	Famille	Effet de référence
Silencieux	Universel	Arme silencieuse, description manuelle.
Stabilisateur	Universel	Coefficient Delta−1.
Canon renforcé	Universel	Puissance+1.
Assistance de visée	Universel	Visée+2.
Percuteur optimisé	Universel	Critique+1.
Crosse repliable	Force	Ignore les malus de surprise ; interprétation contextuelle MJ.
Holster magnétique	Agilité	Dégainage gratuit ; application manuelle.
Munitions perforantes	Perception	Ignore un niveau de couverture ; application contextuelle MJ.

Les quatre valeurs numériques sont les valeurs applicatives validées par ARB-003. Les armes Technique n’ont pas d’accessoires spécifiques natifs ; cela n’exclut pas les accessoires universels. Aucune restriction individuelle supplémentaire n’est inventée à partir du nom d’un accessoire.
5.8 Implants et gadgets natifs
Les implants exigent un emplacement ouvert par VOL et leur prérequis propre. Les informations d’activation et d’Overdrive sont consultables, sans résolution automatique de l’Overdrive.
Implant	Prérequis	Activation	Incidence permanente automatisable / description utile
AEGIS	CON14	Passif	+2 Armure ; cumul temporaire après attaques géré par MJ.
COLOSSUS	CON16	Passif	+4 Armure ; réussite CON extérieure aux implants décrite et appliquée par MJ.
VELOS	AGI14	Réaction	Déplacement augmenté, description/Overdrive manuels.
SKIA	AGI16	Passif	Dissimulation après élimination, manuelle.
ENCELADE	FOR14	Réaction pendant son tour	Bond et Déstabilisation manuels.
TITAN	FOR16	Passif	Manipulation/projection du décor, manuelle.
SCOPOS	PER14	Passif	Ricochet, application manuelle.
ARGUS	PER16	Passif	Dissimulation/Vigilance, application manuelle.
HARPIE	TEC16	Réaction	Vol et déplacement, manuels.
PHALANX	TEC14	Réaction	Barrière, manuelle ; pas d’ajout à l’Armure permanente.
ANCHOR	VOL14	Passif	Un Avantage aux tests VOL ; autres effets et Overdrive manuels.
ECLIPSE	VOL16	Action	Portail et Immobilisation, manuels.

Les gadgets ne demandent pas de test d’activation. Les éventuelles résistances des cibles sont des règles séparées, laissées au MJ. La fiche indique portée, coût, usages et description, sans compteur automatique de consommation.
Gadget	Portée	Activation / usages	Effet de référence consultable
Grappin	Courte	Action / illimité	Rejoindre un point fixe d’ancrage.
Mine IEM	Courte	Réaction / 2 par combat	Zone5×5 ; désactivation temporaire d’équipement.
Champ gravitationnel	Moyenne	Réaction / 1 par combat	Zone5×5 ; résistance CON et arrêt du déplacement.
Grenade explosive	Moyenne	Action / 1 par combat	8 dégâts, zone3×3.
Grenade flash	Moyenne	Action / 1 par combat	Aveuglement, zone5×5.
Fumigène	Moyenne	Réaction / 2 par combat	Zone7×7 ; −10 Visée pour les attaques traversantes.
Médikit	Contact	Action / 1 par combat	Soin de8 PV.
Cocktail d’urgence	Contact	Action / 1 par combat	Retire les effets négatifs.
Charge de brèche	Contact	Action / 1 par combat	Destruction d’une structure selon la description.
Écran de protection	Courte	Réaction / 1 par combat	Mur de3, absorption20 dégâts ; excédent normal.
Intercepteur balistique	Courte	Réaction / 2 par combat	Zone3×3 ; interception de la prochaine attaque à distance concernée.

Les descriptions complètes, durées et conditions proviennent des sections IV à VI et de l’annexe des états du LdR, complétées par les décisions applicatives. Leur consultation n’ajoute pas de suivi automatique de ces effets.
6. Catalogue
6.1 Consultation, création et édition
Le catalogue privé réunit armes, accessoires, implants, gadgets et Perks. Le MJ peut créer des éléments personnalisés et modifier les natifs. Chaque élément présente son identité, sa nature, sa définition active et ses paramètres de génération.
Les champs structurés proposés correspondent aux capacités réellement comprises par l’application : bonus/malus de Puissance, Visée, Critique, coefficient Delta, Armure, PV, Réactions ; modifications de slots armes/gadgets/implants ; prérequis de caractéristiques ; compatibilités. Les effets et modes natifs nécessaires, dont Annihilation et Fulgurance, restent identifiables.
Pour la PR2, cette automatisation est volontairement bornée aux effets numériques que GMTK sait calculer directement : Puissance, Visée, Critique, coefficient Delta, PVmax, Armure, Réactions, slots principaux/secondaires/gadgets/implants, prérequis et compatibilités. Des conditions simples peuvent qualifier un calcul lorsque le CDC les prévoit explicitement, par exemple cible Robot, cible Marquée ou activation d’un Avantage de Perk. Ces conditions n’introduisent pas de suivi d’état, de cible ou de tour.
Un effet doit avoir une portée précise : porteur, arme concernée ou arme portant l’accessoire, par exemple. Un bonus propre à une occurrence ne s’applique pas automatiquement à toutes les armes de la fiche. Les conditions structurées ne deviennent pas un moteur de combat général.
Une zone de texte libre permet de décrire tout effet spécial non automatisé. Un texte renseigné seul ne modifie aucun calcul. Suppression, Vigilance, Brûlure, Ricochet, Déstabilisation, Overdrive et les autres sous-systèmes exclus restent descriptifs/manuels sauf décision explicite ultérieure.
6.2 Natifs, référence et restauration
Un natif conserve sa référence TMP applicative, incluant les compléments mécaniques validés. L’application distingue l’état actif de cette référence et indique si l’élément est modifié.
Remettre par défaut demande confirmation, conserve l’identité de l’élément et restaure les valeurs natives. Un personnalisé ne propose pas de fausse restauration TMP. Le périmètre de restauration des paramètres de génération, distincts des valeurs mécaniques, reste identifié en section 18.
Les références natives peuvent être communes en lecture. Les modifications actives appartiennent à chaque utilisateur. Une entrée native non personnalisée utilise sa référence ; une entrée modifiée utilise sa définition locale. Les personnages pointent vers l’identité stable de l’entrée privée.
6.3 Catalogue vivant
Modifier la Puissance de la Carabine de5 à6 actualise ses utilisations dans les versions et instances du même utilisateur. Une override de Puissance conserve sa priorité. L’autre utilisateur et les anciens jets ne sont pas modifiés.
Modifier localement l’équipement d’une fiche change ses affectations ; modifier la définition du catalogue change les utilisations de cette définition. Ces deux actions doivent être identifiables sans ambiguïté.
6.4 Pools et raretés
Chaque élément pertinent possède une autorisation Mob et une autorisation Élite, chacune distincte, ainsi qu’une rareté par catégorie : Commun, Peu commun, Rare, Très rare. Le MJ manipule ces catégories, pas les poids internes.
Un élément personnalisé est exclu des deux pools par défaut. Un élément interdit au randomizer reste disponible dans l’éditeur manuel. Les Perks automatiques de seuil ne sont pas transformés en récompenses facultatives par ces réglages.
La correspondance rareté/poids et les probabilités de remplissage sont calibrées pendant l’implémentation. Elles ne sont pas déduites des tables de loot du LdR.
6.5 Suppression protégée
Une suppression cassant une référence vivante est refusée. L’application indique les usages concernés : profils et niveaux, instances ou autres éléments explicitement référents, dans le périmètre privé du compte.
Le masquage/désactivation éventuel d’un natif ne détruit pas les références existantes. Il est distinct de l’interdiction Mob/Élite. Ses modalités de gestion restantes figurent en section 18.
7. Éditeur manuel
Le MJ choisit le type de personnage, le niveau et le mode standard ou Évolution. L’assistant utilise les règles communes de la section 5 et affiche les points offensifs et défensifs restant à répartir.
La construction N1 conserve l’attribution des quatre bonus offensifs imposés. Pour un niveau supérieur, l’assistant distingue le départ légal et le budget de progression. Les choix manuels mettent à jour la conformité et les conséquences calculables en temps réel.
Atteindre un seuil fait apparaître automatiquement ses conséquences : Perks16, bonus de PV, emplacements, coefficients Delta, prérequis nouvellement satisfaits. À TEC12, le MJ choisit sa spécialisation. À plusieurs offensives18, il choisit son unique Perk18 offensif.
Les équipements sont présentés par caractéristique associée lorsque pertinent. Ceux correspondant aux caractéristiques fortes sont recommandés, tout en laissant accès au catalogue complet. Un équipement non conforme reste sélectionnable avec warning. Une arme sous minimum de Force conserve le malus TMP applicable.
Si Fulgurance est possédée, l’éditeur met en avant les configurations adaptées, notamment plusieurs armes lorsque les règles le permettent. Cette recommandation n’est pas une obligation d’équipement.
Les modifications et forçages suivent la section 3. La sauvegarde au Bestiaire conserve la construction, ses choix, ses affectations et ses overrides ; elle ne nécessite pas de supprimer les warnings mécaniques.
8. Mode Évolution
Le mode Évolution est choisi à la création du profil. Il permet de construire jusqu’aux dix versions N1 à N10, avec un parcours strictement séquentiel.
Pour créer N+1, le niveau N doit avoir été terminé. La nouvelle version hérite de ses caractéristiques, équipements, accessoires, implants, gadgets, capacités et autres données de construction. L’éditeur ajoute ensuite les possibilités normales de progression +2 offensifs/+1 défensif. Les choix sont manuels ; l’équipement hérité peut être conservé ou modifié.
La progression est sauvegardée. Le MJ peut quitter au N6 et reprendre la construction de N7 ultérieurement. Les versions N1 à N6 déjà validées sont utilisables immédiatement, sans attendre N10. Le profil indique qu’il est évolutif, les niveaux disponibles et, le cas échéant, la construction en cours.
L’ajout à une rencontre ou à la Table utilise exactement la version choisie, avec sa construction et ses références d’équipement actuelles. Aucun niveau absent n’est proposé ; aucune version n’est générée indépendamment pour compléter un saut.
Il n’existe aucune rétropropagation automatique entre versions. Les conséquences d’une modification d’une ancienne version sur la validation de la suite restent un point de recette identifié en section 18, sans propagation inventée.
9. Randomizer
9.1 Entrées et résultat attendu
Le randomizer crée de nouvelles fiches au moment de la génération. Il ne pioche jamais automatiquement dans le Bestiaire. Il remplit les mêmes données fonctionnelles que l’éditeur manuel, en appliquant les règles TMP et les politiques de génération ci-dessous.
Le MJ fournit le niveau ou la fourchette, la quantité et le type Mob/Élite, ou le nombre d’Élites pour une composition. La quantité représente le total, Élites inclus : huit personnages dont deux Élites produisent six Mobs et deux Élites.
Le camp est choisi avant génération : Ennemi par défaut, avec switch Allié/Ennemi. La validation ajoute directement le lot sélectionné dans ce camp, sans demander à nouveau sa destination.
La faction n’influence pas le générateur. Elle demeure une information de classement et de recherche pour les profils.
9.2 Ordre du pipeline
Étape	Traitement obligatoire
1. Contraintes du lot	Conserver quantité totale, nombre d’Élites, bornes de niveau et camp.
2. Types, niveaux et orientations	Élites au maximum de la fourchette ; Mobs dans la fourchette. Si quantité≥4, garantir au moins une orientation FOR, AGI, PER et TEC ; orientations supplémentaires libres selon calibration.
3. Caractéristiques	Construire des valeurs légales pour le niveau selon la section 5. Mob semi-aléatoire ; Élite par allocation offensive prioritaire.
4. Capacités	Attribuer les seuils automatiques ; choisir aléatoirement le Perk18 offensif parmi les éligibles et une spécialisation Technique si TEC≥12.
5. Armure de base	Tirer la valeur0/1/2/3 selon la distribution Mob/Élite validée.
6. Emplacements	Calculer les capacités disponibles après les Perks et effets applicables.
7. Équipement admissible	Filtrer selon catégorie, slot, compatibilités, prérequis et autorisation Mob/Élite ; exclure toute arme sous minimum FOR.
8. Arme principale	Chercher dans les offensives maximales ; départager aléatoirement ; se replier sur les valeurs suivantes si aucun candidat légal.
9. Autres affectations	Remplir secondaire, slots additionnels, accessoires, implants et gadgets selon les règles et probabilités applicables.
10. Contrôle final	Recalculer les valeurs ; vérifier budget, prérequis, compatibilités, emplacements, choix et présence d’au moins une arme.
11. Prévisualisation	Présenter les nouvelles fiches sélectionnées par défaut, avec reroll et modification individuels.
12. Validation	Ajouter la sélection à la Table, sans création automatique de profils du Bestiaire.

9.3 Construction Mob et Élite
Un Mob peut être relativement polyvalent ou naturellement spécialisé. Sa répartition est semi-aléatoire, dans le budget légal.
Un Élite utilise un ordre de priorité des quatre offensives. Le générateur investit autant que légalement possible dans la première, puis dans la suivante lorsqu’elle est suffisamment remplie ou plafonnée, et ainsi de suite. Le budget de niveau et le plafond18 restent obligatoires. Cette concentration, et non des points supplémentaires, produit la spécialisation. Les modalités non chiffrées d’allocation restent dans les paramètres à définir/calibrer ; elles ne permettent jamais de contourner le départ N1.
Une orientation de génération n’est ni une classe ni un Perk. Une fois les stats établies, la dominante correspond à leur maximum offensif. Les égalités sont résolues aléatoirement, sans priorité artificielle d’une caractéristique. L’orientation conservée pour le reroll appartient aux contraintes de cette génération.
9.4 Choix des armes
Toutes les caractéristiques partageant la valeur maximale sont candidates pour fournir l’arme principale, indépendamment du Perk18 choisi. AGI18/PER18 avec Fulgurance peut donc recevoir une principale de PER.
En l’absence d’arme principale légale dans la famille maximale examinée, le générateur considère les autres candidats au même rang puis les caractéristiques suivantes par valeur décroissante, avec départage aléatoire des égalités. Il ne régénère pas le personnage pour ce motif.
Le secondaire est souhaitable mais non garanti. Sa famille est choisie parmi la meilleure valeur offensive et la deuxième valeur du classement, égalités incluses. Ainsi16/13/13/13 conserve les quatre caractéristiques candidates ;16/14/12/9 ne conserve que celles à16 et14. Adaptation autorise une principale dans le slot secondaire.
Les slots supplémentaires suivent la même logique de capacités légales et de remplissage que les slots standards. Les armes identiques sont autorisées lorsque la configuration le rend pertinent, notamment akimbo/Fulgurance. Le choix du Perk18 ne restreint pas leurs familles.
Le résultat généré doit posséder au moins une arme. Si tout le catalogue admissible est vide, l’application ne peut annoncer une génération conforme ni inventer une arme ou contourner une interdiction. Le traitement précis de cette impossibilité est un point de recette de la section18.
9.5 Pools, remplissage et doublons
Le nombre de slots vient des règles TMP et des effets structurés, jamais d’un quota artificiel propre au type Mob/Élite.
Les Mobs peuvent laisser des slots disponibles vides. Les Élites exploitent davantage leurs possibilités légales. Cette différence s’applique aux armes secondaires/additionnelles, accessoires, implants et gadgets.
Pour chaque affectation, le système prend en compte emplacement réel, prérequis, compatibilités, autorisation de la catégorie, rareté correspondante et probabilité de remplissage. Un accessoire est sélectionné pour l’arme précise qui le porte.
Le randomizer ne génère pas de doublons d’implants, de gadgets ou d’accessoires sur un même personnage. L’exception autorisée concerne les armes. Ces politiques aléatoires ne constituent pas des interdictions de sauvegarde des fiches forcées manuellement.
Les capacités automatiques ne sont pas soumises à un tirage de remplissage. Les éléments personnalisés n’entrent dans les tirages qu’après activation explicite de leur autorisation.
9.6 Armure de base
Armure de base	Mob	Élite
0	50%	10%
1	30%	50%
2	15%	30%
3	5%	10%

La valeur tirée est stockée dans la fiche. Les bonus permanents s’y ajoutent ensuite. Ces distributions sont validées et ne sont pas remplacées par les calibrations différées des raretés ou du remplissage.
9.7 Génération multiple, prévisualisation et sauvegarde
Une quantité de cinq produit cinq constructions individuelles, pas cinq copies d’un même profil. Tous les résultats sont sélectionnés par défaut ; le MJ peut gérer la sélection avant validation globale.
Reroll régénère seulement la fiche choisie en conservant type, niveau et orientation offensive. Les autres fiches ne changent pas. Modifier ouvre la modification manuelle avec warnings et forçages habituels.
Valider la sélection ajoute le lot sélectionné à la Table. Sauvegarder au Bestiaire est une action explicite disponible pour chaque fiche générée ; elle n’est jamais exécutée implicitement par la validation du lot.
Les probabilités précises de rareté, de remplissage et les autres pondérations non fournies sont calibrées pendant l’implémentation à partir de séries de générations. Le CDC fixe les invariants ci-dessus, sans inventer les pourcentages manquants.
10. Bestiaire
Le Bestiaire est la bibliothèque privée de profils réutilisables. Il permet création, consultation, modification, suppression protégée et sauvegarde explicite de personnages générés.
Le MJ organise les profils dans des dossiers/sous-dossiers libres : création, renommage, déplacement et suppression sous les protections de la section16. Cette organisation n’impose pas de faction ni de hiérarchie prédéfinie.
Une recherche par nom complète les filtres de type, niveau, dominante offensive, présence d’implant, gadget ou Perk. La faction peut servir au classement et à la recherche. Les outils de recherche restent utilisables indépendamment des dossiers.
Un filtre N6 affiche directement la versionN6 des profils évolutifs qui la possèdent et l’ont validée. Les autres filtres mécaniques s’appliquent à cette même version. Le MJ peut choisir une autre version disponible avant ajout. Un niveau inexistant ou non validé n’est pas proposé comme disponible.
L’ajout à une rencontre ou à la Table permet de choisir la quantité et la version pertinente. Sur Table, plusieurs exemplaires deviennent des instances indépendantes. Une modification du profil n’actualise pas leur construction déjà copiée.
Depuis une instance possédant une source, Mettre à jour le profil du Bestiaire est une action distincte, avec confirmation avant écrasement. Le contenu exact repris et le cas d’un niveau local modifié sont précisés avant implémentation de ce parcours, selon la section18.
11. Scénarios et rencontres
L’espace Scénarios utilise son propre arbre de dossiers et sous-dossiers, sans profondeur métier imposée. Des dossiers peuvent représenter campagne, épisode, scène ou variantes, sans transformer l’application en outil d’écriture narrative.
Une rencontre préparée est une composition nommée et persistante. Elle contient des entrées référençant les CharacterVersion du Bestiaire, avec quantité et camp Alliés/Ennemis. Un ordre préparatoire peut être conservé s’il est utilisé pour la composition ; il n’est pas un système d’initiative.
Le MJ doit pouvoir préparer, consulter et modifier ces compositions, les classer, les renommer, les déplacer, les retrouver et les supprimer selon les protections applicables. La recherche par nom et l’organisation en dossiers sont disponibles ; les filtres supplémentaires non déterminés restent un point de recette.
Si une version du Bestiaire change, le prochain chargement de la rencontre utilise sa construction actuelle. Le chargement crée de nouvelles instances indépendantes pour les quantités demandées. Blesser, modifier, changer de camp ou retirer une instance ne modifie ni la rencontre ni son profil source.
Le choix entre ajout et remplacement lors d’un chargement sur Table occupée n’est pas imposé par ce CDC tant que le point de recette correspondant n’est pas précisé. Aucune donnée courante ne doit être perdue par une interprétation silencieuse de ce cas.
12. Table de jeu
12.1 Accueil et organisation
Après authentification, la page d’accueil est la Table de jeu de l’utilisateur. Le Bestiaire, le générateur, le catalogue et les scénarios restent accessibles depuis cet espace principal.
La Table distingue visuellement Alliés et Ennemis, avec le même système de fiche. Le Drag & Drop change le camp sans modifier les autres données de construction ou de combat. Le réordonnancement dans un camp est libre et persistant ; il ne représente pas un ordre d’initiative imposé.
12.2 Fiche compacte et modifications locales
Chaque fiche montre l’identité, le niveau, les PV, l’Armure, les caractéristiques, les Réactions maximales, l’armement et les capacités utiles. Perks, implants et gadgets peuvent être affichés principalement par leur nom. Les armes montrent leur nom et leur accessoire éventuel ; hover/clic donne stat, Puissance, portée, Delta, propriété et effets de l’accessoire.
Les boutons de jet sont associés aux caractéristiques et aux armes. Les champs de modificateur et contrôles ADV/DES sont rapidement accessibles. Les descriptions de règles ne nécessitent pas d’ouvrir le LdR pour l’usage courant.
Le MJ peut modifier localement caractéristiques, équipement, capacités et valeurs autorisées. Les overrides locales sont visibles et persistantes. Les équipements restent liés au catalogue actif du compte.
12.3 PV et Armure
Chaque instance possède ses PV actuels propres et une barre dynamique affichant PV actuels/PVmax effectifs.
Deux opérations complémentaires sont disponibles :
    • Dégâts bruts : le MJ saisit le montant ; l’application applique l’Armure effective puis retire la perte de PV correspondante. Exemple8 dégâts avec Armure2 : perte6. Une réduction ne crée pas de soin.
    • Modification directe des PV : correction manuelle de la barre/valeur, sans seconde application d’Armure. Elle permet soins, dommages particuliers, effets ignorant l’Armure et situations exceptionnelles.
Le calcul d’un jet d’attaque ne retire pas automatiquement des PV à une cible. Le MJ reste responsable de la réaction de la cible et de l’application des résultats.
PV=0 donne une fiche grisée/Hors combat, sans retrait automatique. PV>0 rétablit l’affichage normal. Ce statut visuel n’ajoute ni stabilisation, ni sursis, ni mort, ni blocage des jets utiles au MJ.
Les bonus temporaires d’Armure et leur expiration ne sont pas suivis. Une correction locale peut être utilisée par le MJ sans créer de compteur AEGIS ou de gestionnaire de tours.
12.4 Retrait et nettoyage
Le bouton de retrait individuel retire immédiatement l’instance sans confirmation. Il est suffisamment isolé des commandes fréquentes pour limiter les erreurs. Le profil source, la rencontre et le journal sont conservés.
Nettoyer la Table demande confirmation puis retire les instances. Cette action ne supprime aucun profil, scénario, rencontre ou jet historique. La Table, ses camps, son ordre, ses PV et ses modifications locales survivent aux fermetures, reconnexions et changements de PC tant qu’ils ne sont pas explicitement retirés.
13. Dice Roller
13.1 Périmètre du calcul
Le Dice Roller automatise d20, caractéristique utilisée, seuil effectif, bonus/malus, Avantage/Désavantage, verdict, Critique, coefficient et Bonus Delta, Puissance, dégâts, effets structurés directement applicables et Fulgurance.
Les tests génériques de caractéristiques/résistance sont accessibles. Ils ne déclenchent pas automatiquement les sous-systèmes de survie, d’Overdrive ou les résistances secondaires d’armes.
Portée, couverture, surprise, positionnement et autres circonstances de scène ne sont pas interprétés automatiquement. Le MJ utilise les ajustements proches du dé et les descriptions consultables. L’interface n’ajoute pas systématiquement des questions de portée ou de couverture.
Les contrôles contextuels apparaissent uniquement lorsqu’ils modifient réellement un calcul pris en charge : par exemple Robot/Marqué pour les bonus de Puissance IEM, ou l’activation d’un Avantage conditionnel comme Dextérité. Ils peuvent être présentés sous forme de petites icônes ou contrôles directement sur la carte de l’arme afin de rester rapides à utiliser. Cliquer une telle condition signifie uniquement « cette condition s’applique à ce jet » : GMTK ne mémorise pas que la cible est Robot, Marquée, verrouillée ou dans un état particulier. Un sélecteur purement narratif ou redondant, notamment de protocole Med Rifle sans différence utile au calcul demandé, n’est pas ajouté.
13.2 Valeurs de préparation du jet
La caractéristique de l’arme est sélectionnée automatiquement. Le seuil effectif est la valeur de la caractéristique augmentée ou diminuée des modificateurs applicables, dont le bonus/malus MJ. Les effets structurés connus et leurs portées sont pris en compte ; le détail permet de distinguer leurs contributions des ajustements contextuels.
La Puissance effective provient de l’arme, de l’accessoire, des bonus structurés applicables au contexte et des overrides prioritaires. La plage de Critique tient compte des bonus applicables, dont ceux des accessoires et Perks.
Le coefficient Delta effectif est déterminé par la caractéristique réelle et les modificateurs qui ciblent explicitement le coefficient Delta. Un bonus ou malus appliqué au seuil du jet ne fait jamais franchir un palier de coefficient Delta. Exemple : une caractéristique à11 avec +5 au jet utilise un seuil effectif16 mais conserve son coefficient Delta natif5, sauf effet explicite tel qu’un Stabilisateur.
13.3 Avantage et Désavantage
Les niveaux d’Avantage et Désavantage s’annulent niveau par niveau, en combinant les sources automatiques connues et les ajustements indiqués par le MJ.
Entrées	Solde	Dés lancés et retenus
ADV2 et DES1	ADV1	2d20, meilleur résultat.
ADV1 et DES1	Normal	1d20.
ADV1 et DES2	DES1	2d20, pire résultat.
ADV2 seulement	ADV2	3d20, meilleur résultat.

Dans la résolution ordinaire sous caractéristique, le meilleur est le plus petit résultat et le pire le plus grand. Tous les dés et celui retenu sont affichés. Les contrôles permettent Normal, ADV/DES1 et2, ainsi que les niveaux supérieurs nécessaires. Un modificateur numérique et ADV/DES sont deux entrées distinctes et cumulables.
13.4 Ordre de résolution
    1. Calculer le seuil effectif, la Puissance, le coefficient Delta et la plage critique applicables.
    2. Combiner les Avantages/Désavantages et calculer le solde.
    3. Lancer le nombre de d20 requis et déterminer le résultat retenu.
    4. Si ce résultat est un 20 naturel, conclure à l’échec critique.
    5. Sinon, s’il appartient à la plage critique, conclure à la réussite critique, même s’il dépasse le seuil effectif.
    6. Sinon, comparer au seuil effectif : résultat inférieur ou égal = réussite ; supérieur = échec.
    7. Pour une attaque réussie, calculer le Bonus Delta et les dégâts selon les formules ci-dessous.
    8. Afficher le résultat et conserver son contexte dans l’historique.
La présence d’un20 sur un dé non retenu ne remplace pas le résultat du dé retenu. Les conséquences narratives d’un échec critique sont déterminées par le MJ.
13.5 Bonus Delta et dégâts
Pour une attaque réussie :
Bonus Delta = partie entière inférieure de ((seuil effectif − résultat retenu) / coefficient Delta effectif), avec un minimum de0.
Dégâts ordinaires = Puissance effective + Bonus Delta.
Dégâts critiques standards = Puissance effective×2 + Bonus Delta.
Dégâts critiques avec Annihilation = Puissance effective×3 + Bonus Delta.
Le Bonus Delta n’est jamais multiplié par le critique. Annihilation remplace le multiplicateur2 par3, sans cumuler les deux.
Exemple validé : PER16, malus−2, seuil14, résultat7, coefficient4 → plancher((14−7)/4)=+1 Delta. Le calcul ne repart pas de PER16 brute.
Un critique reste prioritaire lorsqu’il appartient à la plage critique malgré un résultat supérieur au seuil effectif. Dans ce cas, la réussite critique est conservée et le Bonus Delta vaut0. Exemple : seuil effectif2, plage critique1–3, résultat3 → réussite critique, Bonus Delta0.
Ces dégâts sont les dégâts calculés du jet, avant application manuelle à une cible et réduction par son Armure via la Table. Un échec n’inflige pas automatiquement les dégâts génériques d’une attaque réussie ; les propriétés spéciales restent au MJ.
13.6 Fulgurance
Fulgurance utilise un seul jet d’attaque et un seul calcul de dégâts d’une frappe. Le Dice Roller propose Concentré / Réparti et affiche le résultat correspondant à partir de cette même valeur.
Pour une frappe calculée à5 dégâts :
    • Concentré : deux frappes de5 dégâts sont appliquées à la même cible ; la présentation peut afficher10 dégâts bruts au total, mais les deux frappes restent distinctes pour l’application de l’Armure.
    • Réparti : 5 dégâts sur la cibleA et5 sur la cibleB.
Il n’y a ni deuxième jet, ni deuxième calcul Delta indépendant. Le même résultat mécanique est appliqué deux fois. En mode Concentré, l’Armure de la cible s’applique séparément à chacune des deux frappes. Exemple : frappe5, Armure2 → (5−2)+(5−2)=6 PV perdus, et non10−2=8.
Les restrictions aux armes légères/moyennes restent applicables. L’utilisation de Fulgurance avec le Fusil de précision applique le Désavantage prévu pour cette combinaison à l’unique jet de Fulgurance ; aucun second jet n’est créé. Le choix de cible, ses Réactions et les autres effets tactiques ne deviennent pas un suivi automatique.
13.7 Présentation du résultat
Le résultat doit permettre de comprendre rapidement : stat et seuil employés, modificateur, dés, dé retenu, réussite/échec/critique/échec critique, Bonus Delta et dégâts pertinents. Les contributions structurées et le mode Fulgurance sont accessibles lorsqu’ils interviennent.
Une valeur définie seulement par texte libre ne reçoit pas de contribution numérique implicite. Une fiche peut conserver une override même si cette valeur rend un calcul particulier impossible. Dans ce cas, GMTK ne fabrique aucun résultat : le Dice Roller refuse uniquement le calcul concerné et affiche un message explicite indiquant la valeur invalide à corriger. Exemple : coefficient Delta forcé à0 → fiche conservée, jet non calculé, message d’erreur clair.
14. Historique des jets
Le journal est global au compte, chronologique et persistant jusqu’à sa suppression explicite. Il n’est pas séparé par rencontre et ne nécessite aucune session de jeu à créer, ouvrir ou fermer.
Chaque entrée fige les informations nécessaires pour comprendre le résultat :
    • date/heure et ordre ; identité/nom du personnage au moment du jet ; nature du test ;
    • caractéristique et valeur utilisées ; arme et éléments contributifs identifiables ;
    • bonus/malus, seuil effectif, sources ADV/DES et solde ;
    • dés obtenus et résultat retenu ; plage critique et verdict ;
    • coefficient Delta, Bonus Delta, Puissance et dégâts utilisés/obtenus lorsque pertinents ;
    • choix contextuels calculés et overrides ayant influencé le résultat ;
    • mode Fulgurance, valeur de frappe et résultat présenté lorsque applicable.
Le journal n’a pas besoin d’une copie complète de la fiche ou du catalogue. Il doit cependant conserver les valeurs effectives du jet, et non de simples liens vers leurs valeurs présentes.
Modifier ou supprimer l’instance, modifier le profil, renommer une arme ou changer sa Puissance ne modifie jamais les entrées passées. L’identification historique peut être conservée sans référence vivante obligatoire vers les objets supprimés.
Fermer le navigateur, se reconnecter, changer de PC ou nettoyer la Table conserve le journal. Vider l’historique est une action distincte demandant confirmation ; elle ne nettoie pas la Table ni les bibliothèques.
15. Authentification
L’application est privée. L’authentification est obligatoire pour consulter ou manipuler les données. La V1 prévoit la connexion et la déconnexion, sans inscription publique.
Chaque compte possède ses profils et versions, dossiers, scénarios/rencontres, Table, historique, éléments personnalisés et modifications actives du catalogue. Les références natives TMP communes restent protégées des éditions personnelles.
L’isolation s’applique à la consultation, recherche, filtres, calculs, sauvegardes, chargements, suppressions et listes d’usages. Connaître l’identifiant d’un objet d’un autre compte n’autorise pas son accès. Une relation privée ne peut associer des objets appartenant à deux utilisateurs différents.
Plusieurs comptes doivent être possibles sans refonte du modèle. Aucun groupe, rôle avancé ou partage collaboratif n’est nécessaire en V1. Le moyen opérationnel de création des comptes privés et le mécanisme concret d’authentification sont choisis à la conception technique, sans imposer ici un fournisseur.
Une connexion authentifiée n’est pas une session de jeu. La déconnexion met fin à l’accès authentifié et ne supprime aucune donnée persistante. Une reconnexion au même compte depuis un autre PC retrouve son espace privé.
16. Persistance et intégrité
16.1 Données conservées
La persistance couvre profils, versions validées et travail évolutif en cours, affectations et choix, overrides, classement, rencontres, définitions personnalisées/actives, paramètres privés du catalogue, Table et journal.
Les données propres à une instance restent indépendantes du profil ; les définitions d’équipement continuent à suivre le catalogue privé. Les valeurs dérivées ne sont pas des données saisies supplémentaires à maintenir en parallèle, sauf override explicite. Le journal fait exception au recalcul : il conserve ses snapshots.
16.2 Relations protégées
Une suppression est refusée lorsqu’elle casserait une référence vivante. L’application indique clairement les objets qui l’empêchent. Cela concerne notamment une CharacterVersion utilisée par une rencontre, une source de Bestiaire encore référencée par une instance et un équipement utilisé par une fiche.
Les relations respectent les appartenances au compte, au profil, à la fiche et au dossier. Un accessoire est monté sur une occurrence d’arme de la même fiche ; une version référencée appartient au profil concerné ; les dossiers n’ont pas de cycles ni de parent dans l’autre arbre.
Les snapshots du journal ne sont pas des relations vivantes bloquant le retrait d’instances ou la suppression d’objets autrement non utilisés.
16.3 Actions et portée des effets
Action	Effet direct	Données préservées
Modifier une version du Bestiaire	Sa construction change ; futurs chargements utilisent cette version actuelle.	Constructions des instances déjà présentes et anciens jets.
Modifier une définition du catalogue privé	Ses utilisations vivantes suivent les valeurs actives.	Autres comptes, référence native, overrides prioritaires et anciens jets.
Modifier une instance	Change seulement sa construction/son état local.	Profil, rencontre source et autres instances.
Mettre à jour volontairement la source	Écrasement explicite confirmé selon le parcours prévu.	Pas d’écrasement implicite lors de l’édition locale.
Retirer une instance	Retrait immédiat, sans confirmation.	Profil, rencontre et historique.
Nettoyer la Table	Retire les instances après confirmation.	Bibliothèques, catalogue et historique.
Vider l’historique	Efface les entrées après confirmation.	Table et données de préparation.
Remettre un natif par défaut	Restauration confirmée de l’entrée privée.	Identité, références existantes, overrides, autres comptes et historique.
Se déconnecter	Termine l’accès authentifié.	Toutes les données persistantes du compte.

Les suppressions importantes de données préparées demandent confirmation. La protection contre les références cassées s’applique même après confirmation. La suppression d’un dossier non vide reste à préciser conformément à la section18.
17. Critères d’acceptation
Les critères ci-dessous vérifient les comportements décidés. Les points explicitement ouverts en section18 ne reçoivent pas de résultat attendu inventé. Les exemples mécaniques s’entendent sans autre effet ni override que ceux mentionnés.
17.1 Construction, équipement et évolution
ID	Situation	Résultat attendu
AC-001	Créer un N1 avec offensives13/10/8/5 et défensives11/10.	Répartition conforme, budgets entièrement dépensés.
AC-002	Répartir9/9/9/9 en offensives au N1.	Warning malgré la somme36 ; forçage et sauvegarde manuelle possibles.
AC-003	Créer un standard N4.	Six points offensifs et trois défensifs de progression depuis un N1 légal ; une CharacterVersion unique, pas quatre versions imposées.
AC-004	CON passe de11 à12, puis atteint16.	PVmax théoriques11→17, puis26 ; bonus CON16 cumulé avec celui deCON12.
AC-005	VOL passe de11 à12, puis de15 à16.	Premier puis deuxième emplacement implant débloqués.
AC-006	AGI15→16 et TEC15→16.	Dextérité porte les Réactions maximales1→2 ; Prévoyance porte les slots gadgets1→3. Aucun compteur de consommation ajouté.
AC-007	FOR16, puis Momentum effectivement possédé.	Adaptation autorise une principale dans le secondaire ; Momentum ajoute un principal.
AC-008	AGI18/PER18, choix de Fulgurance.	Un seul choix offensif18 normal ; PER reste candidate pour l’arme principale.
AC-009	TEC atteint12.	Choix de spécialisation demandé en manuel, aléatoire dans le randomizer ; nom et description accessibles sur la fiche.
AC-010	Sélectionner manuellement COLOSSUS avec CON insuffisante ou sans slot normal.	Warning explicite ; sélection et sauvegarde possibles avec forçage.
AC-011	Deux pistolets identiques occupent légalement un principal avec Dextérité.	Deux occurrences distinctes ; modifier l’accessoire ou l’override d’une occurrence ne change pas l’autre.
AC-012	Forcer PVmax à32, puis changer CON.	Calcul théorique actualisé mais PVmax effectifs restent32 ; indicateur d’override ; retour automatique rétablit la valeur théorique actuelle.
AC-013	Construire un évolutif jusqu’àN6, quitter puis revenir.	Travail conservé ; N1–N6 validés utilisables ; N7 absent tant que non construit ; reprise séquentielle possible.
AC-014	Essayer de construire N6 directement aprèsN2.	Saut refusé dans le parcours Évolution ; la liberté de forcer une valeur mécanique ne supprime pas la séquence obligatoire.
AC-015	Créer N5 depuisN4.	Héritage de la construction et de l’équipement ; +2/+1 de progression ; N4 reste une version distincte.

17.2 Catalogue et randomizer
ID	Situation	Résultat attendu
AC-016	Créer un équipement personnalisé.	Disponible dans l’éditeur ; autorisations Mob et Élite désactivées initialement.
AC-017	Autoriser une arme uniquement pour Élite.	Absente des tirages Mob, disponible aux tirages Élite si les autres conditions sont satisfaites ; toujours accessible manuellement.
AC-018	Modifier Carabine P5→P6 dans le catalogue du compteA.	Versions et instances deA utilisant cette entrée suiventP6 sauf override ; compteB et anciens jets restent inchangés.
AC-019	Déclencher puis annuler « Remettre par défaut », puis confirmer.	Annulation sans changement ; confirmation restaure les valeurs natives concernées en conservant l’identité.
AC-020	Décrire un effet spécial uniquement en texte libre.	Description consultable ; aucun bonus numérique automatiquement déduit du texte.
AC-021	Générer huit personnages N4–N6 dont deux Élites.	Six Mobs dans la fourchette et deux Élites N6 ; au moins une orientation FOR/AGI/PER/TEC dans le lot.
AC-022	Générer un Élite à un niveau donné.	Budget exactement égal à celui du niveau ; spécialisation par allocation, aucun point ou bonus de PV artificiel propre au type.
AC-023	Catalogue sans candidat légal dans la dominante, mais candidat disponible dans une offensive suivante.	Repli vers la famille admissible suivante ; pas de régénération complète du personnage.
AC-024	Personnage de FOR14 et arme nécessitant FOR15.	Arme exclue de son pool aléatoire ; en édition manuelle, équipement possible avec malus−1 au test.
AC-025	Générations avec slots implant/gadget/accessoire disponibles.	Aucun doublon de ces éléments sur une fiche générée ; armes identiques possibles dans une configuration pertinente.
AC-026	Vérifier les paramètres de tirage d’Armure.	Mob50/30/15/5% et Élite10/50/30/10% pour valeurs0/1/2/3. Les petits lots ne sont pas contraints à reproduire exactement ces fréquences.
AC-027	Générer cinq fiches puis reroll une fiche.	Cinq constructions individuelles ; seule la fiche visée est régénérée ; son type, niveau et orientation restent identiques.
AC-028	Valider une génération sans sauvegarde explicite.	Ajout de la sélection au camp préchoisi sur Table ; aucun nouveau profil dans le Bestiaire.
AC-029	Sauvegarder explicitement une seule fiche générée.	Seul le profil choisi est conservé dans le Bestiaire ; aucune sauvegarde automatique du reste du lot.

17.3 Bestiaire, rencontres et Table
ID	Situation	Résultat attendu
AC-030	Filtre de Bestiaire N6 sur un évolutif disposant deN1–N6.	Aperçu et ajout directs deN6 ; possibilité de choisir une autre version disponible ; N7 non proposé.
AC-031	Rencontre référençant N6 d’un profil, puis modification de sa construction N6.	Prochain chargement utilisant la nouvelle construction ; instances précédemment chargées inchangées.
AC-032	Ajouter cinq exemplaires d’un profil puis blesser un seul.	Cinq instances indépendantes ; les quatre autres, le profil et la rencontre source restent inchangés.
AC-033	Armure de base2 et AEGIS équipé.	Armure théorique4 ; aucun cumul temporaire d’AEGIS incrémenté automatiquement.
AC-034	Instance à10 PV, Armure2, saisie de8 dégâts bruts.	PV actuels4. Une modification directe ultérieure des PV ne réapplique pas l’Armure.
AC-035	Instance à6 PV, Armure2, saisie de8 dégâts bruts, puis soin vers une valeur positive.	PV0 : fiche grisée conservée ; PV>0 : affichage normal rétabli ; pas de survie automatique.
AC-036	Drag & Drop d’un Ennemi vers Alliés, puis réorganisation et reconnexion.	Camp et ordre conservés ; caractéristiques, PV, équipements et capacités inchangés par le déplacement.
AC-037	Retirer une instance individuellement.	Retrait sans confirmation ; historique, Bestiaire et rencontre préservés.
AC-038	Nettoyer la Table en annulant, puis en confirmant.	Annulation préserve la Table ; confirmation retire les instances seulement.
AC-039	Modifier une instance puis demander une mise à jour de sa source.	L’édition locale n’a pas changé le Bestiaire ; l’action distincte d’écrasement demande confirmation.

17.4 Dice Roller et historique
ID	Situation	Résultat attendu
AC-040	PER16, malus−2, dé7, coefficient4.	Seuil14 et Bonus Delta+1 ; pas+2.
AC-041	Puissance5 et Bonus Delta3, critique standard puis avec Annihilation.	Dégâts13 puis18 ; Delta jamais multiplié.
AC-042	Seuil effectif2, plage critique1–3, dé retenu3.	Réussite critique prioritaire malgré le dépassement du seuil ; Bonus Delta0.
AC-043	Dé retenu20 malgré un seuil modifié supérieur à20.	Échec critique.
AC-044	ADV2 et DES1.	SoldeADV1 ; deux d20, meilleur retenu ; les deux valeurs restent visibles.
AC-045	ADV1 et DES1.	Solde normal, un seul d20.
AC-046	Stabilisateur sur coefficient4 ; Canon renforcé sur Puissance5 ; Assistance ; Percuteur.	Contributions respectives : coefficient3, Puissance6, Visée+2 et Critique+1, chacune dans son cas d’équipement.
AC-047	Fusil IEM contre cible déclarée robot et Marquée.	Puissance de base4 augmentée de2+2, soit8 avant autre effet ; aucune gestion automatique de zone/état.
AC-048	ANCHOR équipé, test deVOL avec DES1 fourni par le MJ.	ADV1 automatique et DES1 s’annulent ; l’application n’exécute pas l’Overdrive d’ANCHOR.
AC-049	Fulgurance produit une frappe de5 dégâts.	Un jet et un calcul ; Concentré applique deux frappes de5 à la même cible et Réparti5 par cible. En Concentré, l’Armure est appliquée séparément à chaque frappe.
AC-050	Jet effectué, puis Puissance/nom de l’arme et stats du personnage modifiés.	Ancienne entrée conservant nom/contexte, Puissance, seuil, dés, verdict, Delta et dégâts de l’époque.
AC-051	Retirer l’instance puis nettoyer la Table et se reconnecter.	Les jets restent lisibles dans le journal du compte.
AC-052	Vider l’historique en annulant, puis en confirmant.	Annulation sans perte ; confirmation efface les jets sans toucher à la Table ni aux profils.

17.5 Accès et intégrité
ID	Situation	Résultat attendu
AC-053	Accès sans authentification à des données privées.	Accès refusé ; connexion nécessaire.
AC-054	CompteB connaît l’identifiant d’un profil, jet ou élément personnalisé deA.	Aucune consultation ou modification autorisée sur les données deA.
AC-055	Tenter de référencer une version deB dans une rencontre deA.	Relation refusée ; aucune référence privée entre comptes.
AC-056	Nettoyer la Table ou l’historique deA.	Aucun effet sur ceux deB.
AC-057	Déconnexion puis reconnexion sur un autre PC.	Accès authentifié nécessaire à nouveau ; données persistantes du compte retrouvées.
AC-058	Supprimer un profil/version utilisé par des rencontres.	Suppression refusée avec identification des usages concernés.
AC-059	Supprimer un équipement encore affecté à une fiche.	Suppression refusée ; un ancien jet figé seul ne constitue pas cette référence vivante.
AC-060	Déplacer un dossier sous l’un de ses descendants, dans l’autre arbre ou vers un autre propriétaire.	Opération incohérente refusée ; contenu et relations préservés.

18. Points de recette à préciser avant implémentation concernée
Les points suivants sont les seuls compléments de recette encore ouverts. RC-02 et RC-03 ont été résolus avant la PR2 et leurs décisions sont désormais intégrées dans les sections 5, 6 et 13 ainsi que dans AC-042 et AC-049. Le volet « effets structurés / contrôles contextuels » de RC-10 est également verrouillé pour la PR2 : seules les valeurs numériques comprises par GMTK et des conditions simples qualifiant le jet courant sont automatisées ; elles ne créent aucun suivi d’état.
ID	Point réellement indéterminé	Limite de la décision actuelle
RC-01	Initialisation des PV actuels d’une nouvelle instance et traitement après variation de PVmax, notamment via catalogue ou override.	PV actuels stockés, PVmax calculés/forcés et soins plafonnés sont acquis ; la règle de transition reste à fixer.
RC-04	Chargement d’une rencontre sur Table occupée et éventuelle utilisation de l’ordre préparatoire.	Références aux versions et nouvelles instances indépendantes sont acquises ; ajout/remplacement n’est pas choisi silencieusement.
RC-05	Champs repris lors d’une remontée volontaire au Bestiaire, cible en cas de niveau local modifié et rattachement après sauvegarde d’une fiche générée.	Sauvegarde explicite et confirmation d’écrasement sont acquises ; aucune remontée automatique.
RC-06	Édition d’une ancienne version évolutive ou de son niveau ; effet sur validation des suivantes ; devenir de choix/équipements après baisse de seuil.	Séquence, disponibilité des niveaux validés, overrides persistantes et absence de rétropropagation sont acquises ; aucune suppression silencieuse décidée.
RC-07	Suppression d’un dossier non vide ; modalités de masquage des natifs ; inclusion des permissions/raretés dans « Remettre par défaut ».	Intégrité des références, restauration des valeurs natives et confirmations prévues restent obligatoires.
RC-08	Détails non chiffrés du pipeline : point de passage de priorité Élite, choix des familles dans certains slots additionnels, catalogue entièrement sans arme admissible et éléments personnalisés ouvrant d’autres possibilités de génération.	Budget légal, repli d’arme sans régénération du personnage, arme minimale, priorités et capacités sont obligatoires ; aucune stratégie de secours interdite n’est inventée.
RC-09	Réglage initial des autorisations/raretés des éléments natifs et pondérations non fournies ; répartition Mob et tirages de niveau.	Les paramètres restent à définir/calibrer pendant l’implémentation. Les distributions d’Armure validées et les invariants de composition ne changent pas.
RC-10	Présentation d’une dominante ex æquo hors tirage, filtres supplémentaires des rencontres et cas des Perks personnalisés sélectionnables.	Le périmètre des effets structurés et contrôles contextuels nécessaires aux calculs est désormais fixé pour la PR2 ; les autres volets restent à préciser dans les PR qui les exposent.

Les anciennes ambiguïtés de propriétés devenues manuelles — Overdrive, drone, survie, états et propriétés spéciales non calculées — ne deviennent pas des blocages à résoudre par l’application. Leur description reste fidèle à la source, sans ajout mécanique.
19. Contraintes de déploiement
L’application doit rester déployable sur un hébergement web standard et être accessible depuis plusieurs PC au moyen d’un navigateur, avec authentification obligatoire et conservation des données privées.
Le choix de l’hébergement et du fournisseur est volontairement différé à la phase de déploiement. Les intentions du brouillon sont conservées : coût gratuit ou faible si possible, absence d’achat obligatoire de nom de domaine et possibilité d’utiliser l’URL fournie par l’hébergeur.
Python/Django ont été envisagés dans le brouillon ; ce CDC n’en déduit ni modèles, ni migrations, ni architecture, ni décision de fournisseur. Le stockage doit permettre la persistance et l’intégrité décrites, sans imposer ici sa réalisation technique.
Le CDC est suffisamment complet pour passer à la conception technique et à l’implémentation, sous réserve de préciser chaque point de recette ouvert avant d’implémenter le comportement concerné.


20. Réconciliation LdR V4 — décisions du 19 septembre 2026
Le référentiel V1 intègre les nouvelles armes et les variantes Ascend/Overcome, les accessoires et gadgets nécessaires à l’affichage/calcul, ainsi que les 18 implants actuels. Les propriétés tactiques non nécessaires au calcul restent descriptives.
Pour les armes à minimum FOR, l’éditeur manuel autorise l’équipement et applique −1 Visée par point manquant ; le Randomizer retire l’arme des candidats lorsque le minimum n’est pas satisfait.
RHODOS : +5 Résistance critique est structuré. Chaque fois qu’une attaque inflige des dégâts au porteur, l’attaquant subit 1 dégât ; ce renvoi, son Overdrive et le gain de Réaction INNOVATE restent manuels.
Les dégâts de poussée existent dans le LdR mais leur résolution géométrique reste hors automatisation V1.
