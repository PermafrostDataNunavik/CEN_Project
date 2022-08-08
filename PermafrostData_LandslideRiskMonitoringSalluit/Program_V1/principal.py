# -*- coding: utf-8 -*-
"""
Created on Fri Aug  6 08:54:46 2021

@author: Sarah Gauthier et Michel Allard
sarah.gauthier.1@ulaval.ca
Centre d'études nordiques, Université Laval

Fichier de code principal pour les données de température de l'air
de la station SILA et de température du sol des sites GN et GS à Salluit pour : 
    - Récupérer les nouvelles données;
    - Convertir les valeurs en °C;
    - Valider les données;
    - Calculer différentes variables et moyennes; 
    - Calculer le risque de glissement de terrain;
    - Créer la couche géospatiale;
    - Mettre à jour la couche ;
    - Diffuser les résultats sur le Web.
    
Tous ces modules, nécessaires au fonctionnement du programme, sont disponibles 
dans le répertoire Data_CSV.
"""

# =============================================================================
# Modules nécessaires 
# =============================================================================
import pandas as pd 
from datetime import datetime
from colorama import Fore, Style
from donnees_sila import DonneesSila
from donnees_pergelisol import DonneesPergelisol
from indices_climatiques_quotidiens import IndicesClimatiques
from couches_web import CoucheWeb
from signal_risque_glissement import AlerteRisqueCourriel


# Chemin d'accès au programme
repertoire = input('Repertoire de travail du programme : ')

debut = datetime.now() # Pour calculer la durée d'exécution du programme

# =============================================================================
# RÉCUPÉRATION DES DONNÉES DE TEMPÉRATURE DE L'AIR QUOTIDIENNE - STATION SALLUIT SILA
# =============================================================================
print(5*'-', 'Récupération des données de la station Salluit SILA', 5*'-')

donnees = DonneesSila(repertoire)                             
donnees.donnees_sila()                      # donnees -> objet de la classe DonneesSila

# =============================================================================
# CALCUL DES INDICES CLIMATIQUES À PARTIR DES NOUVELLES DONNÉES
# =============================================================================
if not donnees.nouvelles_lignes.empty:
    print(f'Calcul des indices climatiques à partir des données de la station sila en date du {debut.date()}', 10*'-')
    
    indices = IndicesClimatiques(donnees.df_sila, repertoire)   
    indices.calcul_indices('Gel', 'Degel')  # indices -> objet de la classe IndicesClimatiques

# =============================================================================
# ESTIMATION DU NIVEAU DE RISQUE DE GLISSEMENT DE TERRAIN QUOTIDIEN ET ALERTE SI NÉCESSAIRE
# =============================================================================
destinataires = ['email@auchoix.ca'] # Liste de destinataire du signal d'alerte
alerte = AlerteRisqueCourriel(destinataires, repertoire) # Argument en entrée : à qui envoyer l'alerte
alerte.generer_rapports()
print()

# =============================================================================
# MISE À JOUR DES DONNÉES SUR LE WEB
# =============================================================================
print(5*'-', 'Mise à jour des couches Web dans ArcGIS Online', 5*'-')
web_sila = CoucheWeb('Station SILA', repertoire)
web_sila.mise_a_jour_couches()

fin = datetime.now()
print(Fore.MAGENTA + '\n\n', 'Programme terminé. Durée de l\'exécution du programme : {} secondes.'.format(fin - debut), Style.RESET_ALL)
del debut, fin

