# -*- coding: utf-8 -*-
"""
Created on Fri Aug  6 15:07:09 2021

@author: Sarah Gauthier, Michel Allard et Emmanuel L'Hérault.
Le calcul de la profondeur de dégel quotidienne est basé sur le programme
2D Thermal Regime Vizualisation and Thaw Depth Estimation from Ground Temperatures Timeserie. 
Programme rédigé avec MATLAB par Emmanuel L'Hérault. Dernière mise à jour en janvier 2021. 

"""
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from colorama import Back, Fore, Style
from scipy.interpolate import interp1d
from pandas.tseries.offsets import MonthEnd
from validation_donnees import ValidationDonnees
import easygui
    
class RisqueGlissementTerrain():
    """
    Cette classe permet l'estimation du niveau de risque de glissement de terrain  
    de type décrochement de couche active dans les dépôts de particules fines 
    silteux-argileux du village de Salluit au Nunavik. 
    
    L'estimation du niveua de risque s'effectue selon :
        ---- Le cumul de degrés-jours de dégel de l'année climatique en cours. 
        la variation de l'indice de dégel par rapport à l'année précédente, mise en relation avec un seuil de risque climatique : 
    
    Le calcul peut aussi s'effectuer selon : 
        ---- Le maximum de dégel par l'interpolation des valeurs de température du sol;'
    
    En raison des problèmes de précisions des valeurs mesurées par les câbles à thermistance
    de la station GN et de l'interruption dans la transmission des données de la station GS, 
    il n'est pas possible de déterminer le niveau de risque selon le paramètre thermique.
    Le programme propose toutefois des méthodes pour y arriver, dans l'éventualité où les mesures
    la précision des données ne seraient plus problématiques.'
    Les lignes à décommenter sont indiquées dans le programme. 
    """
    def __init__(self, df_sol, df_sila, station, repertoire):
        """
        Initialisation de la classe RisqueGlissementTerrain. 
        
        df_sol (DataFrame) : Tableau de données avec la température du sol.
        df_sila (DataFrame) :Tableau de données avec la température de l'air.
        station (str) : Nom de la station avec laquelle s'effectuent les calculs.
        repertoire (str) : Chemin du répertoire de travail avec les fichiers pour l'exécution du programme.
        
        """
        self.repertoire = repertoire
        
        self.df_sol = df_sol    # fichier avec les données de température du sol
        self.df_sila = df_sila  # fichier avec les données de température de l'air
        self.station = station.replace(' ', '_')

        # Bon format de date
        self.df_sol['Date'] = pd.to_datetime(self.df_sol['Date'])
        self.df_sila['Date'] = pd.to_datetime(self.df_sila['Date'])

        # Choisir la méthode d'interpolation - À modifier au besoin. 
# =============================================================================
#         self.methode = 'spline' 
# =============================================================================
        self.methode = 'lineaire'
        
        # Fichier avec les maximums de dégel par année
# =============================================================================
#         self.max_degel = pd.read_csv(f'C:/Users/sagau63/Documents/GitHub/Code_Station/Programme_Pergelisol/Data_CSV/Station_Data/Max_Degel/Max_Degel_{self.station}_{self.methode}.csv')
# =============================================================================

        # Création du dataframe pour le calcul des maximums de dégel 
        self.df_degel = pd.DataFrame(columns = ['Date', 'MaxDegel'])
        self.df_degel['MaxDegel'] = self.df_degel['MaxDegel'].astype(float)
        self.df_degel['Date'] = pd.to_datetime(self.df_degel['Date'])
        
        # Mise en forme du dataframe avec les températures du sol et ajout de la colonne 
        # '0' qui contient les données de température de l'air de la station SILA. 
        self.df_sol = self.df_sol.iloc[:, 0:31]
        
        # Créer la colonne avec les données de température de l'air
        if 'SILA' not in self.df_sol:
            self.df_sol = pd.merge(self.df_sol, df_sila[['Date', 'SILA']])
            col = self.df_sol['SILA']
            self.df_sol.drop(labels=['SILA'], axis=1, inplace = True)
            
            if station == 'FP2':
                self.df_sol.insert(4, 'SILA', col)
            else: 
                self.df_sol.insert(6, 'SILA', col)

            self.df_sol.rename(columns = {'SILA':'0'}, inplace = True)
            
        else: 
            self.df_sol.rename(columns = {'SILA':'0'}, inplace = True)
            
        # Tableau avec les indices climatiques avec leur date de début et de fin 
        self.df_indices_clim = pd.read_csv(f'{self.repertoire}Station_Data/CEN_SILA/Synthese_saisons_programme.csv')
        self.df_indices_clim['DateGel'] = pd.to_datetime(self.df_indices_clim['DateGel'])
        
        # Décommenter pour remplacer les virgules par des points dans les titres des colonnes au besoin 
