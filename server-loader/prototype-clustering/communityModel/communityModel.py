
#--------------------------------------------------------------------------------------------------------------------------
#    Python libraries
#--------------------------------------------------------------------------------------------------------------------------

import os
import pandas as pd
import numpy as np
import importlib

from inspect import getsourcefile
from os.path import abspath
import sys

#--------------------------------------------------------------------------------------------------------------------------
#    Custom Class
#--------------------------------------------------------------------------------------------------------------------------

from context import community_module

# Community model tools
from communityModel.communityJsonGenerator import CommunityJsonGenerator

# Community detection
from community_module.community_detection.explainedCommunitiesDetection import ExplainedCommunitiesDetection

# similarity measures
from community_module.similarity.complexSimilarityDAO import ComplexSimilarityDAO
from community_module.similarity.interactionSimilarityDAO import InteractionSimilarityDAO

# dao
from dao.dao_csv import DAO_csv
from dao.dao_json import DAO_json
from dao.dao_db_users import DAO_db_users
from dao.dao_db_distanceMatrixes import DAO_db_distanceMatrixes
from dao.dao_db_communities import DAO_db_community
from dao.dao_db_similarities import DAO_db_similarity


#--------------------------------------------------------------------------------------------------------------------------
#    Class
#--------------------------------------------------------------------------------------------------------------------------

