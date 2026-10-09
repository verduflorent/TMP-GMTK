# Mes Scénarios — Architecture de référence

Version documentaire : 1.0 — 9 octobre 2026.
Statut : décisions produit validées ; documents à valider avant toute implémentation.
Dépôt : verduflorent/TMP-GMTK. Branche exclusive : feature/scenario-editor.

## 1. Autorité, portée et références

Ce document précise l'architecture validée pour le chantier narratif. Il complète, sans remplacer, AGENTS.md, CdC.md, LdR.md et Roadmap.md. Aucune règle TMP ne doit être modifiée. Une contradiction avec ces sources bloque uniquement le lot concerné et doit être signalée.

Documents associés : [roadmap](SCENARIOS_ROADMAP.md), [journal de décisions](SCENARIOS_DECISIONS.md), [phase 0](SCENARIOS_PHASE0.md).
Les détails proposés ci-dessous sont à figer dans P1-01/P1-02 avant les migrations. Ils ne doivent pas être présentés comme du code existant.

## 2. Faits observés et référence de tests

Le dépôt local consulté est sur feature/scenario-editor, commit ef668279b9975367f86ec4b08ad20697b0d16c88.
- toolkit/models.py : UserFolder privé et partagé entre BestiaryMob et Encounter ; EncounterDraftMob contient des snapshots de Mobs.
- toolkit/views.py : chargement des Rencontres ajoutant des Mobs à la Table ; filtrage par propriétaire.
- toolkit/services.py : services transactionnels et helper full_clean avant sauvegarde.
- config/settings.py : comptes Django, CSRF, SQLite local et PostgreSQL de production.
- templates/base.html et toolkit/static/ : socle des templates, navigation et thème.
- pyproject.toml : Python 3.14 et Django ; pas de chaîne React observée lors de l'audit.
- build-render.sh : migrations et seed pendant le build ; vérifier la base cible avant tout essai de déploiement.

Le 9 octobre 2026, 195 tests ont été exécutés et réussis avec config.settings_test, DATABASE_URL retirée du processus et PYTHONDONTWRITEBYTECODE=1 :
`manage.py test toolkit rules catalogue --noinput`.
Cette référence est locale/SQLite. Elle n'atteste ni des tests PostgreSQL ni de l'état de production.
Le nombre doit être redécouvert au début de chaque lot ; aucune assertion de total figé à 195.

## 3. Responsabilités

Application Django scenarios, namespace scenarios et préfixe /scenarios/.
Templates et sessions existants ; API privée de commandes JSON uniquement où nécessaire.
Aucun besoin initial de DRF, SPA globale, WebSocket ou refonte de toolkit.

Organisation envisagée :
- models.py, forms.py, urls.py ;
- views/library.py, editor.py, reader.py, board.py, archives.py, media.py ;
- services/mutations.py, revisions.py, duplication.py, archive_export.py, archive_import.py ;
- archive/schema.py, schemas/, upgrades/, remapping.py ;
- templates/scenarios/ et static/scenarios/{js,css}/ ;
- tests/ avec tests de domaine, vues, archives et parcours navigateur.

Les opérations métier passent par les services, y compris duplication, import et éventuelles actions admin. Les vues ne contiennent pas de règle TMP. Aucun import de scénarios ne déclenche une écriture sur la Table.

## 4. Modèle envisagé et invariants

### Scenario

UUID primaire neuf à la création ; owner vers AUTH_USER_MODEL, CASCADE ; title limité ; summary texte ; folder facultatif vers toolkit.UserFolder, SET_NULL ; content_revision et layout_revision entières ; created_at/updated_at.
Provenance facultative : origin_document_id, imported_export_id, imported_content_sha256. Ces valeurs ne servent jamais de permission.
L'identité portable document_id est indépendante de l'UUID applicatif : conservée à travers export/import du même document ; duplication éditoriale crée une nouvelle identité portable.

### Scene

UUID primaire ; scenario CASCADE ; title ; narrative_rank entier positif ou nul ; x/y flottants finis et bornés ; dates.
Index (scenario, narrative_rank). Ordre stable (narrative_rank, UUID).
L'ordre narratif ne dépend jamais des coordonnées, du zoom ou des connexions.
La permutation doit contenir exactement les scènes actuelles une fois chacune. Les rangs contigus sont normalisés par service ; pas de contrainte UNIQUE de rang au MVP.

### SceneBlock

