# Mes Scénarios — Roadmap officielle

Version 1.0 — 9 octobre 2026. Branche exclusive : feature/scenario-editor.
Statut : plan de référence à valider ; tous les lots sont NON COMMENCÉS. Aucune implémentation autorisée avant validation des documents.

Références : [architecture](SCENARIOS_ARCHITECTURE.md), [décisions](SCENARIOS_DECISIONS.md), [phase 0](SCENARIOS_PHASE0.md).
Les sept phases validées sont conservées. Toute extension de périmètre doit être consignée ; aucune modification du moteur de règles.

## Mode d'emploi et définition de terminé

Confier un lot par son ID stable ; lire son périmètre, ses dépendances et les contrats associés avant d'écrire. Les lots peuvent comporter quelques fichiers cohérents, sans micro-PR artificielles. Le graphe de dépendances est l'autorité d'ordonnancement.

Un lot est terminé lorsque chaque critère est démontré, les tests pertinents passent et les preuves (commande, résultat, version, capture ou rapport) sont consignées. Mettre à jour son état dans cette roadmap : NON COMMENCÉ / EN COURS / À VALIDER / ACCEPTÉ. Un lot à valider n'est pas une dépendance acquise. Aucun statut n'est prérempli comme accepté.

Socle de tests commun : isolation à deux utilisateurs pour chaque endpoint ; CSRF/méthodes sur écritures ; persistance après rechargement et conflit pour chaque mutation ; zéro écriture partielle sur erreur. Ajouter PostgreSQL dès le service de revisions, pas uniquement en phase 6. Tests frontend sous l'outil retenu et parcours navigateur réel pour gestes/queue/focus. Les dépendances de développement requises seront ajoutées uniquement dans un lot d'implémentation approuvé.

Référence historique 195 tests ; vérification locale du 9 octobre 2026 : 195 tests passent sur le commit ef668279b9975367f86ec4b08ad20697b0d16c88 avec settings_test et SQLite. Redécouvrir le nombre réel au début du chantier et des lots ; ne pas figer le total. Le plan ne prétend pas avoir validé PostgreSQL ou un prototype.

## Synthèse et jalons

| Phase | Lots | Critère de sortie |
|---|---:|---|
| 0 — Prototype graphique isolé | 4 | Deux prototypes comparables évalués ; décision moteur signée avec données, limites et alternative clavier complète. |
| 1 — Fondations Django | 5 | Contrats figés avant migrations ; modèles isolés, bibliothèque privée et services de revision opérationnels ; aucune écriture sans contrôle. |
| 2 — Éditeur narratif et lecteur MJ | 5 | Scénario ramifié éditable/jouable ; persistance et conflits validés pour toutes mutations ; duplication indépendante. |
| 3 — Tableau narratif connecté | 4 | Tableau connecté fiable ; déplacements et flèches restaurés après rechargement ; seuils graphiques mesurés. |
| 4 — Export/import .tmpcamp | 6 | Archive narrative exportable, vérifiable, réimportable ; remappage et retrait sécurisé ; round-trip de référence réussi. |
| 5 — Illustrations et intégrations TMP | 4 | Six rubriques utilisables ; médias HTTPS réutilisables et références privées ; round-trip des dépendances explicitement non autonomes. |
| 6 — Stabilisation et livraison | 4 | Recette complète, sécurité/accessibilité/non-régression et PostgreSQL validés ; livraison prête, déploiement non implicite. |

Total : 32 lots. Premier lot : **P0-01 — Jeu de données et protocole commun**.

Fin phase 2 : éditeur/lecteur interne utilisable. Fin phase 3 : essai MJ représentatif du tableau. **MVP livrable à la fin de phase 6**, avec six rubriques, tableau, archives narratives et retrait explicite. Le déploiement de production nécessite une autorisation distincte.

Les schémas de médias/références sont anticipés en phase 1/4 ; l'UI et les relations actives sont finalisées en phase 5. Il n'est donc pas nécessaire d'attendre la phase 5 pour valider les archives, et cette phase répète le round-trip complet.

## Phase 0 — Prototype graphique isolé

**Sortie de phase :** Deux prototypes comparables évalués ; décision moteur signée avec données, limites et alternative clavier complète.

### P0-01 — Jeu de données et protocole commun

- **État :** NON COMMENCÉ.
- **Objectif :** Préparer une comparaison reproductible sans application Django.
- **Comportements :** Fixtures déterministes 50/100, 200/400, 500/1000 scènes/connexions ; contrats de carte et gestes ; référence de machine et versions.
- **Fichiers/modules envisagés :** Futur répertoire isolé de prototypes hors runtime applicatif ; docs/SCENARIOS_PHASE0.md ; rapport de référence.
- **Dépendances :** aucune ; validation documentaire préalable.
- **Risques :** Deux démos non équivalentes ou mesures non reproductibles.
- **Tests :** Valider nombre d'entités, références, cycles, boucles, positions et sérialisation commune ; relever les tests Django réels.
- **Acceptation :** Même fichier et même cahier de tâches utilisables par les deux prototypes ; baseline datée ; aucune route/DB de TMP-GMTK.
- **Hors périmètre :** Développement des deux prototypes, installation dans TMP-GMTK, migrations.
- **Complexité relative :** Faible.

