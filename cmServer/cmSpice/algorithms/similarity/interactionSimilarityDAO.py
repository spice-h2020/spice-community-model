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

from cmSpice.dao.dao_db_interactionDistances import DAO_db_interactionDistances


class InteractionSimilarityDAO(SimilarityDAO):
    """
    Class to compute the interaction similarity between two users
    
    a) It computes the distanceMatrix between the objects the users interacted with (interaction objects (IO))
    b) For each IO userA interacted with, it gets the IO userB interacted with most similar to it.
    c) It computes the similarity between interaction attributes on these two IOs (e.g., emotions associated to IO(A) vs emotions associated to IO(B))
    """

#-------------------------------------------------------------------------------------------------------------------------------
#   Artwork Similarity
#-------------------------------------------------------------------------------------------------------------------------------

    def initializeArtworkDistanceMatrix(self):
        
        """
        # Interaction object dao and dataframe
        self.IO_dao = self.getInteractionObjectDAO()
        self.IO_data = self.getInteractionObjectData()
        """

        # Distance information
        self.distanceDict = self.computeIODistanceMatrix()
                
        #self.IO_distanceIndex = list(map(int, self.distanceDict['index']))
        self.IO_distanceIndex = self.distanceDict['index']
        self.IO_distanceMatrix = self.distanceDict['distanceMatrix']
        self.IO_data = self.distanceDict['data']

        """
        print("self.IO_distanceMatrix")
        print(self.IO_distanceMatrix)
        print("\n")
        
        matrix = self.IO_distanceMatrix.copy()
        matrix[matrix == 0.0] = 1.0
        matrix[matrix == 0.12] = 1.0
        
        # Get the two artworks with the highest similarity (In order to get high similarity artworks in iconclass)
        ind = np.unravel_index(np.argmin(matrix, axis=None), matrix.shape)
        """

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

        # Compute similarity between artworks
        IO_similarityMeasure = ComplexSimilarityDAO(daoJson,similarity_functions)        
        IO_distanceMatrix = IO_similarityMeasure.matrix_distance_explanation()
        IO_data = IO_similarityMeasure.data

        # To get self.dominantAttributes
        self.dominantAttributes = IO_similarityMeasure.getSimilarityMeasuresDict()
        
        # Export _id (id artefact) and distance matrix to json file
        IO_distanceDict = {}
        IO_distanceDict['index'] = list(map(str, IO_similarityMeasure.data['id'].tolist()))
        IO_distanceDict['distanceMatrix'] = IO_distanceMatrix
        IO_distanceDict['data'] = IO_data
        
        return IO_distanceDict

        
    def getInteractionObjectDAO(self):        
        route = DataLoader.fileRoute('artworks.json')
        if route:
            daoJson = DAO_json(route)
            return daoJson
        else:
            # TODO: Change by Logger
            print("Unable load artworks.json")
            return None
    
    def getInteractionObjectData(self):
        daoJson = self.getInteractionObjectDAO()
        return daoJson.getPandasDataframe()

