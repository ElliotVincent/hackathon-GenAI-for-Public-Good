# Scripts de récupération des données

Collection de fonctions utilisant les API Géoportail de l'Urbanisme (https://www.geoportail-urbanisme.gouv.fr/api/#/) et Géorisques (https://www.georisques.gouv.fr/doc-api#/Risques/rechercheRisques_4) pour télécharger les fichiers d'urbanisme correspondant à une adresse et les fusionner en un seul fichier JSON.

## Utilisation

```sh
python main.py "<adresse>"
```

Par exemple :
```sh
python main.py "1 Rue de l’Adrech, 48130 Peyre en Aubrac"
```
