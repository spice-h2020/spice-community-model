# Authors: José Ángel Sánchez Martín
import os

from cmSpice.algorithms.similarity.similarityDAO import SimilarityDAO

"""
Extension of the Plutchik wheel of emotions to include the second level of emotions in addition to the basic ones
"""

PLUTCHIK_EMOTIONS = ['anger', 'anticipation', 'joy', 'trust', 'fear', 'surprise', 'sadness', 'disgust']
PLUTCHIK_EMOTIONS_SECOND_LEVEL = ['annoyance','interest', 'serenity','acceptance','apprehension','distraction','pensiveness','boredom']
PLUTCHIK_EMOTIONS_INTERMEDIATE_LEVEL = ['agressiveness', 'optimism', 'love', 'submission', 'awe', 'disapproval', 'remorse', 'contempt']


class ExtendedPlutchikEmotionSimilarityDAO(SimilarityDAO):
    
    def __init__(self, dao, similarityFunction):
        """Construct of TaxonomySimilarity objects.

        Parameters
        ----------
        data : pd.DataFrame
            Dataframe where index is ids of elements, columns a list of taxonomy member and
            values contain the number of times that a taxonomy member is in an element.
        """
        super().__init__(dao, similarityFunction)
        
        # Combine the 3 emotions list
        plutchikEmotions = []
        plutchikEmotions.extend(PLUTCHIK_EMOTIONS)
        plutchikEmotions.extend(PLUTCHIK_EMOTIONS_SECOND_LEVEL)
        plutchikEmotions.extend(PLUTCHIK_EMOTIONS_INTERMEDIATE_LEVEL)

        self.plutchikEmotions = plutchikEmotions
    
    def distanceItems(self, emotionA, emotionB):
        """
        Method to calculate the distance between 2 emotions based on PLUTCHKIN emotions.

        Parameters
        ----------
        emotionA : str
            First emotion.
        emotionB : str
            Second emotion.

        Returns
        -------
        double
            Distance value between emotions.
        """        
        try:
            emotionA = emotionA.lower()
            emotionB = emotionB.lower()

            if (emotionA not in self.plutchikEmotions or emotionB not in self.plutchikEmotions):
                return 1.0
            
            # Real index in the extended list of emotions
            realIndexA = self.plutchikEmotions.index(emotionA)
            realIndexB = self.plutchikEmotions.index(emotionB)
            
            # index in one of the list of emotions
            indexA = realIndexA % 8
            indexB = realIndexB % 8
            
            if indexB > indexA:
                indexA, indexB = indexB, indexA
            
            # Basic result (same list of emotions)
            result = min( (indexA - indexB) / 4, (indexB - indexA + 8) / 4)

            # Update it based on the difference of emotion list
            listA = realIndexA // 8
            listB = realIndexB // 8
            
            # First and second list of emotions
            # Decrease distance by 0.075 (it is less similar)
            if (listA + listB == 1):
                result -= 0.075
                
            # First or second AND third list of emotions (increase by 0.125 - half 0.25 between emotions
            # In the extreme values, increase/decrease by a little
            elif (listA != listB):
                """
                print("emotions are in the same spoke")
                print(emotionA)
                print(emotionB)
                print(result)
                """

                if (result == 1.0):
                    #print("change 1.0")
                    result -= 0.125
                    """
                    print(result)
                    print("\n")
                    """
                elif (result == 0.0):
                    #print("change 0.0")
                    result += 0.125
                elif ( (indexA - indexB) / 4 < (indexB - indexA + 8) / 4 ):
                    result -= 0.125
                else:
                    result += 0.125
            
            
            #print("result emotions (" + str(emotionA) + ", " + str(emotionB) + ") = " + str(result))
            
            # Correction: If lower than 0 or higher than 1, correct it
            result = min(result, 1.0)
            result = max(result, 0.0)

            """
            print("distanceItems emotion")
            print(emotionA)
            print(emotionB)
            print(result)
            print("\n")
            """
            
            return result
            
        # We don't have a Plutchick emotion for that user and artwork
        except ValueError:
            
            print("distanceItems emotion")
            print("Value error")
            print(emotionA)
            print(emotionB)
            print("fin value error")
            print("\n")
            """
            """
            
            #print("Wrong Plutchick emotion: " + "emotionA: " + str(emotionA) + " ; " + "emotionB: " + str(emotionB))
            
            return 1.0
    
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
        """
        emotionsDictA = dict([(x.replace("emotion:",""), y) for x, y in emotionsDictA.items() if x.startswith('emotion:')])
        emotionsDictB = dict([(x.replace("emotion:",""), y) for x, y in emotionsDictB.items() if x.startswith('emotion:')])
        """
        
        emotionsDictA = dict([(x.replace("emotion:",""), y) for x, y in emotionsDictA.items() ])
        emotionsDictB = dict([(x.replace("emotion:",""), y) for x, y in emotionsDictB.items() ])
        
        """
        print("emotionsDictA: " + str(emotionsDictA))
        print("emotionsDictB: " + str(emotionsDictB))
        print("\n\n")
        """
        
        
        if (len(emotionsDictA) <= 0 or len(emotionsDictB) <= 0):
            return 1.0
        else:
            # Get emotions with highest confidence value (dominant emotion)
            emotionA = max(emotionsDictA, key=emotionsDictA.get)
            emotionB = max(emotionsDictB, key=emotionsDictB.get)
            
            
            if (emotionsDictA[emotionA] == 0 or emotionsDictB[emotionB] == 0):
                return 1.0

            emotionA = emotionA.lower()
            emotionB = emotionB.lower()

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
        emotionsDictA = dict([(x.replace("emotion:",""), y) for x, y in emotionsDictA.items() ])
        emotionsDictB = dict([(x.replace("emotion:",""), y) for x, y in emotionsDictB.items() ])
        
        
        if (len(emotionsDictA) <= 0):
            emotionA = ""
        else:
            emotionA = max(emotionsDictA, key=emotionsDictA.get).lower()
            
        if (len(emotionsDictB) <= 0):
            emotionB = ""
        else:
            emotionB = max(emotionsDictB, key=emotionsDictB.get).lower()
        
        
        return emotionA, emotionB

    def dominantDistance(self, emotionsDictA, emotionsDictB):
        """
        Method to obtain the distance between the two dominant values encoding the interaction between A and B
        
        Used to explain dissimilar communities

        Parameters
        ----------
        emotionsDictA : dict
            Dict of Plutchik emotions (key: emotion; value: confidence level)
        emotionsDictB : dict
            Dict of Plutchik emotions (key: emotion; value: confidence level)

        Returns
        -------
        double
            Distance
        """
        dominantItemA, dominantItemB = self.dominantInteractionAttribute(emotionsDictA, emotionsDictB)
        return self.getDistanceBetweenItems(dominantItemA, dominantItemB)
    
    
    