class CommunityModel():

    def __init__(self,perspective,updateUsers = []):
        """
        Construct of Community Model objects.

        Parameters
        ----------
            perspective: perspective object. Composed by:
                id, name
                algorithm: name and parameters
                similarity_functions: name, attribute, weight
            flag: flag object. Composed by:
                perspectiveId
                userid: user to update
        """
        self.perspective = perspective
        self.updateUsers = updateUsers
        self.percentageExplainability = 0.5
        
    def start(self):
        
        # Perspective was not found
        if (len(self.perspective) <= 0):
            return
        
        """
        if (self.flag['userid'] == ""):
            print("not doing the one that is added by default")
            return
        """   
            
        self.similarityMeasure = self.initializeComplexSimilarityMeasure()
        self.distanceMatrix = self.computeDistanceMatrix()
        self.clustering()
        
    def getData(self):
        return self.similarityMeasure.data
    
    def initializeComplexSimilarityMeasure(self):
        """
        Initializes the complex similarity measure associated to the given perspective

        Parameters
        ----------
        
        Returns
        -------
            similarityMeasure: ComplexSimilarityDAO
        """
        print("initialize complex similarity")
        print(self.perspective)
        print(self.perspective['similarity_functions'])
        daoCommunityModel = DAO_db_users()
        # If there are interaction_features use interactionSimilarityDAO
        if (len(self.perspective['interaction_similarity_functions']) > 0):
            similarityMeasure = InteractionSimilarityDAO(daoCommunityModel, self.perspective)
        # Otherwise use complexSimilarityDAO
        else:
            print("there are not interactions HECHT")
            similarityDict = self.perspective['similarity_functions']
            similarityMeasure = ComplexSimilarityDAO(daoCommunityModel,similarityDict)
        
        print("similarity measure: " + str(type(similarityMeasure)))
        
        return similarityMeasure
    
    def computeDistanceMatrix(self):
        """
        Method to calculate the distance matrix between all elements included in data.

        Parameters
        ----------
        
        Returns
        -------
            distanceMatrix: np.ndarray
        """

        # Load previous distance matrix
        daoDistanceMatrixes = DAO_db_distanceMatrixes()
        distanceMatrixJSON = daoDistanceMatrixes.getDistanceMatrix(self.perspective['id'])
        if (len(distanceMatrixJSON) == 0):
            distanceMatrix = np.empty([0,0])
        else:
            distanceMatrix = np.asarray(distanceMatrixJSON['distanceMatrix'])
        
        # Update distance matrix for all users (recalculate distance matrix)
        #if ("flagAllUsers" in self.updateUsers and distanceMatrix.shape[0] == 0):
        if ("flagAllUsers" in self.updateUsers):
            distanceMatrix = self.similarityMeasure.matrix_distance()
        # Update distance matrix for a user
        else:
            distanceMatrix = self.similarityMeasure.updateDistanceMatrix(self.updateUsers, distanceMatrix)
        
        print(distanceMatrix)
        
        
        # Drop irrelevant parameters to explain communities
        #self.similarityMeasure.data.drop(['origin','source_id', '_id'], axis=1, inplace=True)
        
        # They are useful now
        #self.similarityMeasure.data.drop(['origin','source_id'], axis=1, inplace=True)
        #self.similarityMeasure.data = self.similarityMeasure.data.rename(columns={"userid":"user"})
        
        #return self.similarityMeasure.distanceMatrix
        return distanceMatrix
        
            
    def clusteringOLD(self):
        """
        Performs clustering using the distance matrix and the algorithm specified by the perspective object.

        Parameters
        ----------
            
        """
        percentageDefault = 0.78
        percentageDefault = 0.5
        
        algorithmName = self.perspective['algorithm']['name'] + "CommunityDetection"
        algorithmFile = "community_module.community_detection." + algorithmName 
        algorithmModule = importlib.import_module(algorithmFile)
        algorithmClass = getattr(algorithmModule,algorithmName[0].upper() + algorithmName[1:])
        
        community_detection_df = self.similarityMeasure.data.set_index('user')

        distanceMatrix = self.self.similarityMeasure.distanceMatrix
        community_detection = ExplainedCommunitiesDetection(algorithmClass, community_detection_df, distanceMatrix, self.perspective)

        n_communities, users_communities, self.medoids_communities = community_detection.search_all_communities(percentage=percentageDefault) 


        hecht_beliefR_pivot_df2 = community_detection_df.copy()
        hecht_beliefR_pivot_df2['community'] = users_communities.values()
        hecht_beliefR_pivot_df2.reset_index(inplace=True)
        hecht_beliefR_pivot_df2
        
        # Export to json
        self.exportCommunityClusteringJSON(hecht_beliefR_pivot_df2,community_detection,n_communities,percentageDefault,distanceMatrix)
    

    def clusteringExportFileRoute(self, percentageExplainability, algorithmName):
        abspath = os.path.dirname(__file__)
        #relpath = "clustering/" + self.perspective['name'] + " " + "(" + self.perspective['algorithm']['name'] + ")" 
        #relpath = "clustering/" + '(GAMGame_stories_RN_UNITO) ' + self.perspective['name'] + " "
        # relpath = "clustering/" + '(GAM RN) ' + self.perspective['name'] + " "
        relpath = "clustering/" 
        #relpath += "clusters generated/" + self.perspective["algorithm"]["name"] + "/"
        # relpath += "clusters Mine/" + self.perspective["algorithm"]["name"] + "/"
        
        print("clustering export file route")

        relpath += self.perspective['name'].replace("Similar-","S-").replace("Same-","E-") + " "
        if algorithmName != "agglomerative":
            relpath += str(algorithmName) + " "
        relpath += "(" + str(percentageExplainability) + ")"
        
        relpath += ".json"
        route = os.path.normpath(os.path.join(abspath, relpath))
        
        return route
        
    def clusteringOLD(self, exportFile = "clustering.json"):
        """
        Performs clustering using the distance matrix and the algorithm specified by the perspective object.

        Parameters
        ----------
            percentageExplainability: minimum percentage of the most frequent value among 1+ main similarity features.
            
        """
        percentageExplainability = self.percentageExplainability
        
        # Initialize data
        algorithm = self.initializeAlgorithm()
        data = self.similarityMeasure.data
        data = data.set_index('userid')
        
        #interactionObjectData = self.similarityMeasure.getInteractionObjectData()
        interactionObjectData = pd.DataFrame()
        
        # Get results
        community_detection = ExplainedCommunitiesDetection(algorithm, data, self.distanceMatrix, self.perspective)
        communityDict = community_detection.search_all_communities(percentage=percentageExplainability) 
        communityDict['perspective'] = self.perspective
        
        # Export to json
        data.reset_index(inplace=True)
        exportFile = self.clusteringExportFileRoute(percentageExplainability)
        jsonGenerator = CommunityJsonGenerator(interactionObjectData, data, self.distanceMatrix, communityDict, community_detection, self.perspective)
        jsonCommunity = jsonGenerator.generateJSON(exportFile)       
        
        # Save data to database
        insertedId = self.saveDatabase(jsonCommunity)
        
        return insertedId
    
        
    def clustering(self, exportFile = "clustering.json"):
        """
        Performs clustering using the distance matrix and the algorithm specified by the perspective object.

        Parameters
        ----------
            percentageExplainability: minimum percentage of the most frequent value among 1+ main similarity features.
            
        """
        jsonCommunity = self.performClustering(exportFile)
        return self.saveDatabase(jsonCommunity)
        
    def performClustering(self, exportFile = "clustering.json"):
        percentageExplainability = self.percentageExplainability
        
        # Initialize data
        algorithm = self.initializeAlgorithm()
        data = self.similarityMeasure.data
        
        print("perform clustering data")
        print("data columns:")
        print(list(data.columns))
        print("\n")
        print("data")
        print(data)
        print("\n")
        
        # For debugging (delete later)
        data['userNameAuxiliar'] = data['userid']
        data['real_index'] = data.index
                
        # Set index to userName to use in visualization        
        data = data.set_index('userid')
        
        if (self.containsInteractions()):
            interactionObjectData = self.similarityMeasure.getInteractionObjectData()
        else:
            interactionObjectData = pd.DataFrame()
        
        # Get results
        community_detection = ExplainedCommunitiesDetection(algorithm, data, self.distanceMatrix, self.perspective)
        communityDict = community_detection.search_all_communities(percentage=percentageExplainability) 
        communityDict['perspective'] = self.perspective
        
        # Export to json
        data.reset_index(inplace=True)
        exportFile = self.clusteringExportFileRoute(percentageExplainability, self.perspective['algorithm']['name'])
        jsonGenerator = CommunityJsonGenerator(interactionObjectData, data, self.distanceMatrix, communityDict, community_detection, self.perspective)
        jsonCommunity = jsonGenerator.generateJSON(exportFile) 

        return jsonCommunity

    
    def initializeAlgorithm(self):
        algorithmName = self.perspective['algorithm']['name'] + "CommunityDetection"
        algorithmFile = "community_module.community_detection." + algorithmName 
        algorithmModule = importlib.import_module(algorithmFile)
        algorithmClass = getattr(algorithmModule,algorithmName[0].upper() + algorithmName[1:])
        
        return algorithmClass    
        

