import pandas as pd
import numpy as np

import json
import math

import uuid
"""
86ca1aa0-34aa-4e8b-a509-50c905bae2a2
86ca1aa0-34aa-4e8b-a509-50c905bae2a2
"""

import re

import statistics



class CommunityJsonGenerator:

    def __init__(self, interactionObjectData, data, distanceMatrix, communityDict, community_detection, perspective, percentageExplainability = 0.5):
        self.io_df = interactionObjectData
        self.json_df = data.copy()
        self.distanceMatrix = distanceMatrix
        self.communityDict = communityDict
        self.community_detection = community_detection
        self.perspective = perspective
        self.percentageExplainability = percentageExplainability

        print("percentage explainability json generator: " + str(self.percentageExplainability))
        
        """
        print("community json generator")
        print("artworks dominant")
        print(self.json_df['dominantArtworksDominantInteractionGenerated'].tolist())
        print(self.json_df.columns)
        print("artworks dominant community")
        print(self.json_df['community_dominantArtworks'].tolist())
        """

        print("community json generator")
        #print(self.json_df['community_dominantArtworks'])
        print("\n")
        
        
        
        # Adapt self.json_df
        #print(self.json_df)
        # User information
        self.json_df['userid'] = self.json_df['userid']
        self.json_df['label'] = self.json_df['userid']
        self.json_df['group'] = communityDict['users'].values()
        self.json_df['explicit_community'] = self.json_df[communityDict['userAttributes']].to_dict(orient='records')
        if (len(communityDict['implicitAttributes']) > 0):
            self.json_df['implicit_community'] = self.json_df[communityDict['implicitAttributes']].to_dict(orient='records')
        else:
            self.json_df['implicit_community'] = [{} for _ in range(len(self.json_df))]


        if 'community_dominantArtworks' not in self.json_df.columns:
            self.json_df['community_dominantArtworks'] = [[] for _ in range(len(self.json_df))]
        
        
        # Extra to make it work with Marco Visualization
        #self.io_df['year'] = self.io_df['year'].astype(str)
        """
        self.io_df['Year'] = self.io_df['Year'].astype(str)
        
        self.io_df.rename(columns = {}, inplace = True)
        self.io_df.rename(columns = {'Title':'tittle'}, inplace = True)
        self.io_df.rename(columns = {'Author':'author'}, inplace = True)
        self.io_df.rename(columns = {'Year':'year'}, inplace = True)
        self.io_df.rename(columns = {'Link':'image'}, inplace = True)
        """
        
        
    
    def generateDict(self, element):
        # return {'IdArtefact': element[0], 'emotions': element[1]} 
        # return {'artwork_id': str(element[0]), 'feelings': "scettico", 'extracted_emotions': element[1]} 
        extractedEmotions = element[1]
        if (isinstance(extractedEmotions, list)):
            extractedEmotions = {extractedEmotions[i]: 100 / len(extractedEmotions) for i in range(0, len(extractedEmotions))}
        return {'artwork_id': str(element[0]), 'sourceid': element[2], 'feelings': element[3], 'extracted_emotions': extractedEmotions} 
        
        #return {
    
    def generateUserMaster(self):
        # Get IO_attributes
        IO_id = self.perspective['interaction_similarity_functions'][0]['sim_function']['interaction_object']['att_name']
        IO_similarityFeatures = [IO_id]
        for similarity_function in self.perspective['interaction_similarity_functions']:
            IO_similarityFeature = similarity_function['sim_function']['on_attribute']['att_name']
            IO_similarityFeatures.append(IO_similarityFeature)
            
        # https://stackoverflow.com/questions/34066053/from-list-of-dictionaries-to-np-array-of-arrays-and-vice-versa
        # https://stackoverflow.com/questions/8372399/zip-with-list-output-instead-of-tuple
        # Testing 2
        json_df2 = self.json_df[IO_similarityFeatures].head(2)
        IO_columnList = []
        for i in list(json_df2):
            IO_columnList.append(json_df2[i].tolist())
        user_interactions = [list(a) for a in zip(*IO_columnList)]
        
        """
        print("user_interactions: " + str(user_interactions))
        print("\n\n\n")
        """
        
        """
        for i in list(json_df2):
        
        list1 = json_df2['IdArtefact', 'sentiment'].tolist()
        print("List1: " + str(list1))
            
        """   
            
            
        # Testing
        json_df2 = self.json_df.head(2)
        print("testing")
        print(json_df2[IO_id])
        print(json_df2[IO_similarityFeatures])
        print("\n")
        print(json_df2[IO_similarityFeatures].values[0][0])
        print("\n\n\n")
        
        list1 = [[1,2],[3,4],[5,6]]
        result = list(zip(*list1))
        print("result: " + str(result))
        
        list1 = json_df2[IO_similarityFeatures].values
        list1 = [json_df2['IdArtefact'], json_df2['sentiment']]
        print("List1: " + str(list1))
        result = list(zip(*list1))
        print("result: " + str(result))
        
        json_df3 = json_df2.copy()
        json_df3['interactions'] = zip(*json_df2[IO_similarityFeatures])
        print("json_df3")
        print(json_df3['interactions'])
        print("\n\n\n")
            
        # Generate user_interactions
        user_interactions = self.json_df.apply(lambda row: type(row), axis = 1)
        print(user_interactions)
        
        #user_interactions = self.json_df.apply(lambda row: list(map(self.generateDict, list(zip(row[IO_id], row['emotions'])))), axis = 1)
        self.json_df['interactions'] = user_interactions
      
    
    def generateUserCommunityInteractions(self, row):
        # Get community dominant artworks
        dominantArtworks = row['community_dominantArtworks']
        
        """
        # Get IO_id
        IO_id = self.perspective['interaction_similarity_functions'][0]['sim_function']['interaction_object']['att_name']
        
        # Get similarity features
        IO_similarityFeatures = []
        for similarity_function in self.perspective['interaction_similarity_functions']:
            IO_similarityFeature = similarity_function['sim_function']['on_attribute']['att_name']
            IO_similarityFeatures.append(IO_similarityFeature)
        """
        
        # NEW ONE
        self.interactionAttribute = self.perspective['interaction_similarity_functions'][0]['sim_function']['on_attribute']['att_name']
        self.interactionAttributeOrigin = self.interactionAttribute + "_origin"
        self.interactionAttributeText = self.interactionAttribute.rsplit(".",1)[0] + ".text"
        # For DMH
        self.interactionAttributeSource = self.interactionAttribute + '_source'

        # Get trilogy associated to dominant artworks (artworkId, itMakesMeThinkAbout, itMakesMeThinkAbout.emotions)
        userCommunityInteractions = []
        print("row IO_id: " + str(row[self.interactionAttributeOrigin]))
        print("\n\n")
        for artworkId in dominantArtworks:
            artworkIndex = row[self.interactionAttributeOrigin].index(artworkId)
            
        
            # communityInteraction = self.generateDict([artworkId, row[self.interactionAttribute][artworkIndex], row[self.interactionAttributeText][artworkIndex]])
            communityInteraction = self.generateDict([artworkId, row[self.interactionAttribute][artworkIndex], row[self.interactionAttributeSource][artworkIndex], row[self.interactionAttributeText][artworkIndex]])
  
            userCommunityInteractions.append(communityInteraction)
            #{'artwork_id': str(element[0]), 'feelings': element[2], 'extracted_emotions': element[1]} 
        
        return userCommunityInteractions
        
    
    def generateUserCommunityInteractionsColumn(self):
        user_interactions = self.json_df.apply(lambda row: self.generateUserCommunityInteractions(row), axis = 1)
        return user_interactions

        
    def generateUserInteractionColumn(self, IO_id = ""):
        """
        OLD ONE
        # Get interaction columns
        if IO_id == "":
            IO_id = self.perspective['interaction_similarity_functions'][0]['sim_function']['interaction_object']['att_name']
        IO_similarityFeatures = []
        for similarity_function in self.perspective['interaction_similarity_functions']:
            IO_similarityFeature = similarity_function['sim_function']['on_attribute']['att_name']
            IO_similarityFeatures.append(IO_similarityFeature)
                                                           
        # Generate interaction info column
        IO_columns = []
        IO_columns.append(IO_id)
        IO_columns.extend(IO_similarityFeatures)
        print("IO_columns: " + str(IO_columns))
        """
        
        # NEW ONE
        self.interactionAttribute = self.perspective['interaction_similarity_functions'][0]['sim_function']['on_attribute']['att_name']
        self.interactionAttributeOrigin = self.interactionAttribute + "_origin"
        self.interactionAttributeText = self.interactionAttribute.rsplit(".",1)[0] + ".text"
        # For DMH
        self.interactionAttributeSource = self.interactionAttribute + '_source'


        #user_interactions = self.json_df.apply(lambda row: list(map(self.generateDict, list(zip(row[IO_id], row[IO_similarityFeatures[0]], row['itMakesMeThinkAbout'])))), axis = 1)
        user_interactions = self.json_df.apply(lambda row: list(map(self.generateDict, list(zip(row[self.interactionAttributeOrigin], row[self.interactionAttribute], row[self.interactionAttributeSource], row[self.interactionAttributeText])))), axis = 1)
        
        
        
        #user_interactions = self.json_df.apply(lambda row: list(map(self.generateDict, list(zip(row[IO_id], row['emotions'])))), axis = 1)
        
        return user_interactions
        
        
        
    def generateJSON(self,filename):
        # Export community information to JSON format
        self.communityJson = {}
        
        
        
        if (self.containsInteractions()):
            print("it contains interactions")
            # Generate interactions column used in self.userJSON()
            #self.generateUserInteractionColumnMaster()
            self.json_df['interactions'] = self.generateUserInteractionColumn()
            
            """
            print("checking dominantArtworks")
            print(self.json_df[['userName','community_dominantArtworks']])
            print("\n")
            """
            
            # Generate interactions with the artworks used for detecting the community (artworks similar to other members of the community)
            self.json_df['community_interactions'] = self.generateUserCommunityInteractionsColumn()
            
            # Remove from interactions the ones that are in community_interactions
            # https://stackoverflow.com/questions/35187165/python-how-to-subtract-2-dictionaries
            #self.json_df['no_community_interactions'] = self.json_df.apply(lambda row:  all(map( row['interactions'].pop, row['community_interactions'] ))    , axis = 1)
            self.json_df['no_community_interactions'] = self.json_df.apply(lambda row:  [ i for i in row['interactions'] if i not in row['community_interactions'] ]    , axis = 1)
        else:
            print("it doesnt contain interactions")
            self.json_df['interactions'] = [[] for _ in range(len(self.json_df))]
            self.json_df['community_interactions'] = [[] for _ in range(len(self.json_df))]
            self.json_df['no_community_interactions'] = [[] for _ in range(len(self.json_df))]

        # 
        
        # Generate each of the parts composing the JSON visualization file
        self.communityJSON()
        self.userJSON()
        self.similarityJSON()
        self.interactionObjectJSON()
        

        # Insert centroid
        self.insertCentroidVisualization(self.communityJson)
        
        return self.communityJson
        
    def communityJSON(self):
        self.skipPropertyValue = False
        
        
        # Community Data 
        self.communityJson['name'] = self.communityDict['perspective']['name']
        self.communityJson['perspectiveId'] = self.communityDict['perspective']['id']

        extraStr = " (" + str(self.percentageExplainability) + ")" + " " + self.perspective['algorithm']['name']
        extraStr = ""
        #extraStr = " (" + str(self.percentageExplainability) + ", " + str(self.perspective['algorithm']["weightArtworks"]) + ")" + " " + self.perspective['algorithm']['name']
        self.communityJson['name'] = self.communityDict['perspective']['name'] + extraStr
        self.communityJson['perspectiveId'] = self.communityDict['perspective']['id'] + extraStr



        #self.communityJson['numberOfCommunities'] = self.communityDict['number']
        self.communityJson['communities'] = []
        
        self.implicitExplanationJSON()
        
    def implicitExplanationJSON(self):
        # Users without community
        usersWithoutCommunity = []
        
        for c in range(self.communityDict['number']):
            community_data = self.community_detection.get_community(c, answer_binary=False, percentage=self.communityDict['percentage'])
            
            # Check if the community is a valid one (more than one member); otherwise the only member doesn't have a community
            if len(community_data['members']) > 1:
                # basic information
                communityDictionary = {}
                communityDictionary['id'] = self.communityDict['perspective']['id'] + "-" + str(len(self.communityJson['communities']))
                communityDictionary['perspectiveId'] = self.communityDict['perspective']['id']
                communityDictionary['community-type'] = 'implicit'
                communityDictionary['name'] = 'Community ' + str(len(self.communityJson['communities']))
            
                # Explanations
                communityDictionary['explanations'] = []
            
                # medoid
                medoidJson = {'medoid': self.communityDict['medoids'][c]}
                medoidJson = {'explanation_type': 'medoid', 'explanation_data': {'id': self.communityDict['medoids'][c]}, 'visible': True}
                communityDictionary['explanations'].append(medoidJson)

                


                # Implicit community explanation
                implicitPropertyExplanations = {}
                
                for key in community_data['explanation'].keys():
                    #print('\t\t-', k)
                    #communityProperties += '\t\t-' + ' ' + str(k) + ' ' + community_data['properties'][k] + '\n'
                    
                    communityPropertiesDict = {}

                    if (self.skipPropertyValue):
                        communityPropertiesList.append("'" + str(k) + "'")
                    else:

                        communityPropertiesDict = community_data['explanation'][key]['explanation']
                        
                        
                        
                        implicitPropertyExplanations[key] = dict()
                        implicitPropertyExplanations[key]['label'] = community_data['explanation'][key]['label']
                        implicitPropertyExplanations[key]['explanation'] = communityPropertiesDict
                        implicitPropertyExplanations[key]['explanation_type'] = community_data['explanation'][key]['explanation_type']
                
                # Implicit attribute (explanation)
                for implicitAttribute in implicitPropertyExplanations.keys():
                
                    explanationJson = {}
                    
                    explanationJson['explanation_type'] = implicitPropertyExplanations[implicitAttribute]['explanation_type']
                    explanationJson['explanation_key'] = implicitAttribute.replace("community_","")
                    explanationJson['explanation_data'] = {}
                    

                    explanationJson['explanation_data']['label'] = implicitPropertyExplanations[implicitAttribute]['label']
                    explanationJson['explanation_data']['data'] = implicitPropertyExplanations[implicitAttribute]['explanation']

                    if (explanationJson['explanation_type'] == 'implicit_attributes_list'):
                        explanationJson['explanation_data']['accordionMode'] = True
                        
                    if (implicitAttribute == 'community_' + 'id'):
                        explanationJson['visible'] = False
                    else:
                        explanationJson['visible'] = True

                    # Unavailable
                    if (isinstance(explanationJson['explanation_data']['data'], dict) and len(explanationJson['explanation_data']['data']) == 1):
                        keys = list(explanationJson['explanation_data']['data'].keys())
                        if (keys[0] == 'unknown'):
                            explanationJson['unavailable'] = True
                    
                    communityDictionary['explanations'].append(explanationJson)
                

                # Explicit attributes (explanation)
                explanationJson = {}
                explanationJson['explanation_type'] = 'explicit_attributes'
                explanationJson['explanation_data'] = {}
                explanationJson['visible'] = True
                
                communityDictionary['explanations'].append(explanationJson)

                # Get members
                communityDictionary['users'] = []
                communityDictionary['users'] = community_data['members']
                    
                # add it to communities
                self.communityJson['communities'].append(communityDictionary)

                
                # Update the group to which the users belong
                self.json_df.loc[ self.json_df['userid'].isin(community_data['members']), 'group'] = len(self.communityJson['communities']) - 1
                
                # Update the user's interacted artworks which have been considered to detect the community
                if (self.containsInteractions()):
                    aux_df = community_data['data'].copy().set_index('real_index')[['community_' + 'dominantArtworks']]
                    self.json_df.update(aux_df)
  
            else:
                usersWithoutCommunity.extend(community_data['members'])
        
        self.communityJson['numberOfCommunities'] = len(self.communityJson['communities'])
        
        # Add users without community
        if (len(usersWithoutCommunity) > 0):
            communityJson = {}
            communityJson['id'] = self.communityDict['perspective']['id'] + "-" + str(len(self.communityJson['communities'])) + ' (Users without community)'
            communityJson['perspectiveId'] = self.communityDict['perspective']['id']
            communityJson['community-type'] = 'inexistent'
            communityJson['name'] = 'Community ' + str(len(self.communityJson['communities'])) + ' (Users without community)'
            communityJson['explanations'] = []
            communityJson['users'] = usersWithoutCommunity
            
            # medoid (set first one for now since it is not a real community)
            # Hide medoid of users without community
            medoidJson = {'explanation_type': 'medoid', 'explanation_data': {'id': usersWithoutCommunity[0]}, 'visible': False}
            communityJson['explanations'].append(medoidJson)
            
            self.communityJson['communities'].append(communityJson)
        
        # Update the group value for the users not belonging to any community
        self.json_df.loc[ self.json_df['userid'].isin(usersWithoutCommunity), 'group'] = len(self.communityJson['communities']) - 1

   
    def userJSON(self):
        # User Data
        self.communityJson["users"] = []
        
        df = self.json_df.copy()
        df['id'] = df['userid']
        
        self.communityJson['users'] = df[['id','label','group','explicit_community', 'implicit_community', 'community_interactions', 'no_community_interactions']].to_dict('records')

    
    def similarityJSON(self):
        # Similarity Data
        self.communityJson['similarity'] = []    
        # users
        for i in range(len(self.distanceMatrix)):
            for j in range(i+1,len(self.distanceMatrix[i])):
                dicti = {}
                dicti['u1'] = str(self.json_df.iloc[i]['label'])
                dicti['u2'] = str(self.json_df.iloc[j]['label'])
                #dicti['value'] = similarityMatrix[i][j]
                dicti['value'] = round(1 - self.distanceMatrix[i][j],2)
                self.communityJson['similarity'].append(dicti)           
                    
    def interactionObjectJSON(self):
        if (self.containsInteractions()):
            # https://www.leocon.dev/blog/2021/09/how-to-flatten-a-python-list-array-and-which-one-should-you-use/
            # self.io_df2 = self.io_df.filter(regex = '^(?!.*timestamp).*$')
            # key = 'IdArtefact'
            #key = 'id'
            key = self.perspective['interaction_similarity_functions'][0]['sim_function']['interaction_object']['att_name']
            
            """
            print("interaction object json part")
            print("key: " + str(key))
            """
            
            # NEW ONE
            self.interactionAttribute = self.perspective['interaction_similarity_functions'][0]['sim_function']['on_attribute']['att_name']
            self.interactionAttributeOrigin = self.interactionAttribute + "_origin"
            self.interactionAttributeText = self.interactionAttribute.rsplit(".",1)[0] + ".text"
            # For DMH
            self.interactionAttributeSource = self.interactionAttribute + '_source'

            interactedIO = self.json_df[self.interactionAttributeOrigin].tolist()
            interactedIO = list(sum(interactedIO, []))
            interactedIO = list(map(str, interactedIO))
            
            # @id is for ints
            aux_df = self.io_df.copy()
            aux_df['id'] = self.io_df['id'].astype(str)
            
            io_df2 = aux_df[aux_df['id'].isin(interactedIO)]
            self.communityJson['artworks'] = io_df2.to_dict('records')
        else:
            self.communityJson['artworks'] = []

        
    def containsInteractions(self):
        return len(self.perspective['interaction_similarity_functions']) > 0
            

    #--------------------------------------------------------------------------------------------------------------------------
    #    Replace medoid with centroid
    #--------------------------------------------------------------------------------------------------------------------------

    def insertCentroidVisualization(self, visualization):
        """
        print("insert centroid visualization")
        print(visualization)
        print("\n")
        """
        
        medoids = []
        centroids = []

        for community in visualization['communities']:
            if ('(Users without community)' not in community['name']):
                community_explicitAttributes = {}

                centroid = 'centroid' + community['name'].replace("Community ","")
                centroids.append(centroid)

                # Replace medoid with centroid in explanation
                for explanation in community['explanations']:
                    if (explanation['explanation_type'] == 'medoid'):
                        medoid = explanation['explanation_data']['id']
                        medoids.append(medoid)
                        # Replace with centroid
                        explanation['explanation_data']['id'] = centroid
                        community['medoid'] = medoid
                        community['centroid'] = centroid

                # Add centroid to users
                community['users'].append(centroid)

                # Add centroid information to user data
                centroidData = {}
                for userData in visualization['users']:
                    if (userData['id'] in community['users']):
                        for explicitAttribute in userData['explicit_community']:
                            if (explicitAttribute not in community_explicitAttributes):
                                community_explicitAttributes[explicitAttribute] = []
                            community_explicitAttributes[explicitAttribute].append(userData['explicit_community'][explicitAttribute])

                        if (userData['id'] == medoid):
                            centroidData = userData.copy()

                centroidData['id'] = centroid
                centroidData['label'] = centroid
                centroidData['explicit_community'] = {}

                for explicitAttribute in community_explicitAttributes:

                    centroidData['explicit_community'][explicitAttribute] = statistics.mode(community_explicitAttributes[explicitAttribute])
                
                visualization['users'].append(centroidData)

                # Add centroid data to community so it can be easily and quickly accessed for the community similarity computation
                community['centroid'] = centroidData.copy()

                # Update similarity
                centroidSimilarity = []
                for similarity in visualization['similarity']:
                    if (similarity['u1'] == medoid):
                        similarity2 = similarity.copy()
                        similarity2['u1'] = centroid
                        centroidSimilarity.append(similarity2)
                    elif (similarity['u2'] == medoid):
                        similarity2 = similarity.copy()
                        similarity2['u2'] = centroid
                        centroidSimilarity.append(similarity2)

                centroidMedoidSimilarity = {'u1': centroid, 'u2': medoid, 'value': 1}
                centroidSimilarity.append(centroidMedoidSimilarity)

                visualization['similarity'].extend(centroidSimilarity)


        # Update similarity between centroids
        centroidSimilarity = []
        for i in range(len(centroids)):
            centroid = centroids[i]
            medoid = medoids[i]

            similarity2 = {}

            for similarity in visualization['similarity']:
                index = -1
                if (similarity['u1'] != medoid and similarity['u1'] in medoids):
                    if (similarity['u2'] == medoid):
                        index = medoids.index(similarity['u1'])
                        similarity2 = similarity.copy()
                        similarity2['u2'] = centroids[index]
                elif (similarity['u2'] != medoid and similarity['u2'] in medoids):
                    if (similarity['u1'] == medoid):
                        index = medoids.index(similarity['u2'])
                        similarity2 = similarity.copy()
                        similarity2['u2'] = centroids[index]

                if (index > i):
                    similarity2['u1'] = centroid
                    centroidSimilarity.append(similarity2)

        visualization['similarity'].extend(centroidSimilarity)
            
            