### P0-02 — Prototype Cytoscape.js

- **État :** NON COMMENCÉ.
- **Objectif :** Mesurer l'expérience Cytoscape représentative.
- **Comportements :** Cartes compactes, icônes, ouverture, déplacement, flèches via edgehandles, modification/suppression, zoom/pan ; commandes clavier équivalentes ; sauvegarde/rechargement local fictif.
- **Fichiers/modules envisagés :** Prototype isolé Cytoscape et adaptateur du jeu commun ; fiche de mesures.
- **Dépendances :** P0-01.
- **Risques :** Contrôles DOM superposés coûteux, accessibilité artificiellement omise.
- **Tests :** Tous parcours P0 ; export/rechargement des positions et connexions ; 5 mesures froid/chaud.
- **Acceptation :** Fonctions communes démontrées ou lacunes documentées ; aucune donnée perdue ; coût du code spécifique relevé.
- **Hors périmètre :** Backend, persistance Neon, édition de texte complète, intégration au dépôt.
- **Complexité relative :** Moyenne.

### P0-03 — Prototype React Flow

- **État :** NON COMMENCÉ.
- **Objectif :** Mesurer l'expérience React Flow à périmètre égal.
- **Comportements :** Même cartes/icônes/actions et mêmes connexions ; panneau fictif ; clavier ; sérialisation du contrat commun ; build local reproductible.
- **Fichiers/modules envisagés :** Prototype isolé React Flow ; composants de cartes et adaptateur ; fiche de mesures.
- **Dépendances :** P0-01.
- **Risques :** Différence de richesse par rapport à Cytoscape ; rendu et état React coûteux.
- **Tests :** Même protocole que P0-02 ; focus des boutons/poignées ; connexion sans drag ; rechargement local.
- **Acceptation :** Parité fonctionnelle ou écarts explicités ; dépendances/build répertoriés ; mesures reproductibles.
- **Hors périmètre :** SPA globale, authentification et modification des dépendances TMP-GMTK.
- **Complexité relative :** Moyenne.

### P0-04 — Décision graphique argumentée

- **État :** NON COMMENCÉ.
- **Objectif :** Choisir un moteur sur preuves.
- **Comportements :** Essais avec MJ, mesures, scores pondérés et critères éliminatoires ; consigner version et stratégie d'intégration.
- **Fichiers/modules envisagés :** docs/SCENARIOS_PHASE0.md ; SCENARIOS_DECISIONS.md ; rapport comparatif.
- **Dépendances :** P0-02, P0-03.
- **Risques :** Choix au seul FPS ou à l'apparence d'une capture.
- **Tests :** Contrôler comparabilité, tâches clavier, taux réussite, résultats 200/500 et versions.
- **Acceptation :** Un moteur retenu ; motifs et limites tracés ; si les deux échouent, bloquer le choix avec correction ciblée à tester.
- **Hors périmètre :** Nouvelle architecture applicative ou intégration directe du prototype.
- **Complexité relative :** Faible.

## Phase 1 — Fondations Django

**Sortie de phase :** Contrats figés avant migrations ; modèles isolés, bibliothèque privée et services de revision opérationnels ; aucune écriture sans contrôle.

### P1-01 — Contrat de données avant migrations

- **État :** NON COMMENCÉ.
- **Objectif :** Figer les invariants relationnels et d'écriture.
- **Comportements :** Identités locales/portables, transitions canoniques, ordre, cycles/boucles, cascades, propriété, conflits, idempotence et suppression des dépendances.
- **Fichiers/modules envisagés :** docs/SCENARIOS_ARCHITECTURE.md ; SCENARIOS_DECISIONS.md ; tableau des commandes/revisions.
- **Dépendances :** P0-04.
- **Risques :** Modèle laissant des liens orphelins ; faux sentiment de sécurité par clean().
- **Tests :** Revue de cas : suppression destination, référence étrangère, double clic, conflit texte/disposition, duplication.
- **Acceptation :** Contrat sans ambiguïté ; toutes décisions pré-migration résolues ; aucun code/migration dans ce lot.
- **Hors périmètre :** Modèles exécutables, endpoints et fournisseur objet.
- **Complexité relative :** Faible.

### P1-02 — Contrat portable et fixtures

