# -*- coding: utf-8 -*-
"""
Created on Tue May 25 09h16 2021

@author: Sarah Gauthier
sarah.gauthier.1@ulaval.ca
Centre d'études nordiques, Université Laval

Classe qui comprend les méthodes pour lire les données de température du sol
et pour récupérer les données journalières à distance sur le serveur FTP-CEN. 

Les données de température du sol moyennes journalières utilisées pour la période antérieures 
à 2017 sont les données traitées dans le cadre de la publication : 
    
    Allard, M., Chiasson, A., B. St-Amour, A., Aubé-Michaud, S., L'Hérault,
    E., Bilodeau, S., et Deslauriers, C. (2020). Caractérisation géotechnique 
    et cartographie améliorée du pergélisol dans les communautés nordiques du Nunavik. 
    Rapport final. Québec, Centre d'études nordiques, Université Laval. 
    Récupéré de 

# =============================================================================
#  CE MODULE EST EN DÉVELOPPEMENT ET DOIT ÊTRE ADAPTÉ EN FONCTION DE LA STATION 
#  DE SUIVI (CLIMATIQUE, THERMIQUE, ETC.) DONT LES DONNÉES DOIVENT ÊTRE 
#  RÉCUPÉRÉES ET AUSSI DU TYPE DE DONNÉES À TRAITER. 
# =============================================================================

"""

# Importation des modules nécessaires 
from connexion_serveur_ftpcen import recuperer_fichier
import pandas as pd
import numpy as np
from colorama import Back, Style
from validation_donnees import ValidationDonnees
from calcul_risque_glissement import RisqueGlissementTerrain
from datetime import datetime, timedelta
from pandas.tseries.offsets import MonthEnd

