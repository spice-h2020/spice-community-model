# Authors: José Ángel Sánchez Martín
from cmSpice.community_module.similarity.tableSimilarityDAO import TableSimilarityDAO

class ValuesSimilarity(TableSimilarityDAO):

    def __init__(self, dao, similarityFunction):
        """
        Similarity class for moral values specified by the MFT (Moral Foundations Theory)

        Parameters
        ----------
        dao : dao object class
            DAO which processes and provides the data required by the similarity measure.
        similarityFunction: json dict
            Encodes the similarity function parameters (column it is applied to, weight...)
        """
        super().__init__(dao, similarityFunction)

    def getSimilarityTableName(self):
        return "mftHaidt"

    def getMostSimilarValueInList(self, value, valueList):
        mostSimilarValue = ""
        distanceLowest = 1.0
        for valueB in valueList:
            distance = self.distanceTableKeys(value, valueB)
            if (distance < distanceLowest):
                distanceLowest = distance
                mostSimilarValue = valueB
        return mostSimilarValue, distanceLowest

    def distanceValues(self, elemA, elemB):
        """
        Method to obtain the distance between two lists of moral values. Only mft values are considered.

        Parameters
        ----------
        elemA : list
            Values list: includes mft and folk values.
            e.g.:
                "Values": [
                    "mft:Fairness",
                    "folk:Helping",
                    "folk:Impartial",
                    "folk:Understanding",
                    "mft:Care",
                    "folk:Novelty",
                    "bhv:Benevolence",
                    "folk:Intuitive"
                ], 
        elemB : list
            Values list: includes mft and folk values. 
        Returns
        -------
        double
            Distance between the two elements.
        """
        # Filter mft values
        mftListA = [(x.replace("mft:","").lower()) for x in elemA if x.startswith('mft:')]
        mftListB = [(x.replace("mft:","").lower()) for x in elemB if x.startswith('mft:')]

        # Calculate distance
        distanceTotal = 0

        for mftValue in mftListA:
            mftValueB, distance = self.getMostSimilarValueInList(mftValue, mftListB)
            distanceTotal += distance
        for mftValue in mftListB:
            mftValueB, distance = self.getMostSimilarValueInList(mftValue, mftListA)
            distanceTotal += distance
        
        distanceTotal = distanceTotal / max(1,(len(mftListA) + len(mftListB)))

        return distanceTotal