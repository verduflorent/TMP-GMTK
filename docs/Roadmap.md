Roadmap technique du TMP Character Editor et GM Toolkit
1. Résumé de stratégie
Huit PR principales : six pour une V1 fonctionnelle, une pour l’UX et l’habillage, une pour le déploiement. Aucun code ni repository n’est créé à cette étape.
Le découpage reprend le CDC final et ses AC-001 à AC-060. Une modification d’ordre est utile : Table et rencontres en PR 4, Évolution et Randomizer en PR 5. Le randomizer doit valider son lot sur une Table réelle ; construire cette destination avant lui évite une fonctionnalité provisoire et une dépendance circulaire.
Architecture proposée : Django classique, pages rendues par templates, formulaires Django et JavaScript limité aux interactions utiles. Un module Python de règles indépendant de Django ; des services applicatifs simples pour charger les données, appeler les règles et enregistrer les résultats. Pas d’API publique, SPA, moteur générique ou traitement asynchrone sans besoin démontré.
Chaque PR est une branche courte issue de la précédente fusionnée, avec une description du résultat, des AC couverts et des RC concernés, puis tests et revue sur GitHub. Les corrections restent dans cette même PR tant que son périmètre demeure cohérent. Pas de sous-roadmap de micro-états.
Documentation versionnée dès PR 1
Le repository contiendra le CDC final en Markdown, le LdR DOCX original et une extraction Markdown lisible du LdR, tableaux et intitulés conservés. Ajouter un court index des sources et cette roadmap. Les futurs arbitrages RC seront reportés dans le CDC, avec leur décision, dans la PR concernée avant le développement dépendant.
L’extraction du LdR est un outil de documentation hors runtime. Le livre guide la conception ; l’application exécute exclusivement du Python et des données structurées relues. Les corrections ARB intégrées au CDC prévalent sur les passages anciens correspondants du livre. Aucun chargement de DOCX, recherche sémantique ou interprétation de prose pendant un jet ou une génération.
Matérialisation ORM proposée avant le découpage
Conserver quelques modules Django lisibles, par exemple comptes, catalogue et toolkit ; garder les règles hors de leurs modèles. Les noms ci-dessous désignent les modèles proposés, sans imposer une classe ou une table pour chaque nuance du CDC.
Concept	Matérialisation minimale proposée et justification
User / Account	Un modèle User fondé sur AbstractUser, déclaré dès la première migration. Authentification Django standard ; pas de modèle Account supplémentaire, pas de rôles applicatifs.
CharacterProfile	Un modèle portant propriétaire, identité minimale, type, faction, mode et dossier éventuel.
CharacterVersion	Un modèle lié au profil, niveau, validation, six caractéristiques et Armure de base. Unicité profil/niveau ; un standard utilise lui aussi une version.
GameTable	Un modèle en relation un-à-un avec User. Une Table par compte, pas de modèle Session de jeu.
TableInstance	Un modèle avec données locales de construction, PV actuels, camp, rang et source CharacterVersion facultative. Même ensemble de champs de construction que la version, partageable par une petite base abstraite sans table supplémentaire. Pas de CharacterState intermédiaire universel.
CatalogueEntry	Identité privée stable, propriétaire, autorisations/raretés Mob/Élite, référence native éventuelle et définition locale éventuelle. Les fiches pointent toujours ici.
EquipmentDefinition et référence native	Un modèle de définition à nature explicite et champs typés, utilisé pour les références natives protégées et les définitions locales. La référence native n’exige pas une troisième table d’historisation. Définition active = locale si présente, sinon native. Une définition locale appartient à une seule entrée privée ; les natifs peuvent être partagés en lecture.
Arme/accessoire/implant/gadget/Perk	Natures de définition avec groupes de champs explicites et validation adaptée : Puissance, stat, poids, emplacement, activation, usages, seuils, etc. Quelques champs non applicables à certaines natures sont préférables à cinq hiérarchies d’héritage. Pas de cinq modèles vides ne servant que d’étiquettes.
Effets, prérequis, compatibilités	Petites relations typées si plusieurs valeurs sont nécessaires : EquipmentModifier, StatRequirement, EquipmentCompatibility. Valeurs/cibles/conditions limitées à celles comprises par l’application. Pas de langage de règles ni de JSON pour masquer leur structure. Champs finaux affinés en PR 2 après le volet pertinent de RC-10.
EquipmentAssignment	Un modèle d’occurrence avec deux FK explicites facultatives vers Version/Instance, exactement une renseignée. FK CatalogueEntry, slot et position. Accessoire : même modèle, occurrence rattachée à l’arme par une FK facultative ; pas de table de montage distincte. Vérification de même fiche et de nature appropriée.
Choix de capacités	FK de choix offensif18 et de spécialisation directement sur les champs de construction Version/Instance. Petit référentiel TechniqueSpecialization. Pas de modèle séparé pour chaque choix unique.
Exceptions de capacités	Un modèle AbilityException pour ajout/retrait explicite, lié à une version ou instance et au Perk concerné. La liste automatique reste dérivée ; elle n’est pas copiée en permanence.
Override	Un modèle avec propriétaire Version/Instance exclusif, cible calculable, valeur forcée et occurrence équipée facultative. Unicité par cible locale ; types bornés. Les exceptions de présence des Perks sont confiées à AbilityException, plutôt qu’à une override numérique ambiguë.
Folder	Un modèle avec propriétaire, domaine Bestiaire/Scénarios et parent du même domaine. Aucun modèle Campaign/Episode/Scenario séparé sans donnée métier supplémentaire.
Encounter / EncounterEntry	Deux modèles : rencontre nommée/classée ; entrée avec FK CharacterVersion, quantité, camp et rang préparatoire éventuel. Pas de seconde FK indépendante au profil ni de copie de construction.
RollHistoryEntry	Un modèle propre au compte, champs de résultat et de contexte figés ; petites lignes enfants RollDie et RollContribution pour dés et contributions variables. Pas de FK obligatoire vers les objets joués ; pas de snapshot intégral du catalogue.
Randomizer settings	Un ensemble de réglages typés : poids par rareté, taux par type de slot/Mob-Élite et paramètres effectivement retenus. Les probabilités d’Armure validées sont explicites. Pas d’entité persistante par tirage ni de moteur de paramètres arbitraires.

