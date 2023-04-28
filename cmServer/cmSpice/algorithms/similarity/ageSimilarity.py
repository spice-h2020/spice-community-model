# Authors: José Ángel Sánchez Martín

import numpy as np
import pandas as pd
# Import math library
import math

from cmSpice.algorithms.similarity.similarityDAO import SimilarityDAO

class AgeSimilarity(SimilarityDAO):

    def distanceItems(self, itemA, itemB):
        """
        Method to obtain the distance between two ages.

        Parameters
        ----------
        itemA : int
            First age
        itemB : int
            Second age

        Returns
        -------
        double
            Distance between the two elements.
        """

        return (abs(elemA - elemB))

    def distanceValues(self, valueA, valueB):
        """
        Method to obtain the distance between two pandas cell valiues [row, similarityColumn]

        Defaults to getDistanceBetweenItems(self, itemA, itemB) if it is not overwritten by the 
        similarity measure child

        Parameters
        ----------
        valueA : object
            Value of first element corresponding to elemA in self.data
            e.g: GAM emotions: {"serenity": 1.0, "anger": 0.8}
        valueB : object
            Value of first element corresponding to elemB in self.data

        Returns
        -------
        double
            Distance between the two values.
        """
        return super().distanceValues(valueA, valueB)


