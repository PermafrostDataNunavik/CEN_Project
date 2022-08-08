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

# =============================================================================
#  CE MODULE EST EN DÉVELOPPEMENT ET DOIT ÊTRE ADAPTÉ EN FONCTION DE LA STATION 
#  DE SUIVI (CLIMATIQUE, THERMIQUE, ETC.) DONT LES DONNÉES DOIVENT ÊTRE 
#  RÉCUPÉRÉES ET AUSSI DU TYPE DE DONNÉES À TRAITER. 
# =============================================================================


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
        
        # Chemin absolue de l'emplacement du programme et des fichiers nécessaires à l'exécution
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
        
        # NOUVEAU URL SUITE À LA MISE À JOUR : 
# =============================================================================
#         self.url = 'https://www.environnement.gouv.qc.ca/climat/donnees/sommaire.asp?cle=711P788&date_selection=2021-12-01'
# =============================================================================
    
        # La date à récupérer est la date du jour -1 jour
        self.date_jour = (datetime.today() - timedelta(days=1)).date()
        self.date_jour = pd.to_datetime(self.date_jour)
        
# =============================================================================
#         self.date_jour = pd.to_datetime('AAAA-MM-JJ').date()
# =============================================================================
        
    def donnees_sila(self):
        
        # Dernière date du fichier
        date_fichier = (self.df_sila.Date.iloc[-1]).date()
        
        # Tant que le dernier mois dans le fichier n'est le mois actuel
        if date_fichier.month != self.date_jour.month:
    
            # Création du dataframe avec les données journalières et les données sur le serveur
            self.donnees_site_web_melcc()

            # S'il y a des nouvelles données
            if not self.df_mois.empty:
                # Récupération des nouvelles données et écriture
                self.ecriture_donnees_sila()
        
        else:
            # Aller chercher les données du mois actuelle
            self.donnees_site_web_melcc()
    
            # S'il y a des nouvelles données
            if not self.df_mois.empty:
                # Récupération des nouvelles données et écriture
                self.ecriture_donnees_sila()
        
    def ecriture_donnees_sila(self):
        """
        Méthode pour trouver nouvelles données pour le fichier de données du site web du melcc.
        """
        
        try: 

            # Si la colonne 'Jour' est numérique pour exclure la dernière ligne 'Moyenne:'
            df_mensuelle = self.df_mois.loc[self.df_mois['Jour'].str.isnumeric()]
            
            # Dernière date enregistrée dans le fichier
            derniere_date_melcc = self.df_melcc['Date'].iloc[-1]
            
            # Trouver les dates plus récentes
            nouvelles_donnees_melcc = df_mensuelle['Date'] > derniere_date_melcc 
            
            if df_mensuelle.iloc[-1].T_Moy == '-' : 
                df_mensuelle = df_mensuelle.iloc[:-1]
            
            # Localiser les nouvelles dates dans le dataframe
            nouveau_df = df_mensuelle.loc[nouvelles_donnees_melcc]
            
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
            nouvelles_donnees_sila = df_mensuelle['Date'] > derniere_date_sila
    
            # Localiser les nouvelles dates dans le dataframe
            self.nouvelles_lignes = df_mensuelle.loc[nouvelles_donnees_sila]
            
            self.nouvelles_lignes = self.nouvelles_lignes.loc[self.nouvelles_lignes['Date'] <= self.date_jour]
            
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

            # Le programme ne trouve pas de nouvelles données
            else:
                print(Back.MAGENTA + 'Aucune nouvelle données pour la station SILA - Salluit.' + Style.RESET_ALL, end = '\n\n')

        except ValueError:
            print('Aucune nouvelles données.')
    
        except NameError:
            print('Écriture données SILA : Nom du fichier incorrecte.Entrez un autre nom en argument ou vérifier le répertoire.')
            
        except FileNotFoundError:
            print('Écriture données SILA : Fichier introuvable. Essayez un autre nom ou vérifier dans le répertoire.')
            
        except OSError:
            print('Écriture données SILA : Fichier introuvable. Essayez un autre nom ou vérifier dans le répertoire.')
        
    def donnees_site_web_melcc(self):
        """
        Lecture de la page Web du MELCC pour récupérer les données météorologiques 
        diverses de la station SILA. 
        """
        
        print(f'Lecture de la page web {self.url}', end = '\n\n')
        try: 
            
            # Revérifier la dernière date du fichier
            date_fichier = (self.df_sila.Date.iloc[-1]).date()
            
            # Vérifier la dernière date du mois
            dernier_jour_mois = (datetime(date_fichier.year, date_fichier.month, 1) + relativedelta(months=1, days=-1)).date()

            # Si la dernière date dans le fichier est la dernière date du mois
            if date_fichier == dernier_jour_mois:
                # On récupère les données du mois suivant
                date_url = date_fichier + relativedelta(days=1)
            
            else:
                date_url = date_fichier
                
            # URL complet avec la date pour avoir accès à la station SILA avec les données plus à jour
            url = self.url + str(date_url)
            
            # Lire la page web avec pandas et mettre une limite de 20 secondes
            df_MELCC = pd.read_html(requests.get(url, timeout=20).text, decimal = ',', thousands='.')
            
            # Aller chercher le dataframe qui contient les données
            self.df_mois = df_MELCC[1]
            
            # Mise en forme des colonnes du dataframe
            self.df_mois.columns = self.df_mois.columns.get_level_values(1)
            self.df_mois.dropna(subset=['Jour'], inplace = True)
            
            # Création des colonnes Année, mois, jour, nom_mois avec les bons formats
            self.df_mois['Annee'] = date_url.year
            self.df_mois['Mois'] = date_url.month
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
        
        except ValueError:
            print('Données MELCC : Aucune nouvelle donnée.')
            
        except ConnectionError:
            print('Données MELCC : Impossible d\'accéder au site Web. Vérifiez votre connexion internet ou le lien URL.')

        except:
            # Si ça ne fonctionne pas, le programme renvoi un dataframe vide
            self.df_mois = pd.DataFrame()
            self.nouvelles_lignes = pd.DataFrame()
            print(Back.RED + 'Site Web du MELCC actuellement non disponible.' + Style.RESET_ALL, end = '\n\n')

if __name__ == '__main__':
    
    repertoire = input('Entrez le nom du répertoire de travail : ')
    
    print('Initialisation de la classe.', end = '\n\n')
    sila = DonneesSila(repertoire)