class DonneesPergelisol():
    """
    Classe qui comprend les méthodes pour lire les données de température du sol
    et pour récupérer les données journalières à distance sur le serveur FTP-CEN. 
    Les données sont récupérées sur le serveur à distance FTP-CEN tous les jours, 
    à 15h00 HNE. 
    """
    
    def __init__(self, nom_station, repertoire):
        """
        Initialisation de la classe DonneesPergelisol.
        Parameters
        ----------
        nom_station (str) Chaîne de caractère avec le nom de la station de suivi thermique 
                          pour laquelle il faut récupérer les données.

        On crée un dataframe par fichier avec la classe DataFrame du module Pandas. 
                3 DataFrames : self.serveur, self.validees et self.moy_jour.
        """
        # Chemin absolue de l'emplacement du programme et des fichiers nécessaires à l'exécution
        self.repertoire = repertoire

        self.station = nom_station
        
        # Dataframe avec les données de température de l'air de la station SILA
        self.df_sila = pd.read_csv(f'{self.repertoire}Station_Data/CEN_SILA/SILA_Salluit_AirTemp.csv')
        self.df_sila['Date'] = pd.to_datetime(self.df_sila['Date'])
        
        # Dataframe avec les données de la station de suivi du pergélisol GN
        if self.station == 'Station GN':
            self.fichier_serveur = f'{self.repertoire}Station_Data/GN/GN_serveur.csv'       # Fichier récupérer du serveur à distance FTP-CEN
            self.fichier_valide = f'{self.repertoire}Station_Data/GN/GN_validees.csv'       # Fichier avec les données convertis et validées
            self.fichier_jour = f'{self.repertoire}Station_Data/GN/GN_jours_2006_2021.csv'  # Fichier avec les température du sol moyennes journalières
            self.fichier_stats = f'{self.repertoire}Station_Data/GN/GN_min_max.csv'
            
            # Appel à la méthode recuperer_fichier du module connexion_serveur_ftpcen
            recuperer_fichier('GN.csv', self.fichier_serveur)

        # Dataframe avec les données de la station de suivi du pergélisol GS
        if self.station == 'Station GS':
            self.fichier_serveur = f'{self.repertoire}Station_Data/GS/GS_serveur.csv'       # Fichier récupérer du serveur à distance FTP-CEN
            self.fichier_valide = f'{self.repertoire}Station_Data/GS/GS_validees.csv'       # Fichier avec les données convertis et validées
            self.fichier_jour = f'{self.repertoire}Station_Data/GS/GS_jours_2006_2020.csv'  # Fichier avec les température du sol moyennes journalières
            self.fichier_stats = f'{self.repertoire}Station_Data/GS/GS_min_max.csv'

            # Appel à la méthode recuperer_fichier du module connexion_serveur_ftpcen
            recuperer_fichier('GS.csv', self.fichier_serveur)
        
        # Nom des colonnes enregistrées dans le datalogger de la station GN.
        self.names = ['Date', 'RECORD', 'Vbatt_Min', 'TCR1000', '-0.02',
                          '-0.1', '-0.2', '-0.3', '-0.4', '-0.5', '-0.6', '-0.7', '-0.75',
                          '-0.8', '-0.85', '-0.9', '-0.95', '-1', '-1.05', '-1.1',
                          '-1.15', '-1.2', '-1.25', '-1.3', '-1.4', '-1.5', '-1.7', '-2']
        
        self.profondeur = ['-0.02', '-0.1', '-0.2', '-0.3', '-0.4', '-0.5', 
                           '-0.6', '-0.7', '-0.75','-0.8', '-0.85', '-0.9', 
                           '-0.95', '-1', '-1.05', '-1.1','-1.15', '-1.2', 
                           '-1.25', '-1.3', '-1.4', '-1.5', '-1.7', '-2']
        
        self.colonnes = ['Date', 'Annee_Clim', 'Annee', 'Mois', 'Jour',
                         'Nom_Mois', 'SILA', '-0.02', '-0.1', '-0.2', '-0.3', '-0.4', '-0.5', 
                         '-0.6', '-0.7', '-0.75','-0.8', '-0.85', '-0.9', 
                         '-0.95', '-1', '-1.05', '-1.1','-1.15', '-1.2', 
                         '-1.25', '-1.3', '-1.4', '-1.5', '-1.7', '-2']
        
        self.serveur = pd.read_csv(self.fichier_serveur, names = range(28))
        self.serveur.columns = self.names

        self.validees = pd.read_csv(self.fichier_valide)
        self.validees['Date'] = pd.to_datetime(self.validees['Date'])
        
        self.moy_jour = pd.read_csv(self.fichier_jour)
        self.moy_jour['Date'] = pd.to_datetime(self.moy_jour['Date'])
        
        self.df_stats = pd.read_csv(self.fichier_stats)
    
        # Dataframe avec les indices climatiques
        self.df_indices_clim = pd.read_csv(f'{self.repertoire}Station_Data/CEN_SILA/Synthese_saisons_programme.csv')
        self.df_indices_clim['DateGel'] = pd.to_datetime(self.df_indices_clim['DateGel'])
        self.df_indices_clim['FinDegel'] = pd.to_datetime(self.df_indices_clim['FinDegel'])
    
    def donnees_temperature_sol(self):
        """
        Méthode principal qui appelle les autres méthodes pour mettre 
        en forme les tableaux de données, récupérer le nouvelles données et
        les écrire dans le bon fichier. 
        """
        
        # Création d'un dataframe avec les nouvelles données
        self.tableau_donnees() 

        # Récupération des données de température du sol
        self.nouvelles_donnees_serveur()
        
        # Écriture des nouvelles données dans leur fichier respectif
        if not self.nouvelles_lignes.empty:
        
            # Conversion et nettoyage des données avec la classe ValidationDonnees
            validation = ValidationDonnees(self.nouvelles_lignes, self.profondeur, self.station, 'Heures')
            self.lignes_validees = validation.validation_donnees_pergelisol()
            self.validees = self.validees.append(self.lignes_validees, ignore_index = True)
            self.ecriture_donnees_sol(self.lignes_validees, self.fichier_valide)
            
            # Calcul de la température moyenne journalière à partir des données horaires
            self.moyenne_journaliere()
            self.ecriture_donnees_sol(self.nouvelles_lignes_moy, self.fichier_jour)
            self.stats_df_total()
            
        # Décommenter pour appeler la classe RisqueGlissementTerrain pour le calcul du risque de glissement de terrain
        # selon les différents paramètres : seuil climatique = cumul de degrés-jour de dégel et thermique : maximum de dégel
