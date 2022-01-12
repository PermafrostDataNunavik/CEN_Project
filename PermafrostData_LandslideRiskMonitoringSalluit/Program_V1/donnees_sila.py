# -*- coding: utf-8 -*-
"""
Created on Thu Apr 29 15:04:21 2021
@author: Sarah Gauthier,
Université Laval, Québec

Données de température de l'air de la station SILA à Salluit.
    Latitude :  62° 11' 31'' 
    Longitude :  75° 38' 9'' 
    Altitude :  130 m
    
La journée climatologique commence à 08h01 HNE et se termine à 
08h00 HNE le lendemain (Temp Min de 18h01 HNE la veille à 18h00 HNE)

Récupération des données sur le site Web du MELCC :
https://www.environnement.gouv.qc.ca/climat/donnees/sommaire.asp?cle=711P788&date_selection=

"""
# Importation des modules nécessaires 
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from colorama import Style, Back
from dateutil.relativedelta import relativedelta
import requests

class DonneesSila():
    
    def __init__(self, repertoire):
        """
        Création des tableau de données à partir des fichiers sur le disque local. 
        
        self.df_melcc (DataFrame) : Tableau de données avec les données récupérées chaque jour 
                                   sur le site web du MELCC. 
            
        self.df_sila (DataFrame) : Tableau de données mis en forme avec la température de l'air et 
                                  le cumul de degrés-jours selon la saison de gel et de dégel.
                              
        self.repertoire (str) : Chaîne de caractère avec le répertoire du programme et des fichiers
        """
        
        # Chemin absolu de l'emplacement du programme et des fichiers nécessaires à l'exécution
        self.repertoire = repertoire
        
        # Définir l'emplacement des fichiers
        self.fichier_melcc = f'{self.repertoire}Station_Data/MELCC_SILA/SILA_MELCC_Daily.csv'
        self.fichier_sila = f'{self.repertoire}Station_Data/CEN_SILA/SILA_Salluit_AirTemp.csv'
        
        # Dataframe avec données du site web melcc
        self.df_melcc = pd.read_csv(self.fichier_melcc)
        self.df_melcc['Date'] = pd.to_datetime(self.df_melcc['Date'])

        # Dataframe avec données de température de l'air
        self.df_sila = pd.read_csv(self.fichier_sila)
        self.df_sila['Date'] = pd.to_datetime(self.df_sila['Date'])
        
        self.url = 'https://www.environnement.gouv.qc.ca/climat/donnees/sommaire.asp?cle=711P788&date_selection='
  
        ##### AJOUTER IF-ELSE POUR TROUVER QUELLE DATE RÉCUPÉRER ####
        # La date à récupérer est la date du jour -1 jour
        self.date_jour = (datetime.today() - timedelta(days=1)).date()

        # La date à récupérer est la dernière date du fichier
# =============================================================================
#         self.date_jour = (self.df_sila.Date.iloc[-1]).date()
# =============================================================================
# =============================================================================
#         self.date_jour = pd.to_datetime('AAAA-MM-JJ').date()
# =============================================================================
        
    def donnees_sila(self):

        # Création du dataframe avec les données journalières et les données sur le serveur
        self.donnees_site_web_melcc()

