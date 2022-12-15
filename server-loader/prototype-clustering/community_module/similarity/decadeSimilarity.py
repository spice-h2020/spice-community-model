# Authors: José Ángel Sánchez Martín

import numpy as np
import pandas as pd
# Import math library
import math

from community_module.similarity.similarityDAO import SimilarityDAO


HECHT_BELIEFS_E = ['Justify','Balanced','Oppose']


class DecadeSimilarity(SimilarityDAO):

    def distanceValues(self, elemA, elemB):
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
        decadeA = int(elemA / 10)
        decadeB = int(elemB / 10)
        
        return (abs(decadeA - decadeB)) / max(decadeA,decadeB)