Le User personnalisé est à déclarer dès le démarrage pour éviter un changement tardif du modèle utilisateur ; c’est également la recommandation de la documentation Django sur le modèle utilisateur. La version de Django à figer sera choisie au bootstrap, sans dépendre d’un fournisseur d’hébergement.
Contraintes dès PR 1 : relations protégeant les références vivantes ; unicité profil/niveau ; une Table par compte ; propriétaires cohérents ; rattachement Version/Instance exclusif. Une vérification de même propriétaire entre objets liés se fait explicitement dans les services d’écriture et leurs tests : une FK seule ne la garantit pas. Ne pas mettre en contraintes bloquantes les budgets, plafonds TMP ou quotas de slots que le MJ peut forcer.
Les modèles préparent toutes les relations en PR 1. Des migrations additives ciblées pour les champs d’effets ou de contexte définitivement précisés en PR 2/6 restent normales. Cela ne justifie ni de résoudre RC-10 à la place du MJ ni de construire un schéma universel spéculatif.
Répartition des responsabilités Python
Règles pures : budgets, validité de N1 et progression, seuils/Perks, éligibilités, PV/Armure/Réactions/slots, calculs Delta/Critique/ADV-DES, conformité d’équipement, puis génération aléatoire. Entrées et sorties Python simples, sans requête ORM ni dépendance HTTP. Le tirage aléatoire est injectable pour les tests ; cela n’ajoute pas une fonctionnalité de rejeu au produit.
Services Django : sélectionner le catalogue privé actif, préparer les entrées du moteur, enregistrer une fiche, copier une construction vers Table, charger une rencontre, appliquer des PV, sauvegarder un jet. Les opérations à plusieurs écritures sont transactionnelles pour éviter des lots ou des snapshots partiels, au moyen des transactions Django.
Vues/formulaires : authentification, validation des entrées, appel du service et affichage. Ni formules cachées dans les vues, ni cascade de signaux pour faire évoluer silencieusement les fiches.
2. Graphe simple des dépendances
flowchart LR
    P1[PR 1 Socle et modèle] --> P2[PR 2 Référentiel et règles]
    P2 --> P3[PR 3 Catalogue et Bestiaire]
    P3 --> P4[PR 4 Rencontres et Table]
    P4 --> P5[PR 5 Évolution et Randomizer]
    P2 --> P6[PR 6 Dice Roller et historique]
    P4 --> P6
    P5 --> P7[PR 7 UX et habillage]
    P6 --> P7
    P7 --> P8[PR 8 Déploiement]
