
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 28 10:07:16 2021

@author: Sarah Gauthier et Michel Allard
sarah.gauthier.1@ulaval.ca
Centre d'études nordiques, Université Laval
    
Module pour créer une couche géospatiale à partir d'un tableau de données (DataFrame) 
pour les stations SILA, GN et GS. 

Une fois les points géoréférencer avec es coordonnées de la station, 
le DataFrame est enregistré en couche shapefile (.shp) et 
les données sont mise à jour sur ArcGIS Onlie. 

# =============================================================================
#  CE MODULE EST EN DÉVELOPPEMENT ET DOIT ÊTRE ADAPTÉ EN FONCTION DE LA STATION 
#  DE SUIVI (CLIMATIQUE, THERMIQUE, ETC.) DONT LES DONNÉES DOIVENT ÊTRE 
#  RÉCUPÉRÉES ET PUBLIER. 
# =============================================================================

"""

from datetime import datetime, timedelta
from arcgis.features import GeoAccessor, FeatureLayer, Table
from arcgis.gis import GIS
import pandas as pd

class CoucheWeb():
    """
    Classe pour mettre à jour les couches géospatiales avec les données de la station SILA. 
    """
    
    def __init__(self, station, repertoire):
        """
        Initialisation de la classe et connexion au compte ArcGIS Online du Centre d'études nordiques 
        pour y mettre à jour les données.

        gis (ArcGIS Online) : Connexion au compte CEN.AGOL_ulaval avec le module GIS de ArcGIS API 1.8.5;
        sila (DataFrame) : Tableau de données à jour avec la température de l'air et le cumul de degrés-jour (SILA, Salluit);
        data_frame (DataFrame) : Tableau de données à jour selon la station (SILA, GN et GS); 
        indices_clim (DataFrame): Tableau de données avec les indices climatiques à jour;
        nouvelles_lignes (DataFrame) : Tableau de données avec les nouvelles lignes de données récupérées.
        
        """
        # Chemin absolu de l'emplacement du programme et des fichiers nécessaires à l'exécution
        self.repertoire = repertoire
        utilisateur = input('Compte utilisateur ArcGIS Online : ')
        mot_de_passe = input('Mot de passe : ')
        
        # Connexion au compte du Centre d'études nordiques sur ArcGIS Online
        self.gis = GIS(username = utilisateur, password = mot_de_passe)
        print('Connexion au compte ArcGIS Online CEN.AGOL_ulaval établie.')
        
        # Dossier dans lequel on enregistre les couches Web
        self.fichier_web = 'Couches_Salluit'
        
        self.station = station

        self.indices_clim = pd.read_csv(f'{self.repertoire}Station_Data/CEN_SILA/Synthese_saisons_programme.csv')

        self.sila = pd.read_csv(f'{self.repertoire}Station_Data/CEN_SILA/SILA_Salluit_AirTemp.csv')
        self.sila = pd.to_datetime(self.sila['Date']) #+ timedelt
        
        if self.station == 'Station SILA':
            self.data_frame = pd.read_csv(f'{self.repertoire}Station_Data/CEN_SILA/SILA_Salluit_AirTemp.csv')

            self.indices_clim.loc[:, 'DateGel'] = pd.to_datetime(self.indices_clim['DateGel']) 
            self.indices_clim.loc[:, 'FinGel'] = pd.to_datetime(self.indices_clim['FinGel']) 
            self.indices_clim.loc[:, 'DateDegel'] = pd.to_datetime(self.indices_clim['DateDegel']) 
            self.indices_clim.loc[:, 'FinDegel'] = pd.to_datetime(self.indices_clim['FinDegel']) 
                        
            self.nom_couche = 'title: Donnees_SILA_2'
            self.couche_indices = 'title: Indices_Climatiques_Salluit'
            
        if self.station == 'Station GN':
            self.data_frame  = pd.read_csv(f'{self.repertoire}Station_Data/GN/GN_jours_2006_2021.csv')
            self.data_frame = self.data_frame.loc[:, :'200_CM']
# =============================================================================
#             self.data_frame.columns = ['Date', 'Annee_Clim', 'Annee', 'Mois', 'Jour', 'Nom_Mois', '-0.02',
#                               '-0.1', '-0.2', '-0.3', '-0.4', '-0.5', '-0.6', '-0.7', '-0.75',
#                               '-0.8', '-0.85', '-0.9', '-0.95', '-1', '-1.05', '-1.1',
#                               '-1.15', '-1.2', '-1.25', '-1.3', '-1.4', '-1.5', '-1.7', '-2']
# =============================================================================
            self.data_frame.columns = ['Date', 'Annee_Clim', 'Annee', 'Mois', 'Jour', 'Nom_Mois','SILA', '2',
                                        '10', '20', '30', '40', '50', '60', '70', '75',
                                        '80', '85', '90', '95', '100', '105', '110',
                                        '115', '120', '125', '130', '140', '150', '170',
                                        '200']
            
            self.nom_couche = 'title: Donnees_GN'
            
            self.df_stats  = pd.read_csv(f'{self.repertoire}Station_Data/GN/GN_min_max.csv')
            self.couche_trompette = 'title: GN_min_max'
            
        if self.station == 'Station GS':
            self.data_frame = pd.read_csv(f'{self.repertoire}Station_Data/GS/GS_jours_2006_2020.csv')
# =============================================================================
#             self.data_frame.columns = ['Date', 'Annee_Clim', 'Annee', 'Mois', 'Jour', 'Nom_Mois', '-0.02',
#                               '-0.1', '-0.2', '-0.3', '-0.4', '-0.5', '-0.6', '-0.7', '-0.75',
#                               '-0.8', '-0.85', '-0.9', '-0.95', '-1', '-1.05', '-1.1',
#                               '-1.15', '-1.2', '-1.25', '-1.3', '-1.4', '-1.5', '-1.7', '-2']
# =============================================================================
            self.data_frame.columns = ['Date', 'Annee_Clim', 'Annee', 'Mois', 'Jour', 'Nom_Mois','SILA', '2',
                                        '10', '20', '30', '40', '50', '60', '70', '75',
                                        '80', '85', '90', '95', '100', '105', '110',
                                        '115', '120', '125', '130', '140', '150', '170',
                                        '200']

            self.nom_couche = 'title: Donnees_GS'
            
            self.df_stats = pd.read_csv(f'{self.repertoire}Station_Data/GS/GS_min_max.csv')
            self.couche_trompette = 'title: GS_min_max'
        
        # Mettre bon format de date
        self.data_frame.loc[:, 'Date'] = pd.to_datetime(self.data_frame.loc[:, 'Date']) 

        print(f'Tableaux de données pour la {self.station} initialisées.', end = '\n\n')
        
    def mise_a_jour_couches(self): 
        """
        Méthode principale qui fait appel aux méthodes nécessaires pour 
        bien géoréférencer et mettre à jour toutes les couches géospatiales.

        Parameters
        ----------
        station : Nom de la station à mettre à jour.
        """
        # Récupérer les nouvelles données à publier
        self.nouvelles_donnees()
        
        # Ajouter coordonnées géographiques            
        self.colonnes_geometrie()
        
        # Décommenter pour enregistrer un shapefile avec toutes les données sur le disque local
# =============================================================================
#         self.enregistre_shapefile()
# =============================================================================
    
        # Mettre à jour les données dans les couches Web 
        self.couche_web_tableau_donnees()
        
        if self.station == 'Station SILA':
            self.couche_web_indices_climatiques()
            self.derniere_donnees_disponibles()
        
# =============================================================================
#         self.supprime_mauvaise_date()
# =============================================================================
        print(f'Publication des couches Web de {self.station} terminée.')
    
    def supprime_mauvaise_date(self): 
        """
        Pour supprimer les erreurs de publication en lien avec les dates.
        """
        
        couche_web = self.gis.content.search(self.nom_couche, 'Feature Layer')[0].layers[0]
        
        df_web = pd.DataFrame.spatial.from_layer(couche_web)

        df_web.sort_values(by = ['date'], inplace = True)
        
        df_web = df_web[df_web['date'].str[0] != '2']
        
        indices_entites = df_web.spatial.to_featureset()
        
        couche_web.edit_features(deletes = indices_entites) 
        
    def nouvelles_donnees(self):
        """
        Méthode pour identifier les nouvelles lignes à publier sur le Web. 
        """
        try: 
            
            # Récupérer la couche avec la date du dernier update
            couche_web = self.gis.content.search(self.nom_couche, 'Feature Layer')[0].layers[0]
            
            df_web = pd.DataFrame.spatial.from_layer(couche_web)
            df_web.sort_values(by = ['date'], inplace = True)
    
            derniere_date = df_web['date'].iloc[-1]
            dates = self.data_frame['Date'] >= derniere_date
            
            self.nouvelles_lignes = pd.DataFrame(columns = self.data_frame.columns)
            self.nouvelles_lignes = self.data_frame.loc[dates, :]
# =============================================================================
#             self.nouvelles_lignes =  self.nouvelles_lignes[self.nouvelles_lignes['date'].str[0] != '2']
# =============================================================================
            
            # Mettre bon format de date
# =============================================================================
#             self.nouvelles_lignes.loc[:, 'Date'] = pd.to_datetime(self.nouvelles_lignes.loc[:, 'Date']) + timedelta(hours = 12)
# =============================================================================
        
            if self.nouvelles_lignes.empty:
                print('Aucune nouvelle donnée à publier.', end = '\n\n')
            
            else:
                print(self.nouvelles_lignes)
        
        except Exception:
            print('Impossible de récupérer les nouvelles données.')
            
    def colonnes_geometrie(self):
                        
        # Coordonnées géographiques selon la station en entrée
        if self.station == 'Station SILA': 
            
            if not self.nouvelles_lignes.empty:
                self.nouvelles_lignes.loc[:,'lat'] = 62.1918 
                self.nouvelles_lignes.loc[:,'lon'] = -75.6379
            
            self.indices_clim.loc[:,'lat'] = 62.1918 
            self.indices_clim.loc[:,'lon'] = -75.6379
            
            self.data_frame.loc[:,'lat'] = 62.1918  
            self.data_frame .loc[:,'lon'] = -75.6379
            
        elif self.station == 'Station GN': 
            if not self.nouvelles_lignes.empty:
                self.nouvelles_lignes.loc[:,'lat'] = 62.19582 
                self.nouvelles_lignes.loc[:,'lon'] = -75.64170
                
            self.df_stats.loc[:,'lat'] = 62.19582 
            self.df_stats.loc[:,'lon'] = -75.64170
            
            self.data_frame.loc[:,'lat'] = 62.19582 
            self.data_frame.loc[:,'lon'] = -75.64170
        
        elif self.station == 'Station GS': 
            if not self.nouvelles_lignes.empty:
                self.nouvelles_lignes.loc[:,'lat'] =  62.193723
                self.nouvelles_lignes['lon'] =  -75.637789
            
            self.df_stats.loc[:,'lat'] =  62.193723
            self.df_stats.loc[:,'lon'] =  -75.637789
            
            self.data_frame.loc[:,'lat'] =  62.193723
            self.data_frame.loc[:,'lon'] =  -75.637789
            
        else:
            print('Nom de la station invalide.')
        
    def couche_web_indices_climatiques(self):
        
        try: 
            
            # Récupérer la couche web à mettre à jour 
            couche_web = self.gis.content.search(self.couche_indices, 'Feature Layer')[0].layers[0]
            
            # Convertir la couche web en spatial dataframe
            df_web = pd.DataFrame.spatial.from_layer(couche_web)
        
            df_web.loc[df_web.index[-1], 'annee_clim'] = self.indices_clim['Annee_Clim'].iloc[-1]
            df_web.loc[df_web.index[-1], 'date_gel'] = self.indices_clim['DateGel'].iloc[-1]
            df_web.loc[df_web.index[-1], 'fin_gel'] = self.indices_clim['FinGel'].iloc[-1]
            df_web.loc[df_web.index[-1], 'duree_gel'] = self.indices_clim['DureeGel'].iloc[-1]
            df_web.loc[df_web.index[-1], 'total_gel'] = self.indices_clim['TotalGel'].iloc[-1]
            df_web.loc[df_web.index[-1], 'date_degel'] = self.indices_clim['DateDegel'].iloc[-1]
            df_web.loc[df_web.index[-1], 'fin_degel'] = self.indices_clim['FinDegel'].iloc[-1]
            df_web.loc[df_web.index[-1], 'duree_dege'] = self.indices_clim['DureeDegel'].iloc[-1]
            df_web.loc[df_web.index[-1], 'total_dege'] = self.indices_clim['TotalDegel'].iloc[-1]
            df_web.loc[df_web.index[-1], 'ratio_fi_t'] = self.indices_clim['RatioFiTi'].iloc[-1]
            df_web.loc[df_web.index[-1], 'moyenne'] = self.indices_clim['Moyenne'].iloc[-1]
            df_web.loc[df_web.index[-1], 'variation_'] = self.indices_clim['VariationCumul'].iloc[-1]
            df_web.loc[df_web.index[-1], 'niveau_ris'] = self.indices_clim['NiveauRisque'].iloc[-1]
            df_web.loc[df_web.index[-1], 'risk_level'] = self.indices_clim['RiskLevel'].iloc[-1]
            
            # Décommenter les deux lignes ci-bas si le max de dégel est fonctionnelle 
# =============================================================================
#             df_web.loc[df_web.index[-1], 'max_degel'] = self.indices_clim['max_degel'].iloc[-1]
#             df_web.loc[df_web.index[-1], 'variation_'] = self.indices_clim['variation_max_degel'].iloc[-1]
# =============================================================================
        
            # Convertir le dataframe en classe d'entité
            indices_entites = df_web.spatial.to_featureset()
            
            # Publication des mises à jours
            couche_web.edit_features(updates = indices_entites) # adds = entites, deletes = entites
            
            print(f'Couche {self.couche_indices} mise à jour.')
            
        # Gestion des erreurs possibles
        except ConnectionError:  
            print('COUCHE WEB INDICES CLIMATIQUES : impossible de se connecter au serveur ftp. Vérifiez votre connexion au réseau VPN.')
    
        except NameError:
            print('COUCHE WEB INDICES CLIMATIQUES : Nom du fichier incorrect.Entrez un autre nom en argument ou vérifiez le répertoire.')
    
    def derniere_donnees_disponibles(self):
        
        try: 
                
            if not self.nouvelles_lignes.empty: 
                # Récupérer la couche avec la date du dernier update
                couche_update = self.gis.content.search('title: Update', 'Feature Layer')[0].layers[0]
                df_update = pd.DataFrame.spatial.from_layer(couche_update)
                
                # Mettre à jour la date dans le SEDF
                df_update.loc[df_update.index[-1], 'date'] = self.nouvelles_lignes['Date'].iloc[-1]
                df_update.loc[df_update.index[-1], 'annee_clim'] = self.nouvelles_lignes['Annee_Clim'].iloc[-1]
                df_update.loc[df_update.index[-1], 'annee'] = self.nouvelles_lignes['Annee'].iloc[-1]
                df_update.loc[df_update.index[-1], 'mois'] = self.nouvelles_lignes['Mois'].iloc[-1]
                df_update.loc[df_update.index[-1], 'jour'] = self.nouvelles_lignes['Jour'].iloc[-1]
                df_update.loc[df_update.index[-1], 'nom_mois'] = self.nouvelles_lignes['Nom_Mois'].iloc[-1]
                df_update.loc[df_update.index[-1], 'sila'] = self.nouvelles_lignes['SILA'].iloc[-1]
                df_update.loc[df_update.index[-1], 'cumul_dj'] = self.nouvelles_lignes['CUMUL_DJ'].iloc[-1]
        
                # Convertir le SEDF en classe d'entité
                update_entites = df_update.spatial.to_featureset()
        
                # Publication des mises à jours
                couche_update.edit_features(updates = update_entites)
                # Gestion des erreurs possibles
                
        except ConnectionError:  
            print('COUCHE WEB : Impossible de se connecter au serveur ftp. Vérifiez votre connexion au réseau VPN.')
    
        except NameError:
            print('COUCHE WEB : Nom du fichier incorrect.Entrez un autre nom en argument ou vérifiez le répertoire.')
    
        except IndexError:
            print('Attention, index non valide.')
                      
    def couche_web_tableau_donnees(self):
        """
        Ajoute les nouvelles données à la classe d'entité et publie les changements
        dans le compte ArcGIS Online CEN.AGOL_ulaval.
        """
        
        try: 
            
            if not self.nouvelles_lignes.empty: 

                # Création d'un dataframe spatial (SDF)
                print('Mise à jour des données Salluit SILA avec les nouvelles données...')
                sdf = pd.DataFrame.spatial.from_xy(df = self.nouvelles_lignes, x_column = 'lon', y_column = 'lat', sr=4326) # nad83 mtm 9 32189 
                sdf.spatial.set_geometry('SHAPE')
                
                # Récupérer la couche web à mettre à jour
                couche_web = self.gis.content.search(self.nom_couche, 'Feature Layer')[0].layers[0]
                
                # Convertir le spatial dataframe en entités
                entites = sdf.spatial.to_featureset()
                
                # Publier les mises à jour : ajouter les entités à la couche Web
                couche_web.edit_features(adds =  entites)  # updates = entites, deletes = entites
                print(f'Couche {self.nom_couche} mise à jour.', end = '\n\n')

        # Gestion des erreurs possibles
        except ConnectionError:  
            print('COUCHE WEB : Impossible de se connecter au serveur ftp. Vérifiez votre connexion au réseau VPN.')
    
        except NameError:
            print('COUCHE WEB : Nom du fichier incorrect.Entrez un autre nom en argument ou vérifiez le répertoire.')
    
    def couche_courbes_trompettes(self):
        
        couche_update = self.gis.content.search(self.couche_trompette, 'Feature Layer')[0].layers[0]
        df_update = pd.DataFrame.spatial.from_layer(couche_update)
        
        annee_clim = self.indices_clim['Annee_Clim'].iloc[-1]
        df_update = df_update.loc[df_update['annee_clim'] == annee_clim]
        
        df_update.loc[:, 'station'] = self.df_stats.loc[:, 'station']
        df_update.loc[:, 'annee_clim'] = self.df_stats.loc[:, 'annee_clim']
        df_update.loc[:, 'profondeur'] = self.df_stats.loc[:, 'profondeur']
        df_update.loc[:, 't_min'] = self.df_stats.loc[:, 't_min']
        df_update.loc[:, 't_max'] = self.df_stats.loc[:, 't_max']
        df_update.loc[:, 't_moy'] = self.df_stats.loc[:, 't_moy']

        # Convertir le SEDF en classe d'entité
        update_entites = df_update.spatial.to_featureset()

        print(df_update)
        
        # Publication des mises à jour
        couche_update.edit_features(updates = update_entites)
        
    def enregistre_shapefile(self):
        """
        Convertis le dataframe de données en dataframe spatial (pour localiser sur
        la carte la station) puis enregistre localement le dataframe spatial en shapefile.
        """
    
        try: 
            # Emplacement des couches
            chemin_fichier = f'{self.repertoire}Station_Data/Couche_Shapefile/Couche_{self.station}'
            
            # Créer un spatial dataframe
            if self.station == 'Station SILA':
                sdf = pd.DataFrame.spatial.from_xy(df = self.data_frame, x_column = 'lon', y_column = 'lat', sr=4326) # nad83 mtm 9 32189 
                
                chemin_fichier_indices = 'C:/Users/sagau63/Documents/GitHub/Code_Station/Python_GN/Data_CSV/Couche_Shapefile/Couche_SILA_IndicesClimatiques'
                sdf_indices = pd.DataFrame.spatial.from_xy(df = self.indices_clim, x_column = 'lon', y_column = 'lat', sr=4326) # nad83 mtm 9 32189 
                sdf_indices.spatial.to_featureclass(location=chemin_fichier_indices)
                
            elif self.station == 'Station GN':
                sdf = pd.DataFrame.spatial.from_xy(df = self.data_frame , x_column = 'lon', y_column = 'lat', sr=4326) # nad83 mtm 9 32189 
                
            elif self.station == 'Station GS':
                sdf = pd.DataFrame.spatial.from_xy(df = self.data_frame, x_column = 'lon', y_column = 'lat', sr=4326) # nad83 mtm 9 32189 
            
            else:
                print('Nom de la station non valide.')
                
            # Créer une couche géospatiale avec le tableau de données
            print(f'Enregistrement du shapefile de la couche {self.station}...')
            sdf.spatial.to_featureclass(location=chemin_fichier)
            print('Exportation réussie.', end = '\n\n')

        # Gestion des erreurs possibles
        except NameError:
            print('SHAPEFILE : Nom incorrect. Entrez un autre nom en argument ou vérifiez le répertoire.')
            
        except FileNotFoundError:
            print('SHAPEFILE : Fichier introuvable. Essayez un autre nom ou vérifiez dans le répertoire.')
            
        except OSError:
            print('SHAPEFILE : Fichier introuvable. Essayez un autre nom ou vérifiez dans le répertoire.')

    def publier_couche_web(self, df, nom_couche):
        
        df.loc[:, 'Date'] = pd.to_datetime(df.loc[:, 'Date']) + timedelta(days = 1)

        if self.station == 'Station GN':
            df.loc[:,'lat'] = 62.19582 
            df.loc[:,'lon'] = -75.64170
    
        if self.station == 'Station GS':
            df.loc[:,'lat'] =  62.193723
            df.loc[:,'lon'] =  -75.637789
            
        if self.station == 'Station SILA':
            df.loc[:,'lat'] = 62.1918   
            df.loc[:,'lon'] = -75.6379
            
        # Créer un spatial dataframe
        sdf = pd.DataFrame.spatial.from_xy(df = df, x_column = 'lon', y_column = 'lat', sr=4326) # nad83 mtm 9 32189 
        sdf.spatial.set_geometry('SHAPE')
        sdf.sort_values(by = ['Date'], inplace = True)
        
        # Publier les mises à jour : ajouter les entités à la couche Web
        sdf.spatial.to_featurelayer(nom_couche, folder= self.fichier_web)
        print(f'{nom_couche} publiée sur ArcGIS Online.')

if __name__ == '__main__':

# =============================================================================
#     station = input('Entrez le nom de la station : ')
# =============================================================================
    station = 'Station SILA'
    repertoire = input('Chemin complet du répertoire : ')
    
    web = CoucheWeb(station, repertoire)
    
    # Méthode pour mettre à jour le Dashboard
# =============================================================================
#     web.mise_a_jour_couches() 
# =============================================================================