# =============================================================================
#         self.df_sol.columns = self.df_sol.columns.str.replace(',', '.')
# =============================================================================
        
    def calcul_risque(self):
        """
        Appel aux méthodes du module pour le calcul du risque de glissement de terrain
        """
        
        # Décommenter ci-bas pour le calcul du risque de glissement de terrain selon la profondeur de dégel
# =============================================================================
#         # Calcul de la profondeur de dégel maximum pour l'année en cours        
#         self.profondeur_degel_max()
#         self.variation_annuel_max_degel()
# =============================================================================
        
        # Calcul du risque de glissement de terrain selon le cumul de degrés-jours
        self.variation_annuel_cumul_dj()
        
        # Écriture des fichiers avec les nouvelles données
        self.ecriture_fichiers()
        
    def profondeur_degel_max(self):
        """
        Méthode pour faire l'interpolation des valeurs et obtenir
        le maximum de dégel par année.
        """
        # Décommenter pour mettre le bon format et ordre de colonne. Ajouter une station dans la méthode au besoin.
# =============================================================================
#         self.colonnes_profondeurs()
# =============================================================================

        # Décommenter la ligne ci-bas pour faire le calcul pour toutes les années du fichier
        self.df_saison_degel = self.df_sol.copy()
    
        # Décommenter les lignes ci-bas pour faire l'interpolation seulement sur l'année climatique en cours - ou la dernière de disponible.
