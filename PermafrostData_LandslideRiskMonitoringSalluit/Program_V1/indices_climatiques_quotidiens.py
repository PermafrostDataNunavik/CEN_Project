# -*- coding: utf-8 -*-
"""
Created on Mon May 31 10:36:13 2021
@author: Sarah Gauthier et Michel Allard
sarah.gauthier.1@ulaval.ca
Centre d'études nordiques, Université Laval

Module pour la détermination des dates de début des saisons de gel et de dégel 
pour calculer les indices climatiques en fonction des années climatiques.

Indices climatiques possibles à calculer avec ce module: 
    - Indice de gel
    - Indice de dégel 
    - Durée saison de gel
    - Durée saison de dégel
    - Ratio Fi/Ti
    - Facteur-n
    - TMAA

Ces indices sont importants, puisqu'ils serviront à déterminer le niveau 
de risque de glissement de terrain à Salluit (module calcul_risque_glissement.py).

--------------------
Station SALLUIT SILA 
--------------------
    Latitude :       62.1918
    Longitude :     -75.6379
    Altitude :       42 m
"""

# Importation des modules
import pandas as pd
from datetime import datetime, timedelta
from pandas.tseries.offsets import MonthEnd
from colorama import Fore, Style
import numpy as np
from signal_risque_glissement import AlerteRisqueCourriel
import easygui

class IndicesClimatiques:
    
    def __init__(self, df_sila, repertoire):
        """
        Création des tableaux de données à partir des fichiers sur le disque local. 

        df_sila (DataFrame) : Tableau de données mis en forme avec la température de l'air et 
                              le cumul de degrés-jours selon la saison de gel et de dégel.
                              
        df_indices_clim (DataFrame) : Tableau de données avec les dates de débuts de saisons de gel 
                                 et de dégel et avec les indices climatiques calculées à partir
                                 de ces dates.
                                 
        nouvelles_données (DataFrame) : Tableau de données avec les dates de débuts de saisons de gel 
                                        et de dégel et avec les indices climatiques calculées à partir
                                        de ces dates.
        """
        # Chemin absolu de l'emplacement du programme et des fichiers nécessaires à l'exécution
        self.repertoire = repertoire
        
        # Définir l'emplacement des fichiers
        self.fichier_saisons = f'{self.repertoire}Station_Data/CEN_SILA/Synthese_saisons_programme.csv'
        self.fichier_sila = f'{self.repertoire}Station_Data/CEN_SILA/SILA_Salluit_AirTemp.csv'
        
        # Tableau de données de température de l'air avec les données ajoutées
        self.df_sila = df_sila
        self.df_sila['Date'] = pd.to_datetime(self.df_sila['Date'])
        
        # Lecture du fichier avec les dates des saisons et indices climatiques
        self.df_indices_clim = pd.read_csv(self.fichier_saisons)
        
        # Bon format de colonne
        self.df_indices_clim['DateGel'] = pd.to_datetime(self.df_indices_clim['DateGel'])
        self.df_indices_clim['DateDegel'] = pd.to_datetime(self.df_indices_clim['DateDegel'])
        self.df_indices_clim['FinGel'] = pd.to_datetime(self.df_indices_clim['FinGel'])
        self.df_indices_clim['FinDegel'] = pd.to_datetime(self.df_indices_clim['FinDegel'])
        
        self.date_gel = self.df_indices_clim['DateGel'].iloc[-1]
        self.fin_gel = self.df_indices_clim['FinGel'].iloc[-1]
        self.date_degel = self.df_indices_clim['DateDegel'].iloc[-1]
        self.fin_degel = self.df_indices_clim['FinDegel'].iloc[-1]
        
