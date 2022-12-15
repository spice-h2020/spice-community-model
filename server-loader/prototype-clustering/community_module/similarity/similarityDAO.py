# Authors: José Ángel Sánchez Martín
from itertools import product
import numpy as np
import importlib
import json

class SimilarityDAO:
    """Class to define the functions to be implemented to calculate
    the similarity between elements.
    """
    
    def __init__(self, dao, similarityFunction = {}):
        """Construct of Similarity objects.

        Parameters
        ----------
        dao : dao object class
            DAO which processes and provides the data required by the similarity measure.
        
        """
        self.dao = dao
        self.similarityFunction = similarityFunction
        if (len(similarityFunction) > 0):
            self.similarityColumn = similarityFunction['on_attribute']['att_name']
        else:
            self.similarityColumn = ""
            
        self.data = self.dao.getPandasDataframe()
        
    def distanceValues(self, valueA, valueB):
        """
        Method to obtain the distance between two valid values given by the similarity measure.
        e.g., sadness vs fear in plutchickEmotionSimilarity

        Parameters
        ----------
        valueA : object
            Value of first element corresponding to elemA in self.data
        valueB : object
            Value of first element corresponding to elemB in self.data

        Returns
        -------
        double
            Distance between the two values.
        """
        return 1.0
        
    def dissimilarFlag(self, distance):
        if ('dissimilar' in self.similarityFunction and self.similarityFunction['dissimilar'] == True):
            print("apply dissimilar")
            distance = 1 - distance
            
        return distance
        

    def distance(self,elemA, elemB):
        """Method to obtain the distance between two elements whose information is given as a row of a pandas dataframe.

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
        valueA = self.data.loc[elemA][self.similarityColumn]
        valueB = self.data.loc[elemB][self.similarityColumn]
        
        return self.distanceValues(valueA, valueB)

    def similarity(self,elemA, elemB):
        """Method to obtain the similarity between two element.

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
        pass

    def matrix_distance(self):
        """Method to calculate the matrix of distance between all element included in data.

        Returns
        -------
        np.array
            Matrix that contains all similarity values.
        """
        users = self.data.index
        pairs = product(range(len(users)), repeat=2)
        
        # This checks 0,1 and 1,0
        # Change it to only check 0,1 and assign the same to 1,0
        matrix = np.zeros((len(users), len(users)))
        for p in pairs:
            dist = self.distance(users[p[0]], users[p[1]])
            matrix[p[0], p[1]] = dist
            """
            print("user1: " + str(users[p[0]]))
            print("user2: " + str(users[p[1]]))
            print("distance: " + str(dist))
            """


        # Reduce the matrix to 2 decimals
        matrix = np.round(matrix,2)
        
        self.distanceMatrix = matrix

        return matrix
        
    def updateDistanceMatrix(self, userIds, distanceMatrix):
        """
        Method to update the distance matrix with the new elements included in the data.
            
        Parameters
        ----------
            distanceMatrix : np.ndarray
                Previous distance matrix 
            userIds : list
                Includes the ids of the users to update.

        Returns
        -------
            np.ndarray
                Matrix that contains all distance values.
        """
        print("update distance matrix")
        # https://www.geeksforgeeks.org/python-make-pair-from-two-list-such-that-elements-are-not-same-in-pairs/
        # https://www.statology.org/numpy-add-column/
        # https://stackoverflow.com/questions/8486294/how-do-i-add-an-extra-column-to-a-numpy-array
        # https://www.statology.org/pandas-get-index-of-row/
        # https://www.geeksforgeeks.org/python-program-to-get-all-pairwise-combinations-from-a-list/
        indexes = self.data.index
        updateIndexes = self.data[self.data['userid'].isin(userIds)].index #.tolist()
        pairs = product(indexes,updateIndexes)
        
        #print(self.data)
        
        matrix = np.zeros((len(indexes), len(indexes)))
        matrix[0:distanceMatrix.shape[0],0:distanceMatrix.shape[1]] = distanceMatrix
        
        #print(matrix)
        
        for p in pairs:
            """
            print("\n")
            print("pairs")
            print(p[0])
            print(p[1])
            print("\n")
            """
            dist = self.distance(p[0],p[1])
            matrix[p[0], p[1]] = dist
            matrix[p[1],p[0]] = dist
        
        
        
        # Reduce the matrix to 2 decimals
        matrix = np.round(matrix,2)
        self.distanceMatrix = matrix
        
        print(matrix)
        
        return matrix


    def matrix_similarity(self):
        """Method to calculate the matrix of similarity between all element included in data.

        Returns
        -------
        np.ndarray
            Matrix that contains all similarity values.
        """
        users = self.data.index
        pairs = product(range(len(users)), repeat=2)

        matrix = np.zeros((len(users), len(users)))
        for p in pairs:
            dist = self.similarity(users[p[0]], users[p[1]])
            matrix[p[0], p[1]] = dist

        return matrix
    

#-------------------------------------------------------------------------------------------------------------------------------
#   Auxiliar functions
#-------------------------------------------------------------------------------------------------------------------------------

    def initializeFromPerspective(self, dao, similarityFunction):
        similarityName = similarityFunction['sim_function']['name']
        similarityFile = "community_module.similarity." + similarityName[0].lower() + similarityName[1:]
        similarityModule = importlib.import_module(similarityFile)
        similarityClass = getattr(similarityModule,similarityName)
        similarityMeasure = similarityClass(dao,similarityFunction['sim_function'])
        
        return similarityMeasure
    
    def exchangeElements(self, elemA, elemB):
        aux = elemA
        elemA = elemB
        elemB = aux
        
        return elemA, elemB
    
    def exportDistanceMatrix(self, distanceMatrix, exportFile):
        distanceMatrix = distanceMatrix.tolist()
        
        with open(exportFile, "w") as outfile:
            json.dump(distanceMatrix, outfile, indent=4)    
    
    def importDistanceMatrix(self, importFile):
        with open(importFile, 'r', encoding='utf8') as f:
            distanceMatrix = json.load(f)
                
        return np.asarray(distanceMatrix)
        
        
        
        
#-------------------------------------------------------------------------------------------------------------------------------
#   To calculate dominant value in interaction attributes (always dict)
#-------------------------------------------------------------------------------------------------------------------------------
       
    def dominantInteractionAttribute(self, dictA, dictB):
        """
        Method to obtain the dominant sentiment for A and B
        Parameters
        ----------
        dictA : dict
            Keys: String
            Values: double
                Confidence Level
        dictB : dict
            Keys: String

            Values: double
                Confidence Level

        Returns
        -------
        String
            Dominant key
        """
        if (len(dictA) <= 0):
            keyA = ""
        else:
            keyA = max(dictA, key=dictA.get).lower()
            
        if (len(dictB) <= 0):
            keyB = ""
        else:
            keyB = max(dictB, key=dictB.get).lower()
        
        return keyA, keyB
    
#-------------------------------------------------------------------------------------------------------------------------------
#   To calculate dominant value between two values (in order to explain communities)
#-------------------------------------------------------------------------------------------------------------------------------
    
    def dominantElemValue(self, elemA, elemB):
        valueA = self.data.loc[elemA][self.similarityColumn]
        valueB = self.data.loc[elemB][self.similarityColumn]
        
        return self.dominantValue(valueA,valueB)
        
    def dominantValue(self, valueA, valueB):
        return valueA
         