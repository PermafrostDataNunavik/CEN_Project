Created on Fri Feb 19 07:57:17 2021

@author: 
Sarah Gauthier, PhD Candidate
sarah.gauthier.1@ulaval.ca
Centre d'études nordiques, Université Laval, Québec, Qc, Canada.

Michel Allard, PhD
Professeur émérite
Faculté de foresterie, géographie et géomatique - Département de géographie
michel.allard.3@ulaval.ca
Centre d’études nordiques, Université Laval, Québec, Qc, Canada.

Localisation de la station GN :     Salluit, Nunavik.   62,19582     -75,64170
Localisation de la station GS :     Salluit, Nunavik.   62,193723    -75.637789
Localisation de la station SILA :   Salluit, Nunavik.   62.1918      -75.6379

# ================================================================================ #
                                 Automatisation
# ================================================================================ #

*IMPORTANT* Pour que ce script fonctionne, le poste de travail utilisé doit 
être connecté au réseau de l'Université Laval et être ouvert d'exécution du script.

Le programme principal.py est programmé pour fonctionner chaque jour, à 15h.

PLANIFICATEUR DE TÂCHES

Le programme s'exécute automatiquement avec un fichier de commande .bat (batch file)
avec le planificateur de tâches Windows. Pour être fonctionnelle, 
la tâche doit être programmée sur la session administrateur du poste UL. 

Paramètre important : « Exécuter même si l'utilisateur n'est pas connecté. »

Le programme s'exécute à partir du bureau de la session administrateur et est disponible
sur la session pergelisolallard@ffgg.ulaval.ca


# ================================================================================ #
                                 Packages nécessaires (Dependencies)
# ================================================================================ #

Le programme fonctionne avec Python 3.8.5 -> https://www.python.org/downloads/release/python-385/
___________________________________________________________________________________

Installer les packages avec conda : 
conda install -c anaconda paramiko
conda install -c anaconda pandas
conda install -c anaconda scipy

conda install -c esri arcgis

conda install -c conda-forge dataframe_image
conda install -c conda-forge fpdf
conda install -c conda-forge yagmail
___________________________________________________________________________________

Installer les packages avec pip : 
pip install paramiko
pip install pandas
pip install scipy

pip install arcgis

pip install dataframe-image
pip install fpdf
pip install yagmailimport pand


 ==============================================================================
                            Description des modules
 ==============================================================================