#-------------------------------------------------------------------------------------------------------------------------------
#   Interaction Similarity - artwork similarity
#-------------------------------------------------------------------------------------------------------------------------------
  
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
            print("type object A: " + str(type(objectA)))
            print("type IO_distanceIndex: " + str(type(self.IO_distanceIndex[0])))
            print("objectA: " + str(objectA))
            print("IOB: " + str(IOB))
            print("\n")
            """
        
            objectAIndex = self.IO_distanceIndex.index(str(objectA))
            distanceMatrix_IOB_indexes = np.nonzero(np.in1d(self.IO_distanceIndex,IOB))[0]
            distanceMatrix_IOB_values = self.IO_distanceMatrix[objectAIndex, distanceMatrix_IOB_indexes]
            mostSimilarIOIndex = distanceMatrix_IOB_values.argmin()
            mostSimilarIO = IOB[mostSimilarIOIndex]  
            
            """
            print("type object A: " + str(type(objectA)))
            print("type IO_distanceIndex: " + str(type(self.IO_distanceIndex[0])))
            print("objectA: " + str(objectA))
            print("IOB: " + str(IOB))
            print("\n")
            print("IO_distanceIndex: " + str(self.IO_distanceIndex))
            print(self.IO_distanceMatrix)
            print("\n")
            print("objectA index: " + str(objectAIndex))
            print("distanceMatrix_IOB_indexes: " + str(distanceMatrix_IOB_indexes))
            print("distanceMatrix_IOB_values: " + str(distanceMatrix_IOB_values))
            print("minimumDistance index: " + str(mostSimilarIOIndex))
            print("minimumDistance value: " + str(distanceMatrix_IOB_values[mostSimilarIOIndex]))
            print("most similar IO: " + str(mostSimilarIO))
            print("\n\n\n")
            
            """
            
            # Get index of elements above a given threshold (let is say 0.5)
            
            
            # If the best match is still dissimilar
            similarThreshold = 0.35
            similarThreshold = 0.65
            similarThreshold = 0.5

            if ('weightArtworks' in self.perspective['algorithm']):
                """
                print("check similarity threshold perspective")
                print(self.perspective['algorithm']['weightArtworks'])
                print(type(self.perspective['algorithm']['weightArtworks']))
                print("\n")

                print("similarThreshold: " + str(similarThreshold))
                """

                similarThreshold = float(self.perspective['algorithm']['weightArtworks'])

                """
                print("similarThreshold: " + str(similarThreshold))
                print("\n")
                """
            
            distanceThreshold = 1 - similarThreshold

            #similarThreshold = 0.3
            #similarThreshold = 0.8
            #similarThreshold = 0.6
            #similarThreshold = 500.0
            if (distanceMatrix_IOB_values[mostSimilarIOIndex] > distanceThreshold):
                mostSimilarIOIndex = -1
            """
            """
            
            return mostSimilarIOIndex
        
        except ValueError:
            
            print("exception ")
            print("type object A: " + str(type(objectA)))
            """
            """
            print("objectA: " + str(objectA))
            print("IO_distanceIndex: " + str(self.IO_distanceIndex))
            
            objectAIndex = self.IO_distanceIndex.index(str(objectA))
            print("objectA index: " + str(objectAIndex))
            distanceMatrix_IOB_indexes = np.nonzero(np.in1d(self.IO_distanceIndex,IOB))[0]
            print("distanceMatrix_IOB_indexes: " + str(distanceMatrix_IOB_indexes))
            distanceMatrix_IOB_values = self.IO_distanceMatrix[objectAIndex, distanceMatrix_IOB_indexes]
            print("distanceMatrix_IOB_values: " + str(distanceMatrix_IOB_values))
            mostSimilarIOIndex = distanceMatrix_IOB_values.argmin()
            print("most similar IO Index: " + str(mostSimilarIOIndex))
            mostSimilarIO = IOB[mostSimilarIOIndex]
            print("most similar IO: " + str(mostSimilarIO))
            
            print("end exception")
            
            return -1
            
        
        """
        """

#-------------------------------------------------------------------------------------------------------------------------------
#   Interaction Similarity
#-------------------------------------------------------------------------------------------------------------------------------
  
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

        self.initializeArtworkDistanceMatrix()
        
        """
        self.dominantAttributes = {}
        #for similarityFunction in self.perspective["interaction_similarity_functions"] + self.perspective["similarity_functions"]:
        for similarityFunction in self.perspective["similarity_functions"]:
            similarityFeature = similarityFunction['sim_function']['on_attribute']['att_name']
            similarityMeasure = similarityFunction['sim_function']['name']
            self.dominantAttributes[similarityFeature] = self.initializeFromPerspective(self.IO_dao, similarityFunction)
        """
        
        # Interaction similarity function
        self.similarityFunction = self.perspective["interaction_similarity_functions"][0]
        self.similarityColumn = self.similarityFunction['sim_function']['on_attribute']['att_name']
        
        # Interaction attributes
        self.interactionAttribute = self.similarityFunction['sim_function']['on_attribute']['att_name']
        self.interactionAttributeOrigin = self.interactionAttribute + "_origin"
        self.interactionAttributeText = self.interactionAttribute.rsplit(".",1)[0] + ".text"

        # Fill na (interaction attributes)


        # Citizen attributes
        self.citizenAttributes = []
        for citizenAttribute in self.perspective['user_attributes']:
            self.citizenAttributes.append(citizenAttribute['att_name'])
        
        print("self.attribute: " + str(self.interactionAttribute))
        print("self.attribute (Origin): " + str(self.interactionAttributeOrigin))
        print("self.attribute (text): " + str(self.interactionAttributeText))
        print("self.data.columns: " + str(list(self.data.columns)))
        print("\n")

        print("self perspective")
        print(self.perspective)
        print("self.interactionSimilarityFunction")
        print(self.similarityFunction)
        print("\n")
        
        self.interactionSimilarityMeasure = self.initializeFromPerspective(dao, self.similarityFunction)

        print("checking self.interactionSimilarityFunction")
        print(self.interactionSimilarityMeasure.similarityFunction)
        print("\n")
        
        #print(self.interactionSimilarityMeasure)
        
        #print("dafdsfasdf")
        if (self.similarityFunction['sim_function']['name'] != 'NoInteractionSimilarityDAO' or 1==1):
            #print("sfdsf")

            # Remove the interactions with emotion with interactionSimilarityMeasure empty
            IOColumn = self.similarityFunction['sim_function']['interaction_object']['att_name']
            df = self.data.copy()

            print("dsfdsfsdf")

            # Check element count
            print("\n")
            print(df[[self.interactionAttribute]])
            print("\n")
            print(df[[self.interactionAttributeOrigin]])
            print("\n")
            print(df[[self.interactionAttributeText]])
            print("\n")


            df2 = df.explode([self.interactionAttribute, self.interactionAttributeOrigin, self.interactionAttributeText])

            df3 = df2.loc[ df2[self.similarityColumn].str.len() != 0 ]
            
            # Remove NaN values
            df3 = df3.dropna(subset=[self.interactionAttribute])
            
            # Remove False emotion
            
            # Remove interactions with artworks that are not in artworks.json
            df3 = df3.loc[ df3[self.interactionAttributeOrigin].isin(self.IO_data['id'].to_list()) ]

            print("df3")
            print(df3)
            print("\n\n")

            # Flag artwork is enabled (detect communities interacting with one specific artwork)
            # This flag is not added by the perspective configuration tool (for now, it is given manually)
            # if ('communityDetectionForArtwork' in self.perspective):
            # ["35230"] works
            if (self.checkSameArtworksFilter()):
                print("enter check same artwork filter")
                print("df3")
                print(df3)
                print("\n\n")
                df3 = self.applySameArtworksFilter(df3)
                print("df3")
                print(df3)
                print("\n\n")
                    

            print("df3 after artwork flag")
            print(df3)
            print("\n\n")
            
            groupList = []
            groupList.append('userid')
            groupList.extend(self.citizenAttributes)

            # Df3 perspective
            print("df3 perspective")
            print(df3[['userid', self.interactionAttribute, self.interactionAttributeOrigin, self.interactionAttributeText]])
            print("\n")
            
            print("groupby groupList")
            print(groupList)
            print("\n\n")
               
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

            # If self.data only has one user, throw exception
            if (len(self.data) <= 1):
                raise ValueError('Less than 2 interactions were found for the provided parameters. Clustering is impossible')

    def distance(self,elemA, elemB):
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
        print(userInteractionA['userid'])
        print(userInteractionB['userid'])
        """

        # Get interaction objects (IO) the user interacted with
        # print(self.similarityFunction)
        
        # Get ids of artworks the user interacted with
        IOColumn = self.interactionAttribute + "_origin"
        #IOColumn = self.similarityFunction['sim_function']['interaction_object']['att_name']
        IOA = userInteractionA[IOColumn]
        IOB = userInteractionB[IOColumn]
        
        IOA = list(map(str, IOA))
        IOB = list(map(str, IOB))
        
        """
        print("IO Columns")
        print(IOColumn)
        print(IOA)
        print(IOB)
        print("\n\n\n")
        """
        
        """
        """
        
        
        self.exchanged = False
        
        if (len(IOB) > len(IOA)):
            self.exchanged = True
            IOA, IOB = self.exchangeElements(IOA,IOB)
            userInteractionA, userInteractionB = self.exchangeElements(userInteractionA, userInteractionB)
        """
        """

        return self.distanceInteraction(elemA, elemB, userInteractionA, userInteractionB, IOA, IOB)
        
        
    
    def distanceInteraction(self, elemA, elemB, userInteractionA, userInteractionB, IOA, IOB):
        # Set largest list to be A and the other B
        #self.exchanged = False
        
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
            if (self.dominantAttributes[dominantAttribute].dominantValueType() == "list"):
                dominantValues[dominantAttribute] = []
        # Similar artworks users are compared with
        dominantArtworks = []

        try:
        
            # For each IO in A, get most similar IO in B
            for objectIndexA in range(len(IOA)):
                objectA = IOA[objectIndexA]
                objectIndexB = self.getSimilarIOIndex(objectA, IOB)
                objectB = IOB[objectIndexB]

                # A MATCHING SIMILAR ARTWORK WAS FOUND
                if (objectIndexB != -1):

                    # Retrieve the data from the database (if it exists)
                    getDatabaseConditions = {}
                    getDatabaseConditions['attribute'] = self.similarityColumn
                    getDatabaseConditions['similarity'] = self.similarityFunction['sim_function']['name']
                    getDatabaseConditions['citizen1'] = userInteractionA['userid']
                    getDatabaseConditions['artwork1'] = objectA
                    getDatabaseConditions['citizen2'] = userInteractionB['userid']
                    getDatabaseConditions['artwork2'] = objectB

                    daoInteractionDistances = DAO_db_interactionDistances()
                    databaseObject = daoInteractionDistances.getInteractionDistance(getDatabaseConditions)

                    # Get interaction similarity feature associated to IO A and IO B
                    interactionFeatureA = userInteractionA[self.similarityColumn][objectIndexA]
                    interactionFeatureB = userInteractionB[self.similarityColumn][objectIndexB]
                    
                    if (len(databaseObject) > 0):
                        distance = databaseObject['distance']
                        dominantInteractionAttributesList = databaseObject['dominantValue']
                    else:
                        
                        # Calculate distance between them
                        distance = self.interactionSimilarityMeasure.distanceValues(interactionFeatureA, interactionFeatureB)

                        # Add dominant interaction value to list (e.g., emotions = {joy: 3, sadness: 4, trust: 1} -> sadness
                        dominantInteractionAttributesList = self.interactionSimilarityMeasure.dominantValue(interactionFeatureA, interactionFeatureB)

                        
                    dominantInteractionAttributeA = dominantInteractionAttributesList[0]
                    dominantInteractionAttributeB = dominantInteractionAttributesList[1]

                    #dominantInteractionAttributeDistance = self.interactionSimilarityMeasure.dominantDistance(interactionFeatureA, interactionFeatureB)
                    dominantInteractionAttributeDistance = self.interactionSimilarityMeasure.getDistanceBetweenItems(dominantInteractionAttributeA, dominantInteractionAttributeB)


                    # Get dominant value (for each similarity measure attribute) associated to the 2 artworks: objectA and objectB
                    indexA = self.IO_data.loc[ self.IO_data['id'] == objectA ].index.values.astype(int)[0]
                    indexB = self.IO_data.loc[ self.IO_data['id'] == objectB ].index.values.astype(int)[0]

                    for dominantAttribute in self.dominantAttributes:
                        column = self.dominantValueColumn(name = dominantAttribute)
                        dominantValueMatrix = self.IO_data[column].tolist()

                        dominantValueA = dominantValueMatrix[indexA][indexB]
                        dominantValueB = dominantValueMatrix[indexB][indexA]

                        dominantValues[dominantAttribute] = dominantValueA

                        """
                        print("dominant attribute")
                        print(dominantAttribute)
                        print("dominant value - artworks")
                        print(dominantValueMatrix)
                        print("\n")
                        print(dominantValueMatrix[objectIndexA])
                        print("\n")
                        print("\n")
                        print("dominant value A")
                        print(dominantValueA)
                        print("dominant value B")
                        print(dominantValueB)
                        print("\n")
                        
                        """
                    
                    # Correct if exchanged
                    if (self.exchanged):
                        dominantArtworks.append(objectB)
                        dominantInteractionAttribute = dominantInteractionAttributeB
                    else:
                        dominantArtworks.append(objectA)
                        dominantInteractionAttribute = dominantInteractionAttributeA
                        
                    # Add dominant interaction attributes
                    dominantInteractionAttributes.append(dominantInteractionAttribute)
                    #dominantInteractionAttributeDistances.append(dominantInteractionAttributeDistance)
                    if dominantInteractionAttribute not in dominantInteractionAttributeDistances:
                        dominantInteractionAttributeDistances[dominantInteractionAttribute] = []
                    dominantInteractionAttributeDistances[dominantInteractionAttribute].append(dominantInteractionAttributeDistance)

                    # Save data in database
                    getDatabaseConditions['objectA'] = self.IO_data.loc[ self.IO_data['id'] == objectA ]['tittle'].to_list()[0]
                    getDatabaseConditions['indexA'] = str(indexA)
                    getDatabaseConditions['dominantValueA'] = dominantValueA
                    getDatabaseConditions['objectB'] = self.IO_data.loc[ self.IO_data['id'] == objectB ]['tittle'].to_list()[0]
                    getDatabaseConditions['indexB'] = str(indexB)
                    getDatabaseConditions['dominantValueB'] = dominantValueB

                    getDatabaseConditions['distance'] = distance
                    getDatabaseConditions['dominantValue'] = dominantInteractionAttributesList

                    daoInteractionDistances.updateInteractionDistance(getDatabaseConditions)



                # NO SIMILAR ARTWORK    
                else:
                    distance = 1
                

                distanceTotal += distance
                
            # Mean average        
            distanceTotal /= len(IOA)
            
        except Exception as e:
            print("\n\n\n")
            print("Exception dominant attribute")
            print(str(e))
            """
            print("elemA: " + str(elemA))
            print("elemB: " + str(elemB))
            """
            print("userA: " + str(userInteractionA['userid']))
            print("userB: " + str(userInteractionB['userid']))
            print("IOA: " + str(IOA))
            print("IOB: " + str(IOB))
            print("interactionsA: " + str(userInteractionA[self.similarityColumn]))
            print("interactionsB: " + str(userInteractionB[self.similarityColumn]))
            print("objectIndexA: " + str(objectIndexA))
            print("len IOA: " + str(len(IOA)))
            print("IOA: " + str(IOA))
            print(userInteractionA['userid'])

            raise Exception(e)
            
            # Get interaction similarity feature associated to IO A and IO B
            interactionFeatureA = userInteractionA[self.similarityColumn][objectIndexA]
            interactionFeatureB = userInteractionB[self.similarityColumn][objectIndexB]
            
            """
            print("interactionFeatureA: " + str(interactionFeatureA))
            print("interactionFeatureB: " + str(interactionFeatureB))
                    
            print("\n\n\n")
            """


        # Get most frequent element in dominantInteractionAttributes
        """
        print("dominant interaction attributes")
        print(dominantInteractionAttributes)
        """
        if (len(dominantInteractionAttributes) > 0):
            dominantInteractionAttribute = mode(dominantInteractionAttributes)
            distances = dominantInteractionAttributeDistances[dominantInteractionAttribute]
            dominantInteractionAttributeDistance = (sum(distances)) / (len(distances))
        
        else:
            dominantInteractionAttribute = ""
            dominantInteractionAttributeDistance = 1.0
            
            
             
        # Set dominant interaction attribute list
        dominantInteractionAttributeList = self.data.loc[elemA][self.similarityColumn + 'DominantInteractionGenerated']
        dominantInteractionAttributeList.append(dominantInteractionAttribute)
        # Use all the emotions
        #dominantInteractionAttributeList.append(dominantInteractionAttributes)
        self.data.at[elemA, self.similarityColumn + 'DominantInteractionGenerated'] = dominantInteractionAttributeList

        # Add dominant distance
        dominantInteractionAttributeDistanceList = self.data.loc[elemA][self.similarityColumn + 'DistanceDominantInteractionGenerated']
        dominantInteractionAttributeDistanceList.append(dominantInteractionAttributeDistance)
        self.data.at[elemA, self.similarityColumn + 'DistanceDominantInteractionGenerated'] = dominantInteractionAttributeDistanceList

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


