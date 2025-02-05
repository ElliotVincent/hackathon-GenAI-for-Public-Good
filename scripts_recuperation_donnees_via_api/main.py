import json
import os
import pathlib
import requests
import tqdm
import zipfile

def getPartitionsFromGenericDocUrl(url, latitude, longitude):
  """
  Récupère les partitions uniques correspondant à une position à partir d'une URL
  :param url: API sur laquelle récupérer la liste de partitions
  :param latitude: latitude de la position
  :param longitude: longitude de la position
  :returns: liste des partitions uniques correspondant à la position
  """
  resp = requests.get(url, params={"lon": longitude, "lat":latitude})
  ids = []
  for feat in json.loads(resp.content)["features"]:
    if ("partition" in feat["properties"]):
      ids.append(feat["properties"]["partition"])
  return list(set(ids))

def getDUIDsfromPosition(latitude, longitude):
  """
  Récupère les partitions uniques des PLU correspondant à une position à partir d'une URL
  :param latitude: latitude de la position
  :param longitude: longitude de la position
  :returns: liste des partitions uniques des PLU correspondant à la position
  """
  return getPartitionsFromGenericDocUrl("https://www.geoportail-urbanisme.gouv.fr/api/feature-info/du?", latitude, longitude)

def getSUPIDsfromPosition(latitude, longitude):
  """
  Récupère les partitions uniques des Servitudes d'Utilité Publique correspondant à une position à partir d'une URL
  :param latitude: latitude de la position
  :param longitude: longitude de la position
  :returns: liste des partitions uniques des Servitudes d'Utilité Publique correspondant à la position
  """
  return getPartitionsFromGenericDocUrl("https://www.geoportail-urbanisme.gouv.fr/api/feature-info/sup?", latitude, longitude)

def getSCOTIDsfromPosition(latitude, longitude):
  """
  Récupère les partitions uniques des SCOT correspondant à une position à partir d'une URL
  :param latitude: latitude de la position
  :param longitude: longitude de la position
  :returns: liste des partitions uniques des SCOT correspondant à la position
  """
  return getPartitionsFromGenericDocUrl("https://www.geoportail-urbanisme.gouv.fr/api/feature-info/scot?", latitude, longitude)

def getAllPartitionsFromPosition(latitude, longitude):
  """
  Récupère toutes les partitions uniques (PLU, Servitudes et SCOT) correspondant à une position à partir d'une URL
  :param latitude: latitude de la position
  :param longitude: longitude de la position
  :returns: liste de toutes les partitions uniques correspondant à la position
  """
  return getDUIDsfromPosition(latitude, longitude) + getSUPIDsfromPosition(latitude, longitude) + getSCOTIDsfromPosition(latitude, longitude)

def addressToLatLng(text):
  """
  Interroge l'API Géoplateforme de géocodage pour convertir une adresse en coordonnées géographiques
  :param text: adresse
  :returns: tuple correspondant à la position : latitude, longitude
  """
  resp = requests.get("https://data.geopf.fr/geocodage/completion?text=" + text + "&type=PositionOfInterest,StreetAddress&maximumResponses=1")
  return json.loads(resp.content)["results"][0]["y"], json.loads(resp.content)["results"][0]["x"]

def downloadArchiveFromPartition(partition, path):
  """
  Interroge l'API GPU pour télécharger une archive et la dézipper
  :param partition: identifiant de "partition" GPU
  :param path: chemin vers le dossier cible
  """
  response = requests.get("https://www.geoportail-urbanisme.gouv.fr/api/document/download-by-partition/" + partition, stream=True)
  # Sizes in bytes.
  total_size = int(response.headers.get("content-length", 0))
  block_size = 1024
  # TDQM : barre de chargement pour patienter
  with tqdm.tqdm(total=total_size, unit="B", unit_scale=True) as progress_bar:
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)
    with open(pathlib.Path(path, partition + ".zip"), "wb") as file:
      for data in response.iter_content(block_size):
        progress_bar.update(len(data))
        file.write(data)
  # extraction du zip
  with zipfile.ZipFile(pathlib.Path(path, partition + ".zip"), 'r') as zip_ref:
    zip_ref.extractall(pathlib.Path(path))
  # on nettoie...
  os.remove(pathlib.Path(path, partition + ".zip"))

  if total_size != 0 and progress_bar.n != total_size:
    raise RuntimeError("Could not download file")

def downloadAllArchivesFromPartitionList(partitionList, path):
  """
  Interroge l'API GPU pour télécharger les archives et les dézipper
  :param partitionList: liste d'identifiants de "partition" GPU
  :param path: chemin vers le dossier cible
  """
  for partition in partitionList:
    print("Downloading partition " + partition + "...")
    downloadArchiveFromPartition(partition, path)

def getRisquesFromAdress(text, path):
  """
  Interroge l'API Géorisques pour télécharger le pdf correspondant aux risque de l'adresse renseignée
  :param text: adresse
  :param path: chemin vers le dossier cible
  """
  print("Downloading Géorisques pdf")
  response = requests.get("https://www.georisques.gouv.fr/api/v1/rapport_pdf?adresse=" + text)
  # Sizes in bytes.
  total_size = int(response.headers.get("content-length", 0))
  block_size = 1024
  with tqdm.tqdm(total=total_size, unit="B", unit_scale=True) as progress_bar:
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)
    with open(pathlib.Path(path, "Georisques " + text + ".pdf"), "wb") as file:
      for data in response.iter_content(block_size):
        progress_bar.update(len(data))
        file.write(data)