# =============================================================================
#         annees_fichier = self.df_sol['Annee'].unique().tolist()
#         self.df_saison_degel = self.df_sol.loc[self.df_sol['Annee'] == annees_fichier[-1]]
#         self.df_saison_degel.reset_index(drop = True, inplace = True)
# =============================================================================
    
        print(f'Interpolation {self.methode} de la profondeur de dégel maximum ...', end = '\n\n')
    
        for i in range(len(self.df_saison_degel)):
            # Interpolation pchip (shape-preserving piecewise cubic interpolation) sur chaque ligne du dataframe
            ligne = self.df_saison_degel.loc[i, '0':]
            ligne = ligne.astype(float)
            valeurs_nan = ligne.isnull().sum() * 100 / len(ligne)
            
            # Vérifie s'il y a trop de valeur manquante (plus de 30 %)
            if valeurs_nan > 40 :
                self.df_degel.loc[i, 'MaxDegel'] = np.nan
                self.df_degel.loc[i, 'Date'] = self.df_saison_degel.loc[i, 'Date']
        
            else:
                ligne = ligne.dropna()
            
                # Les valeurs sont inférieur à 0 : tout est gelé
                if (ligne < 0).all().any() :
                    self.df_degel.loc[i, 'MaxDegel'] = np.nan
                    self.df_degel.loc[i, 'Date'] = self.df_saison_degel.loc[i, 'Date']
        
                # La profondeur de dégel est plus profonde que les thermistances
                elif (ligne > 0).all().any() :      # Mais dans le dépôt d'argile marine des stations GN et GS, peu probable.
                    self.df_degel.loc[i, 'MaxDegel'] = np.nan
                    self.df_degel.loc[i, 'Date'] = self.df_saison_degel.loc[i, 'Date']
        
                else: 
                    try: 
                        df = ligne.to_frame()
                        df['Profondeur'] = (ligne.index).astype(float)
                        
                        y = df['Profondeur'].to_numpy() # profondeurs dans le sol
                        x = df[i].to_numpy()            # températures du sol
                        
                        if self.methode == 'spline':
                            # Trouver à quel profondeur la température est de 0 °C
                            f = interp1d(x, y, kind = 'cubic')    # Spline cubic
                        
                        if self.methode == 'lineaire':
                            f = interp1d(x, y)                    # Linéaire par défaut
                        
                        temp = 0 
                        
                        # On utilise la fonction obtenue par la méthode interp1d
                        profondeur = f(temp)  
                        
                        if profondeur > 0: 
                            self.df_degel.loc[i, 'MaxDegel'] = np.nan
                            
                        elif profondeur < -2 : 
                            self.df_degel.loc[i, 'MaxDegel'] = np.nan
                            
                        else:                
                            self.df_degel.loc[i, 'MaxDegel'] = profondeur
                        
                        self.df_degel.loc[i, 'Date'] = self.df_saison_degel.loc[i, 'Date']
            
                    except ValueError:
                        self.df_degel.loc[i, 'MaxDegel'] = np.nan
                        self.df_degel.loc[i, 'Date'] = self.df_saison_degel.loc[i, 'Date']
        
        # Colonne avec le maximum de dégel calculé pour chaque date
        self.df_sol = pd.merge(self.df_sol, self.df_degel[['Date', 'MaxDegel']], how = 'outer')
        
        col = self.df_sol['MaxDegel']
        self.df_sol.drop(labels=['MaxDegel'], axis=1, inplace = True)
        
        if station == 'FP2':
            self.df_sol.insert(4, 'MaxDegel', col)
            
        else: 
            self.df_sol.insert(6, 'MaxDegel', col)
            
        self.degel = self.df_degel['MaxDegel'].groupby(self.df_degel['Date'].dt.year).min()
        self.degel = self.degel.to_frame()
        self.degel['Annee'] = self.degel.index
        self.degel.reset_index(drop = True, inplace = True)
        
        for i in range(len(self.degel)): 
            annee_1 = (self.degel['Annee'].iloc[i]) - 1 
            annee_2 = self.degel['Annee'].iloc[i]
            self.degel.loc[i, 'Annee_Clim'] = f'{annee_1}-{annee_2}'
        
        profondeur = round(self.df_sol['MaxDegel'].iloc[-1], 2)
        date = self.df_sol['Date'].iloc[-1]
        profondeur_min = round(self.degel['MaxDegel'].iloc[-1], 2)
        annee = self.degel['Annee'].iloc[-1]
# =============================================================================
#         self.max_degel.loc[self.max_degel['Annee'] == self.degel['Annee'].iloc[-1], 'MaxDegel'] = profondeur
# =============================================================================
        
        self.degel = self.degel[['Annee_Clim', 'Annee', 'MaxDegel']]
        
        print(f'Profondeur de dégel en date du {date} : {profondeur} m', end = '\n\n')
        print(f'Profondeur de dégel maximum {annee} de la {self.station} : {profondeur_min} m', end = '\n\n')

    def variation_annuel_cumul_dj(self): 
        """
        Calcul le pourcentage de variation du cumul de degrés-jours de dégel 
        par rapport à l'année précédente. Si la variation de degrés-jours de dégel 
        est supérieure à 30 %, le risque de glissement de terrain est évalué à élevé. '
        """
        # Décommenter pour calculer le pourcentage de variation de cumul de degrés-jour par rapport à l'année précédente pour chaque année