# =============================================================================
#         if pd.isnull(date_degel) and pd.isnull(fin_degel) and pd.isnull(fin_gel):
#             self.saison = 'Gel'
#         
#         else:
#             self.saison = 'Degel'
# =============================================================================
        
    def calcul_indices(self, gel, degel):
        """
        Appel aux différentes méthodes de la classe pour le calcul des indices climatiques
        pour chaque saison.
        """
        
        # Appel à la méthode pour mettre en forme les tableaux de données
        self.donnees_sila_tableau()
        self.indices_climatiques_tableau()
    
        # Calcul des séries pour identifier saison gel et dégel
        self.serie_saisons(gel)
        self.serie_saisons(degel)
    
        # Calcul des moyennes mobiles et création de la colonne dans le dataframe principal
        self.annee_climatique(gel)
        self.annee_climatique(degel)
    
        # Calcul du cumul de degrés-jour de gel et de dégel
        self.cumul_quotidien(gel)
        
        # Si on est en pleine saison de dégel
        if not pd.isnull(self.date_degel) and pd.isnull(self.fin_degel) :
            self.cumul_quotidien(degel)
            self.variation_cumul()
        
            # Classe pour déterminer si le niveau de risque nécessite d'envoyer une alerte
            destinataires = ['sarah.gauthier.1@ulaval.ca'] #'landuse@krg.ca', Liste de destinataire du signal d'alerte. Ajouter des adresses courriel au besoin
            alerte = AlerteRisqueCourriel(destinataires, repertoire) # Argument en entrée : à qui envoyer l'alerte
            alerte.generer_rapports()
        
        print(self.df_sila[['Date', 'Nom_Mois', 'CUMUL_DJ']].tail(), end = '\n\n')
    
        # Écriture des nouvelles données
        self.ecriture_cumul()
    
    def variation_cumul(self):
        """
        Calcul le pourcentage de variation du total cumulatif de degrés-jours de dégel par rapport 
        à l'année précédente. 
        """
        
        self.df_indices_clim.loc[self.df_indices_clim.index[-1], 'VariationCumul'] = self.df_indices_clim['TotalDegel'].iloc[-2:].pct_change(fill_method ='ffill').iloc[-1] * 100

    def cumul_quotidien(self, saison):
        """
        Calcul des degrés-jours de l'année climatique en court selon les dates de 
        début et de fin de la saison donnée.
        """
# =============================================================================
#         try: 
# =============================================================================
        
        # saison de gel ou de dégel 
        debut_cumul =  self.df_indices_clim['Date'+saison].iloc[-1]
        fin_cumul =  self.df_indices_clim['Fin'+saison].iloc[-1]
        
        # Le cumul continu tant que la saison n'est pas fini
        if pd.isnull(fin_cumul): 
            fin_cumul = self.df_sila['Date'].iloc[-1]
    
        # On récupère l'index auquel le calcul du cumul doit commencer et se terminer
        idx = self.df_sila['CUMUL_DJ'].loc[self.df_sila['Date'] >= debut_cumul].index[0]
        idx_fin = self.df_sila['CUMUL_DJ'].loc[self.df_sila['Date'] <= fin_cumul].index[-1]
        date_range = (self.df_sila['Date'] >= debut_cumul) & (self.df_sila['Date'] <= fin_cumul)
        
        # On vérifie s'il n'y a pas trop de valeurs manquantes.
        self.pourcentage_nan = self.df_sila.loc[date_range, 'SILA'].isnull().sum() * 100 / len(self.df_sila.loc[date_range, 'SILA'])
        
        # Si le nombre de valeurs manquantes est inférieur à 30 %
        if self.pourcentage_nan < 30 :

            # On fait le cumul sur ces valeurs directement dans le dataframe
            self.df_sila.loc[date_range, 'CUMUL_DJ'] = self.df_sila['SILA'].iloc[idx:idx_fin+1].cumsum().abs()
            cumul_saison = self.df_sila['SILA'].iloc[idx:idx_fin+1].cumsum().abs().iloc[-1]
            self.df_indices_clim.loc[self.df_indices_clim.index[-1], 'Total'+saison] = cumul_saison
            cumul_court = "{:.0f}".format(cumul_saison)
            
            # Moyenne pour l'année climatique en cours
            moyenne_annuelle = self.temperature_moyenne()
            self.df_indices_clim.loc[self.df_indices_clim.index[-1], 'Moyenne'] = moyenne_annuelle
            
            # Facteur-n pour l'année climatique en cours
            ratio = self.ratio_fi_ti()
            self.df_indices_clim.loc[self.df_indices_clim.index[-1], 'RatioFiTi'] = ratio

            # Nombre de jours avec une température moyenne supérieur à 0 °C
            jours = self.jours_superieur_0(self.df_sila)
            self.df_indices_clim.loc[self.df_indices_clim.index[-1], 'Nb_Jours_Sup_0'] = jours
            
        # Sinon, le cumul est non disponible
        else: 
            self.df_indices_clim.loc[self.df_indices_clim.index[-1], 'Total'+saison] = np.nan
            self.df_indices_clim.loc[self.df_indices_clim.index[-1], 'Moyenne'] = np.nan
            self.df_indices_clim.loc[self.df_indices_clim.index[-1], 'RatioFiTi'] = np.nan

        if saison == 'Degel':
            print(f'Total de degrés-jours de {saison} en date du {fin_cumul} : {cumul_court}.')
                
        else: 
            annee_clim = self.df_indices_clim['Annee_Clim'].iloc[-1]
            print(f'Total de degrés-jours pour la saison de {saison} de {annee_clim} est de {cumul_court}.', end = '\n\n')
    
        self.df_sila = self.df_sila[['Date', 'Annee_Clim', 'Annee', 'Mois', 'Jour', 'Nom_Mois', 'SILA', 'CUMUL_DJ']]