# =============================================================================
#         sila = ValidationDonnees(self.df_sila, profondeur = None, station = 'SILA', conversion = False)
#         sila.validation_donnees_sila()
# =============================================================================
        
        # si l'objet avec les données mensuelles n'est pas vide
        if not self.df_mois.empty:
            # Récupération des nouvelles données et écritures
            self.ecriture_donnees_sila()
        
    def ecriture_donnees_sila(self):
        
        # On essaye ce bloc de données
        try: 
    # Trouver nouvelles données pour le fichier de données du site web du melcc et les ajouter dans le fichier
    # =============================================================================

            # Récupérer le premier et le dernier jour du mois
            premier_jour = datetime(self.date_jour.year, self.date_jour.month, 1).date()
            dernier_jour = (datetime(self.date_jour.year, self.date_jour.month, 1) + relativedelta(months=1, days=-1)).date()
            
            # Si la date d'hier est le premier jour du mois   
            if self.date_jour == premier_jour:
                df_mensuelles = self.df_mois.iloc[[0]]
            
            # Si la date d'hier est le dernier jour du mois   
            if self.date_jour == dernier_jour: 
                df_mensuelles = self.df_mois.iloc[:-1]
                            
            # Si la date d'hier est n'importe quel autre jour du mois   
            else: 
                df_mensuelles = self.df_mois.iloc[:-2]
            
            # Dernière date enregistrée dans le fichier
            derniere_date_melcc = self.df_melcc['Date'].iloc[-1]
            
            # Trouver les dates plus récentes
            nouvelles_donnees_melcc = df_mensuelles['Date'] > derniere_date_melcc 
            
            # Localiser les nouvelles dates dans le dataframe
            nouveau_df = df_mensuelles.loc[nouvelles_donnees_melcc]
            
            # Le programme trouve des nouvelles données : 
            if not nouveau_df.empty: 
                nouveau_df = nouveau_df.drop_duplicates(subset = 'Date')
                nouveau_df = nouveau_df.sort_values(by = 'Date')
                nouveau_df = nouveau_df.reset_index(drop = True)
                nouveau_df.to_csv(self.fichier_melcc, mode='a', header=False, index = False)
            
    # Trouver nouvelles données du fichier de température de l'air et les ajouter dans le fichier
    # =============================================================================
            # Dernière date enregistrée dans le fichier 
            derniere_date_sila = self.df_sila['Date'].iloc[-1]
            
            # Trouver les dates plus récentes
            nouvelles_donnees_sila = df_mensuelles['Date'] > derniere_date_sila
    
            # Localiser les nouvelles dates dans le dataframe
            self.nouvelles_lignes = df_mensuelles.loc[nouvelles_donnees_sila]
            
            if not self.nouvelles_lignes.empty: 
                self.nouvelles_lignes = self.nouvelles_lignes.drop_duplicates(subset = 'Date')
                self.nouvelles_lignes = self.nouvelles_lignes.sort_values(by = 'Date')
                self.nouvelles_lignes = self.nouvelles_lignes.reset_index(drop = True)

                self.nouvelles_lignes = self.nouvelles_lignes[['Date', 'Annee', 'Mois', 'Jour', 'Nom_Mois', 'T_Moy']]
                self.nouvelles_lignes['CUMUL_DJ'] = np.nan
                self.nouvelles_lignes = self.nouvelles_lignes.rename(columns = {'T_Moy' : 'SILA'})
        
                cols = self.nouvelles_lignes.columns.drop(['Date', 'Nom_Mois'])
                self.nouvelles_lignes['Date'] = pd.to_datetime(self.nouvelles_lignes['Date'])
                self.nouvelles_lignes[cols] = self.nouvelles_lignes[cols].apply(pd.to_numeric, errors='coerce')
        
                self.df_sila = self.df_sila.append(self.nouvelles_lignes, ignore_index = True)

                print('Écriture des nouvelles données journalières dans les fichiers ...')
                print(self.nouvelles_lignes.head(), end = '\n\n')
            
            # Le programme ne trouve pas de nouvelles données
            else:
                print(Back.MAGENTA + 'Aucune nouvelle donnée pour la station SILA - Salluit.' + Style.RESET_ALL, end = '\n\n')

        except ValueError:
            print('Aucune nouvelle donnée.')
    
        except NameError:
            print('Écriture données SILA : Nom du fichier incorrect.Entrez un autre nom en argument ou vérifiez le répertoire.')
            
        except FileNotFoundError:
            print('Écriture données SILA : Fichier introuvable. Essayez un autre nom ou vérifiez dans le répertoire.')
            
        except OSError:
            print('Écriture données SILA : Fichier introuvable. Essayez un autre nom ou vérifiez dans le répertoire.')
        
    def donnees_site_web_melcc(self):
        """
        Lecture de la page Web du MELCC pour récupérer les données météorologiques 
        diverses de la station SILA. 
        
        À MODIFIER POUR ENLEVER LA RÉCUPÉRATION DE LA LIGNE DE MOYENNE...
        """
        
        print(f'Lecture de la page web {self.url}', end = '\n\n')
        try: 
            
            # URL complet avec la date pour avoir accès à la station SILA avec les données plus à jour
            url = self.url + str(self.date_jour)
            
            # Lire la page web avec pandas et mettre une limite de 20 secondes
            df_MELCC = pd.read_html(requests.get(url, timeout=20).text, decimal = ',', thousands='.')
            
            # Aller chercher le dataframe qui contient les données
            self.df_mois = df_MELCC[1]
            
            # Mise en forme des colonnes du dataframe
            self.df_mois.columns = self.df_mois.columns.get_level_values(1)
            self.df_mois.dropna(subset=['Jour'], inplace = True)
            
            # Création des colonnes Année, mois, jour, nom_mois avec les bons formats
            self.df_mois['Annee'] = self.date_jour.year
            self.df_mois['Mois'] = self.date_jour.month
            self.df_mois['Station'] = 'Salluit SILA'
            self.df_mois = self.df_mois.rename(columns = {'Annee':'year', 'Mois':'month', 'Jour':'day'})
            self.df_mois['Date'] = pd.to_datetime(self.df_mois[['year', 'month', 'day']], errors='coerce')
            self.df_mois = self.df_mois.rename(columns = {'year':'Annee', 'month':'Mois', 'day' : 'Jour'})
            self.df_mois['Nom_Mois'] = pd.to_datetime(self.df_mois['Mois'], format='%m').dt.month_name(locale = 'French')
            self.df_mois['Date'] = pd.to_datetime(self.df_mois['Date'])
            
            # df_mois.dropna(subset=['Date'], inplace = True)
    
            self.df_mois = self.df_mois.rename(columns = {'Max.(Â°C)' : 'T_Max', 'Moy.(Â°C)':'T_Moy', 'Min.(Â°C)':'T_Min'})
    
            self.df_mois = self.df_mois[['Station', 'Date', 'Annee', 'Mois', 'Jour', 'Nom_Mois', 'T_Max', 'T_Moy', 'T_Min', 'Pluie(mm)',
                   'Neige(cm)', 'Total(mm)', 'Neigeau sol(cm)']]
            
        except:
            # Si ça ne fonctionne pas, le programme renvoi un dataframe vide
            self.df_mois = pd.DataFrame()
            self.nouvelles_lignes = pd.DataFrame()
            print(Back.RED + 'Site Web du MELCC actuellement non disponible.' + Style.RESET_ALL, end = '\n\n')

        except ValueError:
            print('Données MELCC : Aucune nouvelle donnée.')
            
        except ConnectionError:
            print('Données MELCC : Impossible d\'accéder au site Web. Vérifiez votre connexion internet ou le lien URL.')

if __name__ == '__main__':
    
    repertoire = input('Entrez le nom du répertoire de travail : ')
    
    print('Initialisation de la classe.', end = '\n\n')
    sila = DonneesSila(repertoire)