PR 6 dépend du moteur et de la Table, pas intrinsèquement du Randomizer. L’ordre conseillé reste séquentiel pour limiter l’intégration. La chaîne applicative principale devient : éditeur → version enregistrée → instance Table ; générateur → construction neuve → même service d’ajout Table ; instance → moteur de jet → snapshot historique.
3. Roadmap PR par PR
PR 1 — Socle Django, authentification et relations de données
    1. Objectif : disposer d’une application démarrable, privée, avec un schéma cohérent et des tests exécutés sur GitHub.
    2. Fonctionnalités : documentation de référence ; configuration de développement et dépendances fixées ; connexion/déconnexion, création privée de comptes par les outils Django ; accueil Table vide ; modèles et migrations initiales ; CI. Pas de CRUD métier à construire pour chaque modèle.
    3. Modèles/services : tous les concepts de la matérialisation ci-dessus ; services minimaux d’accès et contrôles d’intégrité. Les relations sont réelles, les parcours futurs ne sont pas simulés.
    4. Dépendances : aucune PR précédente. Le repository cible sera nécessaire au passage à l’action, pas pour valider ce plan.
    5. Tests minimum : migrations sur base vide ; connexion/déconnexion ; deux comptes isolés ; relations entre propriétaires refusées ; suppression de références protégée ; unicités et propriétaires exclusifs. Données de test minimales, pas import complet du LdR.
    6. Acceptation CDC : AC-053/054/055/057, AC-058/059/060 pour leurs protections structurelles ; version standard unique de AC-003. Les scénarios UI complets de suppression/dossiers seront terminés dans les PR concernées.
    7. RC : aucun RC fonctionnel ne bloque ce socle. RC-10 ne doit pas être arbitré implicitement : ne pas figer un langage complet d’effets ni ses écrans ; réserver ses compléments typés à PR 2. RC-07 ne bloque pas une relation parent/enfant, mais empêche d’inventer la suppression récursive.
    8. Hors périmètre : moteur TMP, données natives complètes, éditeur, génération, chargement de rencontre, jets, design final et hébergement.
PR 2 — Référentiel structuré et moteur de règles Python
    1. Objectif : rendre les règles déterministes fiables avant de construire leurs parcours utilisateur.
    2. Fonctionnalités : traduire et charger les natifs approuvés ; initialisation répétable sans écraser les personnalisations ; règles de création/progression, seuils, PV/Armure/Réactions/slots, Perks, éligibilités, équipement, overrides ; calcul pur d’un jet, critiques, Delta et Fulgurance. Le Randomizer sera ajouté en PR 5.
    3. Modèles/services : EquipmentDefinition et relations typées, TechniqueSpecialization ; chargement du référentiel ; module Python de règles ; adaptateur de lecture des définitions actives. Aucune formule dans les modèles/vues.
    4. Dépendances : PR 1 pour la persistance et les propriétaires ; calculs purs testables sans base.
    5. Tests minimum : valeurs N1 et contre-exemple9/9/9/9 ; budgets N1–N10 ; bornes11/12,15/16,17/18 ; choix18 indépendant de l’arme ; minimum FOR ; effets d’accessoires ; overrides ; ADV/DES, priorité20/critique, Delta avec modificateur, Fulgurance ; import natif idempotent et isolation de ses modifications.
    6. Acceptation CDC : partie moteur d’AC-001–012, AC-024/033/040–049 ; les interfaces seront vérifiées ensuite. Contrôler aussi l’inventaire natif : 19 armes, 8 accessoires, 12 implants, 11 gadgets et capacités/spécialisations prévues.
    7. RC : RC-02 et volet calcul de RC-03 avant les fonctions de jet concernées ; RC-10, champs/effets structurés, avant leur matérialisation finale et leur interprétation. Ce sont des décisions à enregistrer avant d’écrire les tests attendus, pas des valeurs à choisir par le développeur. RC-09 n’impose pas encore de poids ou pools de production.
    8. Hors périmètre : écrans métier complets, tirage de personnages, historique UI, simulation de combat, lecture runtime du LdR, calibration et déploiement.
