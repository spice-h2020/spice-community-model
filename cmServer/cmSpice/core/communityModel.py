
# --------------------------------------------------------------------------------------------------------------------------
#    Python libraries
# --------------------------------------------------------------------------------------------------------------------------

import os
import pandas as pd
import numpy as np
import importlib
import json
import copy

from inspect import getsourcefile
from os.path import abspath
import sys

# --------------------------------------------------------------------------------------------------------------------------
#    Custom Class
# --------------------------------------------------------------------------------------------------------------------------


# Community model tools
from cmSpice.core.communityJsonGenerator import CommunityJsonGenerator

# Community detection
from cmSpice.algorithms.clustering.explainedCommunitiesDetection import ExplainedCommunitiesDetection

# similarity measures
from cmSpice.algorithms.similarity.complexSimilarityDAO import ComplexSimilarityDAO
from cmSpice.algorithms.similarity.interactionSimilarityDAO import InteractionSimilarityDAO
from cmSpice.algorithms.similarity.communityModelSimilarity import CommunityModelSimilarity

# dao
from cmSpice.dao.dao_csv import DAO_csv
from cmSpice.dao.dao_json import DAO_json
from cmSpice.dao.dao_db_users import DAO_db_users
from cmSpice.dao.dao_db_distanceMatrixes import DAO_db_distanceMatrixes
from cmSpice.dao.dao_db_communities import DAO_db_community
from cmSpice.dao.dao_db_similarities import DAO_db_similarity

# ------------------
# logger
import logging
import traceback
from cmSpice.logger.logger import getLogger

logger = getLogger(__name__)
# ------------------



# --------------------------------------------------------------------------------------------------------------------------
#    Class
# --------------------------------------------------------------------------------------------------------------------------


class CommunityModel():

    def __init__(self,perspective,updateUsers = [], percentageExplainability = 0.5):
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
        self.percentageExplainability = 0.3
        self.percentageExplainability = percentageExplainability

        if ('weight' in self.perspective['algorithm']):
            self.percentageExplainability = float(self.perspective['algorithm']['weight'])

    def start(self):
        logger.info("update started")
        try:
            # Perspective was not found
            if (len(self.perspective) <= 0):
                return

            self.similarityMeasure = self.initializeComplexSimilarityMeasure()
            self.distanceMatrix = self.computeDistanceMatrix()
            self.clustering()
        except Exception as e:
            logger.error(traceback.format_exc())

    def getData(self):
        return self.similarityMeasure.data

    def getDistanceMatrix(self):
        return self.distanceMatrix

    def getCommunityVisualizationJSON(self):
        return self.jsonCommunity

    def initializeComplexSimilarityMeasure(self):
        """
        Initializes the complex similarity measure associated to the given perspective

        Parameters
        ----------

        Returns
        -------
            similarityMeasure: ComplexSimilarityDAO
        """
        daoCommunityModel = DAO_db_users()

        # Call wrapper to distinguish for HECHT special case.
        similarityMeasureWrapper = CommunityModelSimilarity(daoCommunityModel, self.perspective)
        similarityMeasure, self.perspective = similarityMeasureWrapper.initializeComplexSimilarityMeasure()

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
        distanceMatrixJSON = daoDistanceMatrixes.getDistanceMatrix(
            self.perspective['id'])
        if (len(distanceMatrixJSON) == 0):
            distanceMatrix = np.empty([0, 0])
        else:
            distanceMatrix = np.asarray(distanceMatrixJSON['distanceMatrix'])

        # Update distance matrix for all users (recalculate distance matrix)
        # if ("flagAllUsers" in self.updateUsers and distanceMatrix.shape[0] == 0):
        if ("flagAllUsers" in self.updateUsers):
            distanceMatrix = self.similarityMeasure.matrix_distance()
        # Update distance matrix for a user
        else:
            distanceMatrix = self.similarityMeasure.matrix_distance()

        return distanceMatrix

    def clusteringExportFileRoute(self, percentageExplainability, algorithmName):
        abspath = os.path.dirname(__file__)
        relpath = "clustering/"

        relpath += self.perspective['name'].replace(
            "Similar-", "S-").replace("Same-", "E-") + " "
        if algorithmName != "agglomerative":
            relpath += str(algorithmName) + " "
        relpath += "(" + str(percentageExplainability) + ")"

        relpath += ".json"
        route = os.path.normpath(os.path.join(abspath, relpath))

        return route

    def clustering(self, exportFile="clustering.json"):
        """
        Performs clustering using the distance matrix and the algorithm specified by the perspective object.

        Parameters
        ----------
            percentageExplainability: minimum percentage of the most frequent value among 1+ main similarity features.

        """
        jsonCommunity = self.performClustering(exportFile)
        return self.saveDatabase(jsonCommunity)

    def performClustering(self, exportFile="clustering.json"):
        percentageExplainability = self.percentageExplainability

        # Initialize data
        algorithm = self.initializeAlgorithm()
        data = self.similarityMeasure.data

        # Fill nan values (causes error in the visualization)
        data = data.fillna("")

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
        community_detection = ExplainedCommunitiesDetection(
            algorithm, data, self.distanceMatrix, self.perspective)
        data, communityDict = community_detection.search_all_communities(
            percentage=percentageExplainability)
        communityDict['perspective'] = self.perspective

        

        # Export to json
        data.reset_index(inplace=True)

        exportFile = self.clusteringExportFileRoute(
            percentageExplainability, self.perspective['algorithm']['name'])
        jsonGenerator = CommunityJsonGenerator(
            interactionObjectData, data, self.distanceMatrix, communityDict, community_detection, self.perspective, self.percentageExplainability)
        jsonCommunity = jsonGenerator.generateJSON(exportFile)

        return jsonCommunity

    def initializeAlgorithm(self):
        algorithmName = self.perspective['algorithm']['name'] + \
            "CommunityDetection"
        algorithmFile = "cmSpice.algorithms.clustering." + algorithmName
        algorithmModule = importlib.import_module(algorithmFile)
        algorithmClass = getattr(
            algorithmModule, algorithmName[0].upper() + algorithmName[1:])

        return algorithmClass


