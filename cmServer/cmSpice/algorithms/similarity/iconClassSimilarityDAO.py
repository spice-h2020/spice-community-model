# Authors: José Ángel Sánchez Martín
import os
from cmSpice.algorithms.similarity.similarityDAO import SimilarityDAO

class IconClassSimilarityDAO(SimilarityDAO):
    
    def __init__(self, dao, similarityFunction):
        """Construct of TaxonomySimilarity objects.

        Parameters
        ----------
        data : pd.DataFrame
            Dataframe where index is ids of elements, columns a list of taxonomy member and
            values contain the number of times that a taxonomy member is in an element.
        """
        super().__init__(dao, similarityFunction)
        self.similarityColumn = similarityFunction['on_attribute']['att_name']



    def elemLayer(self,elem):
        return len(elem)
    
    """
    def getIconClassList2(self,iconClassString):
        iconClassList = iconClassString.split("; ")
        iconClassList = [iconClass.split(" ")[0] for iconClass in iconClassList if iconClass]
        return iconClassList  
    
    def getIconClassList(self, elem):
        iconClassString = self.data.loc[elem][self.similarityColumn]
        return self.getIconClassList2(iconClassString)
    
    """
    
    def distanceItems(self,elemA,elemB):
        """Method to obtain the distance between two taxonomy members.

        Parameters
        ----------
        elemA : object
            Id of first element. This id should be in self.data.
        elemB : object
            Id of second element. This id should be in self.data.

        Returns
        -------
        double
            Similarity between the two taxonomy members.
        """
        """       
        print("elemA: " + elemA)
        print("elemB: " + elemB)
        print("commonAncestor: " + commonAncestor)
        print("distance: " + str(1 - sim))
        print("\n")
        """
        """
        elemA = elemA.split("(")[0]
        elemB = elemB.split("(")[0]
        """
        
        # Get first common characters 
        # https://stackoverflow.com/questions/18715688/find-common-substring-between-two-strings
        commonAncestor = os.path.commonprefix([elemA, elemB])
        maxLayer = max(self.elemLayer(elemA), self.elemLayer(elemB))
        if (maxLayer <= 0):
            sim = 0
        else:
            sim = self.elemLayer(commonAncestor) / maxLayer
            
        return 1 - sim
        
    def iconClassBestMatch(self, elemA, iconClassListB):
        """        
        a) It finds the iconClass elem in iconClassListB with the largest common prefix with elemA (most similar)
        
        Parameters
        ----------
        elemA: String
            Iconclass id belonging to artwork A
        iconClassListB: list
            List of iconclass id belonging to artwork B
        
        Returns
        -------
            longestPrefixElemB: String
                Iconclass id in iconClassListB that is most similar to elemA
        """
        longestPrefix = ""
        longestPrefixElemB = ""
        for elemB in iconClassListB:
            prefix = os.path.commonprefix([elemA, elemB])
            if (len(prefix) > len(longestPrefix) or (len(prefix) == len(longestPrefix) and len(longestPrefixElemB) > len(elemB))):
                longestPrefix = prefix
                longestPrefixElemB = elemB
                
        return longestPrefixElemB

    def iconClassDistance(self, elemA, iconClassListB):
        """
        Computes the distance between an iconClass elem from artwork A and the iconClass elements from artwork B
        
        a) It finds the iconClass elem in iconClassListB with the largest common prefix with elemA and compares it.
        b) If none are found, distance is set to 1.
        
        Parameters
        ----------
        elemA: String
            Iconclass id belonging to artwork A
        iconClassListB: list
            List of iconclass id belonging to artwork B
        
        Returns
        -------
            distance: float
        """
        longestPrefixElemB = self.iconClassBestMatch(elemA, iconClassListB)
        return self.getDistanceBetweenItems(elemA,longestPrefixElemB)    

    def distanceValues(self, iconClassListA, iconClassListB):
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
        """
        print("iconclassListA: " + str(iconClassListA))
        print("iconclassListB: " + str(iconClassListB))
        print("\n")
        """
        
        
        # Set largest list to be A and the other B
        if (len(iconClassListB) > len(iconClassListA)):
            aux = iconClassListA
            iconClassListA = iconClassListB
            iconClassListB = aux
        
        """
        print("elemA: " + str(elemA))
        print("elemB: " + str(elemB))
        print("Iconclass A: " + str(iconClassListA))
        print("Iconclass B: " + str(iconClassListB))
        print("\n")
        """
        
        # Compare each element of valueA with the element from B with the biggest common prefix
        # If none from B share a common prefix, distance is equal to 0
        distanceTotal = 0
        for elemA in iconClassListA:
            distance = self.iconClassDistance(elemA,iconClassListB)
            distanceTotal += distance
            
            #print("distance " + str(elemA) + " : " + str(distance))
        
        distanceTotal /= len(iconClassListA)
        """
        print("distanceTotal: " + str(distanceTotal))
        """
        
        return distanceTotal
        
#-------------------------------------------------------------------------------------------------------------------------------
#   To calculate dominant value between two values (in order to explain communities)
#-------------------------------------------------------------------------------------------------------------------------------
    
    def dominantValue(self, iconClassListA, iconClassListB):
        dominantValues = []

        dominantValues.append(self.extractDominantValue(iconClassListA, iconClassListB, self.artworkA, self.artworkB) )
        dominantValues.append(self.extractDominantValue(iconClassListB, iconClassListA, self.artworkB, self.artworkA) )

        return dominantValues


    def extractDominantValue(self, iconClassListA, iconClassListB, artworkA, artworkB):
        explainable_iconclassValues = []
        
        """
        iconClassListA = self.getIconClassList2(iconClassListA)
        iconClassListB = self.getIconClassList2(iconClassListB)
        """
        
        try:
            
            for elemA in iconClassListA:
                longestPrefixElemB = self.iconClassBestMatch(elemA, iconClassListB)
                commonParent = os.path.commonprefix([elemA, longestPrefixElemB])
                maxLayer = max(self.elemLayer(elemA), self.elemLayer(longestPrefixElemB))
                if (self.elemLayer(commonParent) + 2 >= maxLayer):
                    # Previous explanation
                    #explainable_iconclassValues.append(commonParent)

                    # New explanation: add information about the iconclassIDs (children) from which this new one (parent) is derived 
                    commonParentDict = {}
                    commonParentDict[commonParent] = {}
                    commonParentDict[commonParent][elemA] = [ artworkA['id'] ]
                    if (longestPrefixElemB not in commonParentDict[commonParent]):
                        commonParentDict[commonParent][longestPrefixElemB] = []
                    commonParentDict[commonParent][longestPrefixElemB].append( artworkB['id'] )

                    explainable_iconclassValues.append(commonParentDict)

        except Exception as e:
            print("exception")
            print(e)
            
            """
            print("longestPrefixElemB: " + str(longestPrefixElemB))
            print("commonParent: " + str(commonParent))
            print("maxLayer: " + str(maxLayer))
            """
            
        
        return explainable_iconclassValues
    

    
    
    
    
    
    
    
    
    