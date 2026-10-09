# Mes Scénarios — Cahier des charges opérationnel de phase 0

Version 1.0 — 9 octobre 2026. Statut : protocole proposé ; aucun prototype commencé.
Branche de référence : feature/scenario-editor.
Références : [architecture](SCENARIOS_ARCHITECTURE.md), [roadmap](SCENARIOS_ROADMAP.md), [décisions](SCENARIOS_DECISIONS.md).

## 1. Objectif et limites

Comparer Cytoscape.js + edgehandles et React Flow sur une expérience TMP identique. Le résultat doit permettre de choisir le moteur en P0-04.
Aucun modèle/route/base de données ni modification fonctionnelle TMP-GMTK. Aucune dépendance installée dans le projet pendant cette mission documentaire.
Lors de l'exécution future autorisée, prototypes dans un espace isolé du runtime, données fictives seulement. Ni compte utilisateur, ni secret, ni DATABASE_URL, ni appel aux services TMP.
Les prototypes sont des expériences remplaçables : ne pas les promouvoir directement en code de production.

## 2. Lots et livrables

- P0-01 : jeu commun, contrat des actions, versions/machine, mesures de référence.
- P0-02 : prototype Cytoscape et résultats bruts.
- P0-03 : prototype React Flow et résultats bruts.
- P0-04 : tests MJ, grille finale, décision consignée D-20.

Livrables futurs : README d'exécution, lockfiles/versions exactes et licences, fixtures communes, démos, feuille des mesures, liste du code spécifique, rapport de choix.
Le rapport contient résultat par critère, captures aux mêmes échelles, enregistrements des parcours si consentement, défauts, contournements, temps passé et limites de mesure.

## 3. Jeu de données commun

Un générateur déterministe avec graine fixe et un JSON indépendant des bibliothèques :
- scenes : id fictif, titre, narrative_order, position x/y, compte et types de rubriques ;
- transitions : id de rubrique fictif, source, target, label ;
- aucune donnée réelle de MJ.

| Jeu | Scènes | Transitions | Usage |
|---|---:|---:|---|
| S | 50 | 100 | préparation habituelle |
| M | 200 | 400 | scénario soutenu |
| L | 500 | 1 000 | limite du test, sans promesse produit automatique |