# =============================================================================
#         except IndexError: 
#             print('Problème avec le calcul du cumul.')
#             
#         except ValueError: 
#             print('Problème avec le calcul du cumul.')
# =============================================================================
        
    
    def temperature_moyenne(self):
        """
        Température moyenne de l'air annuelle selon les années climatiques.
        Return
        -------
            moyenne_annuelle (float) La moyenne annuelle de l'année climatique. 
        """
        
        debut = self.df_indices_clim['DateGel'].iloc[-1]
        fin = self.df_indices_clim['FinDegel'].iloc[-1]
        
        if pd.isnull(fin): 
            fin = self.df_sila['Date'].iloc[-1]
    
        temperature = self.df_sila[['Date', 'SILA']].loc[(self.df_sila['Date'] >= debut) & (self.df_sila['Date'] <= fin)]
        moyenne_annuelle = temperature['SILA'].mean()
        
    # =============================================================================
    #     dates_saisons.loc[dates_saisons.index[-1], 'Moyenne'] = temperature
    # =============================================================================
        
        return moyenne_annuelle
    
    def jours_superieur_0(self, data_frame):
        """
        Calcul le nombre de jour supérieur à 0 °C pour une année donnée.
        Parameters
        ----------
        data_frame (DataFrame): tableau de données en entrée avec lequel effectuer le calcul. 
        """
        nb_jours = pd.DataFrame(columns = ['Annee_Clim', 'Nb_Jours'])

        # Pour chaque année climatique
        for i in range(len(self.df_indices_clim)):

            df = pd.DataFrame(columns = ['Annee_Clim', 'Nb_Jours'])

            debut = pd.to_datetime(self.df_indices_clim['DateGel']).iloc[i]
            fin  = pd.to_datetime(self.df_indices_clim['FinDegel']).iloc[i]
            
            if pd.isnull(fin):
                fin = data_frame['Date'].iloc[-1]
                    
            df_annee = data_frame.loc[(data_frame['Date'] >= debut) & (data_frame['Date'] <= fin)] 
            
            # Trouver l'année climatique en question
            df.loc[0,'Annee_Clim'] = df_annee['Annee_Clim'].unique()[0]
            
            # Compte le nombre de jours avec une température supérieure à 0 °C
            df.loc[0,'Nb_Jours'] = df_annee['SILA'].loc[df_annee['SILA'] > 0].count()
            
            nb_jours = nb_jours.append(df)
        
        nb_jours.reset_index(drop = True, inplace = True)
        
        # Nombre de jours > 0°C pour l'année en jours
        nb_jours_quotidien = nb_jours['Nb_Jours'].iloc[-1]
        return nb_jours_quotidien
        
        # Décommenter pour avoir le nombre de jour > 0 °C pour toutes les années + commentez deux lignes ci-haut
