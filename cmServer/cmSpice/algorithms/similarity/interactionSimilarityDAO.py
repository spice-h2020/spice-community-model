# Authors: José Ángel Sánchez Martín
import os
import json
import pandas as pd

import numpy as np

from cmSpice.algorithms.similarity.similarityDAO import SimilarityDAO
from cmSpice.algorithms.similarity.complexSimilarityDAO import ComplexSimilarityDAO
from cmSpice.dao.dao_json import DAO_json
from cmSpice.utils.dataLoader import DataLoader

import statistics
from statistics import mode

# ---------logger---------

from cmSpice.logger.logger import getLogger

logger = getLogger(__name__)
# ------------------------

class InteractionSimilarityDAO(SimilarityDAO):
    """
    Class to compute the interaction similarity between two users
    
    a) It computes the distanceMatrix between the objects the users interacted with (interaction objects (IO))
    b) For each IO userA interacted with, it gets the IO userB interacted with most similar to it.
    c) It computes the similarity between interaction attributes on these two IOs (e.g., emotions associated to IO(A) vs emotions associated to IO(B))
    """

    def __init__(self, dao, perspective):
        """Construct of TaxonomySimilarity objects.

        Parameters
        ----------
        data : pd.DataFrame
            Dataframe where index is ids of elements, columns a list of taxonomy member and
            values contain the number of times that a taxonomy member is in an element.
        """
        super().__init__(dao)
        self.perspective = perspective

        # Interaction object data
        self.IO_dao = self.getInteractionObjectDAO()
        self.IO_data = self.getInteractionObjectData()

        self.dominantAttributes = {}
        # for similarityFunction in self.perspective["interaction_similarity_functions"] + self.perspective["similarity_functions"]:
        for similarityFunction in self.perspective["similarity_functions"]:
            similarityFeature = similarityFunction['sim_function']['on_attribute']['att_name']
            similarityMeasure = similarityFunction['sim_function']['name']
            self.dominantAttributes[similarityFeature] = self.initializeFromPerspective(self.IO_dao, similarityFunction)

        # Interaction similarity function
        self.similarityFunction = self.perspective["interaction_similarity_functions"][0]
        self.similarityColumn = self.similarityFunction['sim_function']['on_attribute']['att_name']

        # Interaction attributes
        self.interactionAttribute = self.similarityFunction['sim_function']['on_attribute']['att_name']
        self.interactionAttributeOrigin = self.interactionAttribute + "_origin"
        self.interactionAttributeText = self.interactionAttribute.rsplit(".", 1)[0] + ".text"

        # Citizen attributes
        self.citizenAttributes = []
        for citizenAttribute in self.perspective['user_attributes']:
            self.citizenAttributes.append(citizenAttribute['att_name'])

        logger.info("self.attribute: " + str(self.interactionAttribute))
        logger.info("self.attribute (Origin): " + str(self.interactionAttributeOrigin))
        logger.info("self.attribute (text): " + str(self.interactionAttributeText))
        logger.info("self.data.columns: " + str(list(self.data.columns)))
        logger.info("\n")

        logger.info("self perspective")
        logger.info(self.perspective)
        logger.info("self.interactionSimilarityFunction")
        logger.info(self.similarityFunction)
        logger.info("\n")

        self.interactionSimilarityMeasure = self.initializeFromPerspective(dao, self.similarityFunction)

        logger.info("checking self.interactionSimilarityFunction")
        logger.info(self.interactionSimilarityMeasure.similarityFunction)
        logger.info("\n")

        # logger.info(self.interactionSimilarityMeasure)

        # logger.info("dafdsfasdf")
        if self.similarityFunction['sim_function']['name'] != 'NoInteractionSimilarityDAO' or 1 == 1:
            # logger.info("sfdsf")

            # Remove the interactions with emotion with interactionSimilarityMeasure empty
            IOColumn = self.similarityFunction['sim_function']['interaction_object']['att_name']
            df = self.data.copy()

            logger.info("dsfdsfsdf")

            df2 = df.explode(
                [self.interactionAttribute, self.interactionAttributeOrigin, self.interactionAttributeText])

            df3 = df2.loc[df2[self.similarityColumn].str.len() != 0]

            # Remove NaN values
            df3 = df3.dropna(subset=[self.interactionAttribute])

            # Remove False emotion

            # Remove interactions with artworks that are not in artworks.json
            df3 = df3.loc[df3[self.interactionAttributeOrigin].isin(self.IO_data['id'].to_list())]

            logger.info("df3")
            logger.info(df3)
            logger.info("\n\n")

            # Flag artwork is enabled (detect communities interacting with one specific artwork)
            # This flag is not added by the perspective configuration tool (for now, it is given manually)
            # if ('communityDetectionForArtwork' in self.perspective):
            # ["35230"] works
            """
            if (len(self.perspective['algorithm']['params']) > 0):
                # Filter self.data to only consider users interacting with that artwork
                # Remove interactions with artworks other than the one given by the 'communityDetectionForArtwork' flag
                communityDetectionArtwork = self.perspective['algorithm']['params'][0] #['communityDetectionForArtwork']
                logger.info("communityDetectionArtwork: " + str(communityDetectionArtwork))

                dfArtworkFlag = df3.loc[ df3[self.interactionAttributeOrigin] == communityDetectionArtwork ]
                if (dfArtworkFlag.empty):
                    df3 = df3.head(1)
                else:
                    df3 = dfArtworkFlag.copy()
            """

            logger.info("df3 after artwork flag")
            logger.info(df3)
            logger.info("\n\n")

            groupList = ['userid']
            groupList.extend(self.citizenAttributes)

            # Df3 perspective
            logger.info("df3 perspective")
            logger.info(df3[['userid', self.interactionAttribute, self.interactionAttributeOrigin,
                       self.interactionAttributeText]])
            logger.info("\n")

            logger.info("groupby groupList")
            logger.info(groupList)
            logger.info("\n\n")

            df4 = df3.groupby(groupList).agg(list)
            df4 = df4.reset_index()

            """
            Reset userid to str (to stop encoding problems)
            """
            df4['userid'] = df4['userid'].astype(str)

            # Add columns to save dominant interaction attributes
            for dominantAttribute in self.dominantAttributes:
                # artwork similarity functions
                df4[dominantAttribute + 'DominantInteractionGenerated'] = [[] for _ in range(len(df4))]

            # interaction similarity functions
            df4[self.similarityColumn + 'DominantInteractionGenerated'] = [[] for _ in range(len(df4))]
            df4[self.similarityColumn + 'DistanceDominantInteractionGenerated'] = [[] for _ in range(len(df4))]
            # artworks we could match with a similar artwork
            df4['dominantArtworksDominantInteractionGenerated'] = [[] for _ in range(len(df4))]

            self.data = df4.copy()

        # Get IO distance matrix
        file = self.interactionObjectDistanceMatrixRoute()
        if os.path.exists(file) and 1 == 2:
            self.distanceDict = self.getIODistanceMatrixFromFile(file)
        else:
            self.distanceDict = self.computeIODistanceMatrix()

        # self.IO_distanceIndex = list(map(int, self.distanceDict['index']))
        self.IO_distanceIndex = self.distanceDict['index']
        self.IO_distanceMatrix = np.asarray(self.distanceDict['distanceMatrix'])

        logger.info("self.IO_distanceMatrix")
        logger.info(self.IO_distanceMatrix)
        logger.info("\n")

        matrix = self.IO_distanceMatrix.copy()
        matrix[matrix == 0.0] = 1.0
        matrix[matrix == 0.12] = 1.0

        # Get the two artworks with the highest similarity (In order to get high similarity artworks in iconclass)
        ind = np.unravel_index(np.argmin(matrix, axis=None), matrix.shape)

    def interactionObjectDistanceMatrixRoute(self):
        abspath = os.path.dirname(__file__)
        relpath = "../../core/" + "interactionObjects/" + self.perspective['name'] + ".json"
        exportFile = os.path.normpath(os.path.join(abspath, relpath))

        return exportFile

    def getInteractionObjectDAO(self):
        route = DataLoader.fileRoute('artworks.json')
        if route:
            daoJson = DAO_json(route)
            return daoJson
        else:
            # TODO: Change by Logger
            logger.info("Unable load artworks.json")
            return None

    def getInteractionObjectData(self):
        daoJson = self.getInteractionObjectDAO()
        return daoJson.getPandasDataframe()

    def getIODistanceMatrixFromFile(self, file):
        """
        Method to directly assign already calculated distance matrixes

        Returns
        -------
        np.array
            Matrix that contains all similarity values.
        """
        with open(file, 'r', encoding='utf8') as f:
            IO_distanceDict = json.load(f)

        return IO_distanceDict

    def computeIODistanceMatrix(self):
        """
        Method to calculate the distance matrix between all interaction objects included in data.

        Returns
        -------
        IO_distanceDict: dict
            Includes distance between interaction objects
                index:
                    IO index
                distanceMatrix: np.array
                    Matrix that contains all similarity values.
        """
        # Calculate interaction object (IO) similarity
        similarity_functions = self.perspective['similarity_functions']
        daoJson = self.getInteractionObjectDAO()
        IO_similarityMeasure = ComplexSimilarityDAO(daoJson, similarity_functions)
        IO_distanceMatrix = IO_similarityMeasure.matrix_distance()

        # Export _id (id artefact) and distance matrix to json file
        IO_distanceDict = {}
        # IO_distanceDict['index'] = IO_similarityMeasure.data['id'].tolist()
        IO_distanceDict['index'] = list(map(str, IO_similarityMeasure.data['id'].tolist()))
        IO_distanceDict['distanceMatrix'] = IO_distanceMatrix.tolist()

        exportFile = self.interactionObjectDistanceMatrixRoute()

        with open(exportFile, "w") as outfile:
            json.dump(IO_distanceDict, outfile, indent=4)

        return IO_distanceDict

    def getSimilarIOIndex(self, objectA, IOB):
        """
        Method to obtain the index of the object in IOB that is most similar to objectA
        
        Distance between IOs in the database are calculated beforehand (distanceMatrix). 
        Only IOs above a given x (0.7) are considered similar. If IOB doesn't include a similar object to objectA, the function returns -1.

        Parameters
        ----------
        objectA : object (int, String...)
            IDs of an object userA interacted with
        elemB : list
            List of IDs belonging to the objects userB interacted with.

        Returns
        -------
        double
            Index in the list IOB of the object userB interacted with that is most similar to objectB 
            -1 if all objects in IOB are not similar to objectA
        """
        # https://www.w3resource.com/python-exercises/numpy/python-numpy-exercise-31.php
        # https://stackoverflow.com/questions/15287084/numpy-find-the-values-of-rows-given-an-array-of-indexes
        # https://stackoverflow.com/questions/33678543/finding-indices-of-matches-of-one-array-in-another-array

        # Sometimes objectA is not in the artworks catalogue (ask about this)
        try:
            # Convert to string the object ids because in some cases artwork data has string ids while interactions have int ids
            objectA = str(objectA)
            IOB = list(map(str, IOB))

            """
            logger.info("type object A: " + str(type(objectA)))
            logger.info("type IO_distanceIndex: " + str(type(self.IO_distanceIndex[0])))
            logger.info("objectA: " + str(objectA))
            logger.info("IOB: " + str(IOB))
            logger.info("\n")
            """

            objectAIndex = self.IO_distanceIndex.index(str(objectA))
            distanceMatrix_IOB_indexes = np.nonzero(np.in1d(self.IO_distanceIndex, IOB))[0]
            distanceMatrix_IOB_values = self.IO_distanceMatrix[objectAIndex, distanceMatrix_IOB_indexes]
            mostSimilarIOIndex = distanceMatrix_IOB_values.argmin()
            mostSimilarIO = IOB[mostSimilarIOIndex]

            """
            logger.info("type object A: " + str(type(objectA)))
            logger.info("type IO_distanceIndex: " + str(type(self.IO_distanceIndex[0])))
            logger.info("objectA: " + str(objectA))
            logger.info("IOB: " + str(IOB))
            logger.info("\n")
            logger.info("IO_distanceIndex: " + str(self.IO_distanceIndex))
            logger.info(self.IO_distanceMatrix)
            logger.info("\n")
            logger.info("objectA index: " + str(objectAIndex))
            logger.info("distanceMatrix_IOB_indexes: " + str(distanceMatrix_IOB_indexes))
            logger.info("distanceMatrix_IOB_values: " + str(distanceMatrix_IOB_values))
            logger.info("minimumDistance index: " + str(mostSimilarIOIndex))
            logger.info("minimumDistance value: " + str(distanceMatrix_IOB_values[mostSimilarIOIndex]))
            logger.info("most similar IO: " + str(mostSimilarIO))
            logger.info("\n\n\n")
            
            """

            # Get index of elements above a given threshold (let is say 0.5)

            # If the best match is still dissimilar
            similarThreshold = 0.35
            similarThreshold = 0.65
            similarThreshold = 0.5
            similarThreshold = 0.65
            similarThreshold = 0.5
            similarThreshold = 0.3
            similarThreshold = 0.5
            similarThreshold = 0.6
            # similarThreshold = 0.3
            # similarThreshold = 0.8
            # similarThreshold = 0.6
            # similarThreshold = 500.0
            if distanceMatrix_IOB_values[mostSimilarIOIndex] >= similarThreshold:
                mostSimilarIOIndex = -1
            """
            """

            return mostSimilarIOIndex

        except ValueError:

            logger.info("exception ")
            logger.info("type object A: " + str(type(objectA)))
            """
            """
            logger.info("objectA: " + str(objectA))
            logger.info("IO_distanceIndex: " + str(self.IO_distanceIndex))

            objectAIndex = self.IO_distanceIndex.index(str(objectA))
            logger.info("objectA index: " + str(objectAIndex))
            distanceMatrix_IOB_indexes = np.nonzero(np.in1d(self.IO_distanceIndex, IOB))[0]
            logger.info("distanceMatrix_IOB_indexes: " + str(distanceMatrix_IOB_indexes))
            distanceMatrix_IOB_values = self.IO_distanceMatrix[objectAIndex, distanceMatrix_IOB_indexes]
            logger.info("distanceMatrix_IOB_values: " + str(distanceMatrix_IOB_values))
            mostSimilarIOIndex = distanceMatrix_IOB_values.argmin()
            logger.info("most similar IO Index: " + str(mostSimilarIOIndex))
            mostSimilarIO = IOB[mostSimilarIOIndex]
            logger.info("most similar IO: " + str(mostSimilarIO))

            logger.info("end exception")

            return -1

    def distance(self, elemA, elemB):
        """
        Method to obtain the distance between two element.

        Parameters
        ----------
        elemA : int
            Id of first element. This id should be in self.data.
        elemB : int
            Id of second element. This id should be in self.data.

        Returns
        -------
        double
            Distance between the two elements.
        """
        userInteractionA = self.data.loc[elemA]
        userInteractionB = self.data.loc[elemB]

        """
        logger.info(userInteractionA['userid'])
        logger.info(userInteractionB['userid'])
        """

        # Get interaction objects (IO) the user interacted with
        # logger.info(self.similarityFunction)

        # Get ids of artworks the user interacted with
        IOColumn = self.interactionAttribute + "_origin"
        # IOColumn = self.similarityFunction['sim_function']['interaction_object']['att_name']
        IOA = userInteractionA[IOColumn]
        IOB = userInteractionB[IOColumn]

        IOA = list(map(str, IOA))
        IOB = list(map(str, IOB))

        """
        logger.info("IO Columns")
        logger.info(IOColumn)
        logger.info(IOA)
        logger.info(IOB)
        logger.info("\n\n\n")
        """

        """
        """

        self.exchanged = False

        if len(IOB) > len(IOA):
            self.exchanged = True
            IOA, IOB = self.exchangeElements(IOA, IOB)
            userInteractionA, userInteractionB = self.exchangeElements(userInteractionA, userInteractionB)
        """
        """

        return self.distanceInteraction(elemA, elemB, userInteractionA, userInteractionB, IOA, IOB)

    def distanceInteraction(self, elemA, elemB, userInteractionA, userInteractionB, IOA, IOB):
        # Set largest list to be A and the other B
        # self.exchanged = False

        # Initialize distance
        distanceTotal = 0

        # Dominant interaction attribute value
        dominantInteractionAttribute = ""
        dominantInteractionAttributeDistance = 1.0

        dominantInteractionAttributes = []
        dominantInteractionAttributeDistances = {}

        # Artwork implicit attributes
        dominantValues = {}
        for dominantAttribute in self.dominantAttributes:
            dominantValues[dominantAttribute] = ""
            if self.dominantAttributes[dominantAttribute].dominantValueType() == "list":
                dominantValues[dominantAttribute] = []
        # Similar artworks users are compared with
        dominantArtworks = []

        try:

            # For each IO in A, get most similar IO in B
            for objectIndexA in range(len(IOA)):
                objectA = IOA[objectIndexA]
                objectIndexB = self.getSimilarIOIndex(objectA, IOB)
                objectB = IOB[objectIndexB]

                """
                if (userInteractionA['userid'] == 'e4aM9WL7' and userInteractionB['userid'] == 'BNtsz8zb' and 1 == 2):
                    logger.info("check object index " + str(userInteractionA['userid']))
                    logger.info("elemB: " + str(userInteractionB['userid']))
                    logger.info("objectA: " + str(objectA))
                    logger.info("objectIndexB: " + str(objectIndexB))
                    logger.info("\n\n")
                """

                # logger.info("objectA: " + str(objectA))

                # IGNORED FOR NOW
                if (1 == 2 and objectIndexB != -1 and self.similarityFunction['sim_function'][
                    'name'] == "NoInteractionSimilarityDAO"):
                    objectB = IOB[objectIndexB]
                    distanceMatrixIndexObjectA = self.IO_distanceIndex.index(str(objectA))
                    distanceMatrixIndexObjectB = self.IO_distanceIndex.index(str(objectB))

                    distance = self.IO_distanceMatrix[distanceMatrixIndexObjectA, distanceMatrixIndexObjectB]
                    logger.info("new distance is :" + str(distance))

                # STARTS HERE IF A MATCHING SIMILAR ARTWORK WAS FOUND
                elif objectIndexB != -1:
                    """
                    logger.info("interactionsA: " + str(userInteractionA[self.similarityColumn]))
                    logger.info("interactionsB: " + str(userInteractionB[self.similarityColumn]))
                    logger.info("objectIndexA: " + str(objectIndexA))
                    logger.info("len IOA: " + str(len(IOA)))
                    logger.info("IOA: " + str(IOA))
                    logger.info(userInteractionA['userid'])
                    
                    """

                    # Get interaction similarity feature associated to IO A and IO B
                    interactionFeatureA = userInteractionA[self.similarityColumn][objectIndexA]
                    interactionFeatureB = userInteractionB[self.similarityColumn][objectIndexB]

                    """
                    logger.info("self.interaction similarity measure: " + str(self.interactionSimilarityMeasure))
                    logger.info("interactionFeatureA: " + str(interactionFeatureA))
                    logger.info("interactionFeatureB: " + str(interactionFeatureB))
                    
                    
                    """

                    # Calculate distance between them
                    distance = self.interactionSimilarityMeasure.distanceValues(interactionFeatureA,
                                                                                interactionFeatureB)
                    # logger.info("distance (" + str(interactionFeatureA) + "," + str(interactionFeatureB) + "): " + str(distance))
                    # distance = self.interactionSimilarityMeasure.dissimilarFlag(distance)
                    # logger.info("distance dissimilar (" + str(interactionFeatureA) + "," + str(interactionFeatureB) + "): " + str(distance))
                    # logger.info("\n")

                    # Add dominant interaction value to list (e.g., emotions = {joy: 3, sadness: 4, trust: 1} -> sadness
                    dominantInteractionAttributeA, dominantInteractionAttributeB = self.interactionSimilarityMeasure.dominantInteractionAttribute(
                        interactionFeatureA, interactionFeatureB)
                    dominantInteractionAttributeDistance = self.interactionSimilarityMeasure.dominantDistance(
                        interactionFeatureA, interactionFeatureB)

                    # Add dominant value for each artwork attribute used to compute similarity between them
                    """
                    logger.info("objectA: " + str(objectA))
                    logger.info("objectB: " + str(objectB))
                    logger.info("\n")
                    """

                    # Get objects data
                    column = self.perspective['similarity_functions'][0]['sim_function']['on_attribute']['att_name']
                    artworks_df = self.IO_data.loc[self.IO_data['id'].isin([objectA, objectB])]

                    """
                    logger.info("df")
                    logger.info(df[['id', column]] )
                    logger.info("\n")
                    
                    """

                    # Compute & Save dominant attribute
                    for dominantAttribute in self.dominantAttributes:
                        similarityMeasure = self.dominantAttributes[dominantAttribute]

                        """
                        valueA = artworks_df.loc[ artworks_df['id'] == objectA ][dominantAttribute].to_list()[0]
                        #logger.info(valueA)
                        valueB = artworks_df.loc[ artworks_df['id'] == objectB ][dominantAttribute].to_list()[0]
                        #logger.info(valueB)
                        dominantValue = similarityMeasure.dominantValue(valueA, valueB)
                        #logger.info(dominantValue)
                        dominantValues[dominantAttribute] = dominantValue
                        #logger.info(dominantValues)
                        #logger.info("dominantValue: " + str(dominantValue))
                        """

                        dominantValue = similarityMeasure.dominantElemValue(objectA, objectB)
                        # logger.info(dominantValue)
                        dominantValues[dominantAttribute] = dominantValue
                        # logger.info(dominantValues)
                        # logger.info("dominantValue: " + str(dominantValue))

                    # dominant_artworkSimilarityFeature =

                    # Set artwork ID we successfully found a match for
                    if (self.exchanged):
                        dominantArtworks.append(objectB)
                    else:
                        dominantArtworks.append(objectA)

                    if (userInteractionA['userid'] == 'x2AUnHqw' and 1 == 2):
                        logger.info('x2AUnHqw')
                        logger.info("dominant artworks x2AUnHqw")
                        logger.info(userInteractionB['userid'])
                        logger.info(objectA)
                        logger.info(objectB)
                        logger.info("\n")

                    """
                    logger.info("dominantA: " + str(dominantInteractionAttributeA))
                    logger.info("dominantB: " + str(dominantInteractionAttributeB))
                    
                    
                    
                    """

                    if self.exchanged:
                        dominantInteractionAttribute = dominantInteractionAttributeB
                    else:
                        dominantInteractionAttribute = dominantInteractionAttributeA

                    # Add objectA to the list of compared interacted artworks 

                    dominantInteractionAttributes.append(dominantInteractionAttribute)
                    # dominantInteractionAttributeDistances.append(dominantInteractionAttributeDistance)
                    if dominantInteractionAttribute not in dominantInteractionAttributeDistances:
                        dominantInteractionAttributeDistances[dominantInteractionAttribute] = []
                    dominantInteractionAttributeDistances[dominantInteractionAttribute].append(
                        dominantInteractionAttributeDistance)

                # NO SIMILAR ARTWORK    
                else:
                    distance = 1

                """
                logger.info("distance: " + str(distance))
                logger.info("distanceTotal: " + str(distanceTotal))
                logger.info("\n\n")
                
                """

                """
                """
                distanceTotal += distance

            distanceTotal /= len(IOA)

            """
            logger.info("distanceTotal (FINAL) (" + str(userInteractionA['userid']) + "; " + str(userInteractionB['userid']) + "): " + str(distanceTotal))
            logger.info("\n\n")
            
            """

            """
            """

            if userInteractionA['userid'] == 'e4aM9WL7' and userInteractionB['userid'] == 'BNtsz8zb' and 1 == 2:
                logger.info("check interaction distance " + str(userInteractionA['userid']))
                logger.info("elemB: " + str(userInteractionB['userid']))
                logger.info("distanceTotal (FINAL): " + str(distanceTotal))
                logger.info("\n\n")

        except Exception as e:
            logger.error("\n\n\n")
            logger.error("Exception dominant attribute")
            logger.error(str(e))
            """
            logger.info("elemA: " + str(elemA))
            logger.info("elemB: " + str(elemB))
            """
            logger.error("userA: " + str(userInteractionA['userid']))
            logger.error("userB: " + str(userInteractionB['userid']))
            logger.error("IOA: " + str(IOA))
            logger.error("IOB: " + str(IOB))
            logger.error("interactionsA: " + str(userInteractionA[self.similarityColumn]))
            logger.error("interactionsB: " + str(userInteractionB[self.similarityColumn]))
            logger.error("objectIndexA: " + str(objectIndexA))
            logger.error("len IOA: " + str(len(IOA)))
            logger.error("IOA: " + str(IOA))
            logger.error(userInteractionA['userid'])

            raise Exception(e)

            # Get interaction similarity feature associated to IO A and IO B
            # interactionFeatureA = userInteractionA[self.similarityColumn][objectIndexA]
            # interactionFeatureB = userInteractionB[self.similarityColumn][objectIndexB]

        # Get most frequent element in dominantInteractionAttributes
        """
        logger.info("dominant interaction attributes")
        logger.info(dominantInteractionAttributes)
        """
        if len(dominantInteractionAttributes) > 0:
            dominantInteractionAttribute = mode(dominantInteractionAttributes)
            distances = dominantInteractionAttributeDistances[dominantInteractionAttribute]
            dominantInteractionAttributeDistance = (sum(distances)) / (len(distances))

        else:
            dominantInteractionAttribute = ""
            dominantInteractionAttributeDistance = 1.0

        if self.similarityFunction['sim_function']['name'] != 'NoInteractionSimilarityDAO':

            # logger.info(self.data[[self.similarityColumn]])

            """
            logger.info("dominantInteractionAttributeList: " + str(dominantInteractionAttributeList))
            logger.info("distanceTotal: " + str(distanceTotal))
            logger.info("\n\n")
            
            
            """

            # Set dominant interaction attribute list
            dominantInteractionAttributeList = self.data.loc[elemA][
                self.similarityColumn + 'DominantInteractionGenerated']
            dominantInteractionAttributeList.append(dominantInteractionAttribute)
            # Use all the emotions
            # dominantInteractionAttributeList.append(dominantInteractionAttributes)
            self.data.at[
                elemA, self.similarityColumn + 'DominantInteractionGenerated'] = dominantInteractionAttributeList

            # Add dominant distance
            dominantInteractionAttributeDistanceList = self.data.loc[elemA][
                self.similarityColumn + 'DistanceDominantInteractionGenerated']
            dominantInteractionAttributeDistanceList.append(dominantInteractionAttributeDistance)
            self.data.at[
                elemA, self.similarityColumn + 'DistanceDominantInteractionGenerated'] = dominantInteractionAttributeDistanceList

            # Set dominant implicit attribute (artworks)
            # I have to put it here because maybe it didnt find any similar artwork
            for dominantAttribute in self.dominantAttributes:
                dominantValue = dominantValues[dominantAttribute]
                dominantValueList = self.data.loc[elemA][dominantAttribute + 'DominantInteractionGenerated']
                dominantValueList.append(dominantValue)
                self.data.at[elemA, dominantAttribute + 'DominantInteractionGenerated'] = dominantValueList

            # Set artwork ID we successfully found a match for
            dominantArtworksList = self.data.loc[elemA]['dominantArtworksDominantInteractionGenerated']
            dominantArtworksList.append(dominantArtworks)
            self.data.at[elemA, 'dominantArtworksDominantInteractionGenerated'] = dominantArtworksList

        return distanceTotal