- **État :** NON COMMENCÉ.
- **Objectif :** Figer .tmpcamp 1.0 indépendamment de l'ORM.
- **Comportements :** Structure ZIP/JSON, schémas six types, versions/capacités, IDs internes, limites et politique références non résolues.
- **Fichiers/modules envisagés :** docs/SCENARIOS_ARCHITECTURE.md ; futurs scenarios/archive/schemas/ et tests/fixtures/archives/.
- **Dépendances :** P1-01.
- **Risques :** Archive attachée au schéma ORM ou perdant des types phase 5.
- **Tests :** Fixtures valides/invalides, cycle/convergence, URL externe, Rencontre non résolue et version inconnue.
- **Acceptation :** Schéma et fixture complète approuvés ; SHA/tailles et limites définis ; pas d'ID source utilisable comme permission.
- **Hors périmètre :** Génération ZIP, upload, import ORM ; validation des fichiers binaires.
- **Complexité relative :** Moyenne.

### P1-03 — Application et modèles relationnels

- **État :** NON COMMENCÉ.
- **Objectif :** Installer le socle isolé.
- **Comportements :** Scenario/Scene/SceneBlock, namespace, migrations additives, index et contraintes simples ; owner via utilisateur existant ; dossier partagé.
- **Fichiers/modules envisagés :** scenarios/{apps,models,urls}.py ; config/settings.py et urls.py ; migrations scenarios ; tests/models/.
- **Dépendances :** P1-02.
- **Risques :** Contrainte transversale impossible en SQL simple, cascade imprévue.
- **Tests :** Modèles, contraintes, migrations sur base vide et base existante de test ; check et drift ; tests toolkit/rules/catalogue.
- **Acceptation :** Application charge ; zéro changement des tables métier TMP hors nouvelles FK de scenarios ; aucune UI permettant des écritures prématurées.
- **Hors périmètre :** Médiathèque active, graphe, refactor toolkit ou règles.
- **Complexité relative :** Moyenne.

### P1-04 — Services de permissions et revisions

- **État :** NON COMMENCÉ.
- **Objectif :** Sécuriser toute future mutation.
- **Comportements :** Résolution owner, validation transversale, transactions/verrou Scenario, revisions, réponses 409, idempotence des créations ; CSRF et méthodes.
- **Fichiers/modules envisagés :** scenarios/services/{mutations,revisions}.py ; formulaires/schémas de commandes ; tests/services/.
- **Dépendances :** P1-03.
- **Risques :** Écriture hors service, course entre deux requêtes, replay créant un doublon.
- **Tests :** Deux utilisateurs ; concurrence PostgreSQL ; revision obsolète ; commande invalide sans effet ; clé identique et clé avec payload différent.
- **Acceptation :** Toutes commandes du contrat ont une règle de revision ; aucune mutation partielle ; interfaces utilisables par HTML et JSON.
- **Hors périmètre :** Éditeur, autosave avancée, merge, temps réel.
- **Complexité relative :** Élevée.

### P1-05 — Bibliothèque privée et dossiers

- **État :** NON COMMENCÉ.
- **Objectif :** Livrer création et organisation privées.
- **Comportements :** Liste paginée, créer/renommer/résumé, affecter/retirer dossier ; suppression ordinaire explicite ; retour sûr ; lien navigation.
- **Fichiers/modules envisagés :** scenarios/views/library.py, forms.py ; templates/scenarios/library.html ; base.html ; actions dossiers uniquement si correction ciblée requise.
- **Dépendances :** P1-04.
- **Risques :** Retour next non validé, suppression dossier affectant plusieurs modules, fuite d'objets.
- **Tests :** Authentification, GET sans écriture, CSRF enforce, dossier étranger, persistance après reload et conflit métadonnées ; navigation existante.
- **Acceptation :** Uniquement ressources du compte ; confirmation de suppression précise ; une revision ancienne ne remplace rien.
- **Hors périmètre :** Retrait guidé par archive, duplication et édition de scènes.
- **Complexité relative :** Moyenne.

## Phase 2 — Éditeur narratif et lecteur MJ

**Sortie de phase :** Scénario ramifié éditable/jouable ; persistance et conflits validés pour toutes mutations ; duplication indépendante.

### P2-01 — Scènes : création, ordre, suppression

- **État :** NON COMMENCÉ.
- **Objectif :** Gérer des scènes sans dépendre du graphe.
- **Comportements :** Créer/renommer, permutation narrative, supprimer avec aperçu liens affectés ; coordonnées initiales indépendantes et UUID stables.
- **Fichiers/modules envisagés :** scenarios/services/mutations.py ; views/editor.py ; templates/scenarios/editor.html ; tests/scenes/.
- **Dépendances :** P1-05.
- **Risques :** Ordre incomplet, suppression avec déplacement concurrent.
- **Tests :** Persistance/reload et conflits pour chaque mutation ; permutation invalide ; cascades liens ; interutilisateurs.
- **Acceptation :** Ordre modifié sans modifier x/y ; suppression nettoie liens entrants/sortants ; revisions structurelles cohérentes.
- **Hors périmètre :** Glisser-déposer graphique et auto-layout.
- **Complexité relative :** Moyenne.

### P2-02 — Rubriques textuelles modulaires

