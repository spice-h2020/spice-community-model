# Authors: José Ángel Sánchez Martín
from community_module.similarity.similarityDAO import SimilarityDAO

class ComplexSimilarityDAO(SimilarityDAO):

    def __init__(self,dao,similarityDict):
        """Construct of Similarity objects.

        Parameters
        ----------
        dao : dao to obtain data from database
        similarityDict: dictionary
            Dictionary with keys (similarity measure classes) and values (weight of that similarity measure)
        
        """
        super().__init__(dao)
        
        self.similarityDict = {}
        for similarityFunction in similarityDict:
            similarityMeasure = self.initializeFromPerspective(dao,similarityFunction)
            self.similarityDict[similarityMeasure] = similarityFunction['sim_function']

    def distance(self,elemA, elemB):
        """Method to obtain the distance between two element.

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
        complexDistance = 0
        complexWeight = 0
        for similarity, similarityFunction in self.similarityDict.items():
            weight = similarityFunction.get('weight',0.5)
            
            simDistance = similarity.distance(elemA,elemB)
            
            """
            print("similarity: " + str(similarity))
            print("similarityFunction: " + str(similarityFunction))
            print("elemA: " + str(self.data.loc[elemA]['userid']))
            print("elemB: " + str(self.data.loc[elemB]['userid']))
            print("sim distance: " + str(simDistance))
            print("\n")
            """
            
            # Different mode (return 1 - originalDistance)
            simDistance = similarity.dissimilarFlag(simDistance)
            simDistance2 = simDistance * weight
            
            complexDistance += simDistance2
            complexWeight = complexWeight + weight 
            
        # print("complexDistance: " + str(complexDistance))
        
        complexDistance = complexDistance / complexWeight
        
        # print("complexDistance: " + str(complexDistance))
        # print("\n")
        
        return complexDistance