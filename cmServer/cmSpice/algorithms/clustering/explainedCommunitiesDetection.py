# Authors: José Ángel Sánchez Martín
import numpy as np
import statistics

import pandas as pd

import json

from cmSpice.dao.dao_api_iconclass import DAO_api_iconclass
from cmSpice.algorithms.clustering.explainedCommunity import getCommunity
from cmSpice.algorithms.clustering.explainedCommunity import getMostFrequentElementsList
from cmSpice.algorithms.clustering.explainedCommunity import explainInteractionAttributes



class ExplainedCommunitiesDetection:
    """Class to search all communities that all members have a common
    propertie. This algorithm works with clustering techniques.
    """

    def __init__(self, algorithm, data, distanceMatrix, perspective={}):
        """Method to configure the detection algorithm.

        Args:
            data (DataFrame): Data used to apply the similarity measure between
            users.
            algorithm (Class): Class of clustering technique.
            sim (str/Class, optional): Similarity function used in clustering
            technique. Defaults to 'euclidean'.
        """
        # To get iconclass data
        self.daoAPI_iconclass = DAO_api_iconclass()

        # Initialization
        self.algorithm = algorithm
        self.data = data.copy()
        self.distanceMatrix = distanceMatrix
        self.perspective = perspective

        self.user_attributes = []
        self.interaction_attributes = []
        self.artwork_attributes = []

        if len(self.perspective) == 0:
            self.explanaible_attributes = self.data.columns

        else:

            # user's explicit attributes
            for userAttribute in self.perspective['user_attributes']:
                self.user_attributes.append(userAttribute['att_name'])

            # user's interaction features
            for similarityFunction in self.perspective['interaction_similarity_functions']:
                self.interaction_attributes.append(similarityFunction['sim_function']['on_attribute']['att_name'])

            # artwork's similarity features
            for similarityFunction in self.perspective['similarity_functions']:
                self.artwork_attributes.append(similarityFunction['sim_function']['on_attribute']['att_name'])

            # explainable attributes
            self.explanaible_attributes = []
            if explainInteractionAttributes(self.perspective) == False:
                self.explanaible_attributes = self.artwork_attributes
            else:
                self.explanaible_attributes = self.interaction_attributes

            # dissimilar attributes
            self.dissimilar_attributes = []
            self.dissimilar_atributes_dict = {}
            for similarityFunction in self.perspective['interaction_similarity_functions'] + self.perspective[
                'similarity_functions']:
                if ('dissimilar' in similarityFunction['sim_function'] and similarityFunction['sim_function'][
                    'dissimilar'] == True):
                    self.dissimilar_attributes.append(similarityFunction['sim_function']['on_attribute']['att_name'])
                    self.dissimilar_atributes_dict[
                        similarityFunction['sim_function']['on_attribute']['att_name']] = similarityFunction

    def search_all_communities(self, answer_binary=False, percentage=1.0):
        """Method to search all explainable communities.

        Args:
            answer_binary (bool, optional): True to indicate that a common property
            occurs only when all answers are 1.0. Defaults to False.
            percentage (float, optional): Value to determine the minimum percetage of
            commons answers to detect a community. Defaults to 1.0.

        Returns:
            int: Number of communities detected.
            dict: Dictionary where each user is assigned to a community.
        """
        maxCommunities = len(self.data)
        n_communities = min(2, maxCommunities)
        finish_search = False

        # Special case: not enough data (1 or less users)
        # This can happen if we filter by an artwork and only 1 or less users interacted with it.
        if maxCommunities <= 1:
            finish_search = True
            result2 = []
            result = {}
            for user in self.data.index:
                result[user] = 0
                result2.append(0)

            complete_data = self.data.copy()
            complete_data['community'] = result.values()
            self.complete_data = complete_data

            # Comprobamos que para cada grupo existe al menos una respuesta en común
            self.communities = complete_data.groupby(by='community')

        while not finish_search:
            community_detection = self.algorithm(self.data)
            result = community_detection.calculate_communities(distanceMatrix=self.distanceMatrix,
                                                               n_clusters=n_communities)

            # Asignamos a cada elemento su cluster/comunidad correspondiente (fix this later)
            ids_communities = {}
            for i in range(len(self.data.index)):
                ids_communities[self.data.index[i]] = result[i]

            result2 = result
            result = ids_communities
            self.resultAlgorithm = result2
            self.idsCommunities = result

            # Process community data (explanation)
            complete_data = self.data.copy()
            complete_data['community'] = result.values()
            self.complete_data = complete_data

            # Try to simplifyInteractionAttributes directly in complete_data
            complete_data = self.__simplifyInteractionAttributesCompleteData(complete_data, len(set(result2)),
                                                                             printing=False)

            """
            print("columns")
            print(complete_data.columns)
            print("\n")
            
            print("complete data simplify dominant")
            print(complete_data['community_' + 'dominantArtworks'])
            print("\n")
            """

            # Comprobamos que para cada grupo existe al menos una respuesta en común
            explainables = []
            self.communities = complete_data.groupby(by='community')

            # for c in range(n_communities):
            # n_clusters = min(n_communities,len(set(result2)))
            n_clusters = len(set(result2))
            n_communities_before = n_communities

            # Cannot be explained with implicit
            if n_clusters < n_communities:
                # Set n_communities = n_clusters (communities could not be explained)
                # finish_search = True
                # n_communities = n_clusters
                print()

            else:
                n_communities = n_clusters

                for c in range(n_communities):
                    community = self.communities.get_group(c)
                    # community = self.simplifyInteractionAttributes(community, printing = False)
                    explainables.append(self.__is_explainable(community, answer_binary, percentage))

                finish_search = sum(explainables) == n_communities

            # Each datapoint belongs to a different cluster  
            if n_communities == maxCommunities:
                finish_search = True

            if not finish_search:
                n_communities += 1

        # Set communities to be equal to clusters (if it is bigger, then at least one community cannot be explained)
        n_communities = n_clusters
        # Get medoids
        medoids_communities = self.__getMedoidsCommunities(result2)

        print("complete data communities")
        print(complete_data[['community']])
        print("\n")

        print("community unique")
        print(complete_data['community'].unique())
        print("\n")

        communityDict = {}
        communityDict['number'] = n_communities
        communityDict['users'] = result
        communityDict['medoids'] = medoids_communities
        communityDict['percentage'] = percentage
        communityDict['userAttributes'] = self.user_attributes

        return complete_data, communityDict



    def __simplifyInteractionAttributesCompleteData(self, completeData_df, n_communities, printing=False):
        self.communities = completeData_df.groupby(by='community')
        communities = []

        for c in range(n_communities):
            community = self.communities.get_group(c)
            community = self.__simplifyInteractionAttributes(community, printing=False)

            communities.append(community)

        df = pd.concat(communities)
        completeData_df = df.sort_values(by=['real_index'])

        return completeData_df

    def __simplifyInteractionAttributes(self, community, printing=False):
        """
        Method to obtain the dominant value in the list of interaction attribute values with the other community members.
        
        Parameters
        ----------
        community : pd.dataframe
            Community member information

        Returns
        -------
        community: pd.dataframe
            Updated dataframe including the dominant value for each user-interaction attribute pair in new columns.
            Column name = community_ + 'interaction attribute label'
        """
        if not explainInteractionAttributes(self.perspective):
            return community
        else:

            df = community.copy()
            # for col in self.explanaible_attributes:
            # Include similarity features between artworks too
            # for col in self.explanaible_attributes + self.artwork_attributes + ['dominantArtworks']:
            # Add distance between emotions for dissimilar emotions
            simplify_cols = self.explanaible_attributes + self.artwork_attributes + ['dominantArtworks']

            for attribute in self.dissimilar_attributes:
                simplify_cols.append(attribute + "Distance")

            print("simplify_cols")
            print(simplify_cols)
            print("\n")
            for col in simplify_cols:
                col2 = col + 'DominantInteractionGenerated'

                # Get row index of community members
                communityMemberIndexes = np.nonzero(np.in1d(self.data.index, community.index))[0]

                # communityMemberIndexes = np.nonzero(np.in1d(self.data.index,self.data.index))[0]

                """
                print("community")
                print(community)

                print("data index:")
                print(self.data.index)
                print("community index:")
                print(community.index)
                print("communityMemberIndexes: ")
                print(communityMemberIndexes)
                print("\n")
                """

                """
                if (printing):
                    print("col2: " + str(col2))
                    print(df[col2])
                    print("self.data.index: " + str(self.data.index))
                    print("community.index: " + str(community.index))
                    print("community member indexes: " + str(communityMemberIndexes))
                    print("\n\n")
                
                """

                # print("simplify attribute: " + str(col2))

                # From the attribute list, consider only the ones between the members of the community
                # https://stackoverflow.com/questions/23763591/python-selecting-elements-in-a-list-by-indices
                # Transform attribute list to fit community members
                df.loc[:, ('community_' + col)] = community.apply(
                    lambda row: self.__extractDominantInteractionAttribute(row, col2, communityMemberIndexes), axis=1)
                # df.loc[:, ('community_' + col)] = community.apply(lambda row: statistics.mode([row[col2][i] for i in communityMemberIndexes if row[col2][i] != '']), axis = 1)

            return df



    def __extractDominantInteractionAttribute(self, row, col2, communityMemberIndexes):
        # Skip itself
        communityMembers_interactionAttributeList = [row[col2][i] for i in communityMemberIndexes if
                                                     row[col2][i] != '' and i != row['real_index']]

        print("extract dominant interaction attribute")
        print("col2: " + str(col2))
        print("dominant artworks: " + str(row[col2]))
        print("\n")

        if len(communityMembers_interactionAttributeList) > 0:
            if col2 == 'dominantArtworksDominantInteractionGenerated':
                communityMembers_validInteractionAttributeList = [x for x in communityMembers_interactionAttributeList
                                                                  if len(x) > 0]
                if len(communityMembers_validInteractionAttributeList) > 0:
                    np_array = np.asarray(communityMembers_validInteractionAttributeList, dtype=object)
                    array2 = list(np.hstack(np_array))  # if (len(np_array) > 0)
                else:
                    array2 = communityMembers_validInteractionAttributeList

                # if (row['userNameAuxiliar'] == 'e4aM9WL7' and 1 == 2):
                if row['userNameAuxiliar'] == 'x2AUnHqw' and 1 == 2:
                    print("username: " + row['userNameAuxiliar'])
                    print("community: " + str(row['community']))
                    print("community member indexes: " + str(communityMemberIndexes))
                    print("dominantArtworks: " + str(communityMembers_interactionAttributeList))
                    print("community dominantArtworks: " + str(communityMembers_validInteractionAttributeList))
                    print("community dominantArtworks flatten: " + str(array2))
                    print("result: " + str(list(set(array2))))
                    print("\n")

                return list(set(array2))


            # Testing new iconclass attribute
            # Now, we get dictionaries with keys (iconclassIDs) and values (arrays indicating the [iconclassIDs artworkA, artworkB] they originate from)
            elif 'iconclassArrayIDs' in col2 or 'Materials' in col2:
                communityMembers_validInteractionAttributeList = [x for x in communityMembers_interactionAttributeList
                                                                  if len(x) > 0]

                if len(communityMembers_validInteractionAttributeList) > 0:
                    """
                    print("new iconclass generation")
                    print(communityMembers_validInteractionAttributeList)
                    print("\n")
                    
                    """

                    # print("simplify iconclassArrayIDs")

                    # First, create a combined dictionary containing all the arrays of pairs each iconclassIDs originates from
                    iconclassDictionary = {}
                    for interactionAttribute in communityMembers_validInteractionAttributeList:
                        for interactionAttributeDict in interactionAttribute:
                            for interactionAttributeKey in interactionAttributeDict:
                                if interactionAttributeKey not in iconclassDictionary:
                                    iconclassDictionary[interactionAttributeKey] = []
                                iconclassDictionary[interactionAttributeKey].append(
                                    interactionAttributeDict[interactionAttributeKey])
                    """
                    print("username: " + row['userNameAuxiliar'])
                    print("index: " + str(row['real_index']))
                    print("community: " + str(row['community']))
                    print("dominant artworks: " + str(row[col2]))
                    print("communityMemberIndexes: " + str(communityMemberIndexes))
                    print("communityMembers_interactionAttributeList")
                    print(communityMembers_interactionAttributeList)
                    print("\n")
                    """

                    """
                    print("new iconclass generation 2")
                    print(iconclassDictionary)
                    print("\n")
                    """

                    # Up to now, it also takes the number of times the artwork appears. 
                    # For example, a iconclassID (lovers) may only be linked to La Sirena, but La Sirena is interacted 
                    # with more times than any other artwork.

                    # Now, consider the number of different artworks linked to the iconclass ID

                    for iconclassID in iconclassDictionary:
                        # iconclassDictionary[iconclassID]= list(set(iconclassDictionary[iconclassID]))

                        set_of_jsons = {json.dumps(d, sort_keys=True) for d in iconclassDictionary[iconclassID]}
                        iconclassDictionary[iconclassID] = [json.loads(t) for t in set_of_jsons]

                        # iconclassDictionary[iconclassID] = [dict(t) for t in {tuple(d.items()) for d in iconclassDictionary[iconclassID]}]

                    # Select x (5) keys with the highest number of results
                    # using sorted() + join() + lambda
                    # Sort dictionary by value list length
                    sorted_iconclassDictionary = sorted(iconclassDictionary,
                                                        key=lambda key: len(iconclassDictionary[key]))

                    res = '#separator#'.join(sorted_iconclassDictionary)

                    # From most frequent to less frequent
                    result = res.split('#separator#')

                    result.reverse()

                    # Get children associated to the keys 
                    result2 = []
                    result2 = {k: iconclassDictionary[k] for k in result[0:5:1] if k in iconclassDictionary}

                    # Next work: include the artworks these iconclass IDs originate from in the explanations

                    return result2

                else:
                    return {}

            # Dominant attributes of the form 
            # dict: key (attribute); value (list of artwork(s) id(s) they reference)
            # Example: SAME ARTWORKS 
            # key: artwork id; value: [artwork id]
            elif isinstance(communityMembers_interactionAttributeList[0], dict):
                # return statistics.mode(communityMembers_interactionAttributeList)
                # Sort key by length of the array

                # Print
                """
                print("new dict explanation")
                print("username: " + row['userNameAuxiliar'])
                print("index: " + str(row['real_index']))
                print("community: " + str(row['community']))
                print("dominant artworks: " + str(row[col2]))
                print("communityMemberIndexes: " + str(communityMemberIndexes))
                print("communityMembers_interactionAttributeList")
                print(communityMembers_interactionAttributeList)
                print("\n")
                """

                # Flatten array of dicts into a dict
                # res = {k: v for d in ini_dict for k, v in d.items()}
                explanationDictionary = {}
                for dictionary in communityMembers_interactionAttributeList:
                    for key in dictionary:
                        if key not in explanationDictionary:
                            explanationDictionary[key] = []
                        explanationDictionary[key].append(dictionary[key])

                # Sort it by length of key
                # Select x (5) keys with the highest number of results
                # using sorted() + join() + lambda
                # Sort dictionary by value list length
                res = '#separator#'.join(sorted(explanationDictionary, key=lambda key: len(explanationDictionary[key])))

                # From most frequent to less frequent
                result = res.split('#separator#')
                result.reverse()

                """
                print("result")
                print(result)
                print("\n")
                """

                # Get children associated to the keys 
                result2 = []
                result2 = {k: explanationDictionary[k] for k in result[0:5:1] if k in explanationDictionary}

                """
                print("result2")
                print(result2)
                print("\n")
                """

                return result2

            elif not isinstance(communityMembers_interactionAttributeList[0], list):
                if 'Distance' in col2:
                    print("extract dominant distance dissimilar")
                    print(communityMembers_interactionAttributeList)
                    print("\n")
                    return communityMembers_interactionAttributeList
                else:
                    return statistics.mode(communityMembers_interactionAttributeList)

            # iconclass attribute (OLD) Not used anymore
            else:
                communityMembers_validInteractionAttributeList = [x for x in communityMembers_interactionAttributeList
                                                                  if len(x) > 0]
                # intersection = communityMembers_validInteractionAttributeList[0]
                result = []
                for interactionAttribute in communityMembers_validInteractionAttributeList:
                    # print("interactionAttribute: " + str(interactionAttribute))
                    # intersection = set(intersection).intersection(interactionAttribute)
                    # Union without repetition
                    # intersection = list(set(intersection) | set(lst2))
                    # Union with repetition
                    result.extend(interactionAttribute)

                # Return the 3 most frequent elements
                # print("result: " + str(result))
                result = getMostFrequentElementsList(result, 5)
                result = [x['Number'] for x in result]


                if row['community'] == 6 and 1 == 2:
                    print("community 6")
                    print("col2: " + str(col2))
                    print("index: " + str(row['real_index']))
                    print("userName: " + str(row['userNameAuxiliar']))
                    artworks = [row['dominantArtworksDominantInteractionGenerated'][i] for i in communityMemberIndexes
                                if
                                row['dominantArtworksDominantInteractionGenerated'][i] != '' and i != row['real_index']]
                    print("dominantArtworks: " + str(row['dominantArtworksDominantInteractionGenerated']))
                    print("dominantArtworks community: " + str(artworks))
                    print("\n")

                return result

        else:
            return ''

    def __is_explainable(self, community, answer_binary=False, percentage=1.0):
        explainable_community = False

        # for col in community.columns.values:
        for col2 in self.explanaible_attributes:
            if col2 != 'community':
                if explainInteractionAttributes(self.perspective):
                    col = "community_" + col2
                else:
                    col = col2

                print("is_explainable")
                print("col: " + str(col))
                print("community " + str(community['community'].to_list()[0]))
                print(community[col])
                print("dissimilar attributes")
                print(self.dissimilar_attributes)

                print("answer_binary", answer_binary)


                # https://www.alphacodingskills.com/python/notes/python-operator-bitwise-or-assignment.php
                # (x |= y) is equivalent to (x = x | y)
                explainableAttribute = False
                if answer_binary:
                    explainableAttribute = (len(community[col]) * percentage) <= community[col].sum()
                    print((len(community[col]) * percentage))
                    print(community[col].sum())
                else:
                    explainableAttribute = (len(community[col]) * percentage) <= community[col].value_counts().max()
                    print((len(community[col]) * percentage))
                    print(community[col].value_counts().max())

                print("\n")

                # Apply dissimilar
                # First approximation (most frequent value appears below the community similarity percentage)

                if col2 in self.dissimilar_attributes:

                    explainableAttribute = not explainableAttribute

                    print("apply dissimilar explanation")
                    print(explainableAttribute)
                    print("(len(community[col]) * percentage)")
                    print(str((len(community[col]) * percentage)))
                    print("community[col].value_counts().max()")
                    print(str(community[col].value_counts().max()))
                    print("\n")

                    # Second approximation
                    # Calculate the similarity average of the community members based on [col2] attribute. 
                    # If it is higher or equal to percentage, the community can be explained
                    print("checking distance")
                    print(list(community.columns))
                    print(community[[col + 'Distance']])
                    print("\n")

                    # Now filter distance column using the community 
                    # distanceList = community[col2 + 'DistanceDominantInteractionGenerated'].to_list()
                    distanceList = community[col + 'Distance'].to_list()
                    # Community only has one user (users without community)
                    if len(distanceList) <= 1:
                        explainableAttribute = True
                    else:

                        print("distanceList")
                        print(distanceList)
                        print(str(len(distanceList)))
                        print(str(len(distanceList[0])))
                        print(str(len(community)))
                        print("\n")

                        np_array = np.asarray(distanceList, dtype=object)
                        distanceList_flatten = list(np.hstack(np_array))  # if (len(np_array) > 0)
                        print("distanceList_flatten")
                        print(distanceList_flatten)
                        print(str(len(distanceList_flatten)))
                        print("\n")

                        distanceCommunity = sum(distanceList_flatten)
                        print("distance comunity")
                        print(str(distanceCommunity))
                        print("\n")

                        distanceCommunity = distanceCommunity / len(distanceList_flatten)
                        print("distance comunity final")
                        print(str(distanceCommunity))
                        print("\n")

                        self.distanceCommunity = distanceCommunity

                        if distanceCommunity <= percentage:
                            print("less percentage")
                            explainableAttribute = True
                        else:
                            explainableAttribute = False

                """
                # Second approximation (better, not yet implemented)
                # Maximize a distance function between the different values of the attribute.
                if (col2 in self.dissimilar_attributes):
                    # Perfect case example (emotions): community with only two opposite emotions (joy, sadness)
                    # Distance value: 1.0
                    # If there are equal number of joy and sadness, the distance is 0.5

                    # Pick an emotion, value (compute the dissimilarity between all of them)
                """

                explainable_community |= explainableAttribute

        return explainable_community

    def __getMedoidsCommunities(self, clusteringResult):
        """
        Calculates the community medoid (Representative member)
            
        Parameters
        ----------
            clusteringResult [array]
                Array with the communities each data.row belongs to

        Returns
        -------
            communitiesMedoids [<class 'dict'>]
                Dictionary with keys (community id) and values (pandas dataframe with the medoid row)
        """

        # Get cluster representative (medoid)
        # The one with the smallest distance to each other datapoint in the cluster
        communities_members = {}
        for i in range(len(clusteringResult)):
            communities_members.setdefault(clusteringResult[i], []).append(i)

        medoids_communities = {}
        for key in communities_members.keys():
            clusterIxgrid = np.ix_(communities_members[key], communities_members[key])
            clusterDistanceMatrix = self.distanceMatrix[clusterIxgrid]
            clusterRepresentativeIndex = np.argmin(np.sum(clusterDistanceMatrix, axis=1))
            clusterRepresentative = communities_members[key][clusterRepresentativeIndex]

            medoids_communities[key] = self.data.index[clusterRepresentative]

        return medoids_communities

    # Get the percentage of most frequent value for each feature.
    def __secondExplanation(self, community):
        modePropertiesCommunity = {}

        for attribute in self.explanaible_attributes:
            counts = community[attribute].value_counts(normalize=True).mul(100)
            modeAttribute = community[attribute].value_counts().idxmax()
            modePropertiesCommunity[attribute] = {}
            modePropertiesCommunity[attribute]['representative'] = modeAttribute
            modePropertiesCommunity[attribute]['percentage'] = counts[modeAttribute]

        return modePropertiesCommunity

    def get_community(self, id_community, answer_binary=False, percentage=1.0):
        return getCommunity(id_community, answer_binary, percentage, self.daoAPI_iconclass)

    # def __get_community_genericDict(self, id_community, array, col, col2, explainedCommunityProperties):
    #     print("improved explanation for dict type explanations")
    #     print("col: " + str(col))
    #     print("\n")
    #
    #     print(array)
    #     print("\n")
    #
    #     print("end new dict type explanations")
    #     print("\n")
    #
    #     # Example array
    #     # [{}, {'31D1': [['31D15', '31D12']]}] (iconclass)
    #     #
    #     # {'44174': ['44174']} (id)
    #
    #     # Combine all dictionaries inside the array into one dictionary
    #     iconclassDictionary = {}
    #     for dictionary in array:
    #         for dictionaryKey in dictionary:
    #             if dictionaryKey not in iconclassDictionary:
    #                 iconclassDictionary[dictionaryKey] = []
    #             iconclassDictionary[dictionaryKey].extend(dictionary[dictionaryKey])
    #
    #     if col != ("community_" + "id"):
    #         for key in iconclassDictionary:
    #             print("iconclassDictionary " + "(" + str(key) + ")")
    #             print(iconclassDictionary[key])
    #
    #             set_of_jsons = {json.dumps(d, sort_keys=True) for d in iconclassDictionary[key]}
    #             iconclassDictionary[key] = [json.loads(t) for t in set_of_jsons]
    #
    #             print(iconclassDictionary[key])
    #             print("\n")
    #             """
    #             """
    #
    #     # Sort dictionary
    #     result2 = self.__sortDictionary(iconclassDictionary)
    #
    #     result3 = {}
    #
    #     print("community: " + str(id_community))
    #     print("iconclassDictionary explanation")
    #     print(iconclassDictionary)
    #     print("\n")
    #     print("result2 explanation")
    #     print(result2)
    #     print("\n")
    #
    #     # Prepare explanation text for each of the selected keys
    #     for iconclassID in result2:
    #         print("checking iconclass id " + str(iconclassID))
    #         iconclassText = ""
    #         if col == "community_" + "iconclassArrayIDs":
    #             iconclassText = self.daoAPI_iconclass.getIconclassText(iconclassID)
    #
    #         # Get array of dicts {key: iconclassID, value: artwork it originates from}
    #         np_array = np.asarray(result2[iconclassID], dtype=object)
    #         iconclassChildren = list(np.hstack(np_array))
    #
    #         print("iconclass children")
    #         print(iconclassChildren)
    #         print("\n")
    #
    #         # basic explanation
    #         # iconclassExplanation = str(iconclassID) + " " + iconclassText
    #         iconclassExplanation = iconclassText + " " + "[" + str(iconclassID) + "]"
    #         artworksExplanation = []
    #
    #         # key includes children keys (dict value): iconclass, ontology
    #         if isinstance(iconclassChildren[0], dict):
    #
    #             # Group iconclassChildren into a combined dictionary (values with the same key are added to an array)
    #             iconclassChildrenCombinedDictionary = self.__groupIconclassChildrenCombinedDictionary(iconclassChildren)
    #
    #             if iconclassID in iconclassChildrenCombinedDictionary:
    #                 iconclassExplanation += " (" + ", ".join(
    #                     iconclassChildrenCombinedDictionary[iconclassID]) + ")"
    #                 artworksExplanation.extend(iconclassChildrenCombinedDictionary[iconclassID])
    #             iconclassChildrenText = []
    #             if len(iconclassChildrenCombinedDictionary) > 1:
    #                 print("iconclass combined dictionary")
    #                 print(iconclassChildrenCombinedDictionary)
    #                 print("\n")
    #
    #                 # iconclassExplanation += ". Obtained from the artwork's materials: "
    #                 iconclassExplanation += ". Obtained from the artwork's " + str(
    #                     col2).lower() + ": "
    #                 for iconclassChild in iconclassChildrenCombinedDictionary:
    #                     iconclassChildText = ""
    #                     # Iconclass: Get description of the iconclassID through the Iconclass API
    #                     if col == ("community_" + "iconclassArrayIDs"):
    #                         iconclassChildText = self.daoAPI_iconclass.getIconclassText(
    #                             iconclassChild)
    #                     iconclassChildText += " (" + ", ".join(
    #                         iconclassChildrenCombinedDictionary[iconclassChild]) + ")"
    #                     artworksExplanation.extend(
    #                         iconclassChildrenCombinedDictionary[iconclassChild])
    #                     # iconclassChildrenText.append(str(iconclassChild) + " " + iconclassChildText)
    #                     iconclassChildrenText.append(
    #                         iconclassChildText + " " + "[" + str(iconclassChild) + "]")
    #                 iconclassExplanation += "; ".join(iconclassChildrenText)
    #                 iconclassExplanation += ""
    #
    #         # key references a basic array value: artwork id
    #         else:
    #
    #             iconclassChildren = list(set(iconclassChildren))
    #             iconclassChildrenCombinedDictionary = {iconclassChildren[0]: iconclassChildren}
    #             artworksExplanation.extend(iconclassChildrenCombinedDictionary[iconclassID])
    #             # iconclassChildren = {}
    #
    #         print("iconclass children combined")
    #         print(iconclassChildrenCombinedDictionary)
    #         print("\n")
    #
    #         # result3[iconclassExplanation] = 0.0
    #         result3[iconclassExplanation] = list(set(artworksExplanation))
    #
    #     return self.__setExplainedCommunityProperties(explainedCommunityProperties, result3, col, col2)
    #
    # def __get_community_iconClass(self, array, col, col2, explainedCommunityProperties):
    #     print("improved explanation for iconclass")
    #     print("\n")
    #
    #     print(array)
    #     print("\n")
    #
    #     print("end new iconclass")
    #     print("\n")
    #
    #     # Example array
    #     # [{}, {'31D1': [['31D15', '31D12']]}]
    #
    #     # Combine all into one dictionary
    #     iconclassDictionary = self.__combineIconclassDictionary(array)
    #
    #     # Sort dictionary
    #     result2 = self.__sortDictionary(iconclassDictionary)
    #
    #     result3 = {}
    #     for iconclassID in result2:
    #         iconclassText = self.daoAPI_iconclass.getIconclassText(iconclassID)
    #         # Get array of dicts {key: iconclassID, value: artwork it originates from}
    #         iconclassExplanation, iconclassChildrenCombinedDictionary = self.__getArrayOfDicts(result2, iconclassID,
    #                                                                                            iconclassText)
    #
    #         iconclassChildrenText = []
    #
    #         if len(iconclassChildrenCombinedDictionary) > 1:
    #             print("iconclass combined dictionary")
    #             print(iconclassChildrenCombinedDictionary)
    #             print("\n")
    #
    #             iconclassExplanation += ". Obtained from the artwork's iconclass IDs: "
    #             for iconclassChild in iconclassChildrenCombinedDictionary:
    #                 iconclassChildText = self.daoAPI_iconclass.getIconclassText(iconclassChild)
    #                 iconclassChildText += " (" + ", ".join(
    #                     iconclassChildrenCombinedDictionary[iconclassChild]) + ")"
    #                 iconclassChildrenText.append(str(iconclassChild) + " " + iconclassChildText)
    #             iconclassExplanation += "; ".join(iconclassChildrenText)
    #             iconclassExplanation += ""
    #
    #         result3[iconclassExplanation] = 0.0
    #
    #     return self.__setExplainedCommunityProperties(explainedCommunityProperties, result3, col, col2)
    #
    # def __get_community_materialOntology(self, array, col, col2, explainedCommunityProperties):
    #     print("improved explanation for materials")
    #     print("\n")
    #
    #     print(array)
    #     print("\n")
    #
    #     print("end new materials")
    #     print("\n")
    #
    #     # Example array
    #     # [{}, {'31D1': [['31D15', '31D12']]}]
    #
    #     # Combine all into one dictionary
    #     iconclassDictionary = self.__combineIconclassDictionary(array)
    #
    #     # Sort dictionary
    #     result2 = self.__sortDictionary(iconclassDictionary)
    #
    #     result3 = {}
    #     for iconclassID in result2:
    #         iconclassText = ""
    #         # Get array of dicts {key: iconclassID, value: artwork it originates from}
    #         iconclassExplanation, iconclassChildrenCombinedDictionary = self.__getArrayOfDicts(result2, iconclassID,
    #                                                                                            iconclassText)
    #
    #         iconclassChildrenText = []
    #         if len(iconclassChildrenCombinedDictionary) > 1:
    #             print("iconclass combined dictionary")
    #             print(iconclassChildrenCombinedDictionary)
    #             print("\n")
    #
    #             iconclassExplanation = self.__setIconclassExplanation(iconclassExplanation,
    #                                                                   iconclassChildrenCombinedDictionary,
    #                                                                   iconclassChildrenText)
    #
    #         result3[iconclassExplanation] = 0.0
    #
    #     return self.__setExplainedCommunityProperties(explainedCommunityProperties, result3, col, col2)
    #
    # def __get_community_id(self, array, col, col2, explainedCommunityProperties):
    #
    #     # Example array
    #     # [{}, {'31D1': [['31D15', '31D12']]}]
    #
    #     # Combine all into one dictionary
    #     iconclassDictionary = {}
    #     for dictionary in array:
    #         for dictionaryKey in dictionary:
    #             if dictionaryKey not in iconclassDictionary:
    #                 iconclassDictionary[dictionaryKey] = []
    #             iconclassDictionary[dictionaryKey].extend(dictionary[dictionaryKey])
    #
    #     # Sort dictionary
    #     result2 = self.__sortDictionary(iconclassDictionary)
    #
    #     result3 = {}
    #     for iconclassID in result2:
    #         iconclassText = ""
    #         # Get array of dicts {key: iconclassID, value: artwork it originates from}
    #         np_array = np.asarray(result2[iconclassID], dtype=object)
    #         iconclassChildren = list(np.hstack(np_array))
    #
    #         iconclassExplanation = str(iconclassID) + " " + iconclassText
    #
    #         if isinstance(iconclassChildren[0], dict):
    #             # Group iconclassChildren into a combined dictionary (values with the same key are added to an array)
    #             iconclassChildrenCombinedDictionary = self.__groupIconclassChildrenCombinedDictionary(iconclassChildren)
    #
    #             if iconclassID in iconclassChildrenCombinedDictionary:
    #                 iconclassExplanation += " (" + ", ".join(
    #                     iconclassChildrenCombinedDictionary[iconclassID]) + ")"
    #                 iconclassChildrenText = []
    #                 if len(iconclassChildrenCombinedDictionary) > 1:
    #                     iconclassExplanation = self.__setIconclassExplanation(iconclassExplanation,
    #                                                                           iconclassChildrenCombinedDictionary,
    #                                                                           iconclassChildrenText)
    #
    #         else:
    #             iconclassChildren = list(set(iconclassChildren))
    #             iconclassChildrenCombinedDictionary = {iconclassChildren[0]: iconclassChildren}
    #
    #             # iconclassChildren = {}
    #
    #         # result3[iconclassExplanation] = 0.0
    #         result3[iconclassExplanation] = iconclassChildrenCombinedDictionary[iconclassID]
    #
    #     return self.__setExplainedCommunityProperties(explainedCommunityProperties, result3, col, col2)
    #
    # def __get_community_listTypes(self, array, col, col2, explainedCommunityProperties):
    #
    #     np_array = np.asarray(array, dtype=object)
    #
    #     # array2 = list(np_array.flat)
    #     array2 = list(np.hstack(np_array))
    #
    #     # print("array2: " + str(array2))
    #
    #     result = getMostFrequentElementsList(array2, 5)
    #     result = [x['Number'] for x in result]
    #
    #     result2 = {}
    #
    #     print("before entering iconclass extra functionality")
    #     print(col)
    #     print("\n")
    #
    #     # Iconclass attribute
    #     if col == "community_" + "iconclassArrayIDs":
    #         for iconclassID in result:
    #             iconclassText = self.daoAPI_iconclass.getIconclassText(iconclassID)
    #             result2[str(iconclassID) + " " + iconclassText] = 0.0
    #     # Other array attributes
    #     else:
    #         for element in result:
    #             result2[str(element)] = 0.0
    #
    #     # result2.append(str(array) + " " + "0.0")
    #
    #     print("result2: " + str(result2))
    #
    #     # explainedCommunityProperties[col] = "\n".join(result2)
    #
    #     explainedCommunityProperties[col] = dict()
    #     explainedCommunityProperties[col][
    #         "label"] = 'Community representative properties of the implicit attribute ' + "(" + str(
    #         col2) + ")" + ":"
    #     explainedCommunityProperties[col]["explanation"] = result2
    #
    #     return explainedCommunityProperties
    #
    # def __get_community_stringTypes(self, col, col2, explainedCommunityProperties, community):
    #
    #     print("is explainable get community")
    #
    #     # explainableAttribute = self.__is_explainable(community, answer_binary, percentage)
    #
    #     # Returns dominant one
    #     # explainedCommunityProperties[col] = community[col].value_counts().index[0]
    #
    #     # Remove empty string
    #     df = community.copy()
    #     df2 = df.loc[df[col].str.len() != 0]
    #     percentageColumn = df2[col].value_counts(normalize=True) * 100
    #     percentageColumnDict = percentageColumn.to_dict()
    #
    #     # Returns the values for each of them
    #     """
    #     percentageColumn = community[col].value_counts(normalize=True) * 100
    #     percentageColumnDict = percentageColumn.to_dict()
    #     """
    #
    #     explainedCommunityProperties[col] = dict()
    #     explainedCommunityProperties[col][
    #         "label"] = 'Percentage distribution of the implicit attribute ' + "(" + str(
    #         col2) + ")" + ":"
    #     # if (not explainableAttribute):
    #     # explainedCommunityProperties[col]["label"] += "(This community doesn't meet the dissimilar requirements) :"
    #     # explainedCommunityProperties[col]["label"] += "distanceCommunity: " + str(self.distanceCommunity)
    #     explainedCommunityProperties[col]["explanation"] = percentageColumnDict
    #
    #     return explainedCommunityProperties
    #
    # def __getArrayOfDicts(self, result2, iconclassID, iconclassText):
    #     np_array = np.asarray(result2[iconclassID], dtype=object)
    #     iconclassChildren = list(np.hstack(np_array))
    #
    #     print("iconclass children")
    #     print(iconclassChildren)
    #     print("\n")
    #
    #     # Group iconclassChildren into a combined dictionary (values with the same key are added to an array)
    #     iconclassChildrenCombinedDictionary = self.__groupIconclassChildrenCombinedDictionary(iconclassChildren)
    #
    #     print("iconclass children combined")
    #     print(iconclassChildrenCombinedDictionary)
    #     print("\n")
    #
    #     iconclassExplanation = str(iconclassID) + " " + iconclassText
    #     if iconclassID in iconclassChildrenCombinedDictionary:
    #         iconclassExplanation += " (" + ", ".join(
    #             iconclassChildrenCombinedDictionary[iconclassID]) + ")"
    #
    #     return iconclassExplanation, iconclassChildrenCombinedDictionary
    #
    # def __setExplainedCommunityProperties(self, explainedCommunityProperties, result3, col, col2):
    #     print("result3: " + str(result3))
    #
    #     # explainedCommunityProperties[col] = "\n".join(result2)
    #
    #     explainedCommunityProperties[col] = dict()
    #     explainedCommunityProperties[col][
    #         "label"] = 'Community representative properties of the implicit attribute ' + "(" + str(
    #         col2) + ")" + ":"
    #     explainedCommunityProperties[col]["explanation"] = result3
    #
    #     return explainedCommunityProperties
    #
    # def __setIconclassExplanation(self, iconclassExplanation, iconclassChildrenCombinedDictionary,
    #                               iconclassChildrenText):
    #     iconclassExplanation += ". Obtained from the artwork's materials: "
    #     for iconclassChild in iconclassChildrenCombinedDictionary:
    #         iconclassChildText = ""
    #         iconclassChildText += " (" + ", ".join(
    #             iconclassChildrenCombinedDictionary[iconclassChild]) + ")"
    #         iconclassChildrenText.append(str(iconclassChild) + " " + iconclassChildText)
    #     iconclassExplanation += "; ".join(iconclassChildrenText)
    #     iconclassExplanation += ""
    #     return iconclassExplanation
    #
    # def __sortDictionary(self, iconclassDictionary):
    #     # Sort dictionary
    #     res = '#separator#'.join(
    #         sorted(iconclassDictionary, key=lambda key: len(iconclassDictionary[key])))
    #     result = res.split('#separator#')
    #     result.reverse()
    #
    #     # Get x more frequent keys
    #     result2 = []
    #     result2 = {k: iconclassDictionary[k] for k in result[0:5:1] if k in iconclassDictionary}
    #
    #     return result2
    #
    # def __groupIconclassChildrenCombinedDictionary(self, iconclassChildren):
    #     iconclassChildrenCombinedDictionary = {}
    #     for dictionary in iconclassChildren:
    #         for key, value in dictionary.items():
    #             if key not in iconclassChildrenCombinedDictionary:
    #                 iconclassChildrenCombinedDictionary[key] = []
    #             iconclassChildrenCombinedDictionary[key].extend(value)
    #             iconclassChildrenCombinedDictionary[key] = list(
    #                 set(iconclassChildrenCombinedDictionary[key]))
    #     return iconclassChildrenCombinedDictionary
    #
    # def __combineIconclassDictionary(self, array):
    #     iconclassDictionary = {}
    #     for dictionary in array:
    #         for dictionaryKey in dictionary:
    #             if dictionaryKey not in iconclassDictionary:
    #                 iconclassDictionary[dictionaryKey] = []
    #             iconclassDictionary[dictionaryKey].extend(dictionary[dictionaryKey])
    #     return iconclassDictionary