- **État :** NON COMMENCÉ.
- **Objectif :** Éditer Narration, Interprétation et Note MJ.
- **Comportements :** Ajouter, modifier, supprimer, réordonner ; plusieurs rubriques identiques ; texte brut/payload typé ; erreurs conservant la saisie.
- **Fichiers/modules envisagés :** scenarios/forms.py ; services/mutations.py ; fragments de rubriques ; tests/blocks/.
- **Dépendances :** P2-01.
- **Risques :** XSS, double sauvegarde, écrasement entre onglets.
- **Tests :** Chaque mutation : persistance/reload, conflit, payload invalide et propriétaire ; limites et texte malveillant.
- **Acceptation :** Aucune exécution HTML/JS utilisateur ; conflit visible sans perte de saisie locale ; ordre stable.
- **Hors périmètre :** Texte enrichi, Splash et Rencontre actifs.
- **Complexité relative :** Moyenne.

### P2-03 — Transitions canoniques

- **État :** NON COMMENCÉ.
- **Objectif :** Relier les scènes depuis les rubriques.
- **Comportements :** Créer/modifier libellé et destination/supprimer ; connexions multiples, cycles et boucles selon contrat ; picker privé.
- **Fichiers/modules envisagés :** SceneBlock.target_scene ; services/mutations.py ; formulaires transition ; tests/transitions/.
- **Dépendances :** P2-02.
- **Risques :** Deux sources de vérité ou cible d'un autre scénario.
- **Tests :** Persistance/conflit de chaque action ; parallèle/cycle/boucle ; scénario étranger même propriétaire ; suppression cible.
- **Acceptation :** Une connexion = une rubrique ; destination même scénario ; réorganisation ne change aucun lien.
- **Hors périmètre :** Tableau et conditions automatisées de transition.
- **Complexité relative :** Moyenne.

### P2-04 — Lecteur MJ distinct

- **État :** NON COMMENCÉ.
- **Objectif :** Jouer la narration sans commandes d'édition.
- **Comportements :** Scène lisible, dialogues, rubriques secondaires à la demande, transitions, retour liste/tableau quand disponible, focus.
- **Fichiers/modules envisagés :** scenarios/views/reader.py ; templates/scenarios/reader.html ; CSS/JS lecteur.
- **Dépendances :** P2-03.
- **Risques :** Commandes d'édition exposées ou focus perdu.
- **Tests :** Parcours lecteur clavier, isolation, cycles, contenu échappé, petits écrans ; lecture ne change pas revisions.
- **Acceptation :** Aucune commande d'édition ; transitions accessibles ; liens de retour explicites ; lecteur utile sans graphe.
- **Hors périmètre :** Vue joueur/public, présentation sur second écran.
- **Complexité relative :** Moyenne.

### P2-05 — Duplication indépendante

- **État :** NON COMMENCÉ.
- **Objectif :** Copier sans lien involontaire vers les scènes originales.
- **Comportements :** Nouveaux UUID/document_id, remappage rubriques/transitions, conservation références privées autorisées, copie atomique et idempotente.
- **Fichiers/modules envisagés :** scenarios/services/duplication.py ; action bibliothèque ; tests/duplication/.
- **Dépendances :** P2-04.
- **Risques :** Cible dans original, copie partielle, changement source pendant copie.
- **Tests :** Cycle/convergence, positions et rangs ; conflict revisions source ; rollback ; propriétaire ; reload copie.
- **Acceptation :** Aucune transition ne vise l'original ; source intacte ; copie complète ou zéro copie.
- **Hors périmètre :** Copie des ressources TMP elles-mêmes et partage.
- **Complexité relative :** Moyenne.

## Phase 3 — Tableau narratif connecté

**Sortie de phase :** Tableau connecté fiable ; déplacements et flèches restaurés après rechargement ; seuils graphiques mesurés.

### P3-01 — Adaptateur et lecture du tableau

- **État :** NON COMMENCÉ.
- **Objectif :** Afficher les données réelles dans le moteur retenu.
- **Comportements :** Endpoint résumé privé, cartes compactes, ordre/icônes, sélection et ouverture rapide ; pagination bibliothèque ; chargement scène ciblé.
- **Fichiers/modules envisagés :** views/board.py ; static/scenarios/js/graph_adapter.js ; template board ; build local si React retenu.
- **Dépendances :** P2-05.
- **Risques :** N+1, couplage format moteur/archives, CSS globale.
- **Tests :** Isolation, budget requêtes mesuré, graphe fidèle après rechargement, versions/build reproducible.
- **Acceptation :** Aucune persistance du JSON interne moteur ; résumés sans contenu complet ; autres pages inchangées.
- **Hors périmètre :** Déplacement écrit et connexions graphiques.
- **Complexité relative :** Moyenne.

### P3-02 — Déplacement et sauvegarde groupée