# =============================================================================
#         return nb_jours
# =============================================================================
    
    def ratio_fi_ti(self):
        """
        Calcul le ratio entre l'indice de gel (Fi) et l'indice de dégel (Ti).
        """
        # Récupérer les indices de gel (freezing index ) et de dégel (thawing index)
        fi = self.df_indices_clim['TotalGel'].iloc[-1]
        ti = self.df_indices_clim['TotalDegel'].iloc[-1]
    
        #  Calcul du ratio Fi/Ti
        ratio = fi/ti
                
        return ratio

    def dates_annees_clim(self, saison_debut, saison): 
        """
        Identification des dates de début et de fin des saisons de gel et de dégel. 
        """
        
        date_fichier = self.df_indices_clim['Date'+saison].iloc[-1]
        
        fin_gel = self.df_indices_clim['FinGel'].iloc[-1]
        
    # =============================================================================
    #   Dates saisons de gel 
    # =============================================================================
        if saison == 'Gel':
            
            # S’il s'agit d'une nouvelle saison
            if saison_debut != date_fichier:
                
                # Ajouter une ligne vide à remplir avec les nouvelles valeurs
                self.df_indices_clim = self.df_indices_clim.append(pd.Series(dtype = 'float64'), ignore_index=True)
                
                # Format de la date
                saison_debut = pd.to_datetime(saison_debut)
                
                # Colonne avec les années climatiques
                annee_debut = saison_debut.year
                annee_fin =  annee_debut + 1
                
                self.df_indices_clim.loc[self.df_indices_clim.index[-1], 'Annee_Clim'] =  f'{annee_debut}-{annee_fin}'
                self.df_indices_clim.loc[self.df_indices_clim.index[-1], 'DateGel'] = saison_debut
                
                # Date de fin de la saison de dégel et début de la saison de gel
                self.df_indices_clim.loc[self.df_indices_clim.index[-2], 'FinDegel'] = pd.to_datetime(saison_debut - timedelta(days =1))
        
                # Calcul de la durée de la saison de dégel précédente (nombre de jours)
                duree_degel = abs((self.df_indices_clim['DateDegel'].iloc[-2] - self.df_indices_clim['FinDegel'].iloc[-2]).days)
                self.df_indices_clim.loc[self.df_indices_clim.index[-2], 'DureeDegel'] = duree_degel
                self.df_indices_clim.loc[self.df_indices_clim.index[-1], 'DureeDegel'] = 'N/A'
            
                # Indice de dégel 
                self.df_indices_clim.loc[self.df_indices_clim.index[-2], 'TotalDegel'] = self.df_sila['CUMUL_DJ'].loc[self.df_sila['Date'] == self.df_indices_clim['FinDegel']].iloc[-1]
                self.df_indices_clim.loc[self.df_indices_clim.index[-1], 'TotalDegel'] = 'N/A'

                # Ratio Fi/Ti
                self.df_indices_clim.loc[self.df_indices_clim.index[-2], 'RatioFiTi'] = self.df_indices_clim['TotalGel'].iloc[-2] / self.df_indices_clim['TotalDegel'].iloc[-2]
                self.df_indices_clim.loc[self.df_indices_clim.index[-1], 'RatioFiTi'] = 'N/A'
                
                # Moyenne pour l'année climatique terminée
                TMAA = self.df_sila['SILA'].loc[(self.df_sila['Date'] >= self.df_indices_clim['DateGel'].iloc[-2]) & (self.df_sila['Date'] <= self.df_indices_clim['DateDegel'].iloc[-2])]
                self.df_indices_clim.loc[self.df_indices_clim.index[-2], 'Moyenne'] = TMAA['SILA'].mean()
                
    # =============================================================================
    #   Dates saisons de dégel
    # =============================================================================
        elif saison == 'Degel':
            
            if pd.isnull(fin_gel):
                print('Saison de dégel terminée.')
            
            else: 
                
                if saison_debut != date_fichier:
                    # Date de fin de la saison de gel et début de la saison de dégel
                    self.df_indices_clim.loc[self.df_indices_clim.index[-1], 'FinGel'] = saison_debut - timedelta(days =1)
                    self.df_indices_clim.loc[self.df_indices_clim.index[-1], 'DateDegel'] = saison_debut
                    
                    # Calcul de la durée de la saison de gel précédente (nombre de jours)
                    duree_gel = abs((self.df_indices_clim['DateGel'].iloc[-1] - self.df_indices_clim['FinGel'].iloc[-1]).days)
                    self.df_indices_clim.loc[self.df_indices_clim.index[-1], 'DureeGel'] = duree_gel
                    
        else: 
            print(f'Date de début de la saison de {saison} déjà identifié.')
        
    def annee_climatique(self, saison):
        """
        Fonction pour le calcul de la moyenne mobile. La moyenne mobile est calculée
        sur les valeurs des saisons de gel et de dégel pour identifier les dates de 
        commencement des saisons. La saison de dégel ne peut pas commencer avec un valeur
        de température négative et vis-versa.
        
        Retourne un tuple avec deux DataFrames
            1. Le dataframe avec l'identification des séries de jours consécutifs de gel et de dégel 
               et le calcul de la moyenne mobile;
            2. Les dates de débuts des saisons selon l'année climatique, selon la saison.
        """
        
        # Liste avec les années dans le dataframe
        annees = pd.to_datetime(self.df_sila['Date']).dt.year.unique().tolist()[-2:]
        
        # debut_saison = dates_saisons['Date'+saison].iloc[-1]
        fin_degel = self.df_indices_clim['FinDegel'].iloc[-1]   # On récupère la dernière date de fin
        
        try : 
        
            # Pour l'année climatique en cours : 
            if saison == 'Degel':
                annee = annees[1]
                
            if saison == 'Gel':
                if pd.isnull(fin_degel):         # On vérifie si la saison n'est pas terminée.
                    annee = annees[1]            # Sinon, on vérifie si la nouvelle année est commencée
                else:     
                    annee = annees[0]
    
            debut = self.df_sila['Date'].loc[(self.df_sila[saison] >= 3) & (self.df_sila['Annee'] == annee)]
            
            if debut.empty: 
               saison_debut = self.df_indices_clim['Date'+saison].iloc[-1]
               # self.df_indices_clim.loc[self.df_indices_clim.index[-1], 'Date'+saison] = 'NaN'
                                                   
            else: 
                # Colonne avec la date du début de la séquence = une série de plus de 3 jours avec des valeurs négatives pour la saison de gel (inverse pour la saison de dégel)
                debut = self.df_sila['Date'].loc[(self.df_sila[saison] >= 3) & (self.df_sila['Annee'] == annee)].iloc[0]
                
                # Pour que la moyenne mobile commence à la date de la série avec une fenêtre de 9 jours, on commence le calcul avec les 4 valeurs précédentes 
                date_debut_moyenne = debut - timedelta(days=4)
                
                # La moyenne est calculé d'abord pendant 10 jours
                fin = debut + timedelta(days = 10)
            
                df_moyenne = self.df_sila[['Date', 'SILA', 'Debut_Serie']].loc[(self.df_sila['Date'] >= date_debut_moyenne) & (self.df_sila['Date'] <= fin)]        
                
                # Calcul de la moyenne mobile avec une fenêtre de 9 jours, pendant 10 jours
                df_moyenne['Moy_Mobile_9'] = self.df_sila['SILA'].loc[:].rolling(window=9, min_periods=3).mean()
                
    # Tant que les critères pour déterminer la date de début de la saison ne sont pas satisfaits...
    # =============================================================================
                moyenne_terminee = False
                
                while not moyenne_terminee:
                    # Critère pour déterminer la date : 
                    if saison == 'Gel':
                        #   1. La dernière valeur de la moyenne mobile calculée doit être négative;
                        fin_moyenne = df_moyenne['Moy_Mobile_9'].iloc[-1] < 0
        
                        #   2. Les 3 dernières valeurs de la moyenne sont négatives
                        jours_moyenne = df_moyenne['Moy_Mobile_9'].iloc[-3:] < 0
        
                    if saison == 'Degel':
                        #   1. La dernière valeur de la moyenne mobile calculée doit être positive;
                        fin_moyenne = df_moyenne['Moy_Mobile_9'].iloc[-1] > 0 
        
                        #   2. Les 3 dernières valeurs de la moyenne sont positives
                        jours_moyenne = df_moyenne['Moy_Mobile_9'].iloc[-3:] > 0
                
                    # si la dernière valeur de la moyenne n'est pas négative : 
                    if not fin_moyenne & jours_moyenne.all().any(): 
                            # On recalcul la moyenne mobile, qui commence 5 jours plus tard
                            date_debut_moyenne = date_debut_moyenne + timedelta(days=5)
                            fin_2 = date_debut_moyenne + timedelta(days =10)
                            
                            if date_debut_moyenne > self.df_sila['Date'].iloc[-1]:
                                moyenne_terminee = True
                                saison_debut =  self.df_indices_clim['Date'+saison].iloc[-1]
                                
                            else:
                                df_moyenne = self.df_sila[['Date', 'SILA', 'Debut_Serie']].loc[(self.df_sila['Date'] >= date_debut_moyenne) & (self.df_sila['Date'] <= fin_2)]        
                                df_moyenne['Moy_Mobile_9'] = self.df_sila['SILA'].loc[:].rolling(window=9, min_periods=3).mean()
                                moyenne_terminee = False
                                
                    else:
                        # La température de l'air est négative et il s'agit d'un début de série (température de l'air positive pour la saison de dégel)
                        if saison == 'Gel':
                            saison_debut = df_moyenne['Date'].loc[(df_moyenne['SILA'] < 0) & (df_moyenne['Debut_Serie'] == True)].iloc[0]
                        
                        if saison == 'Degel':
                            saison_debut = df_moyenne['Date'].loc[(df_moyenne['SILA'] > 0) & (df_moyenne['Debut_Serie'] == True)].iloc[0]
                                            
                        # Les critères sont satisfaits et nous avons la date de début. On sort donc de la boucle.
                        moyenne_terminee = True
    # =============================================================================

            # On ajoute la date de début de la saison en cours et de fin de la saison précédente
            self.dates_annees_clim(saison_debut, saison)
            
        except ValueError: 
            print('Problème avec le calcul de la moyenne mobile.')

    def serie_saisons(self, saison): 
        """
        Fonction pour identifier le nombre de jours successifs où la température est 
        supérieure à 0 °C pour la saison de dégel et inférieure à 0 °C pour la saison de gel. 
        Ces séries permettront de déterminer la date de début des saisons. 
    
        Parameters
        ----------
        data_frame (DataFrame) avec les données de température de l'air de la station SILA.
        saison (str) saison en entrée (Gel ou Degel) dont ont souhaite voir les séries. 
        """
        
        try : 
            
            # L'année climatique dans laquelle se déroule la saison
            annees = pd.to_datetime(self.df_sila['Date']).dt.year.unique().tolist()[-2:]
            annee_clim = (self.df_sila['Annee'] == annees[0]) | (self.df_sila['Annee'] == annees[1])
            
            if saison == 'Degel':
                # Les valeurs doivent être dans les mois potentiels de début de la saison de dégel
                mois = self.df_sila['Nom_Mois'].str.contains('Avril|Mai|Juin')
                
                # Température inférieure à 0°C
                c1 = self.df_sila['SILA'] > 0
                
            if saison == 'Gel':
                # Les valeurs doivent être dans les mois potentiels de début de la saison de gel
                mois = self.df_sila['Nom_Mois'].str.contains('Septembre|Octobre|Novembre')
                
                # Température inférieure à 0°C
                c1 = self.df_sila['SILA'] < 0
            
            # Calcul le cumul des jours successifs qui ne respecte pas le critère c1
            g = (c1 != c1.shift()).cumsum()
        
            # Début de chaque série supérieur à 0 si dégel et inférieur à 0 si gel.
            self.df_sila['Debut_Serie'] = c1.ne(c1.shift())
        
            # Compte le nombre d'occurrences dans chaque série
            self.df_sila[saison] =  self.df_sila.groupby(g).Date.transform('count')
        
            # Cherche le nombre d'occurrences par série pour les mois de ciblés
            self.df_sila[saison] = self.df_sila[saison].where(c1 & mois & annee_clim)
            debut = self.df_sila['Debut_Serie'] == True
            
            # Si la série fait plus de quatre jours 
            jours = self.df_sila[saison] >= 4
        
            # Valeur de la longueur de la série attribuée à la colonne, selon les trois conditions    
            self.df_sila[saison] = self.df_sila[saison].where(debut & jours & mois)
            
            # Rempli les valeurs NaN entre les saisons avec la valeur 0
            self.df_sila[saison] = self.df_sila[saison].fillna(0)
            
            return self.df_sila
        
        except ValueError:
            print('ValueError.')
        except IndexError:
            print('IndexError.')
    
    def cumul_annee_clim(self, saison):
        
        try: 
            
            # Variable annee et annee_2 correspondent aux années de données disponibles dans le fichier pour lesquelles
            # il faut calculer le cumul de degrés-jours
            df_saison = pd.DataFrame(columns = ['Jour_Mois', 'Nom_Mois'])
            
            # Pour chaque année dans le fichier de données
            for i in range(0, (len(self.df_indices_clim))):
                # Établir l’étendue de date des colonnes
                
                annee_clim = self.df_indices_clim['Annee_Clim'].iloc[i]
                annee_1 = annee_clim[0:4]
                annee_2 = annee_clim[5:]
                
                # Récupérer les dates de début et de fin selon la saison
                if saison == 'Degel':
                    debut_saison =  self.df_indices_clim['DateDegel'].iloc[i] 
                    fin_saison =  self.df_indices_clim['FinDegel'].iloc[i]
                        
                    debut_range = pd.Timestamp(f'{annee_2}-04-15')
                    fin_range = pd.Timestamp(f'{annee_2}-11-15')
                    
                if saison == 'Gel':
                    debut_saison =  self.df_indices_clim['DateGel'].iloc[i] 
                    fin_saison =  self.df_indices_clim['FinGel'].iloc[i]
                    
                    debut_range = pd.Timestamp(f'{annee_1}-09-15')
                    fin_range = pd.Timestamp(f'{annee_2}-06-15')
                
                if pd.isnull(fin_saison): 
                    fin_saison =  self.df_sila['Date'].iloc[-1]
    
                # Range de date fixe 
                date_range = pd.date_range(start=debut_range, end = fin_range, freq = 'D')
                
                # Ajouter les colonnes avec les valeurs de cumul
                cumul = self.df_sila[['Date', 'SILA']].loc[(self.df_sila['Date'] >= debut_saison) & (self.df_sila['Date'] <= fin_saison)]        
                cumul['CUMUL_DJ'] = cumul['SILA'].cumsum().abs()
                
                # Récupérer la somme des degrés-jours et l'ajouter dans le fichier synthèse de saisons 
                self.df_indices_clim.loc[i, 'Total'+saison] = cumul['CUMUL_DJ'].iloc[-1]
                
                # Mettre le bon titre de colonne avec l'année climatique et la range de date 
    # =============================================================================
    #             cumul = cumul.rename(columns = {'CUMUL_DJ': annee_clim})
    # =============================================================================
                cumul = cumul.set_index('Date').reindex(date_range).rename_axis('Date').reset_index()
        
                # Format des dates et création de la colonne Jour_Mois pour des fins de comparaison interannuelle
                cumul['Date'] = pd.to_datetime(cumul['Date'])
                cumul['Nom_Mois'] = cumul['Date'].dt.month_name(locale = 'French')
                cumul['Jour_Mois'] = cumul['Date'].dt.strftime('%d-%m')
                cumul['Annee_Clim'] = annee_clim
                cumul = cumul[['Annee_Clim', 'Jour_Mois', 'Nom_Mois', 'SILA', 'CUMUL_DJ']]
                
    # =============================================================================
    #             cumul = cumul[['Jour_Mois', 'Nom_Mois', annee_clim]]
    # =============================================================================
        
                # On ajoute l'année calculée au dataframe total
    # =============================================================================
    #             df_saison = pd.merge(df_saison, cumul, how='outer', on=['Jour_Mois', 'Nom_Mois'])        
    # =============================================================================
                df_saison = df_saison.append(cumul, ignore_index = True)
                
            
            # Si saison de gel, on réindexer pour les années bissextiles. Sinon, c'est ok. 
            if saison == 'Gel': 
                idx = df_saison.loc[df_saison['Jour_Mois'] == '01-03'].index[0]
                df_saison.index.values[-1] = idx
                df_saison.sort_index(ignore_index = True, inplace = True)            
                df_saison.reset_index(drop = True, inplace = True)
            
            return df_saison
        
        # Intercepte l'erreur si l'année n'est pas encore terminée et que la valeur n'est pas disponible
        except IndexError: 
            print(f'Valeur non disponible pour la saison de {saison} {annee_clim}.', end = '\n\n')
            return df_saison

    def donnees_sila_tableau(self):
        """
        Ajoute les nouvelles données et met en forme le data_frame 
        de données de température de l'air de la station SILA à Salluit. 
            - Ordonne les dates;
            - Supprime les données dupliquées;
            - Comble les trous;
            - Réinitialise l'index;
            - Bon format de la colonne date.
    
            self.df_sila (DataFrame) Tableau de données nettoyés avec les nouvelles données.
        """
        
        # self.df_sila = self.df_sila.append(self.nouvelles_donnees)
        
        self.df_sila['Date'] = pd.to_datetime(self.df_sila['Date']).dt.date
    
        # S'assurer que les dates sont en ordres + supprimer les doublons
        self.df_sila = self.df_sila.sort_values(by = ['Date'])
        self.df_sila = self.df_sila.drop_duplicates(subset=['Date'])
        
        # Rempli les dates manquantes avec 0
        self.df_sila = self.df_sila.set_index('Date').asfreq('D').reset_index()
        self.df_sila['Annee'] = pd.to_datetime(self.df_sila['Date']).dt.year
        self.df_sila['Mois'] = pd.to_datetime(self.df_sila['Date']).dt.month
        self.df_sila['Jour'] = pd.to_datetime(self.df_sila['Date']).dt.day
        self.df_sila['Nom_Mois'] = pd.to_datetime(self.df_sila['Mois'], format='%m').dt.month_name(locale = 'French')
        
        cols = ['Annee', 'Mois', 'Jour', 'SILA', 'CUMUL_DJ']
        self.df_sila[cols] = self.df_sila[cols].apply(pd.to_numeric, errors='coerce')
        
        # Remet le bon format de date
        self.df_sila['Date'] = pd.to_datetime(self.df_sila['Date']).dt.date

    def colonne_annee_clim(self):
        """
        Colonne avec l'année climatique pour l'année en cours.
        """

        # Colonne année_clim
        for i in range(len(self.nouvelles_lignes)):
            annee_debut = (self.df_indices_clim['DateGel'].iloc[-1]).year
            annee_fin  = (self.df_indices_clim['FinDegel'].iloc[-1]).year
                
            if pd.isnull(annee_fin):
                annee_fin = annee_debut + 1
                
            self.nouvelles_lignes.loc[self.nouvelles_lignes.index[i], 'Annee_Clim'] = f'{annee_debut}-{annee_fin}'
            index = list(self.nouvelles_lignes.index)[i]
            self.df_sila.loc[index, 'Annee_Clim'] = f'{annee_debut}-{annee_fin}'
    
    def colonne_annee_clim_tout(self, data_frame):
        """
        Colonne avec l'année climatique pour tout le tableau de données.
        """
        # Création de la colonne qui va contenir année climatique
        data_frame['Annee_Clim'] = ''
        
        # Colonne année_clim
        for i in range(len(self.df_indices_clim)-1):
            debut = pd.to_datetime(self.df_indices_clim['DateGel']).iloc[i]
            fin  = pd.to_datetime(self.df_indices_clim['FinDegel']).iloc[i]
                
            if pd.isnull(fin):
                fin = data_frame['Date'].iloc[-1]
                    
            data_frame.loc[(data_frame['Date'] >= debut) & (data_frame['Date'] <= fin), 'Annee_Clim'] = f'{debut.year}-{fin.year}'
    
        return data_frame
    
    def indices_climatiques_tableau(self):
        """
        Mettre les bons types pour les colonnes de dates.
        """
        # Format de date pour le dataframe dates_saisons
        self.df_indices_clim['DateGel'] = pd.to_datetime(self.df_indices_clim['DateGel'])
        self.df_indices_clim['DateDegel'] = pd.to_datetime(self.df_indices_clim['DateDegel'])
        self.df_indices_clim['FinGel'] = pd.to_datetime(self.df_indices_clim['FinGel'])
        self.df_indices_clim['FinDegel'] = pd.to_datetime(self.df_indices_clim['FinDegel'])
    
    def ecriture_cumul(self):
        """
        Écriture des données quotidiennes avec le cumul de degrés-jours dans le fichier
        de données de température de l'air de la station SILA. 
        """
        try: 
            pd.options.mode.chained_assignment = None
            
            # Dernière date enregistrée dans le fichier 
            df_fichier = pd.read_csv(self.fichier_sila)
            date_fichier = pd.to_datetime(df_fichier['Date']).iloc[-1]
            
            # Trouver les dates plus récentes
            self.nouvelles_lignes = self.df_sila.loc[(self.df_sila['Date'] > date_fichier)]
            self.colonne_annee_clim()
            
            # Écriture d'un back up - fichier Excel avec toutes les données le dernier jour du mois
            self.back_up_fichiers()
            
            if not self.nouvelles_lignes.empty: 
                print('Écriture des données de température de l\'air et du cumul de degrés-jours et des incices climatiques...')
                # On ajoute la nouvelle ligne de données avec le cumul de degrés jours à la fin du fichier
                self.nouvelles_lignes.to_csv(self.fichier_sila, header = False, index = False, mode = 'a', float_format = '%.2f') 
                
                # Écrire le tableau de saison à jour 
                self.df_indices_clim.to_csv(self.fichier_saisons, index = False, float_format = '%.2f')
                print(f'Écriture terminée. Données disponible dans les fichiers {self.fichier_sila} et {self.fichier_saisons}.', end = '\n\n')
    
            else:
                print(Fore.CYAN  + 'Aucune nouvelle donnée à écrire.'+ Style.RESET_ALL, end = '\n\n')            
            
        except NameError:
            print('NameError Nom du fichier incorrecte.Entrez un autre nom en argument ou vérifiez le répertoire.')
                
        except FileNotFoundError:
            print('FileNotFoundError Fichier introuvable. Essayez un autre nom ou vérifiez dans le répertoire.')
            
        except OSError:
            print('OSError Fichier introuvable. Essayez un autre nom ou vérifiez dans le répertoire.')
    
    def back_up_fichiers(self):
        try:
                
            # Nom et chemin des fichiers de back up
            fichier_excel_donnees = f'{self.repertoire}Station_Data/CEN_SILA/Excel/SILA_Salluit_AirTemp.xlsx'
            fichier_excel_dates = f'{self.repertoire}Station_Data/CEN_SILA/Excel/Synthese_saisons_programme.xlsx'
            
            # Récupérer la date 
            date = datetime.today().date()
            dernier_jour_mois = (pd.to_datetime(date) + MonthEnd(1)).date()
            
            # S'il s'agit du dernier jour du mois, on fait un fichier excel back up 
            if date == dernier_jour_mois:
                self.df_sila.to_excel(fichier_excel_donnees, index = False)
                self.df_indices_clim.to_excel(fichier_excel_dates, index = False)
                print('Écriture du fichier Excel de back up.')
              
        except NameError:
            print('Fichier Backup : NameError Nom du fichier incorrecte.Entrez un autre nom en argument ou vérifiez le répertoire.')

        except FileNotFoundError:
            print('Fichier Backup : FileNotFoundError Fichier introuvable. Essayez un autre nom ou vérifiez dans le répertoire.')
            
        except OSError:
            print('Fichier Backup : OSError Fichier introuvable. Essayez un autre nom ou vérifiez dans le répertoire.')
     
if __name__ == '__main__':
    
    repertoire = input('Entrez le nom du répertoire de travail : ')
   
    fichier_sila = easygui.fileopenbox()
    
    # Si fichier Excel : 
    df_sila  = pd.read_excel(fichier_sol, engine = 'openpyxl')
    
    # Si fichier csv
# =============================================================================
#     df_sila = pd.read_csv(fichier_sol)
# ===================================
    
    indices = IndicesClimatiques(df_sila, repertoire)
    