UUID primaire ; scene CASCADE ; kind parmi narration, interpretation, splash, gm_note, transition, encounter ; rank ; text ; payload JSON limité et versionné.
Plusieurs rubriques identiques sont autorisées ; aucune rubrique obligatoire.
target_scene facultatif vers Scene avec CASCADE pour supprimer les rubriques de transition entrantes lors d'une suppression de destination.
media et encounter seront des relations facultatives SET_NULL introduites/activées en phase 5. Un descripteur de référence non résolue conserve le nom et l'état de la ressource, sans identité propriétaire.
Index (scene, rank). Texte brut échappé au MVP ; pas d'HTML libre.

Contraintes :
- kind=transition impose target_scene non nul ; les autres types interdisent target_scene ;
- source et cible appartiennent au même scénario ;
- media, encounter et folder appartiennent au propriétaire du scénario ;
- références aux médias/Rencontres permises seulement pour les types correspondants ;
- payload validé selon le type et la version, taille et profondeur bornées.

Les règles à travers tables relèvent des services et de full_clean explicite : save() et bulk_create() ne suffisent pas. Les contraintes simples doivent aussi être matérialisées en base.

### Transition canonique

La rubrique Transition est la seule connexion persistée. Source = scene parente ; cible = target_scene ; libellé = texte dédié de la rubrique.
Aucune table de connexions indépendante, aucun target_id caché dans le JSON, aucune sérialisation du moteur graphique comme donnée métier.
Le tableau et le lecteur consomment la même rubrique. Créer une flèche crée une rubrique en une transaction.
Connexions parallèles, embranchements, convergences, cycles et boucles sur soi : détail recommandé à ratifier en P1-01.
Une flèche supprimée supprime sa rubrique. Un changement d'ordre ne modifie aucune connexion.

### MediaAsset — phase 5

UUID ; owner CASCADE ; title ; alt_text ; source_kind ; external_url HTTPS pour V1 ; dates.
Une illustration peut être référencée par plusieurs rubriques du propriétaire. Prévoir une revision propre au média pour éviter l'écrasement de ses métadonnées. L'export capture également les revisions des médias référencés ; la vérification/retrait recontrôle ces dépendances. Fixer en P1-01 l'ordre de verrouillage et la validation de ce snapshot, puis détailler le service média en P5-01.
Aucune image, Base64 ou pièce binaire dans PostgreSQL. Aucun fichier durable sur Render.
L'abstraction permet une clé objet et des métadonnées de fichier ultérieures, sans obligation de les migrer au MVP.

## 5. Suppression, duplication et propriété

- Dossier : SET_NULL sur scénarios ; conserve scènes et rubriques. Confirmation rappelle l'effet sur Bestiaire/Rencontres existants.
- Scène : suppression de ses rubriques et de toutes les rubriques Transition qui la ciblent. Liste/nombre des liens affectés présenté avant confirmation.
- Scénario : suppression de ses scènes/rubriques ; conserve dossiers, Rencontres et médias réutilisables.
- Média/Rencontre : référence SET_NULL ; rubrique conservée avec libellé de secours et état indisponible.
- Compte : cascades privées suivant les conventions existantes.
- Duplication : transaction ; nouveaux UUID et nouveau document_id ; remappage complet des transitions ; médias/Rencontres du même utilisateur restent référencés.

Les ressources sont résolues depuis un queryset appartenant à request.user. Les enfants sont vérifiés via leur scénario ; une UUID ne confère aucun accès. Lecture et écriture sont toutes protégées.
Les erreurs d'accès utilisent une politique homogène (404 pour ressource privée non accessible). Écritures GET refusées, CSRF conservé, owner assigné côté serveur.

## 6. Persistance et conflits dès les premières écritures

Toute mutation existante reçoit la revision attendue, verrouille Scenario dans transaction.atomic, vérifie l'état courant, valide puis écrit et incrémente la revision adéquate :
- métadonnées, contenu, ordre et références : content_revision ;
- positions : layout_revision ;
- création/suppression de scène, retrait du scénario : les deux ;
- transitions : content_revision.

Une revision périmée renvoie 409 sans effet. Les formulaires HTML ont des champs cachés de revision ; les commandes JSON ont un schéma explicite.
Aucun objet persistant n'est créé avant les vérifications de permission et de revision.

Une création sans objet parent reçoit une clé d'idempotence liée au compte et à l'opération. Une répétition identique retourne le résultat existant ; une clé réutilisée avec contenu différent est refusée. Le mécanisme exact de conservation/expiration est arrêté en P1-01. Si une preuve persistante est nécessaire, prévoir un registre minimal MutationReceipt (owner, opération, clé, empreinte de requête, référence de résultat, expiration), unique par owner/opération/clé, écrit dans la même transaction. Le replay d'un résultat supprimé ne recrée pas implicitement la ressource. L'import possède également cette protection ; deux imports volontaires utilisent deux clés.