PR 3 — Catalogue, éditeur standard et Bestiaire
    1. Objectif : permettre au MJ de construire et conserver ses premiers personnages avec une interface fonctionnelle simple.
    2. Fonctionnalités : édition/restauration des natifs, personnalisés et permissions/raretés ; éditeur standard avec budget, recalcul, choix, warnings et overrides ; recommandations ; Bestiaire, dossiers, recherche/filtres ; suppression protégée avec usages visibles. Rafraîchissement dynamique sobre, sans attendre la PR UX.
    3. Modèles/services : CatalogueEntry/definitions/effets ; CharacterProfile/Version, Assignment, AbilityException, Override, Folder ; services d’édition et restauration utilisant le moteur.
    4. Dépendances : PR 1+2.
    5. Tests minimum : parcours créer/éditer/recharger un standard ; sauvegarde non conforme autorisée ; Perk18 et spécialisation ; deux armes identiques indépendantes ; override persistante ; restauration confirmée ; compte B isolé ; déplacements de dossier et usages bloquant suppression.
    6. Acceptation CDC : AC-001–012 côté manuel, AC-016–020 côté catalogue/profils, AC-054/058/059/060. La portée Table/historique d’AC-018 sera complétée en PR 4/6.
    7. RC : RC-06 pour baisse de seuil, RC-07 pour dossiers/restauration/masquage, RC-10 pour dominante ex æquo et champs exposés, avant les actions correspondantes. Pas d’obligation de régler ici l’édition de niveaux évolutifs, les filtres de rencontre ou la calibration.
    8. Hors périmètre : mode Évolution complet, Randomizer, gestion Table/rencontres, Dice Roller utilisateur, identité visuelle finale.
PR 4 — Scénarios, rencontres et Table de jeu
    1. Objectif : obtenir un outil de préparation et de suivi de combat utilisable avec des personnages créés manuellement.
    2. Fonctionnalités : dossiers Scénarios, compositions par versions/quantités/camps ; chargement et ajout multiple ; instances indépendantes ; PV/Armure, édition locale, overrides ; source mise à jour volontairement ; retrait/nettoyage ; ordre persistant et Drag & Drop fonctionnel. La Table est l’accueil.
    3. Modèles/services : Encounter/Entry, GameTable/Instance, affectations/overrides locales ; services de copie, chargement, PV, sauvegarde vers Bestiaire, ordre et nettoyage. Les références catalogue restent vivantes.
    4. Dépendances : PR 3 pour les profils ; PR 2 pour les calculs ; aucune dépendance au Randomizer.
    5. Tests minimum : chargement utilise version actuelle ; cinq instances indépendantes ; conservation des références catalogue ; PV et overrides ; chargement sur Table occupée selon RC ; ordre/camp après reconnexion ; confirmation/remontée source ; isolation des nettoyages.
    6. Acceptation CDC : AC-018 pour instances, AC-031–039, AC-056/057 et intégrité des relations. L’historique n’existant pas encore en interface, son indépendance sera testée bout en bout en PR 6.
    7. RC : RC-01, RC-04, RC-05, avant les services concernés ; RC-03 volet Armure/Fulgurance avant tout traitement de dégâts multi-frappes ; RC-10 filtres supplémentaires des rencontres. RC-07 déjà tranché en PR 3 pour la politique commune de dossiers.
    8. Hors périmètre : génération, jets intégrés, suivi des tours/Réactions/états, synchronisation des constructions avec le Bestiaire, habillage final.