- **État :** NON COMMENCÉ.
- **Objectif :** Persister les positions sans perdre les gestes.
- **Comportements :** Drag/pan/zoom, commandes clavier, batch drag-end, file une requête en vol, état enregistré/échec/conflit et reprise.
- **Fichiers/modules envisagés :** services/revisions.py ; endpoints disposition ; board.js/save_queue.js ; tests/layout/.
- **Dépendances :** P3-01.
- **Risques :** Réponses hors ordre, coords NaN, réponse perdue, déplacement scène supprimée.
- **Tests :** Persistance/reload et concurrence PostgreSQL ; fin geste réseau coupé ; mouvements rapides ; aucune requête pointermove.
- **Acceptation :** Rechargement restitue les positions confirmées ; batch atomique ; conflit ne réécrit pas l'état récent ; queue bornée.
- **Hors périmètre :** Viewport partagé persistant, auto-layout et fusion automatique.
- **Complexité relative :** Élevée.

### P3-03 — Flèches interactives et synchronisation

- **État :** NON COMMENCÉ.
- **Objectif :** Créer/modifier les transitions depuis le tableau.
- **Comportements :** Geste connexion, libellé, cible, suppression ; création rubrique canonique ; synchronisation panneau/lecteur et rollback visuel.
- **Fichiers/modules envisagés :** Adaptateur moteur ; commandes transitions existantes ; board.js ; tests navigateur graph/.
- **Dépendances :** P3-02.
- **Risques :** Lien optimiste fantôme, doublon réseau, clavier incomplet.
- **Tests :** Toute action : reload/persistance/conflit ; double clic/replay ; cycle/convergence ; scène supprimée pendant geste ; alternative clavier.
- **Acceptation :** La même rubrique apparaît dans tableau/éditeur/lecteur ; refus serveur retire ou marque le lien optimiste.
- **Hors périmètre :** Règles conditionnelles, plugins supplémentaires non validés.
- **Complexité relative :** Élevée.

### P3-04 — Validation intégrée du tableau

- **État :** NON COMMENCÉ.
- **Objectif :** Vérifier le tableau connecté aux échelles prévues.
- **Comportements :** Benchmarks Django+frontend, navigation petit écran par liste, focus et carte sélectionnée ; correction ciblée des écarts.
- **Fichiers/modules envisagés :** tests navigateur/performance ; docs/SCENARIOS_PHASE0.md et rapport d'intégration.
- **Dépendances :** P3-03.
- **Risques :** Dégradation par rapport prototype ou promesse 500 non tenue.
- **Tests :** 50/200/500 ; réseau lent ; clavier complet ; lecture sur écran étroit ; tests UI des pages partagées.
- **Acceptation :** Seuils P0 atteints ou limites explicitement validées ; aucun blocage de sauvegarde/lecture ; aucune perte de données.
- **Hors périmètre :** Optimisation globale de TMP-GMTK et fonctions de tableau nouvelles.
- **Complexité relative :** Moyenne.

## Phase 4 — Export/import .tmpcamp

**Sortie de phase :** Archive narrative exportable, vérifiable, réimportable ; remappage et retrait sécurisé ; round-trip de référence réussi.

### P4-01 — Codec et compatibilité .tmpcamp

- **État :** NON COMMENCÉ.
- **Objectif :** Finaliser le format à partir de données réelles.
- **Comportements :** DTO portable et encode/decode purs ; manifeste/versions/capacités ; schémas six rubriques ; convertisseurs explicitement supportés.
- **Fichiers/modules envisagés :** scenarios/archive/{schema,codec}.py, schemas/, upgrades/ ; fixtures archives ; ARCHITECTURE.
- **Dépendances :** P3-04.
- **Risques :** Évolution du format depuis P1 non tracée, donnée inconnue ignorée.
- **Tests :** Sérialisation déterministe pour empreinte ; fixtures P1 ; round-trip DTO ; version inconnue et capacité non supportée.
- **Acceptation :** Contrat 1.0 complet ; zéro dépendance aux PK sources/graph engine ; politique compatibilité documentée.
- **Hors périmètre :** Conteneur export et import en base.
- **Complexité relative :** Moyenne.

### P4-02 — Export cohérent

- **État :** NON COMMENCÉ.
- **Objectif :** Produire une copie portable sans suppression.
- **Comportements :** Snapshot verrouillé/revisions ; ZIP deux fichiers ; SHA/tailles/CRC ; téléchargement privé et résumé dépendances.
- **Fichiers/modules envisagés :** services/archive_export.py ; views/archives.py ; action bibliothèque/éditeur.
- **Dépendances :** P4-01.
- **Risques :** Export mixant revisions, contenu non sauvegardé, données personnelles ajoutées.
- **Tests :** ZIP relu avec codec ; export concurrent mutation ; permission ; déterminisme sémantique ; aucune modification métier après export.
- **Acceptation :** Archive valide ; toutes données confirmées incluses ; compteur ressources et avertissements ; scénario conservé.
- **Hors périmètre :** Médias binaires, fetch externe, suppression après téléchargement.
- **Complexité relative :** Moyenne.

### P4-03 — Validation et vérification sans import

