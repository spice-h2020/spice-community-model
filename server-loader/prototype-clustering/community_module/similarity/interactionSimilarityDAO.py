# Authors: José Ángel Sánchez Martín
import os
import json
import pandas as pd

import numpy as np

from community_module.similarity.similarityDAO import SimilarityDAO
from community_module.similarity.complexSimilarityDAO import ComplexSimilarityDAO
from dao.dao_json import DAO_json


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
        #for similarityFunction in self.perspective["interaction_similarity_functions"] + self.perspective["similarity_functions"]:
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
        self.interactionAttributeText = self.interactionAttribute.rsplit(".",1)[0] + ".text"
        
        # Citizen attributes
        self.citizenAttributes = []
        for citizenAttribute in self.perspective['user_attributes']:
            self.citizenAttributes.append(citizenAttribute['att_name'])
        
        print("self.attribute: " + str(self.interactionAttribute))
        print("self.attribute (Origin): " + str(self.interactionAttributeOrigin))
        print("self.attribute (text): " + str(self.interactionAttributeText))
        print("self.data.columns: " + str(list(self.data.columns)))
        print("\n")
        
        self.interactionSimilarityMeasure = self.initializeFromPerspective(dao, self.similarityFunction)
        #print(self.interactionSimilarityMeasure)
        
        #print("dafdsfasdf")
        if (self.similarityFunction['sim_function']['name'] != 'NoInteractionSimilarityDAO' or 1==1):
            #print("sfdsf")
        
        
            # Remove the interactions with emotion with interactionSimilarityMeasure empty
            IOColumn = self.similarityFunction['sim_function']['interaction_object']['att_name']
            df = self.data.copy()
            df2 = df.explode([self.interactionAttribute, self.interactionAttributeOrigin, self.interactionAttributeText])
            df3 = df2.loc[ df2[self.similarityColumn].str.len() != 0 ]
            
            # Remove NaN values
            df3 = df3.dropna(subset=[self.interactionAttribute])
            
            # Remove False emotion
            
            # Remove interactions with artworks that are not in artworks.json
            df3 = df3.loc[ df3[self.interactionAttributeOrigin].isin(self.IO_data['id'].to_list()) ]
            
            groupList = []
            groupList.append('userid')
            groupList.extend(self.citizenAttributes)
            
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
            # artworks we could match with a similar artwork
            df4['dominantArtworksDominantInteractionGenerated'] = [[] for _ in range(len(df4))]
            
            self.data = df4.copy()
        
        # Get IO distance matrix
        file = self.interactionObjectDistanceMatrixRoute()
        if (os.path.exists(file) and 1 == 2):
            self.distanceDict = self.getIODistanceMatrixFromFile(file)
        else:
            self.distanceDict = self.computeIODistanceMatrix()
                
        #self.IO_distanceIndex = list(map(int, self.distanceDict['index']))
        self.IO_distanceIndex = self.distanceDict['index']
        self.IO_distanceMatrix = np.asarray(self.distanceDict['distanceMatrix'])
        
        matrix = self.IO_distanceMatrix.copy()
        matrix[matrix == 0.0] = 1.0
        matrix[matrix == 0.12] = 1.0
        
        # Get the two artworks with the highest similarity (In order to get high similarity artworks in iconclass)
        ind = np.unravel_index(np.argmin(matrix, axis=None), matrix.shape)
    
    def interactionObjectDistanceMatrixRoute(self):
        abspath = os.path.dirname(__file__)
        relpath = "../../communityModel/" + "interactionObjects/" + self.perspective['name'] + ".json"
        exportFile = os.path.normpath(os.path.join(abspath, relpath))
        
        return exportFile
    
    def getInteractionObjectDAO(self):        
        abspath = os.path.dirname(__file__)
        relpath = "../../communityModel/data/artworks.json"
        #relpath = "../../communityModel/data/GAM_Catalogue_plus processed.json"
        route = os.path.normpath(os.path.join(abspath, relpath))
        
        daoJson = DAO_json(route)
        
        return daoJson
    
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
        IO_similarityMeasure = ComplexSimilarityDAO(daoJson,similarity_functions)        
        IO_distanceMatrix = IO_similarityMeasure.matrix_distance()
        
        # Export _id (id artefact) and distance matrix to json file
        IO_distanceDict = {}
        #IO_distanceDict['index'] = IO_similarityMeasure.data['id'].tolist()
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
            
            if (distanceMatrix_IOB_values[mostSimilarIOIndex] >= 0.6):
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
        
        # Set largest list to be A and the other B
        exchanged = False
        """
        if (len(IOB) > len(IOA)):
            exchanged = True
            IOA, IOB = self.exchangeElements(IOA,IOB)
            userInteractionA, userInteractionB = self.exchangeElements(userInteractionA, userInteractionB)
        """
        
        # Initialize distance
        distanceTotal = 0
        # Dominant interaction attribute value
        dominantInteractionAttribute = ""
        # Artwork implicit attributes
        dominantValues = {}
        for dominantAttribute in self.dominantAttributes:
            dominantValues[dominantAttribute] = ""
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
                    print("check object index " + str(userInteractionA['userid']))
                    print("elemB: " + str(userInteractionB['userid']))
                    print("objectA: " + str(objectA))
                    print("objectIndexB: " + str(objectIndexB))
                    print("\n\n")
                """
                
                #print("objectA: " + str(objectA))
                
                if (1 == 2 and objectIndexB != -1 and self.similarityFunction['sim_function']['name'] == "NoInteractionSimilarityDAO"):
                    objectB = IOB[objectIndexB]
                    distanceMatrixIndexObjectA = self.IO_distanceIndex.index(str(objectA))
                    distanceMatrixIndexObjectB = self.IO_distanceIndex.index(str(objectB))
                    
                    distance = self.IO_distanceMatrix[distanceMatrixIndexObjectA,distanceMatrixIndexObjectB]
                    print("new distance is :" + str(distance))
                    
                elif (objectIndexB != -1):
                    """
                    print("interactionsA: " + str(userInteractionA[self.similarityColumn]))
                    print("interactionsB: " + str(userInteractionB[self.similarityColumn]))
                    print("objectIndexA: " + str(objectIndexA))
                    print("len IOA: " + str(len(IOA)))
                    print("IOA: " + str(IOA))
                    print(userInteractionA['userid'])
                    
                    """
                    
                    
                    # Get interaction similarity feature associated to IO A and IO B
                    interactionFeatureA = userInteractionA[self.similarityColumn][objectIndexA]
                    interactionFeatureB = userInteractionB[self.similarityColumn][objectIndexB]
                    
                    """
                    print("self.interaction similarity measure: " + str(self.interactionSimilarityMeasure))
                    print("interactionFeatureA: " + str(interactionFeatureA))
                    print("interactionFeatureB: " + str(interactionFeatureB))
                    
                    
                    """
                    
                    
                    # Calculate distance between them
                    distance = self.interactionSimilarityMeasure.distanceValues(interactionFeatureA, interactionFeatureB)
                    #print("distance (" + str(interactionFeatureA) + "," + str(interactionFeatureB) + "): " + str(distance))
                    distance = self.interactionSimilarityMeasure.dissimilarFlag(distance)
                    #print("distance dissimilar (" + str(interactionFeatureA) + "," + str(interactionFeatureB) + "): " + str(distance))
                    #print("\n")
                    

                    # Add dominant interaction value to list (e.g., emotions = {joy: 3, sadness: 4, trust: 1} -> sadness
                    dominantInteractionAttributeA, dominantInteractionAttributeB = self.interactionSimilarityMeasure.dominantInteractionAttribute(interactionFeatureA, interactionFeatureB)
                    
                    
                    # Add dominant value for each artwork attribute used to compute similarity between them
                    """
                    print("objectA: " + str(objectA))
                    print("objectB: " + str(objectB))
                    print("\n")
                    """
                    
                    # Get objects data
                    column = self.perspective['similarity_functions'][0]['sim_function']['on_attribute']['att_name']
                    artworks_df = self.IO_data.loc[ self.IO_data['id'].isin([objectA, objectB]) ]
                    
                    """
                    print("df")
                    print(df[['id', column]] )
                    print("\n")
                    
                    """
                    
                    
                    
                    # Compute & Save dominant attribute
                    for dominantAttribute in self.dominantAttributes:
                        similarityMeasure = self.dominantAttributes[dominantAttribute]
                        
                        valueA = artworks_df.loc[ artworks_df['id'] == objectA ][dominantAttribute].to_list()[0]
                        #print(valueA)
                        valueB = artworks_df.loc[ artworks_df['id'] == objectB ][dominantAttribute].to_list()[0]
                        #print(valueB)
                        dominantValue = similarityMeasure.dominantValue(valueA, valueB)
                        #print(dominantValue)
                        dominantValues[dominantAttribute] = dominantValue
                        #print(dominantValues)
                        #print("dominantValue: " + str(dominantValue))
                        
                                            
                    #dominant_artworkSimilarityFeature = 
                    
                    # Set artwork ID we successfully found a match for
                    dominantArtworks.append(objectA)
                    
                    
                    
                    
                    
                    """
                    print("dominantA: " + str(dominantInteractionAttributeA))
                    print("dominantB: " + str(dominantInteractionAttributeB))
                    
                    
                    
                    """
                    
                    

                    if (exchanged):
                        dominantInteractionAttribute = dominantInteractionAttributeB
                    else:
                        dominantInteractionAttribute = dominantInteractionAttributeA
                        
                    # Add objectA to the list of compared interacted artworks 
                    
                else:
                    distance = 1
                
                """
                print("distance: " + str(distance))
                print("distanceTotal: " + str(distanceTotal))
                print("\n\n")
                
                """
                
                """
                """
                distanceTotal += distance
                
            
            distanceTotal /= len(IOA)
            
            """
            print("distanceTotal (FINAL) (" + str(userInteractionA['userid']) + "; " + str(userInteractionB['userid']) + "): " + str(distanceTotal))
            print("\n\n")
            
            """
            
             
            """
            """
            
            if (userInteractionA['userid'] == 'e4aM9WL7' and userInteractionB['userid'] == 'BNtsz8zb' and 1 == 2):
                print("check interaction distance " + str(userInteractionA['userid']))
                print("elemB: " + str(userInteractionB['userid']))
                print("distanceTotal (FINAL): " + str(distanceTotal))
                print("\n\n")
            
        except Exception as e:
            print("\n\n\n")
            print("Exception dominant attribute")
            print(str(e))
            print("elemA: " + str(elemA))
            print("elemB: " + str(elemB))
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
            
            # Get interaction similarity feature associated to IO A and IO B
            interactionFeatureA = userInteractionA[self.similarityColumn][objectIndexA]
            interactionFeatureB = userInteractionB[self.similarityColumn][objectIndexB]
            
            """
            print("interactionFeatureA: " + str(interactionFeatureA))
            print("interactionFeatureB: " + str(interactionFeatureB))
                    
            print("\n\n\n")
            """
            
            
        if (self.similarityFunction['sim_function']['name'] != 'NoInteractionSimilarityDAO'):
        
            
            
            #print(self.data[[self.similarityColumn]])
            
            """
            print("dominantInteractionAttributeList: " + str(dominantInteractionAttributeList))
            print("distanceTotal: " + str(distanceTotal))
            print("\n\n")
            
            
            """
             
            # Set dominant interaction attribute list
            dominantInteractionAttributeList = self.data.loc[elemA][self.similarityColumn + 'DominantInteractionGenerated']
            dominantInteractionAttributeList.append(dominantInteractionAttribute)
            self.data.at[elemA, self.similarityColumn + 'DominantInteractionGenerated'] = dominantInteractionAttributeList
            
            
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
        
        
        
        
        
    
    
    