Édition texte : sauvegarde explicite initiale, confirmation serveur et texte local conservé lors d'un conflit. Ne pas écraser automatiquement ni promettre une fusion.
Déplacements : UI locale ; lot en fin de geste ; une requête en vol ; mouvements suivants coalescés ; aucun POST par pointermove.
Après réponse perdue : relire les revisions et l'état, réconcilier avant nouvelle écriture. États Enregistrement/Enregistré/Échec/Conflit accessibles.
Pas de dépendance à beforeunload pour enregistrer. Avertissement de navigation si changements en attente.

Tests de rechargement, persistance et conflit exigés dans chaque lot d'édition.

## 7. Frontend et lecture

Moteur ouvert jusqu'à P0-04 : Cytoscape.js ou îlot React Flow dans une page Django.
Un adaptateur convertit le modèle métier en nœuds/connexions ; les composants ignorent les modèles ORM.
Cartes : titre, ordre narratif affiché, icônes par type de rubrique, contrôles nommés. Pas de texte complet de scène dans tous les nœuds.
Tableau charge des résumés ; panneau charge une scène sélectionnée. Pas de N+1 ; prefetch/select_related et agrégations ciblées.
Styles limités à scenarios ; scripts uniquement sur pages concernées. Modifications de base.html minimales et vérifiées sur tous les écrans existants.

Mode lecteur séparé : narrations/dialogues lisibles, rubriques secondaires à la demande, Splash agrandi, transitions navigables, retour à la structure. Pas de commandes d'édition.
Clavier : alternative complète à glisser-déposer, connexion par sélection source/cible, réorganisation par boutons, focus visible et restauré après modale.
Petits écrans : liste navigable et lecteur en priorité ; pas d'obligation de déplacer une carte au doigt.
Zoom/viewport sont des préférences d'interface ; hors contenu portable V1.

## 8. Contrat portable .tmpcamp

ZIP non chiffré contenant exactement manifest.json et scenario.json en V1. Pas de fichiers graphiques embarqués, pas d'HTML autonome.
Compression autorisée : Store ou Deflate. Version format indépendante de version Django, version applicative et migrations.

Manifeste :
- format = tmpcamp ;
- format_version = 1.0 ;
- document_id (provenance du document), export_id (nouveau par export), created_at UTC ;
- required_features ;
- files : path, taille exacte, SHA-256 ;
- revisions exportées et profil narrative-v1 pour rendre la vérification explicite.

Document :
- metadata : titre/résumé ;
- scenes : id interne, titre, ordre, x/y ;
- blocks : id interne, scène, type, ordre, texte/payload versionné ;
- transitions représentées uniquement par leurs rubriques avec target_scene_id ;
- resources.media : identités internes, URL HTTPS et texte alternatif ;
- resources.encounters : descripteurs non résolus au MVP ;
- aucun owner, secret, session, URL signée temporaire ni lien d'autorisation.

Le schéma et une fixture complète avec cycles sont figés en P1-02 puis finalisés en P4-01. Les types Splash/Rencontre doivent être représentables avant leur UI de phase 5 ; aucune donnée inconnue n'est perdue silencieusement.

### Export

Vérification des deux revisions, lecture cohérente sous le même verrou Scenario que les mutations et capture cohérente des métadonnées/révisions de médias référencés. Copier les données nécessaires dans une transaction courte ; compresser après libération du verrou. Pas de requête réseau.
L'UI attend la fin des sauvegardes ou annonce explicitement que seuls les changements confirmés sont exportés.
Résumé des éléments inclus et des dépendances externes. Une URL d'image ne constitue pas une illustration embarquée.

### Validation/import

Vérifier conteneur, CRC lors de lecture intégrale, tailles/empreintes, schémas, identités uniques et toutes références avant transaction d'écriture.
Lire les membres autorisés sans extractall. Refuser chemins absolus, traversées, séparateurs détournés, noms dupliqués, symlinks, archives imbriquées, chiffrement et méthode inconnue.
Compter les octets réellement décompressés avec arrêt immédiat à la limite ; ne pas se fier au manifeste.
JSON : UTF-8, clés dupliquées refusées, NaN/Infinity refusés, profondeur/longueurs limitées.
SHA-256 détecte corruption ; aucune preuve d'auteur ni de confiance.

Limites proposées à ratifier P1-02 : archive 10 Mio, décompressé cumulé 20 Mio, exactement deux fichiers, 500 scènes, 5 000 rubriques, 2 000 transitions. Limites également côté requêtes et services, pas seulement UI.

