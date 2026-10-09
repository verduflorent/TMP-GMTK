# Mes Scénarios — Journal des décisions

Version 1.0 — 9 octobre 2026. Branche : feature/scenario-editor.
Le statut VALIDÉ concerne les principes expressément acceptés par le MJ. Les détails PROVISOIRES proposés par la conception doivent être arrêtés dans les lots indiqués.
Aucun prototype, migration ou développement n'est accompli par cette validation documentaire.

Références : [architecture](SCENARIOS_ARCHITECTURE.md), [roadmap](SCENARIOS_ROADMAP.md), [phase 0](SCENARIOS_PHASE0.md).

## 1. Procédure

Chaque décision possède un ID stable, un statut, une motivation, une conséquence et un lot de clôture. Conserver l'historique en cas de remplacement ; ne pas supprimer les motifs.
Statuts : VALIDÉ / PROVISOIRE / REPORTÉ / REMPLACÉ.
Une décision produit ne peut être changée par une préférence de bibliothèque. Une contradiction bloquante doit être exposée avec preuve avant évolution.
Au démarrage d'un lot, vérifier ses décisions préalables. La validation du présent ensemble de documents est préalable à toute implémentation.

## 2. Principes validés

| ID | Décision | Motivation / conséquence |
|---|---|---|
| D-01 | Application Django indépendante scenarios | Responsabilités séparées ; pas d'extension massive de toolkit/views.py |
| D-02 | Comptes et dossiers existants | Cohérence et réutilisation ; dossiers partagés, suppression déclassant aussi les ressources existantes |
| D-03 | Scénarios, scènes et rubriques relationnels | IDs stables, mutations localisées, relations vérifiables |
| D-04 | Rubrique Transition = connexion canonique | Graphe et lecteur consomment la même donnée ; aucune copie de liens |
| D-05 | Ordre indépendant de disposition | Réorganiser n'altère ni positions ni transitions |
| D-06 | Cycles, embranchements et convergences | Pas de contrainte DAG |
| D-07 | Édition modulaire et lecteur MJ distinct | Lecture fluide sans commandes d'édition |
| D-08 | Revisions et conflits dès premières écritures | Pas d'écrasement silencieux ; tests dans chaque lot d'édition |
| D-09 | .tmpcamp = ZIP + JSON versionné | Format portable indépendant ORM ; contrôle du conteneur requis |
| D-10 | Export/import narratif et retrait explicite dans MVP | Trois actions distinctes ; aucun retrait automatique après export |
| D-11 | Illustrations HTTPS V1 | Métadonnées seulement en base ; pas de stockage durable sur Render |
| D-12 | Isolation stricte | Résolution owner de toutes ressources ; import appartient au destinataire |
| D-13 | Aucun changement moteur TMP | Intégrations de références uniquement, sans nouvelles règles |
| D-14 | Sept phases 0 à 6 dans ordre validé | Prototype tôt ; contrats fiables avant tableau connecté |
| D-15 | Choix du moteur après preuves | Cytoscape n'est pas acquis ; comparaison fonctionnellement égale |
| D-16 | Stockage objet et graphiques embarqués hors MVP | V1 narrative ne prétend pas être autonome pour les images |

Ces décisions proviennent de la demande de validation du MJ du 9 octobre 2026, pas d'un vote automatique du prototype.

## 3. Détails provisoires à clôturer

