
@author: Sarah Gauthier, Candidate au doctorat en sciences géographiques
Département de géographie, Québec, Canada 
Centre d'études nordiques, Université Laval
sarah.gauthier.1@ulaval.ca 

Chercheurs responsables : Michel Allard, PhD
Professeur émérite, Faculté de foresterie, géographie et géomatique. Département de géographie, Québec, Canada
Centre d'études nordiques, Université Laval

Pour suivre le niveau de risque de glissements de terrain à  Salluit: 
FR : https://bit.ly/Suivi-risque-glissement-de-terrain_Plateforme-Salluit 
EN : https://bit.ly/Landslide-Risk-Monitoring_Salluit-Platform 

Pour plus de détails, consulter la documentation de chaque module
https://bit.ly/GitHub_Landslide_Monitoring_Program 


=========================================================================
Description sommaire du programme
=========================================================================

Ce programme a pour objectif d'effectuer le suivi du niveau de risque de décrochement de couche active dans le village de Salluit par l'exécution des différentes tâches automatisées suivante : 

-	Récupération des données validées de température de l'air de station SILA à  Salluit sur le site Web du MELCC;
-	Calcule des moyennes, variables et indices climatiques quotidiens divers; 
-	Évaluation du niveau de risque de glissement de terrain en fonction d'un seuil climatique prédéterminé;
-	Publie le niveau de risque et les données dans un tableau de bord disponible publiquement en ligne, chaque jour;
-	Envoi d'un signal de préalerte et d'alerte à  une liste de contact déterminé avec les décideurs publics locaux et régionaux lorsque le niveau de risque atteint différents seuils critiques.

Localisation de la station SILA : Salluit, Nunavik. 62.1918   75.6379

Site Web du MELCC : https://www.environnement.gouv.qc.ca/climat/donnees/sommaire.asp 

=========================================================================
Modules à  installer (Dependencies)
=========================================================================

L'automatisation du processus d'acquisition des données jusqu'à  la transmission et leur publication sur le Web a été rendue possible par le développement dâun programme source rédigé dans le langage de programmation Python (version 3.8.5). Le programme a été développé avec l'€™environnement de programmation Anaconda 3 et le logiciel Spyder 4.2.5. 

Python 3.8.5 -> https://www.python.org/downloads/release/python-385/ 
_________________________________________________________________________

Installer les modules avec conda : 
conda install -c anaconda paramiko
conda install -c anaconda pandas
conda install -c anaconda scipy
conda install -c anaconda numpy
conda install -c esri arcgis
conda install -c conda-forge dataframe_image
conda install -c conda-forge fpdf
conda install -c conda-forge yagmail

Installer les modules avec pip : 
pip install paramiko
pip install pandas
pip install scipy
pip install arcgis
pip install dataframe-image
pip install fpdf
pip install yagmailimport pand

=========================================================================
Programme 
=========================================================================

principal.py
Principal.py est le programme principal qui fait appel aux autres modules pour récupérer, valider, traiter et publier les données en ligne. Le programme principal.py est programmé pour fonctionner chaque jour, à  15h, sur un poste sécurisé du Centre d'€™études nordiques. Voici les modules utilisés dans principal.py dans l'ordre pour l'exécution du programme : 

-	donnees_sila.py
-	indices_climatiques_quotidiens.py
-	couches_web.py
-	calcul_risque_glissement.py
-	signal_risque_glissement.py

Pour le flux de travail détaillé et l'appel des modules par le programme principal.py,
consulter le fichier work_flow.png accessible à partir du même répertoire. 

===========================================================================
Modules disponibles
===========================================================================

Principal.py	
    Programme principal exécuté qui appelle les modules pour récupérer, 
    nettoyer, traiter, analyser et publier les données en ligne, puis estimer 
    le niveau de risque de glissement de terrain pour l'envoi du signal d'alerte au besoin. 

Donnees_sila.py
    Classe DonneesSila :	Récupère les données de la station SILA sur le site Web du MELCC 
    et met en forme le tableau avec les nouvelles données.

Connexion_serveur_ftpcen.py
    Établir la connexion sécurisée au serveur à  distance FTP avec le protocole SFTP 
    et pour récupérer les données brutes de température du sol.
    *Le service FTP-CEN n'est plus disponible depuis le printemps 2022	

Donnees_pergelisol.py
    Classe DonneesPergelisol : Mettre en forme le tableau avec les nouvelles données 
    et calcule les moyennes quotidiennes à  partir des données horaires. 
    Ce module n'est actuellement pas utilisé dans le programme principal.py
    
Validation_donnees.py
    Classe ValidationDonnees :	Nettoyage et validations des données climatiques et 
    thermiques selon différents critères de validation du Centre d'études nordiques. 
    Conversion en degrés Celsius des données thermiques des câbles GN et GS. 

Indices_cilmatiques.py
    Classe IndicesClimatiques : Détermine les dates de début et de fin des saisons de gel 
    et de dégel et calcul des indices climatiques.
    
Couches_web.py
    Classe CoucheWeb : Connexion au compte ArcGIS Online du CEN et mise à  jour des données
    Web avec les nouvelles données récupérées.
    
Signal_risque_glissement.py
    Classe AlerteRisqueCourriel : Production de deux rapports PDF quotidiens, 
    évaluation du niveau de risque d'occurrence de décrochement de couche active 
    quotidien et envoi du signal d'alerte. 

========================================================================
Critères principaux du module validation_donnees.py
========================================================================

1.	Recherche des données manquantes.
2.	Recherche des erreurs de conversion des résistances / voltages.
3.	Recherche des données > ou < au maximum et minimum autorisé de (respectivement 45°C et   45°C).
4.	Recherche de dates + heures qui se répètent
5.	Vérification format de date (AAAA-MM-JJ   HH : MM : SS)
6.	Recherche des données qui sont antérieures à  celles déjà dans la BD
7.	Recherche de dates + heures qui sont plus récentes que la date actuelle
8.	Recherches des données où l'amplitude journalière est supérieure ou inférieure à l'amplitude autorisée entre deux profondeurs.

*La validation des données repose sur des critères élaborés en fonction des données historiques de la station, et selon les critères utilisés par le Centre d'études nordiques dans la base de données SILA. 


Pour plus de détails, consulter la documentation de chaque module
https://bit.ly/GitHub_Landslide_Monitoring_Program 