- **État :** NON COMMENCÉ.
- **Objectif :** Traiter toute archive comme non fiable.
- **Comportements :** Limites conteneur/décompression/JSON, empreintes, chemins et références ; aperçu ; vérification sans création ; preuve liée aux revisions.
- **Fichiers/modules envisagés :** archive/validation.py ; views/archives.py ; templates aperçu ; tests hostile_archives/.
- **Dépendances :** P4-02.
- **Risques :** ZIP bomb, archive malformée, faux sentiment de confiance via SHA.
- **Tests :** Troncature, membres dupliqués, traversée, symlink, chiffrement, inflation réelle, clé JSON dupliquée, NaN, quota ; zéro écriture métier.
- **Acceptation :** Fichier rejeté avant import si invalide ; erreurs précises ; vérification ne crée aucun scénario ; preuve scope utilisateur/empreinte/revisions.
- **Hors périmètre :** Antivirus de fichiers graphiques et signature d'auteur.
- **Complexité relative :** Élevée.

### P4-04 — Remappage et plan d'import

- **État :** NON COMMENCÉ.
- **Objectif :** Construire un plan indépendant de la base source.
- **Comportements :** Maps IDs par type, nouveaux UUID, validation destinations, descripteurs médias/Rencontres, provenance ; aucun lookup ancien ID.
- **Fichiers/modules envisagés :** archive/remapping.py ; services/archive_import.py partie plan ; tests/remapping/.
- **Dépendances :** P4-03.
- **Risques :** Collision, lien entre copies/utilisateurs, perte de références.
- **Tests :** IDs dupliqués, références manquantes, cycles/parallèles, même archive pour deux comptes, descripteurs phase 5.
- **Acceptation :** Plan complet valide avant écritures ; tous liens internes remappés ; références personnelles non résolues déclarées.
- **Hors périmètre :** Création ORM et association automatique aux ressources existantes.
- **Complexité relative :** Moyenne.

### P4-05 — Import transactionnel et nouvelle copie

- **État :** NON COMMENCÉ.
- **Objectif :** Créer atomiquement le scénario appartenant au destinataire.
- **Comportements :** Confirmation aperçu, choix dossier privé, import nouvelle copie, idempotence réseau, avertissement provenance déjà importée ; aucune Table écrite.
- **Fichiers/modules envisagés :** services/archive_import.py ; vues/formulaires import ; tests/import/.
- **Dépendances :** P4-04.
- **Risques :** Import partiel, doublon involontaire, propriétaire source conservé.
- **Tests :** Faute injectée à chaque étape ; rollback complet ; imports concurrents/replay ; deux comptes ; reload ; référence dossier étrangère.
- **Acceptation :** Tout ou rien ; copie indépendante ; réimport volontaire autorisé ; zéro accès aux données source.
- **Hors périmètre :** Remplacement/merge, fichiers objet et import autonome TMP.
- **Complexité relative :** Élevée.

### P4-06 — Retrait sécurisé et round-trip de référence

- **État :** NON COMMENCÉ.
- **Objectif :** Permettre l'archivage local sans suppression prématurée.
- **Comportements :** Action distincte, preuve de fichier vérifié, contrôle revisions, confirmation des dépendances ; suppression scénario seulement ; comparaison sémantique.
- **Fichiers/modules envisagés :** services/mutations.py ; vues archive/retrait ; tests/round_trip/ ; documentation utilisateur.
- **Dépendances :** P4-05.
- **Risques :** Archive ancienne, perte locale après retrait, suppression médias partagés.
- **Tests :** Créer → Enregistrer → Exporter → Vérifier → Retirer → Importer → Comparer ; variation après export ; autre compte ; CSRF ; rollback.
- **Acceptation :** Identités locales neuves mais contenu/rangs/positions/liens identiques ; modification post-export bloque retrait guidé ; fichiers externes annoncés.
- **Hors périmètre :** Suppression automatique, corbeille durable prétendant libérer la base, garantie de sauvegarde locale.
- **Complexité relative :** Élevée.

## Phase 5 — Illustrations et intégrations TMP

**Sortie de phase :** Six rubriques utilisables ; médias HTTPS réutilisables et références privées ; round-trip des dépendances explicitement non autonomes.

### P5-01 — Médiathèque HTTPS privée

- **État :** NON COMMENCÉ.
- **Objectif :** Réutiliser les références sans stocker les images.
- **Comportements :** MediaAsset, CRUD privé, URL HTTPS validée, titres/alt, relations SET_NULL et fallback ; contrat export antérieur respecté.
- **Fichiers/modules envisagés :** models.py et migration additive médias ; forms/validators ; views/media.py ; tests/media/.
- **Dépendances :** P4-06.
- **Risques :** SSRF via futur proxy, médias d'autres comptes, URL avec secret.
- **Tests :** URL locale/protocoles refusés ; owner/CSRF ; CRUD reload/conflits sur références de scénario ; suppression ressource en cours d'édition.
- **Acceptation :** Aucun fetch serveur, fichier/base64 en DB ou disque durable ; références privées ; suppression garde rubriques et état indisponible.
- **Hors périmètre :** Upload, déduplication mondiale et stockage objet.
- **Complexité relative :** Moyenne.