| ID | Détail recommandé | Clôture | Blocage |
|---|---|---|---|
| D-20 | Cytoscape.js + edgehandles OU îlot React Flow ; mesure/grille commune | P0-04 | intégration graphique ; pas une raison de coupler le format portable |
| D-21 | UUID locaux ; document_id portable distinct ; duplication nouveau document_id ; import conserve provenance | P1-01 | avant P1-03 |
| D-22 | Transition dans SceneBlock.target_scene, sans table séparée ; boucles sur soi et transitions parallèles permises | P1-01 | avant P1-03 |
| D-23 | CASCADE scénarios/scènes/transitions ; SET_NULL dossiers/médias/Rencontres ; fallback des références | P1-01 | avant P1-03 |
| D-24 | Deux revisions Scenario, verrou transactionnel ; mutations structurelles contrôlent les deux | P1-01 | avant P1-03 |
| D-25 | Idempotence liée au compte/opération ; conservation/expiration et réponse à replay après suppression | P1-01 | avant premières écritures |
| D-26 | Texte brut échappé, JSON limité/versionné, six types ; UI quatre types en phase 2 puis deux en phase 5 | P1-01 | avant P1-03 |
| D-27 | ZIP deux fichiers UTF-8, schémas 1.0 et capacités requises ; pas de version liée aux migrations | P1-02 | avant P1-03 pour invariants ; codec P4-01 |
| D-28 | Limites 10 Mio reçus / 20 Mio décompressés / 500 scènes / 5000 rubriques / 2000 transitions | P1-02 | validation import P4-03 |
| D-29 | Import nouvelle copie, nouveaux UUID ; provenance signale doublon ; aucun remplacement/merge | P1-01/P1-02 | modèle provenance avant P1-03 |
| D-30 | Export des Rencontres par descripteurs non résolus ; association explicite chez destinataire | P1-02 | contrat avant P1-03 |
| D-31 | Retrait guidé exige fichier vérifié lié aux revisions ; suppression ordinaire distincte avec avertissement | P1-01 puis P4-06 | règle de commande avant P1-03 ; UX phase 4 |
| D-32 | Budget machine et seuils graphiques proposés dans phase 0 | P0-01, constat P0-04 | décision moteur |
| D-33 | Propriété média, partage privé, réutilisation à import, revision et cohérence de ses métadonnées | invariants P1-01, détail P5-01 | invariants de references avant P1-03 ; média avant sa migration |
| D-34 | Budget de requêtes tableau mesuré, pas de contenus complets en graphe | P3-01/P3-04 | acceptation tableau |
| D-35 | Préproduction PostgreSQL distincte, migration additive, activation et retour arrière | P6-03 | livraison ; PostgreSQL concurrence dès P1-04 |
| D-36 | Compatibilité versions publiées par convertisseurs testés ; refus majeure/capacité inconnue | P1-02/P4-01 | import |

Les seuils sont des propositions de critères, pas des mesures obtenues. Les modèles sont envisagés, pas présents dans le dépôt.
En cas de changement des détails de format après publication de 1.0, appliquer sa politique de version et conserver les fixtures antérieures.

## 4. Décisions reportées hors MVP

| ID | Sujet | Condition de reprise |
|---|---|---|
| D-40 | Fournisseur objet et quotas | besoin d'upload ; vérifier conditions réelles du compte et accès privé |
| D-41 | Fichiers graphiques dans .tmpcamp | stockage durable à import, validation raster et staging/compensation définis |
| D-42 | Snapshots TMP autonomes | exporteur métier traitant équipements/dépendances, respect LdR/CdC |
| D-43 | Chargement Rencontre depuis lecteur | comportement ajout/remplacement Table décidé et testé séparément |
| D-44 | Partage public et campagnes multi-scénarios | permissions dédiées et extension portable versionnée |
| D-45 | Texte enrichi | format limité et nettoyage serveur avant ouverture |
| D-46 | Merge/réimport avec remplacement, collaboration temps réel | besoin prouvé ; aucun effet automatique dans V1 |
| D-47 | Historique complet, corbeille et récupération automatique | stockage/coût/durée définis ; ne pas prétendre libérer la base par masquage |

Ces sujets ne bloquent pas la V1. Ne pas installer une infrastructure ou créer des modèles génériques pour les anticiper sans lot autorisé.

## 5. Traçabilité initiale

- Audit et révision : principes expliqués au MJ, puis validés dans sa demande de roadmap.
- Vérification documentaire du 9 octobre : branche feature/scenario-editor, commit ef668279b9975367f86ec4b08ad20697b0d16c88.
- Référence historique : 195 tests ; réexécution actuelle : 195 passent en settings_test/SQLite. Aucun benchmark ni test PostgreSQL exécuté pour ces documents.
- Tous lots NON COMMENCÉS ; aucun moteur retenu ni fournisseur objet choisi.
- Première action après validation documentaire : P0-01.

## 6. Registre des évolutions à tenir

Pour chaque nouvelle entrée : date, auteur/décideur, ID, ancien/nouveau statut, preuves, lots affectés et conséquence sur compatibilité.
Après P0-04, renseigner moteur/version et rapport ; après P1-01/P1-02, fermer tous détails pré-migration ; à P6-04, publier limites MVP et conserver les décisions reportées.