# =============================================================================
#         # self.df_indices_clim['VariationCumul'] = (self.df_indices_clim['TotalDegel'].pct_change(fill_method ='ffill')) * 100
# =============================================================================

        # Calcul le pourcentage de variation par rapport à l'année précédente pour l'année en cours
        self.df_indices_clim.loc[self.df_indices_clim.index[-1], 'VariationCumul'] = self.df_indices_clim['TotalDegel'].iloc[-2:].pct_change(fill_method ='ffill').iloc[-1] * 100
        
        # Récupérer la statistique pour l'année en cours
        variation_cumul = self.df_indices_clim['VariationCumul'].iloc[-1]
        
        jour = self.df_sila['Jour'].iloc[-1] 
        mois = self.df_sila['Nom_Mois'].iloc[-1]
        annee = self.df_sila['Annee'].iloc[-1]
        
        if variation_cumul > 30:
            self.df_indices_clim.loc[self.df_indices_clim.index[-1], 'NiveauRisque'] = 'Élevé'
            self.df_indices_clim.loc[self.df_indices_clim.index[-1], 'RiskLevel'] = 'High'
            print(Back.RED + 'Élevé. Seuil climatique dépassé.' + Style.RESET_ALL)
            
        elif variation_cumul  < 30 and variation_cumul > 25:
            self.df_indices_clim.loc[self.df_indices_clim.index[-1], 'NiveauRisque'] = 'Modéré'
            self.df_indices_clim.loc[self.df_indices_clim.index[-1], 'RiskLevel'] = 'Moderate'
            risque = 'Attention'
    
        elif variation_cumul  < 25 and variation_cumul > 20:
            self.df_indices_clim.loc[self.df_indices_clim.index[-1], 'NiveauRisque'] = 'Modéré'
            self.df_indices_clim.loc[self.df_indices_clim.index[-1], 'RiskLevel'] = 'Moderate'
            risque = 'Modéré'
            
        elif variation_cumul < 20 :
            self.df_indices_clim.loc[self.df_indices_clim.index[-1], 'NiveauRisque'] = 'Faible'
            self.df_indices_clim.loc[self.df_indices_clim.index[-1], 'RiskLevel'] = 'Low'
            risque = 'Faible'
        
        elif variation_cumul == np.nan:
            self.df_indices_clim.loc[self.df_indices_clim.index[-1], 'NiveauRisque'] = 'Non disponible'
            self.df_indices_clim.loc[self.df_indices_clim.index[-1], 'RiskLevel'] = 'Not available'
            risque = 'Faible'
            
        else: 
            print('Niveau de risque non disponible.')
            self.df_indices_clim.loc[self.df_indices_clim.index[-1], 'NiveauRisque'] = 'Non disponible'
            self.df_indices_clim.loc[self.df_indices_clim.index[-1], 'RiskLevel'] = 'Not available'
            risque = 'Non disponible'
            
        print(Fore.GREEN + f'Niveau de risque pour le {jour} {mois} {annee} est {risque}' + Style.RESET_ALL)
        print(f'Pourcentage de variation du cumul de degrés-jours pour Salluit SILA : {round(variation_cumul, 2)} %',  end = '\n\n')
      
        
    def variation_annuel_max_degel(self):
        """
        Calcul du pourcentage de variation du maximum de dégel par rapport à
        l'année précédente. Si la variation du maximum de dégel est supérieure à 9 %, 
        le risque de glissement de terrain est évalué à élevé. '
        """
        # Décommenter pour ajouter la colonne complète dans df_indices_clim