### P5-02 — Splash dans éditeur et lecteur

- **État :** NON COMMENCÉ.
- **Objectif :** Afficher les illustrations avec dégradation sûre.
- **Comportements :** Picker médiathèque, rubrique Splash, grand format, lazy loading, no-referrer, alt/fallback ; icône carte.
- **Fichiers/modules envisagés :** Fragments Splash ; lecteur/éditeur ; résumés board ; tests navigateur media/.
- **Dépendances :** P5-01.
- **Risques :** Image distante remplacée/lourde, focus modale, URL non disponible.
- **Tests :** Persistance/reload/conflits de toute mutation ; image absente ; clavier/alt ; séquence export/import avec URL.
- **Acceptation :** Même média réutilisé dans plusieurs scènes ; lecture possible sans image ; agrandissement accessible.
- **Hors périmètre :** Compression distante garantie et images embarquées.
- **Complexité relative :** Moyenne.

### P5-03 — Références de Rencontres privées

- **État :** NON COMMENCÉ.
- **Objectif :** Référencer TMP sans modifier les règles ni la Table.
- **Comportements :** Picker owner-scoped, rubrique Rencontre, consultation ; association explicite d'un descripteur importé ; fallback suppression.
- **Fichiers/modules envisagés :** SceneBlock.encounter, migration si nécessaire ; vues/formulaires ; toolkit.Encounter en lecture ; tests/integrations/.
- **Dépendances :** P5-02.
- **Risques :** Association à rencontre étrangère, copie brute payload non portable.
- **Tests :** Persistance/reload/conflits ; autre compte ; suppression ressource ; import non résolu ; aucune mutation Table/rules.
- **Acceptation :** Seules Rencontres du destinataire sélectionnables ; aucun ancien ID exporté utilisé ; Table inchangée.
- **Hors périmètre :** Chargement sur Table, snapshots autonomes Mobs/équipements.
- **Complexité relative :** Moyenne.

### P5-04 — Round-trip des six rubriques

- **État :** NON COMMENCÉ.
- **Objectif :** Valider le MVP portable enrichi de références.
- **Comportements :** Export décrit médias HTTPS et Rencontres non résolues ; import crée/déduplique selon politique privée validée et propose associations ; messages de dépendances.
- **Fichiers/modules envisagés :** Export/import DTO, schémas existants ; tests/round_trip et UI aperçu.
- **Dépendances :** P5-03.
- **Risques :** Régression format 1.0, doublons inutiles, ressource externe présentée comme embarquée.
- **Tests :** Six rubriques, URL expirée, Rencontre supprimée/source autre compte, copie double ; toutes fixtures phase 4.
- **Acceptation :** Archive narrative reste 1.0 si contrat inchangé ; aucune donnée perdue ; associations explicites ; référence de round-trip complète.
- **Hors périmètre :** Version archive avec ressources graphiques et partage public.
- **Complexité relative :** Moyenne.

## Phase 6 — Stabilisation et livraison

**Sortie de phase :** Recette complète, sécurité/accessibilité/non-régression et PostgreSQL validés ; livraison prête, déploiement non implicite.

### P6-01 — Sécurité et concurrence de bout en bout

- **État :** NON COMMENCÉ.
- **Objectif :** Fermer les écarts de sécurité mesurés.
- **Comportements :** Matrice lecture/écriture owner, CSRF/méthodes, limites, conflits et idempotence sur toutes commandes.
- **Fichiers/modules envisagés :** tests/security et concurrency ; services ciblés si correction nécessaire.
- **Dépendances :** P5-04.
- **Risques :** Chemin secondaire non protégé, comportement SQLite trompeur.
- **Tests :** Matrice endpoints ; payloads XSS/ZIP/JSON ; deux onglets ; tests transactionnels PostgreSQL ; fuzz borné parser.
- **Acceptation :** Aucun accès interutilisateur ni écrasement silencieux ; archive invalide sans donnée ; écarts corrigés et retestés.
- **Hors périmètre :** Audit/refonte générale hors module.
- **Complexité relative :** Moyenne.

### P6-02 — Accessibilité et non-régression navigateur

- **État :** NON COMMENCÉ.
- **Objectif :** Vérifier l'expérience MJ et le socle existant.
- **Comportements :** Parcours clavier, focus, petits écrans, états erreur ; tests ciblés thème/navigation/modales.
- **Fichiers/modules envisagés :** tests navigateur scenarios et smoke toolkit ; CSS/templates ciblés.
- **Dépendances :** P6-01.
- **Risques :** Icône muette, contrôle inaccessible, collisions globales.
- **Tests :** MJ : créer/jouer/archiver/restaurer ; axe ou équivalent + revue manuelle ; Monster Builder/Bestiaire/Rencontres/Table/Équipements.
- **Acceptation :** Aucune tâche essentielle exige drag ; lecteur sans édition ; autres modules conformes ; suite Django réelle complète passe.
- **Hors périmètre :** Refonte DA, interface joueur et fonctions nouvelles.
- **Complexité relative :** Moyenne.