# --------------------------------------------------------------------------------------------------------------------------
#    Community jsons (visualization)
# --------------------------------------------------------------------------------------------------------------------------

    def saveDatabase(self, jsonCommunity):
        # Store distance matrix data
        daoDistanceMatrixes = DAO_db_distanceMatrixes()
        daoDistanceMatrixes.updateDistanceMatrix(
            {'perspectiveId': self.perspective['id'], 'distanceMatrix': self.similarityMeasure.distanceMatrix.tolist()})

        # Store community data
        daoCommunityModelCommunity = DAO_db_community()
        # drop previous data
        daoCommunityModelCommunity.drop(
            {'perspectiveId': self.perspective['id']})
        daoCommunityModelCommunity.dropFullList(
            {'perspectiveId': self.perspective['id']})
            
        # humanize some keys and values
        self.jsonCommunity = copy.deepcopy(jsonCommunity)
        humanizedJsonCommunity = self.humanizator(jsonCommunity)
        # add new data
        daoCommunityModelCommunity.insertFileList("", humanizedJsonCommunity)

        logger.info("json data saved")

# --------------------------------------------------------------------------------------------------------------------------
#   Auxiliar function
# --------------------------------------------------------------------------------------------------------------------------

    def containsInteractions(self):
        return len(self.perspective['interaction_similarity_functions']) > 0

# ---
#   Humanizator (rename keys, values)
# ---

    def renameValues(self, my_dict, humanizator):
        for e in humanizator:
            for path in e.keys():
                self.drill_down(my_dict, path.split(), e[path])
        return my_dict

    def drill_down(self, obj, path, value):
        if len(path) == 1:
            if isinstance(obj, dict):
                for key in obj.keys():
                    if key == path[0] and not isinstance(obj[key], dict) and obj[key] in value:
                        obj[path[0]] = value[obj[path[0]]]
            elif isinstance(obj, list):
                for elem in obj:
                    #elem = drill_down(elem, path, value)
                    for key in elem.keys():
                        if key == path[0] and elem[key] in value:
                            elem[path[0]] = value[elem[path[0]]]
            elif obj[path[0]] in value:
                obj[path[0]] = value[obj[path[0]]]

        else:
            if isinstance(obj, dict):
                obj[path[0]] = self.drill_down(obj[path[0]], path[1:], value)
            elif isinstance(obj, list):
                for elem in obj:
                    elem = self.drill_down(elem[path[0]], path[1:], value)
            return obj

    def renameKeys(self, my_dict, humanizator):
        if isinstance(my_dict, dict):
            for key in list(my_dict.keys()):
                if key in humanizator:
                    my_dict[humanizator[key]] = self.renameKeys(
                        my_dict.pop(key), humanizator)
                else:
                    my_dict[key] = self.renameKeys(
                        my_dict.pop(key), humanizator)
        elif isinstance(my_dict, list):
            for e in my_dict:
                self.renameKeys(e, humanizator)
        return my_dict

    def humanizator(self, jsonCommunity):
        # open all files inside /humanizator dir
        dict2Use = "dict"

        dir = "cmSpice/core/humanizator/"
        dictsList = []
        # for filename in os.listdir(dir):
        #    f =  open(dir + "/" + filename)

        f = open(dir + dict2Use + ".json")
        humanizator = json.load(f)

        newJsonCommunity = self.renameValues(
            jsonCommunity, humanizator["values"])
        newJsonCommunity = self.renameKeys(
            newJsonCommunity, humanizator["keys"])

        return newJsonCommunity