# =============================================================================
#         risque = RisqueGlissementTerrain(self.moy_jour, self.df_sila, self.station, self.repertoire)
#         risque.calcul_risque()
# =============================================================================
        
        self.back_up_fichiers()
        
    def moyenne_journaliere(self):
        """
        Calculer la température moyenne de l'air journalière.         
        ----------
        """
        
        # Dernière date dans le fichier avec les moyennes journalières
        date = self.moy_jour['Date'].iloc[-1] + timedelta(days=1)
        
        # Localiser les données qui sont plus récentes que la dernière date dans le fichier
        jours = self.validees.loc[self.validees['Date'] > date]
        
        # Calcul des moyennes journalières
        self.nouvelles_lignes_moy = jours.groupby(pd.Grouper(freq='D', key='Date')).mean()
        self.nouvelles_lignes_moy.insert(0,'Date', self.nouvelles_lignes_moy.index)
        self.nouvelles_lignes_moy['Nom_Mois'] = self.nouvelles_lignes_moy['Date'].dt.month_name(locale = 'French')
        self.nouvelles_lignes_moy.reset_index(drop = True, inplace = True)
        
        # On ajoute la colonne avec l'année climatique 
        self.colonne_annee_clim()
        
        # Écarter la dernière date, parce que les données ne sont pas complète (jusqu'à 13h00)
        self.nouvelles_lignes_moy = self.nouvelles_lignes_moy.iloc[:-1]

        # On ajoute les données de température de l'air
        self.nouvelles_lignes_moy = pd.merge(self.nouvelles_lignes_moy, self.df_sila[['Date', 'SILA']])
# =============================================================================
#         self.nouvelles_lignes_moy['Date'] = self.nouvelles_lignes_moy.index
# =============================================================================
        
        # Remettre le bon ordre des colonnes après les ajouts
        self.nouvelles_lignes_moy = self.nouvelles_lignes_moy[self.colonnes]
        
        self.nouvelles_lignes_moy.loc[:, 'Jour'] = self.nouvelles_lignes_moy.loc[:, 'Jour'].astype(int)
        self.nouvelles_lignes_moy.loc[:, 'Mois'] = self.nouvelles_lignes_moy.loc[:, 'Mois'].astype(int)
        self.nouvelles_lignes_moy.loc[:, 'Annee'] = self.nouvelles_lignes_moy.loc[:, 'Annee'].astype(int)
        
        self.moy_jour = self.moy_jour.append(self.nouvelles_lignes_moy, ignore_index = True)
        self.moy_jour.reset_index(drop = True, inplace = True)
        
    def stats_df_total(self):
        """
        Méthode pour calculer les statistiques de température minimum, moyenne et maximum
        par profondeur pour une période de temps donnée, soit par année climatique. 
        """
        

        # Décommenter les lignes ci-bas pour refaire une validation sur les moyennes calculées 