PR 5 — Mode Évolution et Randomizer complet
    1. Objectif : accélérer la préparation avec versions progressives et génération de lots directement utilisables sur la Table existante.
    2. Fonctionnalités : N1→N10 séquentiel, reprise et niveaux validés utilisables ; filtrage/choix de version ; pipeline Mob/Élite, pools, slots, arme minimale/repli, doublons, Armure ; prévisualisation, reroll conservant type/niveau/orientation, édition puis validation ; sauvegarde explicite au Bestiaire ; calibration documentée.
    3. Modèles/services : CharacterVersion et services de progression ; module pur Randomizer avec hasard injectable ; réglages typés ; prévisualisation puis réutilisation des services Table de PR 4. Pas de copie du code de l’éditeur.
    4. Dépendances : PR 2–4. La validation du lot dispose déjà d’une destination fonctionnelle, avec politique de PV et de sauvegarde connue.
    5. Tests minimum : absence de saut et conservation des anciennes versions ; N1–N6 utilisables ; invariants de génération sur plusieurs niveaux/configurations ; toutes orientations si quantité≥4 ; Élites au maximum ; pools vides/repli ; doublons ; reroll ciblé ; aucune insertion automatique au Bestiaire ; distributions testées sans exiger des fréquences exactes sur petit lot.
    6. Acceptation CDC : AC-009 côté génération, AC-013–015, AC-021–030. Test de lot complet : générer huit N4–N6 dont deux Élites, reroll une fiche, valider, sauvegarder un seul profil.
    7. RC : RC-06 volet anciennes versions avant édition évolutive ; RC-08 avant pipeline concerné ; RC-09 pendant cette PR, avant recette/fusion ; RC-10 Perks personnalisés sélectionnables avant leur tirage. Les probabilités peuvent être calibrées ici comme autorisé ; les décisions fonctionnelles ambiguës restent au MJ. RC-01/05 sont déjà tranchés pour les services réutilisés.
    8. Hors périmètre : équilibrage mathématique de rencontre, tirage depuis Bestiaire, économie/loot, optimisation de builds, rétropropagation, effets de combat automatiques.
PR 6 — Dice Roller utilisateur et historique durable
    1. Objectif : terminer la V1 fonctionnelle par les jets depuis les fiches et leur journal fiable.
    2. Fonctionnalités : jets de caractéristiques/armes, bonus/malus, ADV/DES, contributions automatiques et contexte utile, Critique/Delta/dégâts/Fulgurance ; résultats lisibles ; snapshots du contexte ; journal global au compte, persistant, nettoyage confirmé indépendant.
    3. Modèles/services : RollHistoryEntry/Die/Contribution ; service préparant les valeurs effectives puis enregistrant le résultat du moteur PR 2 ; endpoints internes simples et templates de la Table.
    4. Dépendances : PR 2+4 ; PR 5 recommandée auparavant pour tester de vrais profils variés, mais non indispensable au calcul.
    5. Tests minimum : transmission correcte des effets/overrides et du contexte ; dés injectés ; un seul jet Fulgurance ; historique inchangé après renommage/stat/arme/suppression d’instance ; nettoyage isolé ; aucun accès intercompte ; enregistrement complet du jet sans résultat partiellement sauvegardé.
    6. Acceptation CDC : AC-040–052 bout en bout, AC-018 pour l’historique, AC-053/054/056/057 sur les nouveaux endpoints.
    7. RC : RC-02/03 doivent avoir été décidés en amont pour le moteur et l’Armure ; RC-10, contrôles contextuels exacts, avant construction du formulaire de jet. Si l’intégration expose une décision restée ouverte, elle est tranchée avant son comportement, pas reportée en PR UX.
    8. Hors périmètre : moteur de combat, sélection automatique des cibles, états/portées/couvertures interprétés, Overdrive, drone, survie, API publique.