Conversion pure de version supportée vers schéma courant ; refus de majeure inconnue/capacité requise non supportée. Fixtures historiques maintenues. Ne pas promettre compatibilité perpétuelle.

Import par défaut = nouvelle copie. Nouveau Scenario et nouveaux UUID de toutes entités ; table de remappage par type ; destination des transitions résolue uniquement dans l'archive.
Dossier proposé au destinataire et vérifié chez lui ; aucun import de propriété source.
Détection de provenance/empreinte déjà présente : avertissement et confirmation d'une nouvelle copie, jamais remplacement implicite.
Une erreur après validation ou pendant les écritures annule toutes données nouvelles.
Deux utilisateurs importent indépendamment la même archive.

### Références TMP

Pas de copie brute d'EncounterDraftMob.payload comme garantie de portabilité : il peut référencer des équipements personnels.
V1 : descripteurs non résolus et association explicite à une Rencontre appartenant au destinataire.
Aucune recherche par ancien ID d'utilisateur et aucune modification de Table.
Snapshots autonomes des Rencontres/Mobs et dépendances : hors MVP.

### Retrait sécurisé

Trois actions distinctes : Exporter une copie ; Importer une archive ; Retirer du stockage en ligne.
Aucune suppression automatique après téléchargement.
Vérifier un fichier choisi localement sans créer de données ; afficher périmètre inclus et dépendances.
Pour parcours guidé de retrait : preuve de vérification liée au compte, scénario, empreinte et revisions ; revalider les deux revisions et les revisions des médias inclus au retrait. Une modification ultérieure impose un nouvel export/vérification.
Confirmation explicite et CSRF ; conserver médias/Rencontres partagés.
La vérification ne garantit pas conservation future du fichier. Recommander plusieurs copies sans prétendre détecter le succès du téléchargement.

## 9. Médias et évolution

HTTPS externe V1 : validation syntaxique stricte ; refus data/javascript/file et destinations locales/privées ; sans récupération serveur. Redirections et changement du contenu externe restent hors contrôle.
Chargement navigateur différé, referrerpolicy=no-referrer, placeholder et texte alternatif. Aucune iframe ni SVG/HTML utilisateur embarqué. Dégradation sans bloquer la lecture.
Sans proxy, l'application ne garantit ni taille réelle distante ni compression. Conseiller des images optimisées ; ne pas annoncer un quota de téléchargement garanti.

Stockage objet et archives binaires : hors MVP. Ultérieurement fichiers privés, validation/décodage/réencodage, métadonnées séparées, déduplication par propriétaire, staging et nettoyage compensatoire. Transaction DB seule ne rend pas un upload objet atomique.
Aucun tarif gratuit supposé acquis ; conditions et quotas à vérifier au moment du choix.

## 10. Livraison et périmètre

MVP livré après phase 6 : bibliothèque/dossiers/duplication, six rubriques, lecteur, tableau, sauvegardes avec conflits, médias HTTPS, références de Rencontres, archive narrative/import et retrait explicite.
Hors MVP : upload/stockage objet, médias embarqués, snapshots TMP portables, chargement sur Table depuis lecteur, partage public, campagnes multi-scénarios, temps réel, HTML enrichi libre et historique complet.

Préproduction avec base PostgreSQL distincte ; migrations additives ; tests non-régression avant activation. Aucune commande de déploiement autorisée par ces documents seuls.
Retour arrière applicatif/activation sans destruction des nouvelles tables. Sauvegarde vérifiée avant première migration de production.

## 11. Exemple minimal de structure de document

Exemple illustratif valide pour deux scènes et une transition ; les checksums du manifeste seront produits par le codec, jamais saisis manuellement.

```json
{
  "metadata": {"title": "Exemple fictif", "summary": ""},
  "scenes": [
    {"id": "s1", "title": "Arrivée", "order": 0, "position": {"x": 0, "y": 0}},
    {"id": "s2", "title": "Station", "order": 1, "position": {"x": 300, "y": 120}}
  ],
  "blocks": [
    {"id": "b1", "scene_id": "s1", "type": "narration", "order": 0, "schema_version": 1, "text": "La station apparaît.", "payload": {}},
    {"id": "b2", "scene_id": "s1", "type": "transition", "order": 1, "schema_version": 1, "text": "Entrer", "payload": {}, "target_scene_id": "s2"}
  ],
  "resources": {"media": [], "encounters": []}
}
```

Les IDs s1/s2/b1/b2 sont locaux au paquet et ne sont pas recherchés dans la base. P1-02 fige les noms exacts du schéma et P4-01 les implémente.
