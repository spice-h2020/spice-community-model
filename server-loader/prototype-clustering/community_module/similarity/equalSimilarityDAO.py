# Authors: José Ángel Sánchez Martín
import os
import json

import numpy as np

from community_module.similarity.similarityDAO import SimilarityDAO

class EqualSimilarityDAO(SimilarityDAO):
    """
    Class to check if two attribute values are equal
    """
    
    def distanceValues(self, valueA, valueB):
        """
        Method to obtain the distance between two valid values given by the similarity measure.

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
        if (valueA != valueB):
            return 1.0
        else:
            return 0.0
        
        
    
    
    