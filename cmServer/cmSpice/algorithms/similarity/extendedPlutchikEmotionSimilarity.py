# Authors: José Ángel Sánchez Martín
import os

from cmSpice.algorithms.similarity.extendedPlutchikEmotionSimilarityDAO import ExtendedPlutchikEmotionSimilarityDAO

"""
Extension of the Plutchik wheel of emotions to include the second level of emotions in addition to the basic ones
"""

"""
Use at least two emotions to perform the similarity
"""

PLUTCHIK_EMOTIONS = ['anger', 'anticipation', 'joy', 'trust', 'fear', 'surprise', 'sadness', 'disgust']
PLUTCHIK_EMOTIONS_SECOND_LEVEL = ['annoyance','interest', 'serenity','acceptance','apprehension','distraction','pensiveness','boredom']
PLUTCHIK_EMOTIONS_INTERMEDIATE_LEVEL = ['agressiveness', 'optimism', 'love', 'submission', 'awe', 'disapproval', 'remorse', 'contempt']


class ExtendedPlutchikEmotionSimilarity(ExtendedPlutchikEmotionSimilarityDAO):
    
    def distanceValues(self, emotionsDictA, emotionsDictB):
        """
        Method to obtain the distance between two combination of emotions
        
        a) Get common emotions.
        b) For the different emotions (diffA, diffB), compute distance between each element in diffA and the most similar emotion in diffB

        Parameters
        ----------
        emotionsDictA : dict
            Dict of Plutchik emotions (key: emotion; value: confidence level)
        emotionsDictB : dict
            Dict of Plutchik emotions (key: emotion; value: confidence level)

        Returns
        -------
        double
            Distance between the two combination of emotions.
        """
        emotionsDictA = dict([(x.replace("emotion:",""), y) for x, y in emotionsDictA.items() ])
        emotionsDictB = dict([(x.replace("emotion:",""), y) for x, y in emotionsDictB.items() ])
        
        if (len(emotionsDictA) <= 0 or len(emotionsDictB) <= 0):
            return 1.0
        else:

            # Sort emotions by value
            sorted_emotionsDictA = {k: v for k, v in sorted(emotionsDictA.items(), key=lambda item: item[1], reverse=True)}
            sorted_emotionsDictB = {k: v for k, v in sorted(emotionsDictB.items(), key=lambda item: item[1], reverse=True)}
        
            numValues = 2
            emotionsListA = list(dict(itertools.islice(sorted_emotionsDictA.items(),numValues)).keys())
            emotionsListB = list(dict(itertools.islice(sorted_emotionsDictB.items(),numValues)).keys())

            return self.distanceBetweenLists(emotionsListA, emotionsListB)

    def distanceListElements(self, elementA, elementB):
        """
        Distance between two MFT_values.
        Specialization of the inherited function for calculating distance between list members

        Parameters
        ----------
        elementA : String
            MFT_Value name (String)
        
        elementB : String
            MFT_Value name (String)

        Returns
        -------
        double
            Distance between the MFT_Values
        """
        
        # Fix value String
        mftValueA = elementA.lower().replace(" ", "")
        mftValueB = elementB.lower().replace(" ", "")

        print("distance between elements emotions")
        print("mftvalueA: " + str(mftValueA))
        print("mftvalueB: " + str(mftValueB))
        print("\n")

        return self.getDistanceBetweenItems(emotionA, emotionB)

    def dominantValue(self, emotionsDictA, emotionsDictB):
        """
        Method to obtain the dominant value in each combination of emotions
        
        Parameters
        ----------
        emotionsDictA : dict
            Dict of Plutchik emotions (key: emotion; value: confidence level)
        emotionsDictB : dict
            Dict of Plutchik emotions (key: emotion; value: confidence level)

        Returns
        -------
        String
            Dominant emotion for A and B
        """
        
        """
        emotionsDictA = dict([(x.replace("emotion:",""), y) for x, y in emotionsDictA.items() if x.startswith('emotion:')])
        emotionsDictB = dict([(x.replace("emotion:",""), y) for x, y in emotionsDictB.items() if x.startswith('emotion:')])
        """
        return self.lowestDistancePair[0], self.lowestDistancePair[1]
    
    
    