# Authors: José Ángel Sánchez Martín
from cmSpice.algorithms.similarity.similarityDAO import SimilarityDAO

from owlready2 import *

class OntologySimilarity(SimilarityDAO):
    
    def __init__(self, dao, similarityFunction = {}):
        """Construct of TaxonomySimilarity objects.

        Parameters
        ----------
        data : pd.DataFrame
            Dataframe where index is ids of elements, columns a list of taxonomy member and
            values contain the number of times that a taxonomy member is in an element.
        """
        super().__init__(dao,similarityFunction)
        # load ontology
        #onto_path.append("ontologies")
        self.onto = get_ontology(os.path.join(os.path.dirname(__file__), 'ontologies/' + self.similarityColumn.lower() + '.owl'))      

        self.onto.load()


    def distanceItems(self, ontologyValueA, ontologyValueB):
        """
        Method to obtain the distance between two ages.

        Parameters
        ----------
        ontologyValueA : String
            First ontology id
        ontologyValueB : String
            Second ontology id

        Returns
        -------
        double
            Distance between the two elements.
        """

        if (ontologyValueB != "none"):

            # Get ancestors chosen values
            ancestorsA = self.onto[ontologyValueA.capitalize()].ancestors()
            ancestorsB = self.onto[ontologyValueB.capitalize()].ancestors()

            # Intersection ancestors (common ancestors)
            commonAncestors = ancestorsA.intersection(ancestorsB)
            lowestCommonAncestor, lowestCommonAncestorLayer = self.getOntologyLowestCommonAncestor(commonAncestors)

            # Get distance
            sim = lowestCommonAncestorLayer / max(self.elemLayer(ancestorsA), self.elemLayer(ancestorsB))
            distance = 1 - sim
        else:
            distance = 1.0

        return distance

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
        try:
            valueA = self.data.loc[elemA][self.similarityColumn]
            valueB = self.data.loc[elemB][self.similarityColumn]
                    
            return self.ontologyDistance(valueA,valueB)
        except Exception as e:
            print("exception materials ontology - distance")
            print(e)
            print("elemA: " + str(elemA))
            print("elemB: " + str(elemB))
            print("similarityColumn: " + self.similarityColumn)
            print("materialA: " + str(valueA))
            print("materialB: " + str(valueB))
            print("\n")
            return 1

    def distanceValues(self, valueA, valueB):
        return self.ontologyDistance(self, valueA, valueB)

    def ontologyDistance(self, valueA, valueB):
        """Method to obtain the distance between two taxonomy members.

        Parameters
        ----------
        elemA : list
            Id of first element. This id should be in self.data.
        elemB : object
            Id of second element. This id should be in self.data.

        Returns
        -------
        double
            Similarity between the two taxonomy members.
        """
        try:
            

            # Some artworks have more than one material (separated by ,)
            ontologyValueListA, ontologyValueListB = self.getOntologyValueList(valueA, valueB)

            

            # Compare each of the ontologyValueListA with each of the ontologyValueListB and the other way around
            distance1 = self.ontologyDistanceList(ontologyValueListA, ontologyValueListB)
            
            distance2 = self.ontologyDistanceList(ontologyValueListB, ontologyValueListA)
            

            

            return (distance1 + distance2) / 2
            
        # One of the elements is not in the taxonomy
        except Exception as e:
            print("exception ontologyDistance")
            print(e)

            print("ontologyDistance")
            print(valueA)
            print(valueB)
            print("\n")

            print("ontologyDistance List")
            print(ontologyValueListA)
            print(ontologyValueListB)
            print("\n")

            print("distance1: " + str(distance1))
            print("distance2: " + str(distance2))


            print("ontology distance")
            print(distance1)
            print(distance2)
            print("\n")


            return 1

    def ontologyDistanceList(self, ontologyValueListA, ontologyValueListB):
        """Method to obtain the distance between two taxonomy members.

        Parameters
        ----------
        ontologyValueListA : list
            List 1 of ontology values
        ontologyValueListB : list
            List 2 of ontology values

        Returns
        -------
        double
            Similarity between the two taxonomy members.
        """
        distanceTotal = 0
        valuesNumber = 0

        for ontologyValueA in ontologyValueListA:
            # Get most similar ontologyValueB in ontologyValueListB
            print("before calling most similar")
            ontologyValueB = self.mostSimilarOntologyValue(ontologyValueA, ontologyValueListB)
            print("ontologyDistanceList function after calling most similar")
            print("ontologyValueA: " + str(ontologyValueA))
            print("ontologyValueB: " + str(ontologyValueB))
            print("\n")

            distance = self.getDistanceBetweenItems(ontologyValueA, ontologyValueB)

            distanceTotal += distance
            valuesNumber += 1

        if (valuesNumber > 0):
            distanceTotal = distanceTotal / valuesNumber

        return distanceTotal

    def getOntologyLowestCommonAncestor(self, commonAncestors):
        """
        Returns the lowest common ancestor among a list of ancestors given by an ontology.

        Parameters
        ----------
        commonAncestors : list
            List of common ancestors

        Returns
        -------
        object
            Lowest common ancestor
        """
        lowestAncestor = None
        lowestAncestorLayer = -1
        for ancestor in commonAncestors:
            ancestor_ancestors = ancestor.ancestors()
            ancestorLayer = self.elemLayer(ancestor_ancestors)
            if (ancestorLayer > lowestAncestorLayer):
                lowestAncestorLayer = ancestorLayer
                lowestAncestor = ancestor
            
        return lowestAncestor, lowestAncestorLayer

    def elemLayer(self,ancestors):
        return len(ancestors)

    def getOntologyValueList(self, valueA, valueB):
        """
        ontologyValueListA = valueA.split(', ')
        ontologyValueListB = valueB.split(', ')
        if ('none' in ontologyValueListA):
            ontologyValueListA.remove('none')
        if ('none' in ontologyValueListB):
            ontologyValueListB.remove('none')
        
        return ontologyValueListA, ontologyValueListB
        """

        ontologyValueListA = valueA
        ontologyValueListB = valueB

        if ('none' in ontologyValueListA):
            ontologyValueListA.remove('none')
        if ('none' in ontologyValueListB):
            ontologyValueListB.remove('none')

        return ontologyValueListA, ontologyValueListB
        
    def mostSimilarOntologyValue(self, ontologyValueA, ontologyValueListB):
        chosenValue = "none"

        try:
            chosenLowestCommonAncestor = "none"
            chosenLowestCommonAncestorLayer = -1
            for ontologyValueB in ontologyValueListB:
                """
                print("most similar function")
                print("ontologyValueA: " + str(ontologyValueA))
                print("ontologyValueA 2: " + str(self.onto[ontologyValueA.capitalize()]))
                print("ontologyValueB: " + str(ontologyValueB))
                print("ontologyValueB 2: " + str(self.onto[ontologyValueB.capitalize()]))
                print("\n")
                """
                
                # Get ancestors chosen values
                ancestorsA = self.onto[ontologyValueA.capitalize()].ancestors()
                ancestorsB = self.onto[ontologyValueB.capitalize()].ancestors()

                # Intersection ancestors (common ancestors)
                commonAncestors = ancestorsA.intersection(ancestorsB)
                """
                print("common ancestors most similar")
                print(commonAncestors)
                print("\n")
                """

                lowestCommonAncestor, lowestCommonAncestorLayer = self.getOntologyLowestCommonAncestor(commonAncestors)

                """
                print("lowest common ancestor")
                print(lowestCommonAncestor)
                print(lowestCommonAncestorLayer)
                print("\n")
                """
                
                if (lowestCommonAncestorLayer > chosenLowestCommonAncestorLayer):
                    chosenLowestCommonAncestor = lowestCommonAncestor
                    chosenLowestCommonAncestorLayer = lowestCommonAncestorLayer
                    chosenValue = ontologyValueB
        
        except Exception as e:
            print("mostSimilarOntologyValue")
            print(e)
            print("\n")
            return 1

        return chosenValue