# =============================================================================
#         self.df_indices_clim = pd.merge(self.df_indices_clim, self.max_degel[['Annee_Clim', 'MaxDegel']], how = 'outer')
# =============================================================================
        
        # Décommenter pour calculer le pourcentage de variation par rapport à l'année précédente pour chaque année du fichier
        self.df_indices_clim.loc[:, 'VariationMaxDegel'] = self.max_degel['MaxDegel'].pct_change(fill_method ='ffill') * 100

        # Calcul le pourcentage de variation par rapport à l'année précédente pour la dernière année disponible
        self.df_indices_clim.loc[self.df_indices_clim.index[-1], 'VariationMaxDegel'] = self.df_indices_clim['MaxDegel'].iloc[-2:].pct_change(fill_method ='ffill').iloc[-1] * 100
        self.df_indices_clim.loc[:, 'VariationMaxDegel'] = self.df_indices_clim.loc[:, 'VariationMaxDegel'].replace(0, np.nan)   # Remplace les 0 par NaN
        
        variation_max_degel = self.df_indices_clim['VariationMaxDegel'].iloc[-1]
        
        jour = self.df_sol['Jour'].iloc[-1] 
        mois = self.df_sol['Nom_Mois'].iloc[-1]
        annee = self.df_sol['Annee'].iloc[-1]

        # On vérifie le pourcentage de valeurs manquantes.
        self.pourcentage_nan = self.df_saison_degel.loc[:, '0'].isnull().sum() * 100 / len(self.df_saison_degel.loc[:, '0'])
        
        # Si le nombre de valeurs manquantes est inférieur à 30 %
        if self.pourcentage_nan > 30:
            self.df_indices_clim.loc[self.df_indices_clim.index[-1], 'NiveauRisqueDegel'] = 'Non disponible'

        else:
        
            if variation_max_degel > 9:
                self.df_indices_clim.loc[self.df_indices_clim.index[-1], 'NiveauRisqueDegel'] = 'Élevé'
                print(Back.RED + 'Élevé. Seuil climatique dépassé.' + Style.RESET_ALL)
                
            elif variation_max_degel  < 9 and variation_max_degel > 7:
                self.df_indices_clim.loc[self.df_indices_clim.index[-1], 'NiveauRisqueDegel'] = 'Modéré'
                risque = 'Attention, seuil bientôt dépassé'
        
            elif variation_max_degel  < 7 and variation_max_degel > 5:
                self.df_indices_clim.loc[self.df_indices_clim.index[-1], 'NiveauRisqueDegel'] = 'Modéré'
                risque = 'Modéré'
                
            elif variation_max_degel < 5 :
                self.df_indices_clim.loc[self.df_indices_clim.index[-1], 'NiveauRisqueDegel'] = 'Faible'
                risque = 'Faible'
            
            elif variation_max_degel == np.nan:
                self.df_indices_clim.loc[self.df_indices_clim.index[-1], 'NiveauRisqueDegel'] = 'Non disponible'
                risque = 'Faible'
                
            else: 
                print('Niveau de risque non disponible.')
                self.df_indices_clim.loc[self.df_indices_clim.index[-1], 'NiveauRisqueDegel'] = 'Non disponible'
                risque = 'Non disponible'
            
        print(Fore.GREEN + f'Niveau de risque selon la profondeur de dégel en date du {jour} {mois} {annee} est {risque}' + Style.RESET_ALL)
        
        print(f'Pourcentage de variation du maximum de dégel pour la {self.station} : {round(variation_max_degel, 2)} %',  end = '\n\n')
    
        
    def colonnes_profondeurs(self):
        """
        Méthode pour mettre en forme les noms des colonnes. 
        """
        
        if self.station == 'Station SAL4':
            self.df_sol = self.df_sol[['Date', 'Annee', 'Mois', 'Jour', 'Nom_Mois', '0', '-0.02', '-0.2', '-0.5', '-0.75', 
                                   '-1.0', '-1.25', '-1.5', '-1.75', '-2.0', '-2.25', 
                                   '-2.5', '-2.7', '-2.9']]
            
        if self.station == 'Station_GN' or self.station == 'Station_GS':
            self.df_sol.columns = ['Date', 'Annee_Clim', 'Annee', 'Mois', 'Jour', 'Nom_Mois','0', '-0.02',
                              '-0.1', '-0.2', '-0.3', '-0.4', '-0.5', '-0.6', '-0.7', '-0.75',
                              '-0.8', '-0.85', '-0.9', '-0.95', '-1', '-1.05', '-1.1',
                              '-1.15', '-1.2', '-1.25', '-1.3', '-1.4', '-1.5', '-1.7', '-2']
                
            self.df_sol = self.df_sol[['Date', 'Annee_Clim', 'Annee', 'Mois', 'Jour', 'Nom_Mois', '0', '-0.02',
                             '-0.1', '-0.2', '-0.3', '-0.4', '-0.5', '-0.6', '-0.7', '-0.75',
                             '-0.8', '-0.85', '-0.9', '-0.95', '-1', '-1.05', '-1.1',
                             '-1.15', '-1.2', '-1.25', '-1.3', '-1.4', '-1.5', '-1.7', '-2']]
            
        if self.station == 'Station FP2':
            self.df_sol = self.df_sol[['Date', 'Annee', 'Mois', 'Jour', '0', '-0.25', '-1', '-1.5',
                                       '-2', '-4', '-6', '-8', '-10', '-12', '-15', '-20', '-27']]

        print(self.df_sol.head())
        
    def ecriture_fichiers(self):
        """
        Écriture des fichiers avec les nouvelles données selon le nom de la station et la 
        méthode d'interpolation en entrée.
        """
        
        # Décommenter si calcul de la profondeur de dégel 
