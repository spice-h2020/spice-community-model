# Authors: José Ángel Sánchez Martín
import numpy as np
import statistics

import pandas as pd



from cmSpice.dao.dao_api_iconclass import DAO_api_iconclass


class ExplainedCommunitiesDetection:
    """Class to search all communities that all members have a common
    propertie. This algorithm works with clustering techniques.
    """

    def __init__(self, algorithm, data, distanceMatrix, perspective = {}):
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
        
        if (len(self.perspective) == 0):
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
            if (self.explainInteractionAttributes() == False):
                self.explanaible_attributes = self.artwork_attributes
            else:
                self.explanaible_attributes = self.interaction_attributes

        

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
        if (maxCommunities <= 1):
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
            result = community_detection.calculate_communities(distanceMatrix = self.distanceMatrix, n_clusters=n_communities)
            
            # Asignamos a cada elemento su cluster/comunidad correspondiente (fix this later)
            ids_communities = {}
            for i in range(len(self.data.index)):
                ids_communities[self.data.index[i]] = result[i]
                
            result2 = result
            result = ids_communities
            self.resultAlgorithm = result2
            self.idsCommunities = result
            
            complete_data = self.data.copy()
            complete_data['community'] = result.values()
            self.complete_data = complete_data

            # Comprobamos que para cada grupo existe al menos una respuesta en común
            explainables = []
            self.communities = complete_data.groupby(by='community')
            
            #for c in range(n_communities):
            n_clusters = min(n_communities,len(set(result2)))
            
            # Cannot be explained with implicit
            if (n_clusters < n_communities):
                finish_search = True 
                n_communities = n_clusters
            else:
                for c in range(n_communities):
                    community = self.communities.get_group(c)
                    community = self.simplifyInteractionAttributes(community, printing = False)
                    explainables.append(self.is_explainable(community, answer_binary, percentage))

                finish_search = sum(explainables) == n_communities
            
            # Each datapoint belongs to a different cluster  
            if (n_communities == maxCommunities):
                finish_search = True
                
            if not finish_search:
                n_communities += 1
            """
            if finish_search:
                print("finish search")
                for c in range(n_communities):
                    community = self.communities.get_group(c)
                    print("community " + str(c))
                    print(community[['userNameAuxiliar','community']])
                    print("\n")
            """

        # Get medoids
        medoids_communities = self.getMedoidsCommunities(result2)

        """
        print("complete data")
        print(self.complete_data)
        print("\n")
        """
        
        communityDict = {}
        communityDict['number'] = n_communities
        communityDict['users'] = result
        communityDict['medoids'] = medoids_communities
        communityDict['percentage'] = percentage
        communityDict['userAttributes'] = self.user_attributes
        
        return communityDict
    
    def explainInteractionAttributes(self):
        return len(self.perspective['interaction_similarity_functions']) > 0
            
    def simplifyInteractionAttributes(self, community, printing = False):
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
        """
        print("simplify interaction attributes")
        print(community['community'].tolist())
        print("\n\n")
        """
        
        if (self.explainInteractionAttributes() == False):
            return community
        else:
                    
            df = community.copy()
            #for col in self.explanaible_attributes:
            # Include similarity features between artworks too
            for col in self.explanaible_attributes + self.artwork_attributes + ['dominantArtworks']:
                col2 = col + 'DominantInteractionGenerated'

                # Get row index of community members
                communityMemberIndexes = np.nonzero(np.in1d(self.data.index,community.index))[0]
                #communityMemberIndexes = np.nonzero(np.in1d(self.data.index,self.data.index))[0]
                
                """
                if (printing):
                    print("col2: " + str(col2))
                    print(df[col2])
                    print("self.data.index: " + str(self.data.index))
                    print("community.index: " + str(community.index))
                    print("community member indexes: " + str(communityMemberIndexes))
                    print("\n\n")
                
                """   



                #print("simplify attribute: " + str(col2))
                
                # From the attribute list, consider only the ones between the members of the community
                # https://stackoverflow.com/questions/23763591/python-selecting-elements-in-a-list-by-indices
                # Transform attribute list to fit community members
                df.loc[:, ('community_' + col)] = community.apply(lambda row: self.extractDominantInteractionAttribute(row, col2, communityMemberIndexes), axis = 1)
                # df.loc[:, ('community_' + col)] = community.apply(lambda row: statistics.mode([row[col2][i] for i in communityMemberIndexes if row[col2][i] != '']), axis = 1)
            


            if (1 == 2):
                print("dominantArtworks")
                print(df[['real_index','userNameAuxiliar', 'community_dominantArtworks']])
                print("\n")

            """
            if (printing):
                print('dominant artworks')
                print(df[['real_index', 'community_' + 'dominantArtworks']])
                print("\n")
            
            """
            
            return df
    
    def getMostFrequentElementsList(self, array, k):
        df=pd.DataFrame({'Number': array, 'Value': array})
        df['Count'] = df.groupby(['Number'])['Value'].transform('count')
        
        df1 = df.copy()
        df1 = df1.sort_values(by=['Count'], ascending=False)
        df1 = df1.drop_duplicates(['Number'])
        
        #return df1.head(k)['Number'].tolist()
        
        return df1.head(k)[['Number','Count']].to_dict('records')
    
    def extractDominantInteractionAttribute(self, row, col2, communityMemberIndexes):
        #communityMembers_interactionAttributeList = [row[col2][i] for i in communityMemberIndexes if row[col2][i] != '']
        # Skip itself
        communityMembers_interactionAttributeList = [row[col2][i] for i in communityMemberIndexes if row[col2][i] != '' and i != row['real_index']]
        
        #if (row['userNameAuxiliar'] == 'e4aM9WL7' and col2 == 'dominantArtworksDominantInteractionGenerated' and 1 == 2):
        if (row['userNameAuxiliar'] == 'x2AUnHqw' and col2 == 'dominantArtworksDominantInteractionGenerated' and 1 == 1):
         
        
            """
            print("username: " + row['userNameAuxiliar'])
            print("index: " + str(row['real_index']))
            print("community: " + str(row['community']))
            print("dominant artworks: " + str(row[col2]))
            print("communityMemberIndexes: " + str(communityMemberIndexes))
            print(communityMembers_interactionAttributeList)
            print("\n")

            
            """
                    
        if (len(communityMembers_interactionAttributeList) > 0):
            if col2 == 'dominantArtworksDominantInteractionGenerated':
                communityMembers_validInteractionAttributeList = [x for x in communityMembers_interactionAttributeList if len(x) > 0]
                if (len(communityMembers_validInteractionAttributeList) > 0):
                    np_array = np.asarray(communityMembers_validInteractionAttributeList, dtype=object)
                    array2 = list(np.hstack(np_array)) #if (len(np_array) > 0)
                else:
                    array2 = communityMembers_validInteractionAttributeList
                
                
                #if (row['userNameAuxiliar'] == 'e4aM9WL7' and 1 == 2):
                if (row['userNameAuxiliar'] == 'x2AUnHqw' and 1 == 2):
                    print("username: " + row['userNameAuxiliar'])
                    print("community: " + str(row['community']))
                    print("community member indexes: " + str(communityMemberIndexes))
                    print("dominantArtworks: " + str(communityMembers_interactionAttributeList))
                    print("community dominantArtworks: " + str(communityMembers_validInteractionAttributeList))
                    print("community dominantArtworks flatten: " + str(array2))
                    print("result: " + str(list(set(array2))))
                    print("\n")
                    
                    """
                    print("username: " + str(row['userNameAuxiliar']))
                    print("community: " + str(row['community']))
                    print("\n")
                    """
                    
                    """
                    print("dominantArtworks")
                    print("username: " + str(row['userNameAuxiliar']))
                    print("community: " + str(row['community']))
                    print(communityMembers_interactionAttributeList)
                    print("\n")
                    """
                    
                return list(set(array2))
            #elif (isinstance(communityMembers_interactionAttributeList[0],str)):
            elif (isinstance(communityMembers_interactionAttributeList[0],list) == False):
                return statistics.mode(communityMembers_interactionAttributeList)

            # Testing new iconclass attribute
            # Now, we get dictionaries with keys (iconclassIDs) and values (arrays indicating the [iconclassIDs artworkA, artworkB] they originate from)
            elif ('iconclassArrayIDs' in col2 or 'Materials' in col2):
                communityMembers_validInteractionAttributeList = [x for x in communityMembers_interactionAttributeList if len(x) > 0]

                if (len(communityMembers_validInteractionAttributeList) > 0):
                    """
                    print("new iconclass generation")
                    print(communityMembers_validInteractionAttributeList)
                    print("\n")
                    
                    """

                    # First, create a combined dictionary containing all the arrays of pairs each iconclassIDs originates from
                    iconclassDictionary = {}
                    for interactionAttribute in communityMembers_validInteractionAttributeList:
                        for interactionAttributeDict in interactionAttribute:
                            for interactionAttributeKey in interactionAttributeDict:
                                if (interactionAttributeKey not in iconclassDictionary):
                                    iconclassDictionary[interactionAttributeKey] = []
                                iconclassDictionary[interactionAttributeKey].append(interactionAttributeDict[interactionAttributeKey])

                    
                    print("new iconclass generation 2")
                    print(iconclassDictionary)
                    print("\n")
                    """
                    """

                    # Select x (5) keys with the highest number of results
                    # using sorted() + join() + lambda
                    # Sort dictionary by value list length
                    res = '#separator#'.join(sorted(iconclassDictionary, key = lambda key: len(iconclassDictionary[key])))

                    # From most frequent to less frequent
                    result = res.split('#separator#')
                    result.reverse()

                    print("result")
                    print(result)
                    print("\n")

                    # Get children associated to the keys 
                    result2 = []
                    result2 = {k:iconclassDictionary[k] for k in result[0:5:1] if k in iconclassDictionary}

                    # Next work: include the artworks these iconclass IDs originate from in the explanations


                    return result2

                else:
                    return {}


            # iconclass attribute (OLD) Not used anymore
            else:
                communityMembers_validInteractionAttributeList = [x for x in communityMembers_interactionAttributeList if len(x) > 0]
                #intersection = communityMembers_validInteractionAttributeList[0]
                result = []
                for interactionAttribute in communityMembers_validInteractionAttributeList:
                    #print("interactionAttribute: " + str(interactionAttribute))
                    # intersection = set(intersection).intersection(interactionAttribute)
                    # Union without repetition
                    #intersection = list(set(intersection) | set(lst2))
                    # Union with repetition
                    result.extend(interactionAttribute)

                # Return the 3 most frequent elements
                #print("result: " + str(result))
                result = self.getMostFrequentElementsList(result,5)
                result = [ x['Number'] for x in result ]
                
                #print(row.index)
                #print("row: " + str(row['userNameAuxiliar']) + " ; " + str(communityMembers_validInteractionAttributeList))
                
                # print
                """
                if (row['community'] == 6):
                    print("community 6")
                    print("communityMemberIndexes: " + str(communityMemberIndexes))
                    print("attribute list: " + str(communityMembers_interactionAttributeList))
                    print("index: " + str(row['real_index']))
                    print("userName: " + str(row['userNameAuxiliar']))
                    print("result: " + str(result))
                    print("\n")
                """
                
                """
                print("community: " + str(row['community']))
                print("col2: " + str(col2))
                print("index: " + str(row['real_index']))
                print("userName: " + str(row['userNameAuxiliar']))
                print("attribute list (not empty): " + str(communityMembers_interactionAttributeList))
                print("valid ones: " + str(communityMembers_validInteractionAttributeList))
                print("result: " + str(result))
                print("\n")
                """
                
                
                #artworks = [row['iconclassArrayIDsDominantInteractionGenerated'][i] for i in communityMemberIndexes if row['iconclassArrayIDsDominantInteractionGenerated'][i] != '' and i != row['real_index']]
                #print("dominant iconclassArrayIDs: " + str(row['iconclassArrayIDsDominantInteractionGenerated']))
                #print("dominant iconclassArrayIDs community: " + str(artworks))
                #print("\n")
                    
                    
                if (row['community'] == 6 and 1==2):
                    print("community 6")
                    print("col2: " + str(col2))
                    print("index: " + str(row['real_index']))
                    print("userName: " + str(row['userNameAuxiliar']))
                    artworks = [row['dominantArtworksDominantInteractionGenerated'][i] for i in communityMemberIndexes if row['dominantArtworksDominantInteractionGenerated'][i] != '' and i != row['real_index']]
                    print("dominantArtworks: " + str(row['dominantArtworksDominantInteractionGenerated']))
                    print("dominantArtworks community: " + str(artworks))
                    print("\n")
                
                return result

        else:
            return ''
        
    
        
    def is_explainable(self, community, answer_binary=False, percentage=1.0):
        explainable_community = False
        
        """
        print("is_explainable")
        print(community)
        print("\n")
        print("self.explanaible_attributes: " + str(self.explanaible_attributes))
        print("\n")
        """
        
        #for col in community.columns.values:
        for col2 in self.explanaible_attributes:
            if col2 != 'community':
                if (self.explainInteractionAttributes()):
                    col = "community_" + col2
                else:
                    col = col2
                    
                """    
                print("col: " + str(col))
                print(community[col])
                print("\n")
                """
                
                # https://www.alphacodingskills.com/python/notes/python-operator-bitwise-or-assignment.php
                # (x |= y) is equivalent to (x = x | y)
                if answer_binary:
                    explainable_community |= (len(community[col]) * percentage)  <= community[col].sum()
                else:
                    explainable_community |= (len(community[col]) * percentage) <= community[col].value_counts().max()
        
        return explainable_community
    
    
    
    
    def getMedoidsCommunities(self, clusteringResult):
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
            communities_members.setdefault(clusteringResult[i],[]).append(i)
        
        medoids_communities = {}
        for key in communities_members.keys():
            clusterIxgrid = np.ix_(communities_members[key],communities_members[key])
            clusterDistanceMatrix = self.distanceMatrix[clusterIxgrid]
            clusterRepresentativeIndex = np.argmin(np.sum(clusterDistanceMatrix, axis=1))
            clusterRepresentative = communities_members[key][clusterRepresentativeIndex]
            
            medoids_communities[key] = self.data.index[clusterRepresentative]

        return medoids_communities
    
    # Get the percentage of most frequent value for each feature.
    def secondExplanation(self,community):
        modePropertiesCommunity = {}

        for attribute in self.explanaible_attributes:
            counts = community[attribute].value_counts(normalize=True).mul(100)
            modeAttribute = community[attribute].value_counts().idxmax()
            modePropertiesCommunity[attribute] = {}
            modePropertiesCommunity[attribute]['representative'] = modeAttribute
            modePropertiesCommunity[attribute]['percentage'] = counts[modeAttribute]
    
        return modePropertiesCommunity
    
    
    
    def get_community(self, id_community, answer_binary=False, percentage=1.0):
        """Method to obtain all information about a community.

        Args:
            id_community (int): Id or name of community returned by detection method.
            answer_binary (bool, optional): True to indicate that a common property
            occurs only when all answers are 1.0. Defaults to False. Defaults to False.

        Returns:
            dict: All data that describes the community:
                - name: name of community.
                - members: list of index included in this community.
                - properties: common properties of community. It is a dictionary where:
                    each property is identified by column_name of data, and the value is
                    the common value in this column.
        """
        try:
        
            #print("get community: " + str(id_community))
            
            community = self.communities.get_group(id_community)
            community = self.simplifyInteractionAttributes(community, printing = False)

            community_user_attributes = community[self.user_attributes]

            community_data = {'name': id_community}
            community_data['percentage'] = str(percentage * 100) + " %"
            community_data['members'] = list(community_user_attributes.index.values)
            
            community_data['data'] = community
            
            """
            print("self.communities")
            print(community[['userNameAuxiliar','community']])
            print("\n")
            
            """

            explainedCommunityProperties = dict()       

            #for col in community.columns.values:
            #for col2 in self.explanaible_attributes:
            for col2 in self.explanaible_attributes + self.artwork_attributes:
                if col2 != 'community':
                    if (self.explainInteractionAttributes()):
                        col = "community_" + col2
                    else:
                        col = col2
                   # print(community)
                    #print(len(community[col]))
                    #print('-', col, community[col].value_counts().index[0])
                    if answer_binary:
                        if (len(community[col]) * percentage) <= community[col].sum():
                            explainedCommunityProperties[col] = community[col].value_counts().index[0]
                            
                            
                            
                            # print('-', col, community[col].value_counts().index[0])
                    else:
                    
                        array = community[col].tolist()                        
                        # For iconclass (list) types
                        #if (len(community[col] > 0 and isinstance(community[col][0],list))):
                        
                        """
                        print("\n")
                        print(community[col])
                        print(col)
                        print(type(community[col]))
                        print(type(community[col][0]))
                        print("\n")
                        
                        
                        """
                        """
                        if (col2 == "Colour"):
                            print("colour column array")
                            print("id_community: " + str(id_community))
                            print("check array")
                            print(array)
                            print("\n")
                        """
                        
                        # For iconclass
                        if (col == "community_" + "iconclassArrayIDs"):
                            print("improved explanation for iconclass")
                            print("\n")

                            print(array)
                            print("\n")

                            print("end new iconclass")
                            print("\n")

                            # Example array
                            # [{}, {'31D1': [['31D15', '31D12']]}]

                            # Combine all into one dictionary
                            iconclassDictionary = {}
                            for dictionary in array:
                                for dictionaryKey in dictionary:
                                    if (dictionaryKey not in iconclassDictionary):
                                        iconclassDictionary[dictionaryKey] = []
                                    iconclassDictionary[dictionaryKey].extend(dictionary[dictionaryKey])

                            # Sort dictionary
                            res = '#separator#'.join(sorted(iconclassDictionary, key = lambda key: len(iconclassDictionary[key])))
                            result = res.split('#separator#')
                            result.reverse()

                            # Get x more frequent keys
                            result2 = []
                            result2 = {k:iconclassDictionary[k] for k in result[0:5:1] if k in iconclassDictionary}

                            result3 = {}
                            for iconclassID in result2:
                                iconclassText = self.daoAPI_iconclass.getIconclassText(iconclassID)
                                # Get array of dicts {key: iconclassID, value: artwork it originates from}
                                np_array = np.asarray(result2[iconclassID], dtype=object)
                                iconclassChildren = list(np.hstack(np_array))

                                print("iconclass children")
                                print(iconclassChildren)
                                print("\n")

                                # Group iconclassChildren into a combined dictionary (values with the same key are added to an array)
                                iconclassChildrenCombinedDictionary = {}
                                for dictionary in iconclassChildren:
                                    for key, value in dictionary.items():
                                        if (key not in iconclassChildrenCombinedDictionary):
                                            iconclassChildrenCombinedDictionary[key] = []
                                        iconclassChildrenCombinedDictionary[key].extend(value)
                                        iconclassChildrenCombinedDictionary[key] = list(set(iconclassChildrenCombinedDictionary[key]))

                                print("iconclass children combined")
                                print(iconclassChildrenCombinedDictionary)
                                print("\n")
                                
                                iconclassExplanation = str(iconclassID) + " " + iconclassText 
                                if (iconclassID in iconclassChildrenCombinedDictionary):
                                    iconclassExplanation += " (" + ", ".join(iconclassChildrenCombinedDictionary[iconclassID]) + ")"
                                iconclassChildrenText = []
                                if (len(iconclassChildrenCombinedDictionary) > 1):
                                    print("iconclass combined dictionary")
                                    print(iconclassChildrenCombinedDictionary)
                                    print("\n")

                                    iconclassExplanation += ". Obtained from the artwork's iconclass IDs: "
                                    for iconclassChild in iconclassChildrenCombinedDictionary:
                                        iconclassChildText = self.daoAPI_iconclass.getIconclassText(iconclassChild)
                                        iconclassChildText += " (" + ", ".join(iconclassChildrenCombinedDictionary[iconclassChild]) + ")"
                                        iconclassChildrenText.append(str(iconclassChild) + " " + iconclassChildText)
                                    iconclassExplanation += "; ".join(iconclassChildrenText)
                                    iconclassExplanation += ""

                                result3[iconclassExplanation] = 0.0

                            print("result3: " + str(result3))
                            
                            
                            #explainedCommunityProperties[col] = "\n".join(result2)
                            
                            explainedCommunityProperties[col] = dict()
                            explainedCommunityProperties[col]["label"] = 'Community representative properties of the implicit attribute ' + "(" + str(col2) + ")" + ":"
                            explainedCommunityProperties[col]["explanation"] = result3

                        # For materials ontology
                        elif (col == "community_" + "Materials" and 1 == 1):
                            print("improved explanation for materials")
                            print("\n")

                            print(array)
                            print("\n")

                            print("end new materials")
                            print("\n")

                            # Example array
                            # [{}, {'31D1': [['31D15', '31D12']]}]

                            # Combine all into one dictionary
                            iconclassDictionary = {}
                            for dictionary in array:
                                for dictionaryKey in dictionary:
                                    if (dictionaryKey not in iconclassDictionary):
                                        iconclassDictionary[dictionaryKey] = []
                                    iconclassDictionary[dictionaryKey].extend(dictionary[dictionaryKey])

                            # Sort dictionary
                            res = '#separator#'.join(sorted(iconclassDictionary, key = lambda key: len(iconclassDictionary[key])))
                            result = res.split('#separator#')
                            result.reverse()

                            # Get x more frequent keys
                            result2 = []
                            result2 = {k:iconclassDictionary[k] for k in result[0:5:1] if k in iconclassDictionary}

                            result3 = {}
                            for iconclassID in result2:
                                iconclassText = ""
                                # Get array of dicts {key: iconclassID, value: artwork it originates from}
                                np_array = np.asarray(result2[iconclassID], dtype=object)
                                iconclassChildren = list(np.hstack(np_array))

                                print("iconclass children")
                                print(iconclassChildren)
                                print("\n")

                                # Group iconclassChildren into a combined dictionary (values with the same key are added to an array)
                                iconclassChildrenCombinedDictionary = {}
                                for dictionary in iconclassChildren:
                                    for key, value in dictionary.items():
                                        if (key not in iconclassChildrenCombinedDictionary):
                                            iconclassChildrenCombinedDictionary[key] = []
                                        iconclassChildrenCombinedDictionary[key].extend(value)
                                        iconclassChildrenCombinedDictionary[key] = list(set(iconclassChildrenCombinedDictionary[key]))

                                print("iconclass children combined")
                                print(iconclassChildrenCombinedDictionary)
                                print("\n")
                                
                                iconclassExplanation = str(iconclassID) + " " + iconclassText 
                                if (iconclassID in iconclassChildrenCombinedDictionary):
                                    iconclassExplanation += " (" + ", ".join(iconclassChildrenCombinedDictionary[iconclassID]) + ")"
                                iconclassChildrenText = []
                                if (len(iconclassChildrenCombinedDictionary) > 1):
                                    print("iconclass combined dictionary")
                                    print(iconclassChildrenCombinedDictionary)
                                    print("\n")

                                    iconclassExplanation += ". Obtained from the artwork's materials: "
                                    for iconclassChild in iconclassChildrenCombinedDictionary:
                                        iconclassChildText = ""
                                        iconclassChildText += " (" + ", ".join(iconclassChildrenCombinedDictionary[iconclassChild]) + ")"
                                        iconclassChildrenText.append(str(iconclassChild) + " " + iconclassChildText)
                                    iconclassExplanation += "; ".join(iconclassChildrenText)
                                    iconclassExplanation += ""

                                result3[iconclassExplanation] = 0.0

                            print("result3: " + str(result3))
                            
                            
                            #explainedCommunityProperties[col] = "\n".join(result2)
                            
                            explainedCommunityProperties[col] = dict()
                            explainedCommunityProperties[col]["label"] = 'Community representative properties of the implicit attribute ' + "(" + str(col2) + ")" + ":"
                            explainedCommunityProperties[col]["explanation"] = result3

                        # For list types (artworks and iconclass)
                        elif (len(array) > 0 and isinstance(array[0],list)):
                            
                            
                            """
                            print("\n")
                            print("iconclass list type")
                            print(community[col])
                            print(array)
                            print("\n\n\n")
                            
                            
                            
                            """
                            
                            np_array = np.asarray(array, dtype=object)
                            
                            """
                            print("shape")
                            print(np_array.shape)
                            print(np.hstack(np_array))
                            
                            """
                            #array2 = list(np_array.flat)
                            array2 = list(np.hstack(np_array))
                            
                            #print("array2: " + str(array2))
                            
                            result = self.getMostFrequentElementsList(array2,5)
                            result = [ x['Number'] for x in result ]
                            
                            result2 = {}
                            
                            """
                            print("result: " + str(result))
                            
                            
                            print("before entering iconclass extra functionality")
                            print(col)
                            print("\n")
                            
                            
                            """
                            
                            print("before entering iconclass extra functionality")
                            print(col)
                            print("\n")
                            
                            # Iconclass attribute
                            if (col == "community_" + "iconclassArrayIDs"):
                                for iconclassID in result:
                                    iconclassText = self.daoAPI_iconclass.getIconclassText(iconclassID)
                                    result2[str(iconclassID) + " " + iconclassText] = 0.0
                            # Other array attributes
                            else:
                                for element in result:
                                    result2[str(element)] = 0.0
                            
                            #result2.append(str(array) + " " + "0.0")
                                
                            print("result2: " + str(result2))
                            
                            
                            #explainedCommunityProperties[col] = "\n".join(result2)
                            
                            explainedCommunityProperties[col] = dict()
                            explainedCommunityProperties[col]["label"] = 'Community representative properties of the implicit attribute ' + "(" + str(col2) + ")" + ":"
                            explainedCommunityProperties[col]["explanation"] = result2
                            
                            
                            
                        
                        # For string types
                        elif (len(community[col]) * percentage) <= community[col].value_counts().max():
                            # Returns dominant one
                            # explainedCommunityProperties[col] = community[col].value_counts().index[0]
                            
                            # Returns the values for each of them
                            percentageColumn = community[col].value_counts(normalize=True) * 100
                            percentageColumnDict = percentageColumn.to_dict()
                            
                            explainedCommunityProperties[col] = dict()
                            explainedCommunityProperties[col]["label"] = 'Percentage distribution of the implicit attribute ' + "(" + str(col2) + ")" + ":"
                            explainedCommunityProperties[col]["explanation"] = percentageColumnDict

                            
                            
                            """
                            
                            if (col2 == "Colour"):
                                print("colour error")
                                print("id_community: " + str(id_community))
                                print(col)
                                print(col2)
                                print(percentageColumn)
                                print(percentageColumn.to_string())
                                print("end colour error")
                                print("\n\n")
                            """
                            
                            
            # Second explanation  
            #print(explainedCommunityProperties)    
            """
            community_data['explanation'] = []
            community_data['explanation'].append(explainedCommunityProperties)
            """
            
            community_data['explanation'] = explainedCommunityProperties
            
            
            #community_data['explanation'].append(self.secondExplanation(community))
            
        except Exception as e:
            
            print(str(e))
            print(self.communities)
            print("\n")
            # data with communities
            print(self.complete_data)
            print("\n\n")
            print("algorithm result")
            print(self.resultAlgorithm)
            print(self.idsCommunities)
            print("\n")
            raise Exception("Exception retrieving community " + str(id_community))

            
            return -1
            
    
            
        return community_data
    
    
    
        