PR 7 — Grosse passe UX, habillage et responsive
    1. Objectif : rendre l’ensemble agréable et rapide en partie, sur une V1 déjà fonctionnelle et testée.
    2. Fonctionnalités : cohérence visuelle ; fiches compactes, hiérarchie des informations, hover/clic ; formulaires et prévisualisation plus rapides ; responsive ; Drag & Drop et alternatives utilisables au tactile/clavier ; erreurs et confirmations lisibles ; recommandations Fulgurance.
    3. Modèles/services : templates, styles et JavaScript d’interaction principalement. Pas de refonte du modèle ni de déplacement des calculs vers le navigateur.
    4. Dépendances : PR 5+6.
    5. Tests minimum : quelques parcours navigateur représentatifs : créer/générer→Table→jet→PV ; recharger une évolution ; catalogue/override ; mobile et clavier ; gestes de retrait séparés des actions fréquentes. Réexécuter la suite métier existante.
    6. Acceptation CDC : sections1,7,9,12,13 ; AC-012/027/030/036–039/044/049/052 ; revue complète de couverture AC-001–060. La cible « un ou deux clics » reste un objectif UX, pas une restriction artificielle universelle.
    7. RC : aucun RC fonctionnel nouveau attendu. Tous les volets nécessaires à la V1 doivent être clos dans leurs PR propriétaires. Les choix visuels ordinaires ne deviennent pas des arbitrages mécaniques.
    8. Hors périmètre : nouvelles règles, nouvelles familles de fonctionnalités, partage multijoueur, refactor massif, optimisation prématurée.
PR 8 — Déploiement et vérification sur plusieurs appareils
    1. Objectif : publier la V1 privée sur l’hébergement choisi à ce moment seulement.
    2. Fonctionnalités : choix fournisseur selon contraintes du CDC ; configuration production, secrets externes au dépôt, HTTPS, fichiers statiques, base persistante, migrations et chargement contrôlé ; création privée des comptes ; procédure simple de sauvegarde/restauration et de mise à jour.
    3. Modèles/services : configuration et fichiers de déploiement ; commandes d’exploitation documentées. Pas de changement du domaine pour satisfaire un fournisseur évitable.
    4. Dépendances : PR 7. Cette PR peut être différée si la publication n’est pas encore souhaitée.
    5. Tests minimum : installation sur environnement vide ; vérifications de configuration production ; reconnexion depuis deux navigateurs/appareils ; données conservées après redémarrage ; deux comptes isolés ; sauvegarde restaurable ; chargement natif n’écrasant pas les personnalisations.
    6. Acceptation CDC : sections15,16,19 ; AC-053–057 sur l’environnement cible, plus parcours Table/jet/historique complet.
    7. RC : aucun arbitrage mécanique à déplacer ici ; vérifier que les volets RC nécessaires sont clos. Le choix d’hébergement est un choix différé explicite, pas un RC bloquant les PR précédentes.
    8. Hors périmètre : plateforme publique, inscription ouverte, architecture distribuée, montée en charge speculative, nouveaux usages métier.
4. Correspondance RC → PR et dernier moment pour décider
Les identifiants du CDC sont RC-01 à RC-10 ; ils sont conservés tels quels. Un RC regroupant plusieurs sujets est traité par volet, sans créer dix sous-PR. Les réponses fonctionnelles viennent du MJ ; la calibration explicitement autorisée peut être menée par essais documentés.
RC du CDC	PR concernées	Dernier moment raisonnable
RC-01 PV initiaux et variation PVmax	PR 4 ; réutilisé PR 5	Avant le service de création d’instance et la gestion de variation PVmax, y compris suite à édition catalogue.
RC-02 Delta limite, palier temporaire, override non calculable	PR 2 ; intégration PR 6	Avant les fonctions de calcul et leurs résultats de tests. Ne pas laisser PR 6 découvrir une convention implicite.
RC-03 Fulgurance/Armure et tirs successifs	PR 2, PR 4 ; integration PR 6	Désavantage de tirs successifs avant résolution pure en PR 2 ; Armure avant traitement multi-frappes en PR 4.
RC-04 Table occupée et ordre préparatoire	PR 4	Avant le service de chargement et son interface.
RC-05 Remontée source et rattachement après sauvegarde	PR 4 ; réutilisé PR 5	Avant le service commun Table→Bestiaire ; le Randomizer réutilise cette décision.
RC-06 Baisse de seuil, anciennes versions, changement de niveau	PR 3 puis PR 5	Baisse de seuil avant sauvegarde d’une édition PR 3 ; révision des versions avant éditeur évolutif PR 5.
RC-07 Dossier non vide, masquage, restauration de pools	PR 3 ; réutilisé PR 4	Avant d’exposer ces opérations ; la PR 1 peut créer les relations sans les implémenter.
RC-08 Priorités Élite, slots additionnels, pool vide, effets sur génération	PR 5	Avant les branches correspondantes du pipeline, pas après une première génération annoncée légale.
RC-09 Pools initiaux et calibration	PR 5 ; données préparables PR 2	Avant recette du générateur/fusion PR 5. Aucune calibration inventée pour faire passer PR 2 ; Armure déjà fixée inchangée.
RC-10 Effets structurés, égalités affichées, filtres, Perks custom, contrôles	PR 2/3/4/5/6	Effets avant modèle détaillé/moteur PR 2 ; affichage/édition PR 3 ; filtres rencontre PR 4 ; Perks custom PR 5 ; contrôles de jet PR 6.