# =============================================================================
#         self.max_degel.to_csv(f'{self.repertoire}Station_Data/Max_Degel/Max_Degel_{self.station}_{self.methode}.csv', index = False, float_format = '%.4f')
#         self.df_sol.to_csv(f'{self.repertoire}C:/Users/sagau63/Documents/GitHub/Code_Station/Programme_Pergelisol/Data_CSV/Station_Data/Max_Degel/Max_Degel_{self.station}_tsol.csv', index = False, float_format = '%.4f')
# =============================================================================
        self.df_indices_clim.to_csv(f'{self.repertoire}Station_Data/CEN_SILA/Synthese_saisons_programme.csv', index = False, float_format = '%.4f')
        
        # Récupérer la date 
        date = datetime.today().date()
        dernier_jour_mois = (pd.to_datetime(date) + MonthEnd(1)).date()
        
        # S'il s'agit du dernier jour du mois, on fait un fichier excel back up 
        if date == dernier_jour_mois:
# =============================================================================
#             self.max_degel.to_excel(f'{self.repertoire}Station_Data/Max_Degel/Excel/Max_Degel_{self.station}_{self.methode}.xlsx', index = False, float_format = '%.4f')
#             self.df_sol.to_excel(f'{self.repertoire}Station_Data/Max_Degel/Excel/Max_Degel_{self.station}_tsol.xlsx', index = False, float_format = '%.4f')
# =============================================================================
            self.df_indices_clim.to_excel('{self.repertoire}Station_Data/Max_Degel/Excel/Synthese_saisons_programme.xlsx', index = False, float_format = '%.4f')

if __name__ == '__main__':
    
# Module à installer pour ouvrir le fichier à partir de la boîte de dialogue
# =============================================================================
#   conda install -c conda-forge easygui 
# =============================================================================

    fichier_sol = easygui.fileopenbox()
    fichier_sila = easygui.fileopenbox()
    station = input('Entrez le nom de la station sans espace : ')
    
    # Si fichier Excel : 
    df_sol = pd.read_excel(fichier_sol, engine = 'openpyxl')
    
    # Si fichier csv
# =============================================================================
#     df_sol = pd.read_csv(fichier_sol)
# =============================================================================
    
    df_sila = pd.read_csv(fichier_sila)
    df_sila['Date'] = pd.to_datetime(df_sila['Date']) # bon format de date
    
    repertoire = 'C:/Users/sagau63/Documents/GitHub/Code_Station/Programme_Pergelisol/Data_CSV/'
    
    risque = RisqueGlissementTerrain(df_sol, df_sila, station, repertoire) 

# Méthode pour le calcul du niveau de risque et de la profondeur de dégel
# =============================================================================
#     risque.calcul_risque()
#     risque.profondeur_degel_max()
# =============================================================================

