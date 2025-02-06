# Hackathon GenAI for Public Good 🤖

## urbAIn, l'assistant des agents municipaux pour l'instruction des demandes de permis de construire

#### 🛠 Track 2 : Cas d'Usage à Fort Impact avec des APIs
Exploitez des APIs comme **Albert** pour concevoir des outils concrets pour l'administration publique.

### 📝 Informations à renseigner pour l’évaluation

##### Pertinence
Les Plans Locaux d’Urbanisme sont touffus, un mixte de cartes et de réglements. À ces documents s'ajoutent les Servitudes d'Utilité Publique, les risques géonaturels, les réserves Natura 2000... Les agents publics doivent vérifier la concordance des demandes des usagers avec la réglementation **dans un temps limité**. Notre outil permet aux agents d'accéder plus rapidement aux données pertinentes pour respecter au mieux les délais **et** la réglementation.

##### Impact
Les résultats attendus sont un gain d'efficacité dans le traitement des demandes de permis de construire. Cela est mesurable en vérifiant l'évolution des délais de réponse lors de la soumission de demandes de permis de construire.

##### Faisabilité
Les APIs sur lesquelles se base le MVP sont ouvertes, il est également possible à l'avenir de les utiliser de manière plus poussée pour récupérer des informations plus précises (notamment l'API du Géoportail de l'urbanisme).

##### Scalabitilité
La solution est adaptable à chaque municipalité qui pourra charger ses propres documents dans le corpus d'*urbAIn*. Les APIs utilisées sont ouvertes et les fonctions facilement réutilisables avec notamment la mise en place d'un interface en ligne de commande.

---

### Principe d'urbAIn

urbAIn est un agent conversationnel à destination des agents municipaux pour les assister dans l'instruction des demandes de permis de construire. L'ensemble des documents règlementaires associés à la demande (via sa localisation) (PLU, SCOT, servitudes, risques...) sont chargés dans le corpus afin d'informer les réponses du modèle. Le but est de pointer vers les informations pertinentes par rapport à la demande de permis pour fluidifier la vérification du respect de la règlementation.

### Étapes de fonctionnement

Après avoir extrait une adresse ou une parcelle via la demande de permis, nos scripts convertissent cette information en localistation géographique via les APIs de l'IGN, puis interrogent les API du Géoportail de l'urbanisme (mis en oeuvre par l'IGN) et Géorisques (mise en oeuvre par le BRGM) pour récupérer les informations et documents relatifs à la demande.

Cet ensemble de documents est chargé en tant que corpus via l'API Albert, ce qui permettra à l'agent municipal d'obtenir des réponses pertinentes via l'agent conversationnelExploitez des APIs comme Albert pour concevoir des outils concrets pour l'administration publique..

L'agent municipal pourra ensuite charger dans urbAIn la demande de permis de construire, et demander à urbAIn des références vers le corpus par rapport à la demande.