##### Pour plus de détails sur les classes et méthode de chaque module, consulter leurs documentations. 

    - principal.py
            Programme qui fait appel aux autres modules pour récupérer, valider, traiter, calculer
            le niveau de risque de glissement de terrain et publier les données en ligne publiquement (envoi d'un
            signal d'alerte au besoin).

Modules utilisés dans principal.py dans l'ordre pour l'exécution du programme : 
____________________________________________________________________________________

    - connexion_serveur_ftpcen.py
            Module pour établir la connexion entre le serveur FTP-CEN pour la récupération 
            des données journalières de températures du sol. 
                   
    - donnees_sila.py
            Récupération des données de température de l'air de la station SILA à Salluit
            à partir du site web du MELCC. Ces données ont déjà été validées.       
            
    - donnees_pergelisol.py
            Lecture, validation et traitement des données de températures du sol. 

    - validation_donnees.py
            Méthodes pour la validation des données brutes pour une station 
            de suivi climatique ou de suivi thermique du pergélisol. Les différents critères 
            de validation sont basés sur ceux de la base de données SILA. 
            
    - indices_climatiques_quotidiens.py
            Module pour déterminer les dates de début et fin des saisons de gel et de dégel 
            pour calculer les indices climatiques et le niveau de risque de glissement de terrain
            en fonction des années climatiques.

    - couches_web.py
            Module pour créer une couche géospatiale à partir d'un tableau de données (DataFrame) 
            pour les stations SILA, GN et GS pour publier sur ArcGIS Online dans le Dashboard 
            pour le suivi quotidien du niveau de risque de glissement de terrain. 
            
    - calcul_risque_glissement.py
            Estimation du niveau de risque de glissement de terrain de type décrochement de 
            couche active dans les dépôts de particules fines silteux-argileux riches en glace
            du village de Salluit au Nunavik. 
            
    - signal_risque_glissement.py
            Module avec les méthodes nécessaires pour la création d'un rapport journalier avec le statut de transmission 
        des stations (active ou inactive) et pour l'envoi du signal d'alerte au besoin 
        à la personne contact choisi. 
   

#==============================================================================
                            Information pertinente
#==============================================================================

-------- Stations de suivi thermique équipées d'un datalogger CR1000 --------
    
Titre des colonnes par défaut avec le programme de base des CR1000 :
        
        'Date', 'Record', 'Vbatt_Min', 'Temp_Celsius_CR1000',  
        'thermistor(1)', 'thermistor(2)', 'thermistor(3)', 'thermistor(4)', 
        'thermistor(5)', 'thermistor(6)', 'thermistor(7)', 'thermistor(8)',
        'thermistor(9)', 'thermistor(10)', 'thermistor(11)', 'thermistor(12)'
        'thermistor(13)', 'thermistor(14)', 'thermistor(15)', 'thermistor(16)',
        'thermistor(17)', 'thermistor(18)', 'thermistor(19)', 'thermistor(20)',
        'thermistor(21)', 'thermistor(22)', 'thermistor(23)', 'thermistor(24)',
        'thermistor(25)', 'thermistor(26)', 'thermistor(27)', 'thermistor(28)', 
        'thermistor(29)', 'thermistor(30)', 'thermistor(31)', 'thermistor(32)', 
        'SE1Volt', 'SE2Volt'
        
Titre des colonnes de la station GN et de la station GS: 
    
         ['Date', 'Record', 'Vbatt_Min', 'Temp_Celsius_CR1000'
         '-0.02', '-0.1', '-0.2', '-0.3', '-0.4', '-0.5', '-0.6', 
         '-0.7', '-0.75', '-0.8', '-0.85', '-0.9', '-0.95', '-1.0',
         '-1.05', '-1.1', '-1.15', '-1.2', '-1.25', '-1.3', '-1.4', 
         '-1.5', '-1.7', '-2.0']


              ÉQUATION DE CONVERSION DES VALEURS EN DEGRÉS CELSIUS 
____________________________________________________________________________________

Équation de SteinhartHart pour la conversion des données de température du sol 
mesurées (voltage) en degrés Celsius à partir des constantes du manufacturier. 
Constantes sont propres aux modèles YSI 44033. 

ÉQUATION DE STEINHART-HART AVEC LA LECTURE DU VOLTAGE
    
    Variables de base des YSI 44033 (pour le calcul des constantes A, B et C): 
    
        - RTlow = 12460.0 ohms
        - RTmid = 7355.0 ohms
        - RThigh = 4482.0 ohms
         
        - Tlow = -10.0 °C
        - Tmid = 0.0 °C
        - Thigh = 10.0 °C
        
        - Voltage d'excitation = 2000 mV
        - Resistance de référence = 7500 ohms
    
    *Constantes par défaut du manufacturier des thermistances YSI 44033 :
    
        - A = 1.473349 x 1e-03  (0.001473349)
        - B = 2.37371 x 1e-04   (0.000237371)
        - C = 1.05274e-07       (0.000000105274)
     
    Aucune thermistance du CEN n’est calibrée, ces coefficients sont des 
    constantes fournies par le manufacturier.

------------------
FORMULES UTILISÉES
------------------
    
Étape 1 : convertir le voltage en résistance

    rs = resistance*((excitation/voltage)-1)
    
Étape 2 : convertir la résistance en température
    
    celsius = 1 / (A + B * LN(rs) + C * LN(rs) ** 3 ) - 273.15

____________________________________________________________________________________

        VALIDATION ET NETTOYAGE DES DONNÉES - RÉDACTION DU SCRIPT EN COURS
____________________________________________________________________________________

Les validations des données sont basées sur les critères de validation du Centre d'études nordiques. 
Ceux-ci sont également développés en fonction des données historiques de la station. 
    
 ==============================================================================
                        Serveur à distance FTP-CEN
 ==============================================================================

Module connexion_serveur_ftpcen.py

Compte de service créé par Valeria Science avec un accès au serveur pour lire et télécharger les données. 
Ce compte n'est pas lié à un IDUL et est permanent.

Hote : ftp-cen.valeria.science
Protocole SFTP - SSH File Transfert Protocole (port 22)

Pour que la connexion fonctionne, il faut être connecté au réseau de l'Université Laval : 
    - soit à distance sur le vpn.ulaval.ca avec un identifiant
    - soit en étant directement branché sur le campus. 

Pour toutes questions ou demande d'information sur les infrastructures de Valeria Science,
écrire à info@valeria.science

 ==============================================================================
                         Accès aux données en ligne 
 ==============================================================================

Dashboard Français Suivi du niveau de risque de glissement de terrain - Salluit, Nunavik (FR)
https://bit.ly/Suivi-risque-glissement-de-terrain_Plateforme-Salluit

Dashboard Anglais : Monitoring of landslide risk level in Salluit, Nunavik
https://bit.ly/Landslide-Risk-Monitoring_Salluit-Platform

GitHub : 
https://github.com/PermafrostDataNunavik/CEN_Project.git

