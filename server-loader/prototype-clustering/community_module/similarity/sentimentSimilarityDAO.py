# Authors: José Ángel Sánchez Martín
import os
import json

import numpy as np

from community_module.similarity.tableSimilarityDAO import TableSimilarityDAO

class SentimentSimilarityDAO(TableSimilarityDAO):
    
    def distanceValues(self, sentimentsDictA, sentimentsDictB):
        """
        Method to obtain the distance between two valid values given by the similarity measure.

        Parameters
        ----------
        sentimentsDictA : dict
            Keys: String
                Positive, Negative, Neutral
            Values: double
                Confidence Level
        sentimentsDictB : dict
            Keys: String
                Positive, Negative, Neutral
            Values: double
                Confidence Level

        Returns
        -------
        double
            Distance between the two values.
        """
        if len(sentimentsDictA) <= 0 or len(sentimentsDictB) <= 0:
            return 1.0
        else:
            sentimentA = max(sentimentsDictA, key=sentimentsDictA.get).lower()
            sentimentB = max(sentimentsDictB, key=sentimentsDictB.get).lower()

            return super().distanceValues(sentimentA, sentimentB)
        
        
    def dominantValue(self, sentimentsDictA, sentimentsDictB):
        """
        Method to obtain the dominant sentiment for A and B
        Parameters
        ----------
        sentimentsDictA : dict
            Keys: String
                Positive, Negative, Neutral
            Values: double
                Confidence Level
        sentimentsDictB : dict
            Keys: String
                Positive, Negative, Neutral
            Values: double
                Confidence Level

        Returns
        -------
        String
            Dominant sentiment
        """
        if (len(sentimentsDictA) <= 0):
            sentimentA = ""
        else:
            sentimentA = max(sentimentsDictA, key=sentimentsDictA.get).lower()
            
        if (len(sentimentsDictB) <= 0):
            sentimentB = ""
        else:
            sentimentB = max(sentimentsDictB, key=sentimentsDictB.get).lower()
        
        return sentimentA, sentimentB
    
       
    