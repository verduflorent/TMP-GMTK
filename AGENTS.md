# TMP-GMTK — Instructions prioritaires du dépôt

## Sources d'autorité

Pour toute implémentation, respecter cet ordre :

1. `docs/CDC.md` — autorité sur le comportement de TMP-GMTK et les arbitrages applicatifs.
2. `docs/LdR.md` — autorité sur les données et règles de THE MOIRA PROTOCOL.
3. `docs/Roadmap.md` — autorité sur le découpage et le périmètre des PR.

Les fichiers DOCX présents dans `docs/source/` sont les documents originaux.
Les fichiers Markdown sont leurs versions de travail destinées au développement.

## Règle absolue — intégrité des données TMP

Toute donnée TMP implémentée dans le code ou injectée en base doit correspondre exactement à sa source autoritaire.

Cela concerne notamment :

- caractéristiques ;
- seuils ;
- Perks ;
- armes ;
- Puissance ;
- portée ;
- poids ;
- emplacement ;
- prérequis ;
- accessoires ;
- implants ;
- gadgets ;
- spécialisations ;
- GPB ;
- Biopuces ;
- propriétés ;
- valeurs numériques ;
- descriptions utilisées par l'application.

Ne jamais :

- inventer une valeur absente ;
- compléter une règle par intuition ;
- modifier une valeur pour équilibrer ou simplifier ;
- utiliser une ancienne valeur mémorisée ;
- remplacer silencieusement une donnée du LdR ;
- interpréter une ambiguïté comme une décision acquise.

Si `CDC.md` contient un arbitrage explicitement destiné à TMP-GMTK qui précise ou remplace le LdR, cet arbitrage prévaut pour l'application.

Sinon, `LdR.md` reste l'autorité.

## Workflow obligatoire pour les données de règles

Avant d'implémenter ou modifier une donnée TMP :

1. retrouver sa définition dans `docs/LdR.md` ;
2. vérifier si `docs/CDC.md` contient un arbitrage applicable ;
3. implémenter uniquement la valeur ainsi obtenue ;
4. ajouter ou mettre à jour le test correspondant ;
5. vérifier que la donnée structurée produite correspond à la source.

Si une contradiction ou une ambiguïté subsiste :

**STOP. Ne pas arbitrer automatiquement. Signaler le point au MJ.**

## Référentiel structuré

Le LdR n'est jamais interprété à runtime.

`LdR.md` est une source documentaire.

Les règles utilisées par l'application sont traduites explicitement en Python et/ou données structurées testables.

Le code doit permettre de retrouver facilement la correspondance entre :

`LdR/CDC → donnée structurée → règle Python → test`

## Modification du LdR

Une modification future de `LdR.md` ne doit jamais entraîner une adaptation approximative du code.

Lorsqu'une règle source change :

1. identifier les données/règles impactées ;
2. modifier leur représentation structurée ;
3. modifier les calculs concernés ;
4. mettre à jour les tests ;
5. vérifier les critères d'acceptation du CDC concernés.

## Périmètre

Ne pas profiter d'une modification pour effectuer un refactor, une optimisation ou une abstraction non nécessaire au chantier courant.

En particulier :

**la fidélité au LdR et au CDC est prioritaire sur l'élégance, la généralisation et l'optimisation du code.**