#--------------------------------------------------------------------------------------------------------------------------
#    Community jsons (visualization)
#--------------------------------------------------------------------------------------------------------------------------

    def saveDatabase(self,jsonCommunity):
        """
        daoCommunityModelVisualization = DAO_visualization()
        daoCommunityModelVisualization.drop()
        daoCommunityModelVisualization.insertJSON(jsonCommunity)
        """
        
        # Store distance matrix data
        # https://pynative.com/python-serialize-numpy-ndarray-into-json/
        daoDistanceMatrixes = DAO_db_distanceMatrixes()
        #daoDistanceMatrixes.drop()
        daoDistanceMatrixes.updateDistanceMatrix({'perspectiveId': self.perspective['id'], 'distanceMatrix': self.similarityMeasure.distanceMatrix.tolist()})
        
        # Store community data
        daoCommunityModelCommunity = DAO_db_community()
        # drop previous data
        daoCommunityModelCommunity.drop({'perspectiveId': self.perspective['id']})
        daoCommunityModelCommunity.dropFullList({'perspectiveId': self.perspective['id']})
        #daoCommunityModelCommunity.dropFullList()
        # add new data
        daoCommunityModelCommunity.insertFileList("", jsonCommunity)
    
#--------------------------------------------------------------------------------------------------------------------------
#   Auxiliar function
#--------------------------------------------------------------------------------------------------------------------------
   
    def containsInteractions(self):
        return len(self.perspective['interaction_similarity_functions']) > 0