# -*- coding: utf-8 -*-
"""
Created on Thu Apr  8 08:45:13 2021
@author: Sarah Gauthier et Michel Allard
sarah.gauthier.1@ulaval.ca
Centre d'études nordiques, Université Laval

Module pour établir la connexion entre le serveur FTP-CEN pour la récupération 
des données journalières. 

Accès permanent au serveur FTP-CEN avec un compte de service créé par ValériaScience
au nom du Centre d'études nordiques.

# =============================================================================
#  CE MODULE EST EN DÉVELOPPEMENT ET DOIT ÊTRE ADAPTÉ EN FONCTION DE LA STATION 
#  DE SUIVI (CLIMATIQUE, THERMIQUE, ETC.) DONT LES DONNÉES DOIVENT ÊTRE 
#  RÉCUPÉRÉES ET AUSSI DU TYPE DE DONNÉES À TRAITER. 
# =============================================================================

"""

import paramiko

def recuperer_fichier(path, localpath):
    """
    Connexion à distance au serveur FTP-CEN de ValeriaScience.
    
    Attention : Pour que la connexion fonctionne, le poste doit être branché directement
    sur le réseau de l'Université Laval, ou à distance avec le VPN.
    """

    host = input('Host : ')                   # Serveur hôte 
    port = 22                                 # port par défaut du protocole SFTP
    
    transport = paramiko.Transport((host, port))
    
    username = input('ID : ')                 # Identifiant au serveur FTP-CEN
    password = input('Mot de passe : ')     
    
    
    try: 
        # Établissement de la connexion au serveur FTP-CEN
        print('Connexion au serveur FTP-CEN et téléchargement des données...')
        
        transport.connect(username = username, password = password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        
           
        sftp.get(path, localpath)
    
        print(f'Données téléchargées et disponibles dans le fichier : {localpath}...', end = '\n\n')
    
        # Fermeture de la connexion
        sftp.close()
        transport.close()
        
    # Gestion des erreurs possibles
    except ConnectionError:  
        print('Impossible de se connecter au serveur ftp. Vérifiez votre connexion au réseau VPN.')

    except NameError:
        print('Nom du fichier incorrect.Entrez un autre nom en argument ou vérifiez le répertoire.')
        
    except FileNotFoundError:
        print('Fichier introuvable. Essayez un autre nom ou vérifiez dans le répertoire.')
        
    except OSError:
        print('Fichier introuvable. Essayez un autre nom ou vérifiez dans le répertoire.')

if __name__ == '__main__':
    
    chemin_serveur = 'GN.csv'
    chemin_local = 'Data_CSV/Station_Data/GN/GN_daily1.csv'
    
    recuperer_fichier(chemin_serveur, chemin_local)