#-------------------------------------------------------------------------------------------------------------------------------
#   Optimize distance
#-------------------------------------------------------------------------------------------------------------------------------

    def distanceOptimized(self,elemA, elemB):
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
        print(userInteractionA['userid'])
        print(userInteractionB['userid'])
        """

        # Get interaction objects (IO) the user interacted with
        # print(self.similarityFunction)
        
        # Get ids of artworks the user interacted with
        IOColumn = self.interactionAttribute + "_origin"
        #IOColumn = self.similarityFunction['sim_function']['interaction_object']['att_name']
        IOA = userInteractionA[IOColumn]
        IOB = userInteractionB[IOColumn]
        
        IOA = list(map(str, IOA))
        IOB = list(map(str, IOB))
        
        """
        print("IO Columns")
        print(IOColumn)
        print(IOA)
        print(IOB)
        print("\n\n\n")
        """
        
        """
        """
        
        
        self.exchanged = False
        
        if (len(IOB) > len(IOA)):
            self.exchanged = True
            IOA, IOB = self.exchangeElements(IOA,IOB)
            userInteractionA, userInteractionB = self.exchangeElements(userInteractionA, userInteractionB)
        """
        """

        return self.distanceInteractionOptimized(elemA, elemB, userInteractionA, userInteractionB, IOA, IOB)
        
        
    
    def distanceInteractionOptimized(self, elemA, elemB, userInteractionA, userInteractionB, IOA, IOB):
        # Set largest list to be A and the other B
        #self.exchanged = False
        
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
            if (self.dominantAttributes[dominantAttribute].dominantValueType() == "list"):
                dominantValues[dominantAttribute] = []
        # Similar artworks users are compared with
        dominantArtworks = []

        try:
        
            # For each IO in A, get most similar IO in B
            for objectIndexA in range(len(IOA)):
                objectA = IOA[objectIndexA]
                objectIndexB = self.getSimilarIOIndex(objectA, IOB)
                objectB = IOB[objectIndexB]

                # A MATCHING SIMILAR ARTWORK WAS FOUND
                if (objectIndexB != -1):

                    # Retrieve the data from the database (if it exists)
                    getDatabaseConditions = {}
                    getDatabaseConditions['attribute'] = self.similarityColumn
                    getDatabaseConditions['similarity'] = self.similarityFunction['sim_function']['name']
                    getDatabaseConditions['citizen1'] = userInteractionA['userid']
                    getDatabaseConditions['artwork1'] = objectA
                    getDatabaseConditions['citizen2'] = userInteractionB['userid']
                    getDatabaseConditions['artwork2'] = objectB

                    daoInteractionDistances = DAO_db_interactionDistances()
                    databaseObject = daoInteractionDistances.getInteractionDistance(getDatabaseConditions)

                    # Get interaction similarity feature associated to IO A and IO B
                    interactionFeatureA = userInteractionA[self.similarityColumn][objectIndexA]
                    interactionFeatureB = userInteractionB[self.similarityColumn][objectIndexB]
                    
                    if (len(databaseObject) > 0):
                        distance = databaseObject['distance']
                        dominantInteractionAttributesList = databaseObject['dominantValue']
                    else:
                        
                        # Calculate distance between them
                        distance = self.interactionSimilarityMeasure.distanceValues(interactionFeatureA, interactionFeatureB)

                        # Add dominant interaction value to list (e.g., emotions = {joy: 3, sadness: 4, trust: 1} -> sadness
                        dominantInteractionAttributesList = self.interactionSimilarityMeasure.dominantValue(interactionFeatureA, interactionFeatureB)

                        
                    dominantInteractionAttributeA = dominantInteractionAttributesList[0]
                    dominantInteractionAttributeB = dominantInteractionAttributesList[1]

                    #dominantInteractionAttributeDistance = self.interactionSimilarityMeasure.dominantDistance(interactionFeatureA, interactionFeatureB)
                    dominantInteractionAttributeDistance = self.interactionSimilarityMeasure.getDistanceBetweenItems(dominantInteractionAttributeA, dominantInteractionAttributeB)


                    # Get dominant value (for each similarity measure attribute) associated to the 2 artworks: objectA and objectB
                    indexA = self.IO_data.loc[ self.IO_data['id'] == objectA ].index.values.astype(int)[0]
                    indexB = self.IO_data.loc[ self.IO_data['id'] == objectB ].index.values.astype(int)[0]

                    for dominantAttribute in self.dominantAttributes:
                        column = self.dominantValueColumn(name = dominantAttribute)
                        dominantValueMatrix = self.IO_data[column].tolist()

                        dominantValueA = dominantValueMatrix[indexA][indexB]
                        dominantValueB = dominantValueMatrix[indexB][indexA]

                        dominantValues[dominantAttribute] = dominantValueA

                        """
                        print("dominant attribute")
                        print(dominantAttribute)
                        print("dominant value - artworks")
                        print(dominantValueMatrix)
                        print("\n")
                        print(dominantValueMatrix[objectIndexA])
                        print("\n")
                        print("\n")
                        print("dominant value A")
                        print(dominantValueA)
                        print("dominant value B")
                        print(dominantValueB)
                        print("\n")
                        
                        """
                    
                    # Correct if exchanged
                    if (self.exchanged):
                        dominantArtworks.append(objectB)
                        dominantInteractionAttribute = dominantInteractionAttributeB
                    else:
                        dominantArtworks.append(objectA)
                        dominantInteractionAttribute = dominantInteractionAttributeA
                        
                    # Add dominant interaction attributes
                    dominantInteractionAttributes.append(dominantInteractionAttribute)
                    #dominantInteractionAttributeDistances.append(dominantInteractionAttributeDistance)
                    if dominantInteractionAttribute not in dominantInteractionAttributeDistances:
                        dominantInteractionAttributeDistances[dominantInteractionAttribute] = []
                    dominantInteractionAttributeDistances[dominantInteractionAttribute].append(dominantInteractionAttributeDistance)

                    # Save data in database
                    getDatabaseConditions['objectA'] = self.IO_data.loc[ self.IO_data['id'] == objectA ]['tittle'].to_list()[0]
                    getDatabaseConditions['indexA'] = str(indexA)
                    getDatabaseConditions['dominantValueA'] = dominantValueA
                    getDatabaseConditions['objectB'] = self.IO_data.loc[ self.IO_data['id'] == objectB ]['tittle'].to_list()[0]
                    getDatabaseConditions['indexB'] = str(indexB)
                    getDatabaseConditions['dominantValueB'] = dominantValueB

                    getDatabaseConditions['distance'] = distance
                    getDatabaseConditions['dominantValue'] = dominantInteractionAttributesList

                    daoInteractionDistances.updateInteractionDistance(getDatabaseConditions)



                # NO SIMILAR ARTWORK    
                else:
                    distance = 1
                

                distanceTotal += distance
                
            # Mean average        
            distanceTotal /= len(IOA)
            
        except Exception as e:
            print("\n\n\n")
            print("Exception dominant attribute")
            print(str(e))
            """
            print("elemA: " + str(elemA))
            print("elemB: " + str(elemB))
            """
            print("userA: " + str(userInteractionA['userid']))
            print("userB: " + str(userInteractionB['userid']))
            print("IOA: " + str(IOA))
            print("IOB: " + str(IOB))
            print("interactionsA: " + str(userInteractionA[self.similarityColumn]))
            print("interactionsB: " + str(userInteractionB[self.similarityColumn]))
            print("objectIndexA: " + str(objectIndexA))
            print("len IOA: " + str(len(IOA)))
            print("IOA: " + str(IOA))
            print(userInteractionA['userid'])

            raise Exception(e)
            
            # Get interaction similarity feature associated to IO A and IO B
            interactionFeatureA = userInteractionA[self.similarityColumn][objectIndexA]
            interactionFeatureB = userInteractionB[self.similarityColumn][objectIndexB]
            
            """
            print("interactionFeatureA: " + str(interactionFeatureA))
            print("interactionFeatureB: " + str(interactionFeatureB))
                    
            print("\n\n\n")
            """


        # Get most frequent element in dominantInteractionAttributes
        """
        print("dominant interaction attributes")
        print(dominantInteractionAttributes)
        """
        if (len(dominantInteractionAttributes) > 0):
            dominantInteractionAttribute = mode(dominantInteractionAttributes)
            distances = dominantInteractionAttributeDistances[dominantInteractionAttribute]
            dominantInteractionAttributeDistance = (sum(distances)) / (len(distances))
        
        else:
            dominantInteractionAttribute = ""
            dominantInteractionAttributeDistance = 1.0
            
            
             
        # Set dominant interaction attribute list
        dominantInteractionAttributeList = self.data.loc[elemA][self.similarityColumn + 'DominantInteractionGenerated']
        dominantInteractionAttributeList.append(dominantInteractionAttribute)
        # Use all the emotions
        #dominantInteractionAttributeList.append(dominantInteractionAttributes)
        self.data.at[elemA, self.similarityColumn + 'DominantInteractionGenerated'] = dominantInteractionAttributeList

        # Add dominant distance
        dominantInteractionAttributeDistanceList = self.data.loc[elemA][self.similarityColumn + 'DistanceDominantInteractionGenerated']
        dominantInteractionAttributeDistanceList.append(dominantInteractionAttributeDistance)
        self.data.at[elemA, self.similarityColumn + 'DistanceDominantInteractionGenerated'] = dominantInteractionAttributeDistanceList

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


#-------------------------------------------------------------------------------------------------------------------------------
#   Filter (SAME ARTWORKS)
#-------------------------------------------------------------------------------------------------------------------------------
    
    # Flag artwork is enabled (detect communities interacting with one specific artwork)
    # This flag is not added by the perspective configuration tool (for now, it is given manually)
    # if ('communityDetectionForArtwork' in self.perspective):
    # ["35230"] works
    def checkSameArtworksFilter(self):
        return len(self.perspective['similarity_functions']) == 1 and len(self.perspective['similarity_functions'][0]['sim_function']['params']) > 0

    def applySameArtworksFilter(self, df3):
        # Filter self.data to only consider users interacting with that artwork
        # Remove interactions with artworks other than the one given by the 'communityDetectionForArtwork' flag
        artworkId = self.perspective['similarity_functions'][0]['sim_function']['params'][0]['artworkId']
        #logger.info("communityDetectionArtwork: " + str(artworkId))

        # Get ids
        artworkIds = []
        for element in self.perspective['similarity_functions'][0]['sim_function']['params']:
            artworkIds.append(element['artworkId'])

        
        print("apply same artworks filter")
        print(df3[[self.interactionAttributeOrigin]])
        print("\n")

        #dfArtworkFlag = df3.loc[ df3[self.interactionAttributeOrigin] == artworkId ]
        dfArtworkFlag = df3.loc[ df3[self.interactionAttributeOrigin].isin(artworkIds) ] 
        if (dfArtworkFlag.empty):
            df3 = df3.head(1)
            #logger.info("There are not interactions with the artwork with id " + str(artworkId))
        else:
            df3 = dfArtworkFlag.copy()

        print("after apply same artworks filter")
        print(df3[[self.interactionAttributeOrigin]])
        print("\n")

        return df3      
        
    
    
    