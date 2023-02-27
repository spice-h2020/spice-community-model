# Authors: José Ángel Sánchez Martín
import os
import json

import numpy as np

from cmSpice.algorithms.similarity.similarityDAO import SimilarityDAO

class EqualSimilarityDAO(SimilarityDAO):
    """
    Class to check if two attribute values are equal
    """
    
    def distanceItems(self, valueA, valueB):
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

#-------------------------------------------------------------------------------------------------------------------------------
#   To calculate dominant value
#-------------------------------------------------------------------------------------------------------------------------------
       
    def dominantValue(self, valueA, valueB):
        #return valueA
        if self.similarityColumn == 'id':
            return [{valueA: self.artworkA['id'].to_list()[0]}, {valueB: self.artworkB['id'].to_list()[0]}]
        else:
            return [valueA, valueB]
        
        
    
    
    