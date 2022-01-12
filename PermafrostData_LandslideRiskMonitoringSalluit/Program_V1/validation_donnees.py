# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 09:06:40 2021

@author: Sarah Gauthier
418-933-5671
sarah.gauthier.1@ulaval.ca
Centre d'études nordiques, Université Laval

Contiens les méthodes pour la validation des données brutes pour une station 
de suivi thermique du pergélisol. 

Critères basés sur ceux de la base de données SILA du Centre d'études nordiques (CEN), Université Laval.
"""
# Importation des modules nécessaires 
import datetime
import pandas as pd
import numpy as np
from numpy import log, nan

class ValidationDonnees():
    """
    Classe qui contient différentes méthodes pour valider les données de température 
    du sol de la station en entrée.
    
    Validations effectuées : 
         - Suppression des données dupliquée;
         - Suppression des dates dupliquées;
         - Bon format de colonne;
         - Combler les valeurs manquantes;
    """
    def __init__(self, data_frame, profondeur, station, conversion = True):
        """
        Initialisation de la classe pour la validation des données de température 
        du sol de la station en entrée.
        ----------
        station (str) : Nom de la station dont il faut valider les données.
        data_frame (DataFrame): tableau de données à valider.
        profondeur (list) : Profondeur des thermistances.
        conversion (bool) : True si les données doivent être converties en degrés Celsius, False autrement.
            
        """
        # Chemin absolu de l'emplacement local
        self.repertoire = 'C:/Users/sagau63/Documents/GitHub/Code_Station/Programme_Pergelisol/Data_CSV/'
        
        self.station = station
        self.data_frame = data_frame   # tableau de données avec les données journalières
        self.conversion = conversion   # si les données doivent être convertis en degrés Celsius
        
        self.profondeur = profondeur
        
        if self.station == 'SILA': 
            self.conversion = False

        self.df_indices_clim = pd.read_csv(f'{self.repertoire}Station_Data/CEN_SILA/Synthese_saisons_programme.csv')
        self.df_indices_clim['DateGel'] = pd.to_datetime(self.df_indices_clim['DateGel'])
        self.df_indices_clim['FinDegel'] = pd.to_datetime(self.df_indices_clim['FinDegel'])

    def validation_donnees_sila(self):
        # Vérifie si le data_frame contient des données
        if self.data_frame.empty : 
            print('Aucune donnée à valider pour la station {self.station}.')
    
        # Fonction à appliquer s'il y a des données à valider
        else: 
            print(f'_____ Validation des données de la station {self.station}_____')
            # Format de date
            self.data_frame.loc[:, 'Date'] = pd.to_datetime(self.data_frame.loc[:, 'Date'])
    
            # Filtrer les dates
            self.filtre_date()
            
            # Filtrer les doublons
            self.drop_duplicates()
            self.drop_duplicates_dates()
            
            # Mettre les données en ordre selon la date
            self.data_frame.sort_values(by = ['Date'], inplace = True)
            
            # Ajouter les dates manquantes
            self.remplir_jours_manquants()
            
            # Définir les bons formats de colonne
            cols = self.data_frame.columns.drop(['Date', 'Annee_Clim', 'Annee', 'Mois', 'Jour', 'Nom_Mois'])
            self.data_frame[cols] = self.data_frame[cols].apply(pd.to_numeric, errors='coerce')
                
            # Réinitialise l'index du dataframe
            self.data_frame.reset_index(drop = True, inplace = True)
    
            # Remplacer les valeurs de 0 par np.nan
            self.data_frame.replace(0, np.nan, inplace=True)

            print(f'Validation {self.station} terminée.', end='\n\n')
            
            return self.data_frame

    def validation_donnees_pergelisol(self, unites):
        
        """
        Appel aux fonctions de ce module pour valider et nettoyer les données. 
        ----------
        self.data_frame (DataFrame) tableau de donnée nettoyée et validée.
        """
        # Vérifie si le data_frame contient des données
        if self.data_frame.empty : 
            print('Aucune donnée à valider pour la {self.station}.')
    
        # Fonction à appliquer s'il y a des données à valider
        else: 
            print(f'_____ Validation des données de la {self.station}_____')
            # Conversion des données en degrés Celsius
            self.conversion_donnees()
            
            # Format de date
            self.data_frame.loc[:, 'Date'] = pd.to_datetime(self.data_frame.loc[:, 'Date'])
    
            # Filtrer les dates
            self.filtre_date()
            
            # Filtrer les doublons
            self.drop_duplicates()
            self.drop_duplicates_dates()
            
            # Mettre les données en ordre selon la date
            self.data_frame.sort_values(by = ['Date'], inplace = True)
            
            # Filtrer les valeurs > ou < que le minimum et maximum autorisé
            self.filtre_min_max()
            
            # S'il s'agit des données horaires
            if unites == 'Heures':
                # Ajouter les dates manquantes
                self.remplir_heures_manquantes()
                cols = self.data_frame.columns.drop(['Date', 'Annee', 'Mois', 'Jour', 'Heures', 'Nom_Mois'])
                
            # S'il s'agit des données quotidiennes
            if unites == 'Jours':
                # Ajouter les dates manquantes
                self.remplir_jours_manquants()
# =============================================================================
#                 cols = self.data_frame.columns.drop(['Date', 'Annee_Clim', 'Annee', 'Mois', 'Jour', 'Nom_Mois'])
# =============================================================================
    
            self.filtre_amplitude()
            
            # Définir les bons formats de colonne
            self.data_frame[self.profondeur] = self.data_frame[self.profondeur].apply(pd.to_numeric, errors='coerce')
                
            # Réinitialise l'index du dataframe
            self.data_frame.reset_index(drop = True, inplace = True)
    
            # Remplacer les valeurs de 0 par np.nan
            self.data_frame.replace(0, np.nan, inplace=True)

            print(f'Validation {self.station} terminée.', end='\n\n')
            
            return self.data_frame
    
    def filtre_min_max(self):
        """
        Filtre les données aberrantes qui ont des valeurs plus > que le maximum autorisé 
        et plus < que le minimum autorisé. Pour l'instant, le minimum est établi à -50°C 
        et le maximum à 50°C. 
        
        Il y a également une étape pour filtrer les données aberrantes pour 
        les thermistances plus profondes que 1m selon une fourchette de température 
        plus étroite (inférieur à -25 °C et supérieur à 10 °C).
        """
        
        for col in self.data_frame[self.profondeur]:
            for i in range(0, (len(self.data_frame[col]))):
                if self.data_frame[col].loc[i] < -50:
                    self.data_frame.loc[i, col] = np.nan
                    
                elif self.data_frame[col].loc[i] > 50:
                    self.data_frame.loc[i, col] = np.nan
        
# =============================================================================
#         for col in self.data_frame[self.profondeur]:
#             for i in range(0, (len(self.data_frame[col]))):
#                 if float(col) < -1 :
#                     if self.data_frame[col].loc[i] < -25:
#                         self.data_frame.loc[i, col] = np.nan
#                         
#                     elif self.data_frame[col].loc[i] > 10:
#                         self.data_frame.loc[i, col] = np.nan
# =============================================================================
                
        print('Valeur minimum et maximum filtré.')

    def filtre_amplitude(self):
        """
        Calculer l'amplitude entre les valeurs de chaque profondeur avec la ligne suivante

        """
        
        if self.station == 'Station GN' or self.station == 'Station GS':
                  
            df_diff = pd.DataFrame()
            
    
            # Pour comparer les valeurs avec celle de la profondeur suivante
            df_diff = self.data_frame.loc[:, '-0.02':].diff(axis = 1)
            
            for i in df_diff.columns:
                amp = (df_diff[i] > 4) | (df_diff[i] < -4)
                self.data_frame.loc[(amp == True), i] = np.nan
            
    def filtre_date(self):
        """
        Recherche de dates + heures qui sont plus récentes que la date actuelle
        conserve les données entre la date d'aujourd'hui et la date du premier enregistrement. 
        """
        # Filtrer les dates plus récentes que la aujourd'hui
        today_date = pd.to_datetime('today')
        before_date = self.data_frame['Date'] <= today_date
    
        # Filtrer les dates antérieures à celles dans la BD SILA
        start_date = '2006-05-01'
        after_BD_date = self.data_frame['Date'] >= start_date
        
        # Trouver quelles sont les dates valides
        between_dates = before_date & after_BD_date
        
        # Dataframe avec les bonnes dates
        self.data_frame = self.data_frame.loc[between_dates]
        
    def drop_duplicates_dates(self):
        """
        Recherche de dates + heures qui se répètent en se basant sur la colonne 'Date'.
        Supprime les données dupliquées en conservant la première occurrence.
        """
    
        self.data_frame = self.data_frame.drop_duplicates(subset=['Date'])
        
    def drop_duplicates(self): 
        """
        Recherche les doublons en se basant sur toutes les colonnes.
        Supprime les données dupliquées en conservant la première occurrence.
        """
        self.data_frame = self.data_frame.drop_duplicates()
        
    def remplir_heures_manquantes(self): 
        """
        Cherche s'il manque des dates ou des heures : est-ce qu'il y a un trou entre la première date 
        des données et la dernière date transmise. S'il y a un trou, les dates et heures manquantes sont remplies, 
        et on leur attribue la valeur NaN pour chaque profondeur.
        """
        
        start = self.data_frame['Date'].iloc[0]
        
        end = self.data_frame['Date'].iloc[-1]
        
        date_range = pd.date_range(start = start, end = end, freq='H') 
        
        self.data_frame = self.data_frame.set_index('Date').reindex(date_range).rename_axis('Date').reset_index()    
        # ajouter .fillna('') après .reindex(date_range) pour remplacer les nan par des espaces vides ou autre
        
        self.data_frame['Annee'] = self.data_frame['Date'].dt.year
        self.data_frame['Mois'] = self.data_frame['Date'].dt.month
        self.data_frame['Jour'] = self.data_frame['Date'].dt.day
        self.data_frame['Nom_Mois'] = self.data_frame['Date'].dt.month_name(locale = 'French')
        self.data_frame['Heures'] = self.data_frame['Date'].dt.hour
    
    def remplir_jours_manquants(self): 
        """
        Cherche s'il manque des dates ou des heures : est-ce qu'il y a un trou entre la première date 
        des données et la dernière date transmises. S'il y a un trou, les dates et heures manquantes sont remplies, 
        et ont leur attribuent la valeur NaN pour chaque profondeur.
        """
        
        debut = self.data_frame['Date'].iloc[0]
        
        fin = self.data_frame['Date'].iloc[-1]
        
        date_range = pd.date_range(start = debut, end = fin, freq='D') 
        
        self.data_frame = self.data_frame.set_index('Date').reindex(date_range).rename_axis('Date').reset_index()    
        # ajouter .fillna('') après .reindex(date_range) pour remplacer les nan par des espaces vides ou autre
        
        self.data_frame['Annee'] = self.data_frame['Date'].dt.year
        self.data_frame['Mois'] = self.data_frame['Date'].dt.month
        self.data_frame['Jour'] = self.data_frame['Date'].dt.day
        self.data_frame['Nom_Mois'] = self.data_frame['Date'].dt.month_name(locale = 'French')
    
    def conversion_donnees(self):
        if self.conversion == True:
                
            if not self.data_frame.empty:
                
                for col in self.data_frame[self.profondeur]:
                    for i in range(0, (len(self.data_frame[col]))):
                        voltage = self.data_frame.loc[i, col]
                        celsius = self.equation_conversion(voltage)
                        self.data_frame.loc[i, col] = celsius
                        
            else:
                print('Aucune valeur à convertir.')
                        
    def conversion_donnees_2(self):
        """
        Fonction pour convertir les valeurs mesurées de voltage par le câble à thermistances
        en °C pour chaque cellule du dataframe, en appelant la fonction equation_conversion 
        du module steinhart-hart, une colonne à la fois.  
        -------
        Return:  data_frame (DataFrame) avec les données de températures du sol en °C. 
        -------
        """
        if self.conversion == True:
                
            if not self.data_frame.empty:
    # =============================================================================
    #           CÂBLE D'EMMANUEL L'HÉRAULT - Conversion par colonne de profondeur
    # =============================================================================
                self.data_frame.loc[:, '2_CM'] = self.data_frame.loc[:, '2_CM'].apply(self.equation_conversion)
                self.data_frame.loc[:, '10_CM'] = self.data_frame.loc[:, '10_CM'].apply(self.equation_conversion)
                self.data_frame.loc[:, '20_CM'] = self.data_frame.loc[:, '20_CM'].apply(self.equation_conversion)
                self.data_frame.loc[:, '30_CM'] = self.data_frame.loc[:, '30_CM'].apply(self.equation_conversion)
                self.data_frame.loc[:, '40_CM'] = self.data_frame.loc[:, '40_CM'].apply(self.equation_conversion)
                self.data_frame.loc[:, '50_CM'] = self.data_frame.loc[:, '50_CM'].apply(self.equation_conversion)
                self.data_frame.loc[:, '60_CM'] = self.data_frame.loc[:, '60_CM'].apply(self.equation_conversion)
                self.data_frame.loc[:, '70_CM'] = self.data_frame.loc[:, '70_CM'].apply(self.equation_conversion)
                self.data_frame.loc[:, '75_CM'] = self.data_frame.loc[:, '75_CM'].apply(self.equation_conversion)
                self.data_frame.loc[:, '80_CM'] = self.data_frame.loc[:, '80_CM'].apply(self.equation_conversion)
                self.data_frame.loc[:, '85_CM'] = self.data_frame.loc[:, '85_CM'].apply(self.equation_conversion)
                self.data_frame.loc[:, '90_CM'] = self.data_frame.loc[:, '90_CM'].apply(self.equation_conversion)
                self.data_frame.loc[:, '95_CM'] = self.data_frame.loc[:, '95_CM'].apply(self.equation_conversion)
                self.data_frame.loc[:, '100_CM'] = self.data_frame.loc[:, '100_CM'].apply(self.equation_conversion)
                self.data_frame.loc[:, '105_CM'] = self.data_frame.loc[:, '105_CM'].apply(self.equation_conversion)
                self.data_frame.loc[:, '110_CM'] = self.data_frame.loc[:, '110_CM'].apply(self.equation_conversion)
                self.data_frame.loc[:, '115_CM'] = self.data_frame.loc[:, '115_CM'].apply(self.equation_conversion)
                self.data_frame.loc[:, '120_CM'] = self.data_frame.loc[:, '120_CM'].apply(self.equation_conversion)
                self.data_frame.loc[:, '125_CM'] = self.data_frame.loc[:, '125_CM'].apply(self.equation_conversion)
                self.data_frame.loc[:, '130_CM'] = self.data_frame.loc[:, '130_CM'].apply(self.equation_conversion)
                self.data_frame.loc[:, '140_CM'] = self.data_frame.loc[:, '140_CM'].apply(self.equation_conversion)
                self.data_frame.loc[:, '150_CM'] = self.data_frame.loc[:, '150_CM'].apply(self.equation_conversion)
                self.data_frame.loc[:, '170_CM'] = self.data_frame.loc[:, '170_CM'].apply(self.equation_conversion)
    
                if self.station == 'Station GN':
                    # CÂBLE D'EMMANUEL L'HÉRAULT - Conversion par colonne de profondeur
                    self.data_frame.loc[:, '200_CM'] = self.data_frame.loc[:, '200_CM'].apply(self.equation_conversion)
                    
                    # CÂBLE DE JULIEN FOUCHER ###
                    self.data_frame.loc[:, 'JF_2_CM'] = self.data_frame.loc[:, 'JF_2_CM'].apply(self.equation_conversion)
                    self.data_frame.loc[:, 'JF_10_CM'] = self.data_frame.loc[:, 'JF_10_CM'].apply(self.equation_conversion)
                    self.data_frame.loc[:, 'JF_20_CM'] = self.data_frame.loc[:, 'JF_20_CM'].apply(self.equation_conversion)
                    self.data_frame.loc[:, 'JF_30_CM'] = self.data_frame.loc[:, 'JF_30_CM'].apply(self.equation_conversion)
                    self.data_frame.loc[:, 'JF_40_CM'] = self.data_frame.loc[:, 'JF_40_CM'].apply(self.equation_conversion)
                    self.data_frame.loc[:, 'JF_50_CM'] = self.data_frame.loc[:, 'JF_50_CM'].apply(self.equation_conversion)
                    self.data_frame.loc[:, 'JF_60_CM'] = self.data_frame.loc[:, 'JF_60_CM'].apply(self.equation_conversion)
                    self.data_frame.loc[:, 'JF_70_CM'] = self.data_frame.loc[:, 'JF_70_CM'].apply(self.equation_conversion)
        
        else:
            print(f'Aucune données à convertir pour la {self.station}.', end = '\n\n')
    
    def calcul_moyennes_journalieres(self): 
        """
        Calcul des moyennes journalières à partir des données horaires.
        """
        self.data_frame = self.data_frame.groupby(pd.Grouper(freq='D', key='Date')).mean()
        self.data_frame.insert(0,'Date', self.data_frame.index)
        self.data_frame.reset_index(drop = True, inplace = True)
        
    def tableau_colonnes_dates(self):
        """
        Méthode pour mettre en forme les colonnes de dates.
        """
        self.data_frame['Date']= pd.to_datetime(self.data_frame['Date'])
        self.data_frame['Annee']= pd.to_datetime(self.data_frame['Date']).dt.year
        self.data_frame['Mois']= pd.to_datetime(self.data_frame['Date']).dt.month
        self.data_frame['Jour']= pd.to_datetime(self.data_frame['Date']).dt.day
        self.data_frame['Nom_Mois']= pd.to_datetime(self.data_frame['Date']).dt.month_name(locale = 'French')
        
        return self.data_frame
    
    def colonne_annee_climatique(self): 
        """
        Création de la colonne Annee_Clim pour tout le dataframe selon les dates
        de début et de fin des années climatiques depuis 2002. 
        """
        
        for i in range(len(self.df_indices_clim)):
            debut = self.df_indices_clim['DateGel'].iloc[i]
            fin  = self.df_indices_clim['FinDegel'].iloc[i]
                
            if pd.isnull(fin):
                fin = self.data_frame['Date'].iloc[-1]
                    
            annee_debut = debut.year
            annee_fin = fin.year
            
            self.data_frame.loc[(self.data_frame['Date'] >= debut) & (self.data_frame['Date'] <= fin), 'Annee_Clim'] = f'{annee_debut}-{annee_fin}'
        
    def equation_conversion(self, voltage):
        """
        Équation de SteinhartHart pour convertir  les données de température du sol 
        mesurées (voltage) en degrés Celsius à partir des constantes du manufacturier. 
        Attention, ces constantes sont propres aux modèles YSI 44033. 
        
            Rs = Rf*((Vx/V1)-1)
            Temp = 1/(A+B*LN(Rs)+C*LN(Rs)^3) - 273.15
        
        Args: voltage (float): la valeur de voltage mesurée par une thermistance.
        
        Return: celsius (float): la valeur de voltage convertie en °C. 
        
        Constantes et coefficients des YSI 44033
        ----------------------------------------
        - A = 1.473349 x 1e-03
        - B = 2.37371 x 1e-04
        - C = 1.05274e-07
        - Voltage = Valeur mesurée par la thermistance
        - Vx : Voltage d'excitation = 2000 mV
        - Rf : Facteur de résistance = 7500 omhs
        - Rs : Valeur mesurée en voltage convertie en résistance
        ----------------------------------------
        """
    
        try: 
            
            # Vérifie si la valeur est un nombre réel ou un str
            voltage = float(voltage)
            
            if voltage == 0 : 
                celsius = nan # est-ce qu'on veut que ce soit 0 ou juste rien? 
                
            # Si la valeur en entrée est un nombre réel, on y applique l'équation suivante
            else: 
                
                a = 1.473349 * 1e-03    # 0.001473349
                b = 2.37371 * 1e-04     # 0.000237371
                c = 1.05274e-07         # 0.000000105274
                
                # Valeur par défaut
                excitation = 2000
                resistance = 7500
                
                # Étape 1 : convertir le voltage en résistance
                rs = resistance*((excitation/voltage)-1)
                
                # Étape 2 : convertir la résistance en °C
                celsius = 1 / (a + b * log(rs) + c * log(rs) ** 3 ) - 273.15
            
            return celsius
        
        # Codification des erreurs de conversion des résistances / voltages et 
        # problèmes avec la formule Steinhart-Hart.
        
        except ValueError: 
            print('Erreur de conversion')
            error = -11111
            # error_cod = -11111
            return error
        
if __name__ == '__main__':

    data_frame = 
    profondeur = 
    station = 
    conversion = True


    validation = ValidationDonnees(station.serveur, station.profondeur, id_station, 'Heures')
# =============================================================================
#     validation.conversion_donnees()
# =============================================================================

