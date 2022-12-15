
from community_module.similarity.extendedPlutchikEmotionSimilarityDAO import ExtendedPlutchikEmotionSimilarityDAO

class HechtExtendedPlutchikEmotionSimilarityDAO(ExtendedPlutchikEmotionSimilarityDAO):


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
        
        return self.distanceEmotions(emotionA,emotionB)

            