# =============================================================================
#         validation = ValidationDonnees(self.moy_jour, self.station, 'Jours', conversion = False)
#         self.moy_jour = validation.validation_donnees_pergelisol()
# =============================================================================
        
        if self.station == 'Station GN': 
            self.moy_jour = self.moy_jour.loc[:, :'200_CM']
            self.profondeur = self.profondeur[:-8]
        
        self.profondeur = ['-0.02', '-0.1', '-0.2', '-0.3', '-0.4', '-0.5', '-0.6', '-0.7', '-0.75',
                              '-0.8', '-0.85', '-0.9', '-0.95', '-1', '-1.05', '-1.1',
                              '-1.15', '-1.2', '-1.25', '-1.3', '-1.4', '-1.5', '-1.7', '-2']
        
        self.moy_jour.columns = ['Date', 'Annee_Clim', 'Annee', 'Mois', 'Jour', 'Nom_Mois', 'SILA', '-0.02',
                              '-0.1', '-0.2', '-0.3', '-0.4', '-0.5', '-0.6', '-0.7', '-0.75',
                              '-0.8', '-0.85', '-0.9', '-0.95', '-1', '-1.05', '-1.1',
                              '-1.15', '-1.2', '-1.25', '-1.3', '-1.4', '-1.5', '-1.7', '-2']
        
        names = ['Station', 'Annee_Clim', 'Profondeur', 'T_Min', 'T_Max', 'T_Moy']
        self.min_max = pd.DataFrame(columns = names)
        
        df_annee_clim = self.df_indices_clim[4:]
        
        # Colonne année_clim pour tout le tableau
        for i in range(len(df_annee_clim)):
            
            if i == 0 :
                debut = self.moy_jour['Date'].iloc[0]
            
            else: 
                debut = df_annee_clim['DateGel'].iloc[i]
            
            fin  = df_annee_clim['FinDegel'].iloc[i]
            annee_clim = df_annee_clim['Annee_Clim'].iloc[i]
            
            if pd.isnull(fin):
                fin = self.moy_jour['Date'].iloc[-1]
                     
            df = pd.DataFrame(columns = names)

            df_date = self.moy_jour.loc[(self.moy_jour['Date'] >= debut) & (self.moy_jour['Date'] <= fin)]
            
            # Calcul de valeurs manquantes pour l'année climatique i
            pourcentage_nan = pd.DataFrame(columns = ['Profondeur', 'Pourcentage_NaN'])
            pourcentage_nan['Pourcentage_NaN'] = df_date.loc[:, '-0.02':].isnull().sum() * 100 / len(df_date)
            pourcentage_nan['Profondeur'] = pourcentage_nan.index
            
            for i in df_date[self.profondeur]:
                
                # Est-ce que le pourcentage de valeurs manquantes est supérieur à la limite acceptée
                limite_nan = pourcentage_nan.loc[pourcentage_nan['Profondeur'] == i, 'Pourcentage_NaN'] > 40
                
                # Si oui, 
                if limite_nan.any()  : 

                    # Valeur de NaN, car trop de valeurs manquantes.
                    df.loc[df['Profondeur'] == i, 'T_Min'] = np.nan
                    df.loc[df['Profondeur'] == i, 'T_Max'] = np.nan
                    df.loc[df['Profondeur'] == i, 'T_Moy'] = np.nan
                
                else: 
                    # Calcul des températures minimums, maximums et moyennes pour chaque profondeur
                    df['T_Min'] = df_date[self.profondeur].min()
                    df['T_Max'] = df_date[self.profondeur].max()
                    df['T_Moy'] = df_date[self.profondeur].mean()
                
            df['Profondeur'] = df_date[self.profondeur].min().index

            df['Annee_Clim'] = annee_clim
            df['Station'] = self.station
            
            self.min_max = self.min_max.append(df, ignore_index = True)
        
        # Si toutes les colonnes ont la même valeurs
        erreur = (self.min_max['T_Min'] == self.min_max['T_Max']) & (self.min_max['T_Max'] == self.min_max['T_Moy'])
        
        # Il y a une erreur, donc on remplace par nan
        self.min_max.loc[erreur, ['T_Min', 'T_Max','T_Moy']] = np.nan
        print(self.min_max.loc[330])
        
        self.min_max = self.min_max.replace(0, np.nan)
        
        self.min_max.to_csv(self.fichier_stats, index = False, float_format = '%.4f')
        
    def tableau_donnees(self):
        """
        Mise en forme du tableau de données. 
        ---------------------------
        self.gn_serveur (DataFrame) : Tableau de données avec les données brutes
                                    récupérées sur le serveur à distance ftp-cen
                                    tous les jours à 14h00.
        """
        self.serveur =  self.serveur[self.serveur['Date'].str[0] == '2']

        del  self.serveur['RECORD']
        del  self.serveur['TCR1000']
        del  self.serveur['Vbatt_Min']
        
        self.serveur.loc[:, 'Date']= pd.to_datetime(self.serveur.loc[:, 'Date'])
        self.serveur.loc[:, 'Annee'] = self.serveur.loc[:, 'Date'].dt.year
        self.serveur.loc[:, 'Mois'] = self.serveur.loc[:, 'Date'].dt.month
        self.serveur.loc[:, 'Jour'] = self.serveur.loc[:, 'Date'].dt.day
        self.serveur.loc[:, 'Nom_Mois'] = self.serveur.loc[:, 'Date'].dt.month_name(locale = 'French')
        self.serveur.loc[:, 'Heures'] = self.serveur.loc[:, 'Date'].dt.hour
        
        ### NOUVELLE LIGNE ###
        self.serveur.reset_index(drop = True, inplace = True)
        
        self.serveur = self.serveur[['Date', 'Annee', 'Mois', 'Jour', 'Heures', 'Nom_Mois', 
                                         '-0.02', '-0.1', '-0.2', '-0.3', '-0.4', '-0.5', 
                                         '-0.6', '-0.7', '-0.75','-0.8', '-0.85', '-0.9', 
                                         '-0.95', '-1', '-1.05', '-1.1','-1.15', '-1.2', 
                                         '-1.25', '-1.3', '-1.4', '-1.5', '-1.7', '-2']]
        
        cols = self.serveur.columns.drop(['Date', 'Annee', 'Mois', 'Jour', 'Heures', 'Nom_Mois'])
        self.serveur[cols] = self.serveur[cols].apply(pd.to_numeric, errors='coerce')
    
    def colonne_annee_clim(self):
        """
        Création de la colonne année climatique. 
        """
        
        # Colonne année_clim
        for i in range(len(self.nouvelles_lignes_moy)):
            debut = self.df_indices_clim['DateGel'].iloc[-1]
            fin  = self.df_indices_clim['FinDegel'].iloc[-1]
                
            if pd.isnull(fin):
                fin = self.nouvelles_lignes_moy['Date'].iloc[-1]
                
            annee_debut = debut.year
            annee_fin = fin.year
            
            self.nouvelles_lignes_moy.loc[(self.nouvelles_lignes_moy['Date'] >= debut) & (self.nouvelles_lignes_moy['Date'] <= fin), 'Annee_Clim'] = f'{annee_debut}-{annee_fin}'
    
    def nouvelles_donnees_serveur(self): 
        """
        Méthode pour récupérer les nouvelles données journalières de température 
        du sol pour selon la station.
        ---------------------------
        self.gn_clean (DataFrame) : Fichier de données prénettoyé
                                    Enregistrés sur le serveur.
                                    
        self.gn_serveur (DataFrame) : Fichier de nouvelles données journalières. 
        
        self.nouvelles_lignes (DataFrame) : Nouvelles lignes de données a ajouter 
                                            au fichier nettoyé.
        """
        
        try:
            
            # Dernière date du fichier le plus récent
            derniere_date = self.validees['Date'].iloc[-1]
            diff = self.serveur['Date'] > derniere_date
            
            # Localiser les nouvelles dates dans le dataframe
            self.nouvelles_lignes = self.serveur.loc[diff]
            
            self.nouvelles_lignes.reset_index(drop = True, inplace = True)
        
            # S'il y a des nouvelles données
            if not self.nouvelles_lignes.empty : 
                # S'il y a eu une interruption, combler le trou.
                self.nouvelles_lignes  = self.nouvelles_lignes.set_index('Date').asfreq('H').reset_index()
                self.nouvelles_lignes.drop_duplicates(inplace = True)
                self.nouvelles_lignes.reset_index(drop = True, inplace = True)
                    
                print(f'Voici les nouvelles données de la {self.station} :')
                print(self.nouvelles_lignes.head(), end='\n\n')
            
            # S'il n'y a pas de nouvelles données
            else: 
                print(Back.MAGENTA + f'Aucune nouvelle donnée dans {self.station}.'  + Style.RESET_ALL, end = '\n\n')
                
        except NameError:
            print(f'{self.station} : NameError Nom du fichier incorrecte.Entrez un autre nom en argument ou vérifier le répertoire.')
            
        except FileNotFoundError:
            print(f'{self.station} : FileNotFoundError Fichier introuvable. Essayez un autre nom ou vérifier dans le répertoire.')
            
        except OSError:
            print(f'{self.station} : OSError Fichier introuvable. Essayez un autre nom ou vérifier dans le répertoire.')
        
    def ecriture_donnees_sol(self, data_frame, fichier):
        """
        Méthode pour écrire les nouvelles données journalières à la fin du fichier. 
        """
        try: 

            # Écrire les nouvelles données à la fin du fichier clean test
            
            if not data_frame.empty : 
                print(f'Écriture du fichier pour la {self.station}.')
                data_frame.to_csv(fichier, mode='a', header=False, index = False, float_format='%.4f')
            
            else: 
                print(f'Aucune nouvelle donnée à écrire. Lecture du fichier de la {self.station} terminée.', end = '\n\n')

        except NameError:
            print(f'{self.station} : NameError Nom du fichier incorrect. Entrez un autre nom en argument ou vérifiez le répertoire.')
            
        except FileNotFoundError:
            print(f'{self.station} : FileNotFoundError Fichier introuvable. Essayez un autre nom ou vérifier dans le répertoire.')
            
        except OSError:
            print(f'{self.station} : OSError Fichier introuvable. Essayez un autre nom ou vérifiez dans le répertoire.')
    
    def back_up_fichiers(self):
        """
        Écriture d'un backup Excel à chaque mois.'
        """
        
        # Nom et chemin des fichiers de back up
        fichier_excel_donnees = f'{self.repertoire}Station_DataExcel_BackUp/{self.station}_heures.xlsx'
        fichier_excel_moyennes = f'{self.repertoire}Station_Data/Excel_BackUp/{self.station}_jours.xlsx'
        
        # Récupérer la date 
        date = datetime.today().date()
        dernier_jour_mois = (pd.to_datetime(date) + MonthEnd(1)).date()
        
        # S'il s'agit du dernier jour du mois, on fait un fichier excel back up 
        if date == dernier_jour_mois:
            self.validees.to_excel(fichier_excel_donnees, index = False)
            self.moy_jour.to_excel(fichier_excel_moyennes, index = False)
            print('Écriture du fichier Excel de back up.')
    
if __name__ == '__main__':
    
    # Instance de la classe DonneesPergelisol        
    id_station = input('Entrez le nom de la station : ')
    
    print('Initialisation de la classe.', end = '\n\n')
    station = DonneesPergelisol(id_station)
    station.donnees_temperature_sol()
    