Règle pratique : ouvrir la PR avec la liste de ses volets RC connus. Les trancher et les intégrer à sa documentation avant le code dépendant ; les travaux indépendants peuvent avancer. Aucun choix silencieux, aucun report en UX d’une ambiguïté mécanique, aucun blocage global par un RC sans rapport avec la PR.
5. Ordre recommandé de développement
PR 1 → PR 2 → PR 3 → PR 4 → PR 5 → PR 6 → PR 7 → PR 8.
    • Après PR 3 : personnages standards créables et réutilisables.
    • Après PR 4 : préparation de rencontres et gestion manuelle sur Table utilisables.
    • Après PR 6 : V1 fonctionnelle complète, avant habillage final.
    • Après PR 7 : V1 confortable ; PR 8 la rend accessible sur l’hébergement retenu.
Chaque PR se fusionne avec ses tests propres et ceux des dépendances. La PR 7 ne sert pas à rendre utilisables pour la première fois des écrans absents ou à découvrir la mécanique.
6. Risques techniques principaux
Risque	Mesure ciblée
Catalogue vivant contaminant un autre compte ou réécrivant le passé	Entrées privées stables, référence native protégée, copie locale à l’édition ; tests à deux comptes et snapshots historiques.
Confusion entre construction copiée et définition vivante	Un service explicite de copie des valeurs/affectations/overrides, conservant les identités de catalogue ; pas de copie profonde de définitions.
Forçage MJ bloqué par le schéma	Contraintes dures pour intégrité et sécurité ; warnings pour règles TMP forçables.
Catalogue personnalisé devenant un moteur universel	Effets typés et bornés, RC-10 traité tôt ; descriptions restantes manuelles.
Générateur bloqué par pool vide ou dépendances de slots	RC-08 avant développement, hasard injectable, tests de configuration impossible et invariants ; pas de boucle de retries sans fin.
Écritures partielles ou écrasements de PV entre appareils	Transactions pour chargement/jet/copie, mises à jour ciblées des PV et de l’ordre ; éviter de sauvegarder toute une fiche pour changer un seul champ. Pas de collaboration temps réel ajoutée.
PR 1 devenant un chantier exhaustif de tous les comportements	Préparer relations et contraintes certaines ; compléter quelques champs par migrations additives après décision, sans UI ni moteur spéculatifs.

7. Première PR à ouvrir
Titre proposé : « Initialiser Django, l’accès privé et les relations du domaine TMP ».
Livraison attendue : documentation CDC/LdR original/LdR Markdown dans le repository ; projet démarrable selon son README ; User configuré dès la première migration ; connexion/déconnexion ; accueil Table vide ; modèles et relations décrits ici ; migrations sur base vierge ; tests d’intégrité et d’isolation à deux comptes ; CI GitHub au vert.
La revue doit pouvoir constater qu’un standard possède sa version unique, qu’une rencontre peut référencer une version, qu’une instance peut avoir ses données locales et une source facultative, qu’un équipement est référencé par identité privée et qu’un ancien jet peut être conservé sans FK vivante obligatoire. Ces vérifications se font avec de petites données de test, pas en développant les écrans des PR suivantes.
La PR 1 ne contient aucun choix sur les RC de calcul, chargement, génération ou suppression récursive. Elle ne charge pas le livre à runtime et ne prépare aucun fournisseur d’hébergement.
Oui, la roadmap est suffisamment définie pour commencer immédiatement la PR 1. Aucun arbitrage MJ supplémentaire n’est nécessaire pour son périmètre. Le repository cible devra simplement être identifié au lancement effectif du développement.
