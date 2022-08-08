
@author: Sarah Gauthier, Candidate au doctorat en sciences g�ographiques
D�partement de g�ographie, Qu�bec, Canada 
Centre d'�tudes nordiques, Universit� Laval
sarah.gauthier.1@ulaval.ca 

Chercheurs responsables : Michel Allard, PhD
Professeur �m�rite, Facult� de foresterie, g�ographie et g�omatique. D�partement de g�ographie, Qu�bec, Canada
Centre d'�tudes nordiques, Universit� Laval

Pour suivre le niveau de risque de glissements de terrain � Salluit: 
FR : https://bit.ly/Suivi-risque-glissement-de-terrain_Plateforme-Salluit 
EN : https://bit.ly/Landslide-Risk-Monitoring_Salluit-Platform 

Pour plus de d�tails, consulter la documentation de chaque module
https://bit.ly/GitHub_Landslide_Monitoring_Program 


=========================================================================
Description sommaire du programme
=========================================================================

Ce programme a pour objectif d'effectuer le suivi du niveau de risque de d�crochement de couche active dans le village de Salluit par l'ex�cution des diff�rentes t�ches automatis�es suivante : 

-	R�cup�ration des donn�es valid�es de temp�rature de l'air de station SILA � Salluit sur le site Web du MELCC;
-	Calcule des moyennes, variables et indices climatiques quotidiens divers; 
-	�valuation du niveau de risque de glissement de terrain en fonction d'un seuil climatique pr�d�termin�;
-	Publie le niveau de risque et les donn�es dans un tableau de bord disponible publiquement en ligne, chaque jour;
-	Envoi d'un signal de pr�alerte et d'alerte � une liste de contact d�termin� avec les d�cideurs publics locaux et r�gionaux lorsque le niveau de risque atteint diff�rents seuils critiques.

Localisation de la station SILA : Salluit, Nunavik. 62.1918   75.6379

Site Web du MELCC : https://www.environnement.gouv.qc.ca/climat/donnees/sommaire.asp 

=========================================================================
Modules � installer (Dependencies)
=========================================================================

L'automatisation du processus d'acquisition des donn�es jusqu'� la transmission et leur publication sur le Web a �t� rendue possible par le d�veloppement d�un programme source r�dig� dans le langage de programmation Python (version 3.8.5). Le programme a �t� d�velopp� avec l'��environnement de programmation Anaconda 3 et le logiciel Spyder 4.2.5. 

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
Principal.py est le programme principal qui fait appel aux autres modules pour r�cup�rer, valider, traiter et publier les donn�es en ligne. Le programme principal.py est programm� pour fonctionner chaque jour, � 15h, sur un poste s�curis� du Centre d'���tudes nordiques. Voici les modules utilis�s dans principal.py dans l'ordre pour l'ex�cution du programme : 

-	donnees_sila.py
-	indices_climatiques_quotidiens.py
-	couches_web.py
-	calcul_risque_glissement.py
-	signal_risque_glissement.py

Pour le flux de travail d�taill� et l'appel des modules par le programme principal.py,
consulter le fichier work_flow.png accessible � partir du m�me r�pertoire. 

===========================================================================
Modules disponibles
===========================================================================

Principal.py	
    Programme principal ex�cut� qui appelle les modules pour r�cup�rer, 
    nettoyer, traiter, analyser et publier les donn�es en ligne, puis estimer 
    le niveau de risque de glissement de terrain pour l'envoi du signal d'alerte au besoin. 

Donnees_sila.py
    Classe DonneesSila :	R�cup�re les donn�es de la station SILA sur le site Web du MELCC 
    et met en forme le tableau avec les nouvelles donn�es.

Connexion_serveur_ftpcen.py
    �tablir la connexion s�curis�e au serveur � distance FTP avec le protocole SFTP 
    et pour r�cup�rer les donn�es brutes de temp�rature du sol.
    *Le service FTP-CEN n'est plus disponible depuis le printemps 2022	

Donnees_pergelisol.py
    Classe DonneesPergelisol : Mettre en forme le tableau avec les nouvelles donn�es 
    et calcule les moyennes quotidiennes � partir des donn�es horaires. 
    Ce module n'est actuellement pas utilis� dans le programme principal.py
    
Validation_donnees.py
    Classe ValidationDonnees :	Nettoyage et validations des donn�es climatiques et 
    thermiques selon diff�rents crit�res de validation du Centre d'�tudes nordiques. 
    Conversion en degr�s Celsius des donn�es thermiques des c�bles GN et GS. 

Indices_cilmatiques.py
    Classe IndicesClimatiques : D�termine les dates de d�but et de fin des saisons de gel 
    et de d�gel et calcul des indices climatiques.
    
Couches_web.py
    Classe CoucheWeb : Connexion au compte ArcGIS Online du CEN et mise � jour des donn�es
    Web avec les nouvelles donn�es r�cup�r�es.
    
Signal_risque_glissement.py
    Classe AlerteRisqueCourriel : Production de deux rapports PDF quotidiens, 
    �valuation du niveau de risque d'occurrence de d�crochement de couche active 
    quotidien et envoi du signal d'alerte. 

========================================================================
Crit�res principaux du module validation_donnees.py
========================================================================

1.	Recherche des donn�es manquantes.
2.	Recherche des erreurs de conversion des r�sistances / voltages.
3.	Recherche des donn�es > ou < au maximum et minimum autoris� de (respectivement 45�C et   45�C).
4.	Recherche de dates + heures qui se r�p�tent
5.	V�rification format de date (AAAA-MM-JJ   HH : MM : SS)
6.	Recherche des donn�es qui sont ant�rieures � celles d�j� dans la BD
7.	Recherche de dates + heures qui sont plus r�centes que la date actuelle
8.	Recherches des donn�es o� l'amplitude journali�re est sup�rieure ou inf�rieure � l'amplitude autoris�e entre deux profondeurs.

*La validation des donn�es repose sur des crit�res �labor�s en fonction des donn�es historiques de la station, et selon les crit�res utilis�s par le Centre d'�tudes nordiques dans la base de donn�es SILA. 


Pour plus de d�tails, consulter la documentation de chaque module
https://bit.ly/GitHub_Landslide_Monitoring_Program 
