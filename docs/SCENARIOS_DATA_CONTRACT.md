# P1-01 — Contrat relationnel et commandes (proposition à valider)

Statut : **À VALIDER**. Ce document n'est pas une migration et ne modifie pas le fonctionnement de TMP-GMTK. La comparaison graphique P0-04 reste incomplète (tests de charge et accessibilité non réalisés), donc P1-01 n'est pas déclaré accepté.

## Identités et propriété
- Scenario.id, Scene.id, SceneBlock.id : UUIDv4 applicatifs, nouveaux lors d'une duplication ou importation.
- Scenario.document_id : UUID portable indépendant ; conservé à l'import avec provenance, renouvelé lors d'une duplication éditoriale.
- owner : FK AUTH_USER_MODEL sur Scenario ; jamais accepté depuis un formulaire ou une archive.
- Scene.scenario : FK CASCADE ; SceneBlock.scene : FK CASCADE.
- Scenario.folder : FK UserFolder SET_NULL, avec validation que le dossier appartient à owner.
- Toutes les lectures/écritures d'enfants passent par Scenario filtré par owner ; une UUID connue ne suffit pas.

## Transitions et ordre
- Une transition est un SceneBlock de kind=transition et target_scene FK Scene.
- target_scene obligatoire uniquement pour transition, interdit pour les autres types.
- Cible et source appartiennent au même Scenario, validées dans un service transactionnel ; aucune table Edge parallèle.
- Autoriser plusieurs flèches entre les mêmes scènes, les boucles sur soi, les cycles et les scènes isolées.
- Suppression d'une scène : supprimer ses blocs et les transitions entrantes (FK target_scene CASCADE) ; avertir sur le nombre de liaisons détruites.
- Scene.narrative_rank entier >= 0, tri (narrative_rank,id) ; renumérotation contiguë dans le service de réorganisation. Scene.x/y : flottants finis bornés (bornes proposées ±100000), non utilisés pour l'ordre narratif.
- SceneBlock.rank : entier >= 0, normalisé dans sa scène ; plusieurs blocs du même kind permis. Narration prioritaire dans l'interface mais pas unique dans les données.

## Contenu et références
- Six kinds : narration, interpretation, splash, gm_note, transition, encounter.
- text : texte brut échappé à l'affichage ; payload : JSON versionné et validé selon kind, taille/profondeur bornées. Aucun HTML ou JS utilisateur exécuté.
- Splash/Encounter : référence nullable à une ressource privée du même propriétaire, avec descripteur de secours en cas de suppression. Les relations pourront être introduites en P5 ; le schéma portable doit déjà savoir les décrire.
- Suppression de scénario : cascade scènes/blocs, mais préserve les dossiers, médias et Rencontres réutilisables. Suppression de dossier : SET_NULL sans perdre les scénarios.

## Révisions et écritures
- Scenario.content_revision et layout_revision démarrent à 0.
- Contenu (métadonnées, scènes, blocs, ordre, transitions) : content_revision ; positions : layout_revision ; création/suppression de scène : les deux.
- Toute commande reçoit la/les révisions attendues, vérifie owner, verrouille Scenario via select_for_update dans transaction.atomic, refuse une révision périmée avec HTTP 409 sans écriture.
- Révision incrémentée une seule fois par commande acceptée ; le client ne doit jamais interpréter une absence de réponse comme une réussite.
- Déplacement : sauvegarde groupée en fin de geste, pas de POST par événement souris. En cas de réponse perdue, relire l'état et réconcilier.
- Édition texte : sauvegarde explicite, affichage Enregistrement/Enregistré/Erreur/Conflit, maintien du texte local lors d'un 409.
- Création de scénario/import : clé d'idempotence par utilisateur + opération + clé ; répétition de même empreinte retourne le résultat existant, empreinte différente => conflit. Registre persistant MutationReceipt recommandé, avec expiration et comportement explicite si résultat supprimé.

## Commandes envisagées
| Commande | Révision attendue | Révision incrémentée |
|---|---|---|
| create_scenario | clé idempotence | 0 initial |
| update_scenario_metadata | content | content |
| create_scene / delete_scene | content + layout | content + layout |
| reorder_scenes | content | content |
| update_scene / create_block / update_block / delete_block | content | content |
| create_transition / update_transition / delete_transition | content | content |
| save_positions | layout | layout |
| duplicate_scenario | clé idempotence et contrôle de propriété | nouvelles révisions 0 |
| import_scenario | clé idempotence | nouvelles révisions 0 |
| remove_scenario | content + layout, confirmation explicite | suppression |

## Cas à tester avant P1-03
1. Une transition vers une scène d'un autre scénario/utilisateur est refusée, même si l'UUID existe.
2. Suppression d'une destination supprime toutes les transitions entrantes et n'affecte pas les autres scénarios.
3. Deux créations identiques avec la même clé ne produisent qu'un seul objet ; une clé réutilisée avec contenu différent est refusée.
4. Deux onglets modifient le texte avec la même révision : un seul gagne ; l'autre reçoit 409 et garde sa saisie.
5. Une modification de position n'écrase pas une modification de narration concomitante.
6. Duplication remappe les scènes et transitions vers les nouveaux UUID sans référencer l'original.
7. L'import chez un autre compte ne récupère ni propriétaire ni dossiers ni permissions source.
8. La suppression ordinaire et le retrait guidé restent deux parcours distincts ; aucune suppression automatique après export.

## Points à trancher avant migrations
- Validation des bornes de coordonnées et des plafonds texte/JSON.
- Durée et comportement de conservation des clés d'idempotence.
- Schéma exact du descripteur de ressource manquante et du payload versionné (P1-02).
- Invariants de verrouillage et de révision des médias lors d'un export/retrait.
- Définition du contrat d'archive versionné P1-02 avant P1-03.

Aucune migration, vue, API ou dépendance n'est créée par P1-01.
