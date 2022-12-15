from context import dao
from dao.dao_csv import DAO_csv

import os
from inspect import getsourcefile
#from os.path import abspath, dirname

import numpy as np

from community_module.similarity.tableSimilarityDAO import TableSimilarityDAO

class HechtSentimentSimilarityDAO(TableSimilarityDAO):


    
    def getSimilarityTable(self):
        dao_csv = DAO_csv(os.path.dirname(os.path.abspath(getsourcefile(lambda:0))) + "/distanceTables/" + "sentiment" + ".csv")
        self.similarityTable = dao_csv.getPandasDataframe().set_index('Key')

    def distanceValues(self, emotionsA, emotionsB):
        """
        Method to obtain the distance between two combination of emotions
        
        Compute distance between the first emotion in each list
        
        Parameters
        ----------
        emotionsA : String
            Emotions separated by ;
        emotionsB : String
            Emotions separated by ;

        Returns
        -------
        double
            Distance between the two combination of emotions.
        """
        if (isinstance(emotionsA, str) == False or isinstance(emotionsB, str) == False):
            return 1.0
            
        emotionA = emotionsA.split(";")[0].lower()
        emotionB = emotionsB.split(";")[0].lower()
        
        return super().distanceValues(emotionA, emotionB)
        

            