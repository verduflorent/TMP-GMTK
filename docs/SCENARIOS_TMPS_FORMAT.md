# P1-02 — Contrat portable TMP Stories (.tmps), version 1.0

**Statut : proposition à valider avant P4-01.** Ce document définit un format d'échange, pas une implémentation d'import/export. Il ne modifie pas les données Django.

## Conteneur et identité

- Extension : `.tmps`, archive ZIP non chiffrée ; exactement deux entrées UTF-8 nommées `manifest.json` et `scenario.json`.
- Méthodes autorisées : ZIP_STORED et ZIP_DEFLATED. Pas de dossiers, liens symboliques, chemins alternatifs, doublons, archive imbriquée, contenu exécutable ni images embarquées.
- `format` dans le manifeste : `tmps` (pas `tmpcamp`). `format_version` : `1.0` ; `profile` : `narrative-v1`.
- `document_id` UUID portable du document source ; `export_id` UUID neuf à chaque export ; `created_at` UTC ISO 8601 ; `required_features` tableau de chaînes connues.
- `content_revision` et `layout_revision` : entiers non négatifs, uniquement provenance et cohérence de l'export ; **jamais** révisions à restaurer comme état de verrouillage d'une copie importée.
- `files` : une entrée pour `scenario.json` avec `path`, `size` (octets UTF-8 non compressés) et `sha256` (hexadécimal minuscule). Le manifeste n'inclut pas sa propre empreinte afin d'éviter une définition récursive.

## Schéma narratif `scenario.json`

```json
{
  "schema_version": "1.0",
  "metadata": {"title": "Épisode 0", "summary": "Exemple"},
  "scenes": [
    {"id": "UUID", "title": "Arrivée", "narrative_order": 0,
     "position": {"x": 10, "y": 20}}
  ],
  "blocks": [
    {"id": "UUID", "scene_id": "UUID", "kind": "narration", "rank": 0,
     "text": "|T1| ARRIVÉE |/T1|", "payload": {"version": 1}},
    {"id": "UUID", "scene_id": "UUID", "kind": "transition", "rank": 1,
     "text": "Continuer", "payload": {"version": 1}, "target_scene_id": "UUID"}
  ],
  "resources": {"media": [], "encounters": []}
}
```

Les `UUID` ci-dessus sont des marqueurs pédagogiques ; la fixture utilise de vrais UUID. L'ordre narratif est indépendant de la position. Une transition est exclusivement un bloc de type `transition` et sa cible est une scène du même document. Boucles, cycles, convergences et flèches parallèles sont autorisés.

### Types et références

- Types autorisés : `narration`, `interpretation`, `gm_note`, `splash`, `transition`, `encounter`. Chaque bloc possède `id`, `scene_id`, `kind`, `rank`, `text`, `payload.version=1`. `target_scene_id` est requis pour une transition, interdit sinon.
- Les balises `|T1|`, `|T2|`, `|TXT|` restent du **texte brut**. Elles ne sont jamais exécutées comme HTML.
- `splash` peut conserver `payload.external_url` HTTPS et `payload.alt_text` ; le média distant n'est **pas** dans l'archive.
- `encounter` peut conserver `payload.resource_key`, pointant vers une entrée de `resources.encounters` avec `key`, `name` et `status: "unresolved"`. Le numéro de PK Django `encounter_id` n'est jamais exporté.
- À l'import, la Rencontre reste non résolue jusqu'à association explicite avec une Rencontre du destinataire. Une référence manquante n'entraîne aucun chargement sur la Table.
- `resources.media` contient des descripteurs `key`, `title`, `alt_text`, `external_url` HTTPS, jamais des identifiants d'utilisateur ou des URL signées.
- Aucune propriété `owner`, `folder_id`, session, token, chemin absolu ou identifiant local d'autorisation.

## Validation obligatoire avant écriture

1. Limites : fichier reçu <= 10 Mio, total décompressé réel <= 20 Mio, 500 scènes, 5 000 blocs, 2 000 transitions, 50 000 caractères par bloc, titre <= 120 caractères.
2. Vérifier signatures ZIP, deux membres exactement, méthodes, absence de chiffrement et symlinks, CRC, longueurs réelles et SHA-256. Ne jamais appeler `extractall`.
3. JSON strict UTF-8, rejet des clés dupliquées, NaN/Infinity, profondeurs excessives, valeurs hors schéma et version/capacité inconnue.
4. UUID uniques par collection, relations existantes, rangs valides, coordonnées finies dans [-100000,100000], URL HTTPS sûres, texte affiché en échappant les caractères spéciaux.
5. Validation pure sans mutation ; ensuite seulement remappage vers **de nouveaux UUID locaux** et transaction de création appartenant au compte connecté.
6. Même archive importée volontairement deux fois : deux copies distinctes avec clés d'idempotence distinctes. Un replay avec la même clé n'en crée pas une troisième.
7. Une archive ZIP et un SHA-256 n'authentifient pas l'auteur ; les contenus externes restent non fiables.

## Compatibilité

- Versions 1.x : convertisseurs purs et fixtures de régression si le schéma évolue.
- Majeure inconnue ou fonctionnalité obligatoire inconnue : refus explicite, sans import partiel.
- Les fichiers ne sont pas liés aux migrations Django ni au moteur Cytoscape.
- Le format actuel représente **un scénario**. Un ensemble multi-scénarios demandera une version/capacité explicite ; ne pas interpréter silencieusement un autre schéma comme une campagne.

## Cas de fixture de référence

La fixture `scenarios/archive/fixtures/reference_v1.json` couvre une boucle, un cycle, une convergence, une transition parallèle, les six types, un Splash HTTPS et une Rencontre non résolue. P4-01 devra en déduire un ZIP déterministe, calculer les tailles/empreintes, puis ajouter des fixtures corrompues (duplicate key, ZIP bomb, chemins détournés, hash incorrect, cible absente, capacité inconnue).

## Décisions encore à valider

- Valeurs exactes de `required_features` et politique d'extensions optionnelles.
- Plafond de profondeur JSON et longueurs de métadonnées, URL et tableaux de ressources.
- Validation des URL externes (syntaxe uniquement, sans fetch réseau) et traitement des ressources supprimées.
- Encodage canonique JSON pour reproductibilité des empreintes.
- Politique de provenance des exports et protection contre la réutilisation d'un document importé.

**Aucun export/import n'est activé par ce lot.**
