# P0-01 — Protocole commun (préparation)

Statut : EN COURS. Aucune bibliothèque graphique sélectionnée. Aucun prototype ni intégration Django.

## Fixture reproductible
Exécuter `node prototypes/scenarios/generate-fixtures.mjs` (Node.js moderne). Le script produit `fixtures/S.json`, `M.json`, `L.json` (50/100, 200/400, 500/1000). Graine fixe 20261009. Les deux moteurs consomment exactement le même JSON. Le générateur vérifie comptes, unicité, références, positions finies, cycle, boucle, parallèles, branchement à cinq sorties, scène isolée et round-trip JSON.

## Contrat des actions
Les deux prototypes doivent exposer les dix parcours définis dans `docs/SCENARIOS_PHASE0.md` : création, déplacement souris/clavier, connexion souris/alternative clavier, modification et suppression de lien, cycles et parallèles, pan/zoom/cadrage, ouverture/fermeture du panneau avec retour du focus, changement d'ordre sans déplacement, sérialisation/rechargement.

La carte affiche titre, ordre, icônes de rubriques, bouton Ouvrir et point de connexion. Les libellés des liens restent consultables. Aucune donnée personnelle, aucun appel réseau TMP, aucun changement Django.

## Mesure comparative (à renseigner avant P0-02)
- Machine : OS ___ ; CPU ___ ; RAM ___ ; résolution ___ ; navigateur/version ___ ; échelle ___.
- Node et gestionnaire de paquets : ___ ; versions et licences Cytoscape/edgehandles : ___ ; React Flow : ___.
- Build : production pour les deux ; même navigateur, machine, données, taille de carte, police et icônes.
- Cinq répétitions pour S/M/L ; froid/chaud séparés ; alterner ordre des moteurs.
- Chronométrer rendu depuis données disponibles, mesurer frames de drag/pan, mémoire si accessible, taille compressée totale et temps d'intégration.
- Seuils **proposés à ratifier avant mesure** : M interactif <=2 s ; 95 % des frames <=33 ms ; L aucun blocage >1 s ; conservation 100 % des liens/positions.
- Évaluation MJ : 3 à 5 MJ, tâches identiques, succès/temps/erreurs, préférence recueillie séparément.
- Pondération de décision : usage 25 %, cartes/DA 20 %, accessibilité 20 %, intégration/maintenance 20 %, performances 15 %.

## Validation restante de P0-01
- Exécuter le générateur dans un environnement Node identifié et vérifier les trois sorties.
- Relever la baseline Django et les versions/machine réelles.
- Ratifier les seuils avant de commencer P0-02 et P0-03.
- Consigner les résultats dans la roadmap et les décisions. Ne pas déclarer P0-01 ACCEPTÉ avant ces preuves.