### P6-03 — Préparation et validation de livraison

- **État :** NON COMMENCÉ.
- **Objectif :** Vérifier migrations/build sur préproduction isolée.
- **Comportements :** Activation progressive, migration additive et drift, statiques, sauvegarde/retour arrière ; base distincte documentée.
- **Fichiers/modules envisagés :** docs/DEPLOIEMENT_RENDER.md et guide scénarios ; scripts/settings uniquement si lot approuvé ; tests deploy/.
- **Dépendances :** P6-02.
- **Risques :** Build pointant production, seed pendant build, statiques manquants.
- **Tests :** PostgreSQL vide puis existant anonymisé ; check/deploy avec env test ; collectstatic ; smoke préproduction autorisée ; rollback applicatif.
- **Acceptation :** Base cible attestée ; aucune donnée production utilisée sans autorisation ; procédure reproductible ; zéro média durable sur Render.
- **Hors périmètre :** Déploiement automatique de production et choix fournisseur objet.
- **Complexité relative :** Moyenne.

### P6-04 — Recette MVP et clôture documentaire

- **État :** NON COMMENCÉ.
- **Objectif :** Déclarer le MVP prêt sur preuves.
- **Comportements :** Recette six rubriques/tableau/lecteur/archives ; inventaire décisions ouvertes et limites ; états lots mis à jour.
- **Fichiers/modules envisagés :** Quatre documents SCENARIOS ; rapport recette et documentation utilisateur.
- **Dépendances :** P6-03.
- **Risques :** Confondre prêt à livrer et déployé, critères déclarés sans preuve.
- **Tests :** Parcours de référence intégral ; suites finale Django/PostgreSQL/navigateur ; grille P0 intégrée ; revue périmètre.
- **Acceptation :** Tous lots requis acceptés, preuves liées ; limitations publiées ; production uniquement après autorisation distincte.
- **Hors périmètre :** Déploiement implicite, fonctions hors MVP.
- **Complexité relative :** Faible.

## Dépendances vérifiables

| Lot | Prérequis directs |
|---|---|
| P0-01 | — |
| P0-02 | P0-01 |
| P0-03 | P0-01 |
| P0-04 | P0-02, P0-03 |
| P1-01 | P0-04 |
| P1-02 | P1-01 |
| P1-03 | P1-02 |
| P1-04 | P1-03 |
| P1-05 | P1-04 |
| P2-01 | P1-05 |
| P2-02 | P2-01 |
| P2-03 | P2-02 |
| P2-04 | P2-03 |
| P2-05 | P2-04 |
| P3-01 | P2-05 |
| P3-02 | P3-01 |
| P3-03 | P3-02 |
| P3-04 | P3-03 |
| P4-01 | P3-04 |
| P4-02 | P4-01 |
| P4-03 | P4-02 |
| P4-04 | P4-03 |
| P4-05 | P4-04 |
| P4-06 | P4-05 |
| P5-01 | P4-06 |
| P5-02 | P5-01 |
| P5-03 | P5-02 |
| P5-04 | P5-03 |
| P6-01 | P5-04 |
| P6-02 | P6-01 |
| P6-03 | P6-02 |
| P6-04 | P6-03 |

P0-02 et P0-03 ont le même préalable P0-01 et peuvent être réalisés indépendamment. Tous les autres prérequis pointent vers des lots précédents : aucun cycle. Ne pas traiter une référence documentaire comme dépendance d'exécution supplémentaire.

## Périmètre exact et garde-fous

MVP : bibliothèque privée et dossiers partagés ; duplication ; scènes ordonnées et coordonnées indépendantes ; six rubriques ; connexions canoniques/cycles ; lecteur ; tableau ; revisions ; HTTPS ; références de Rencontres ; ZIP/JSON narratif ; import nouvelle copie ; vérification et retrait explicite.

Hors MVP : stockage objet/upload, graphiques embarqués, snapshots TMP autonomes, chargement sur Table depuis scénarios, partage public, campagne multi-scénarios, temps réel, fusion automatique, HTML libre, historique complet.

Export ne supprime jamais. Import ne remplace jamais par défaut. Suppression ordinaire de bibliothèque reste distincte du parcours guidé de retrait : elle avertit du risque d'absence de copie et n'est jamais appelée par le téléchargement.

Toute édition exige tests persistance/conflit dans son lot. P6 ajoute une couverture transversale ; il ne sert pas à différer la sécurité.

## Décisions ouvertes et blocages

Voir SCENARIOS_DECISIONS.md : moteur (P0-04), détails relationnels/idempotence (P1-01), contrat version/limites (P1-02), budget requêtes et mesures d'intégration (P3-01/P3-04), politique de réutilisation médias à import (P5-01/P5-04), environnement de préproduction (P6-03).
Avant P1-03, aucune question marquée pré-migration ne doit rester ouverte. Aucun choix de fournisseur objet nécessaire au MVP.