def convert_unicode_text(text):
    """
    Convertit les caractères Unicode spéciaux du texte donné en leurs équivalents ASCII ou les supprime.    
    Args: text (str): La chaîne de caractères d'entrée contenant des caractères Unicode.
    Returns: str: Le texte nettoyé avec les caractères spéciaux remplacés par leurs équivalents ASCII.
    """
    # Dictionnaire de correspondance pour remplacer les caractères Unicode par des caractères ASCII ou un espace
    replacements = {
        rf'\u00e9': 'e',  # é -> e
        rf'\u00e0': 'a',  # à -> a
        rf'\u00e7': 'c',  # ç -> c
        rf'\u00f4': 'o',  # ô -> o
        rf'\u00fb': 'u',  # û -> u
        rf'\u00eb': 'e',  # ë -> e
        rf'\u00ea': 'e',  # ê -> e
        rf'\u00e8': 'e',  # è -> e
        rf'\u00ee': 'i',  # î -> i
        rf'\u00b0': ' ',  # ° -> espace
        rf'\n': ' ',      # Remplace les sauts de ligne par des espaces
        rf'..': '.'       # Remplace les doubles points par un seul point
    }    
    # Effectue les remplacements jusqu'à 10 fois pour s'assurer que toutes les occurrences sont traitées
    for _ in range(10):
        for unicode_char, replacement in replacements.items():
            text = text.replace(unicode_char, replacement)    
    # Supprime les caractères restants qui ne sont pas en ASCII
    return ''.join(char for char in text if ord(char) < 128)

def pdf_to_json(file_path):
    """
    Extrait le contenu d'un fichier PDF et le convertit en texte compatible avec le format JSON.    
    Args: file_path (str): Le chemin vers le fichier PDF.
    Returns: str: Le contenu textuel extrait du fichier PDF au format texte brut.
    """
    # Ouvre le fichier PDF en mode lecture binaire
    pdf_file = open(file_path, 'rb')    
    # Crée un objet PdfReader pour lire le PDF
    read_pdf = PyPDF2.PdfReader(pdf_file)
    # Récupère le nombre total de pages du PDF
    number_of_pages = len(read_pdf.pages)    
    # Initialise un dictionnaire pour stocker le texte extrait
    document = {'text': ''}    
    # Parcourt chaque page du PDF et extrait le texte
    for k in range(number_of_pages):
        page = read_pdf.pages[k]
        page_content = page.extract_text()  # Extrait le texte de la page courante        
        # Convertit le texte extrait au format JSON, puis le nettoie avec convert_unicode_text()
        data = json.dumps(page_content)
        data = convert_unicode_text(data)        
        # Ajoute le texte nettoyé au document
        document['text'] += ' ' + data    
    return document['text']

def data_to_json(root_path):
    """
    Recherche de manière récursive les fichiers PDF dans le répertoire donné et convertit leur contenu en un fichier JSON.
    Args: root_path (str): Le répertoire racine où chercher les fichiers PDF.
    Returns: None: Enregistre un fichier JSON contenant le texte converti de tous les fichiers PDF trouvés.
    """
    # Liste pour stocker les chemins des fichiers PDF trouvés
    paths_to_files_to_merge = []    
    # Parcourt le répertoire et cherche tous les fichiers PDF
    for path, _, files in os.walk(root_path):
        for name in files:
            if '.pdf' in name:
                paths_to_files_to_merge.append(os.path.join(path, name))    
    # Liste pour stocker le contenu extrait de chaque PDF
    file_to_upload = []    
    # Traite chaque fichier PDF et extrait son texte
    for path in tqdm.tqdm(paths_to_files_to_merge):
        file_to_upload.append({'title': path, 'text': pdf_to_json(path)})    
    # Enregistre le contenu extrait sous forme de fichier JSON dans le répertoire racine
    json.dump(file_to_upload, open(os.path.join(root_path, 'data.json'), "w"))
  
def main(address, path="./dist"):
  """
  Enchaînement des fonctions du script pour télécharger tous les fichiers d'urbanisme (PLU, Servitudes, SCOT)
  et la fiche Géorisques à partir d'une adresse
  :param address: adresse pour laquelle récupérer l'ensemble des documents
  :param path: chemin pointant vers un dossier qui contiendra toutes les données, par défaut crée un dossier dist par rapport au contexte d'exécution du script
  """
  allPartitions = getAllPartitionsFromPosition(*addressToLatLng(address))
  print("Partitions to dowload: " + str(allPartitions))
  downloadAllArchivesFromPartitionList(allPartitions, path)
  getRisquesFromAdress(address, path)
  data_to_json(path)

if __name__ == "__main__":
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument("address", nargs="?")
  args = parser.parse_args()
  if args.address:
    main(args.address)
  else:
    main("1 Rue de l’Adrech, 48130 Peyre en Aubrac")