Inclure pour chaque jeu : au moins un cycle de longueur 3, une boucle sur soi, une paire de transitions parallèles, des convergences, des scènes isolées et un embranchement à 5 sorties.
Titres : courts, longs (jusqu'à limite de contrat proposée), accents et mots similaires.
Rubriques : 0 à 6 types représentés ; certaines répétées ; icônes avec noms accessibles.
Ordre narratif volontairement indépendant des coordonnées. Coordonnées préétablies ; aucun layout automatique au chargement.
Valider exactement les nombres, IDs uniques, références internes et coordonnées finies.

Le benchmark n'utilise pas 500 contenus complets de scène : même résumé compact pour chaque moteur. Le panneau fictif ne charge qu'une scène à la fois.
Aucun chargement d'image distante qui fausserait les mesures. Les mêmes SVG d'icônes sont utilisés si techniquement possible ; sinon documenter la différence.

## 4. Contrat visuel

Carte de référence : largeur logique proposée 220 px, titre sur deux lignes avec accès au titre complet, numéro narratif, six emplacements d'icônes, bouton Ouvrir et zone dédiée de connexion.
Même palette TMP papier/encre/rouge, même taille et polices locales/replis ; états sélectionné, survol, focus et erreur.
Contrôles compréhensibles sans couleur seule. Le drag ne doit pas commencer sur un bouton ni sélectionner le texte involontairement.
Libellés des transitions inspectables. Connexions parallèles et boucles identifiables, même si leur tracé diffère entre moteurs.

Écarts de rendu permis s'ils sont documentés et n'améliorent pas artificiellement un prototype. Ne pas disqualifier un moteur parce qu'il n'utilise pas exactement le même pixel de courbe.

## 5. Interactions identiques

1. Créer une scène fictive avec titre/ordre.
2. Déplacer librement une carte ; déplacer par clavier ou commande alternative.
3. Tirer une connexion d'une source vers une destination ; annuler le geste.
4. Créer la même connexion par sélection source/cible sans glisser-déposer.
5. Modifier libellé/destination, supprimer une connexion.
6. Montrer un cycle, une convergence et une connexion parallèle.
7. Pan, zoom +/-/réinitialiser et cadrer la scène sélectionnée.
8. Ouvrir une scène dans le panneau fictif, fermer et restaurer le focus.
9. Changer l'ordre narratif sans bouger les positions/liens.
10. Sérialiser le document commun ; recharger et comparer positions, IDs et connexions.

La sérialisation est une simulation locale (fichier ou mémoire). Ce n'est ni le format .tmpcamp final ni une sauvegarde serveur.
Seuls les mêmes gestes doivent être comparés : aucune connexion par code dans un prototype si l'autre exige une interaction.

## 6. Accessibilité

Tous les parcours essentiels réalisables au clavier, y compris connexion, suppression et accès aux icônes.
Tab ne doit pas imposer la traversée de centaines de contrôles pour sortir du tableau : définir stratégie de navigation, liste parallèle et sélection.
Focus visible, instructions françaises, boutons nommés, état sélection annoncé, zoom accessible, fermeture Escape et retour du focus.
Tester lecteur d'écran disponible sur la machine cible, en plus des tests automatisés.
Petits écrans : démontrer une liste et le panneau/lecteur fictif ; pas d'obligation de drag tactile pour accomplir une tâche.

Les fonctions natives d'accessibilité de React Flow ne prouvent pas l'accessibilité des contrôles personnalisés. Un canvas Cytoscape ne remplace pas une représentation DOM équivalente.

## 7. Mesures et conditions

Machine de référence documentée : OS, CPU, RAM, résolution, navigateur/version, échelle écran ; versions exactes des dépendances et options.
Deux moteurs sur même machine/navigateur, build représentatif de production pour performance. Pas de dev server React comparé à une distribution optimisée Cytoscape.
Même budget de réalisation proposé : 2 jours par prototype, extension seulement si un critère ne peut être testé, motif et temps publiés. Ce budget est une limite expérimentale à confirmer, pas une estimation de développement produit.

Cinq répétitions par jeu/moteur ; mesurer froid et chaud séparément. Réinitialiser fixture/viewport. Alterner l'ordre des moteurs pour limiter apprentissage.
Démarrer le chronomètre quand les données communes sont disponibles ; mesurer séparément temps de téléchargement/build et temps de rendu.
Rapporter médiane, valeurs extrêmes et intervalles entre frames pendant un parcours de drag/pan fixe. Pas de comparaison basée sur un FPS instantané.
Mémoire après chargement puis 20 cycles ouvrir/fermer si instrumentation disponible ; sinon indiquer indisponible, jamais zéro.
Relever taille compressée du bundle total chargé, nombre de dépendances directes, code spécifique écrit et temps d'intégration estimé. Versions/licences vérifiées au moment du prototype.

## 8. Critères mesurables

Seuils proposés : ratifier en P0-01 avant mesure et ne pas les modifier après lecture des résultats.

| Critère | Acceptation / mesure |
|---|---|
| Intégrité | 100 % des positions et connexions conservées après sérialisation/rechargement |
| Fonctionnalités | 100 % des 10 interactions démontrées ou manque déclaré |
| Clavier | toutes tâches essentielles réalisables ; aucune dépendance exclusive au drag |
| Chargement M | interactif en au plus 2 s sur machine de référence |
| Fluidité M | 95 % des intervalles de frames au plus 33 ms pendant parcours fixe |
| Charge L | aucun blocage > 1 s ; fonctionnement et dégradation documentés |
| Essai MJ | au moins 90 % des tâches réussies sans assistance sur l'ensemble des essais |
| Focus | aucun piège ; retour au contrôle source après fermeture |
| Maintenance | versions, licences, build, code spécifique et estimation d'intégration documentés |

3 à 5 MJ réalisent les mêmes tâches : création, déplacement, embranchement, modification transition, ouverture/retour et ordre indépendant.
Instructions courtes identiques, ordre des moteurs alterné. Mesurer réussite, durée, erreurs et besoin d'assistance ; recueillir préférence qualitative séparément.
Un échantillon si petit ne constitue pas une preuve statistique généralisable : rapporter les observations.

## 9. Grille de décision

| Dimension | Poids | Éléments |
|---|---:|---|
| Usage MJ | 25 % | réussite, temps, erreurs, déplacement/connexion/zoom |
| Cartes et DA | 20 % | lisibilité, icônes, contrôles, flexibilité réelle |
| Accessibilité | 20 % | clavier, focus, représentation alternative, lecteur d'écran |
| Intégration/maintenance | 20 % | Django, build, dépendances/licences, code spécifique |
| Performances | 15 % | mesures S/M/L, bundle, mémoire si disponible |

Noter chaque dimension de 0 à 5 avec preuves. Score pondéré = somme(poids * note / 5), sur 100.
Pour performances : note 3 = seuils atteints ; notes supérieures justifiées par marge mesurée sans sacrifier fonctions.
Pour maintenance : note 3 = build reproductible et intégration documentée ; réduire si contournements ou dépendances non maîtrisées.
Ne pas donner un score de performance meilleur au prototype auquel manquent des boutons.

Éliminatoires : perte de données, tâche essentielle sans alternative accessible, licence incompatible, impossibilité d'intégration reproductible.
Si scores proches (écart < 5 points), privilégier réussite MJ et coût de maintenance démontré ; expliciter arbitrage.
Si les deux échouent : aucun choix automatique ; corriger le point bloquant dans une nouvelle itération bornée, conserver les résultats initiaux.

## 10. Conclusion attendue et passage à Django

Rapport P0-04 : moteur retenu, version, données brutes, score, raisons, limites, stratégie assets/build et code à réécrire.
Mettre D-20 à validé sans réécrire les autres décisions produit. Les enseignements ne changent les modèles que si une contradiction technique bloquante est prouvée.
Ne pas intégrer le prototype avant P3-01. Phase 3 répète les mesures avec backend et persistance ; les résultats P0 ne garantissent pas les performances du produit connecté.

Sources techniques de référence, à revérifier lors de P0 :
- [Cytoscape.js](https://js.cytoscape.org/)
- [edgehandles](https://github.com/cytoscape/cytoscape.js-edgehandles)
- [React Flow : cartes personnalisées](https://reactflow.dev/learn/customization/custom-nodes)
- [React Flow : accessibilité](https://reactflow.dev/learn/advanced-use/accessibility)