#-------------------------------------------------------------------------------------------------------------------------------
#   To calculate dominant value between two values (in order to explain communities)
#-------------------------------------------------------------------------------------------------------------------------------
    
    def dominantValue(self, valueA, valueB):
        explainableValues = []

        try:
            ontologyValueListA, ontologyValueListB = self.getOntologyValueList(valueA, valueB)

            for ontologyValueA in ontologyValueListA:
                # Get most similar ontologyValueB in ontologyValueListB
                ontologyValueB = self.mostSimilarOntologyValue(ontologyValueA, ontologyValueListB)
                if (ontologyValueB != "none"):
                    # Get ancestors chosen values
                    ancestorsA = self.onto[ontologyValueA.capitalize()].ancestors()
                    ancestorsB = self.onto[ontologyValueB.capitalize()].ancestors()

                    # Intersection ancestors (common ancestors)
                    commonAncestors = ancestorsA.intersection(ancestorsB)
                    lowestCommonAncestor, lowestCommonAncestorLayer = self.getOntologyLowestCommonAncestor(commonAncestors)

                    # Explanation requires string (not Thing.class)
                    commonParent = lowestCommonAncestor.name.lower()
                    commonParentDict = {}
                    commonParentDict[commonParent] = {}
                    commonParentDict[commonParent][ontologyValueA] = [ self.artworkA['id'].to_list()[0] ]
                    #commonParentDict[commonParent][ontologyValueA] = { "id": [self.artworkA['id'].to_list()[0]], "tittle": [self.artworkA['tittle'].to_list()[0]] }
                    if (ontologyValueB not in commonParentDict[commonParent]):
                        commonParentDict[commonParent][ontologyValueB] = []
                        #commonParentDict[commonParent][ontologyValueB] = {"id": [], "tittle": []}
                    commonParentDict[commonParent][ontologyValueB].append( self.artworkB['id'].to_list()[0] )
                    #commonParentDict[commonParent][ontologyValueB]['id'].append( self.artworkB['id'].to_list()[0] )
                    #commonParentDict[commonParent][ontologyValueB]['tittle'].append( self.artworkB['tittle'].to_list()[0] )

                    explainableValues.append(commonParentDict)

        except Exception as e:
            print("exception")
            print(e)
            print("ontology A: " + str(valueA))
            print("ontology B: " + str(ontologyValueB))
            print("checking test")
            print("\n")
            
            """
            print("longestPrefixElemB: " + str(longestPrefixElemB))
            print("commonParent: " + str(commonParent))
            print("maxLayer: " + str(maxLayer))
            """

        if (len(ontologyValueListA) > 0 and len(ontologyValueListB) > 0):
            print("explanainable values")
            print("valueA: " + str(ontologyValueListA))
            print("valueB: " + str(ontologyValueListB))
            print("\n")
            print(explainableValues)
            print("\n")    
        
        return explainableValues
    
    
    
    
    
    
    