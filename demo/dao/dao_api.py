import json
import requests
from requests.auth import HTTPBasicAuth

from context import dao
from dao.dao_class import DAO

class DAO_api(DAO):
    """
    DAO used only for performing requests to Spice API (Local)
    """
    def __init__(self, route=""):
        super().__init__(route)
        
        #--------------------------------------------------------------------------------------------------------------------------
        #    Change server
        #--------------------------------------------------------------------------------------------------------------------------
        
        self.server = "http://localhost:8080"
            

    def getData(self):
        raise ValueError('Incorrect operation. Please use a specific method for the API request')

    def addPerspective(self, ugc):
        str1 = "{}/v1.1/perspective".format(self.server)
        print("str1: " + str(str1))
        print("ugc: " + str(ugc))
        response = requests.post("{}/v1.1/perspective".format(self.server), json=ugc)
        return response

    def responseProcessing(self, response):
        """Process response from API"""
        if response.status_code == 400:
            return
        self.data = response.json()

    """__API for users__"""

    def userCommunities(self, userId):
        response = requests.get("{}/v1.1/users/{}/communities".format(self.server,userId))
        self.responseProcessing(response)
        return self.data, response

    def updateUser(self, userId, ugc):
        response = requests.post("{}/v1.1/users/{}/update-generated-content".format(self.server,userId),
                                 json=ugc)
        return response

    """__API for communities__"""

    def communityList(self):
        response = requests.get("{}/v1.1/communities".format(self.server))
        self.responseProcessing(response)
        return self.data, response

    def communityDescription(self, communityId):
        response = requests.get("{}/v1.1/communities/{}".format(self.server,communityId))
        self.responseProcessing(response)
        return self.data, response

    def communityUsers(self, communityId):
        response = requests.get("{}/v1.1/communities/{}/users".format(self.server,communityId))
        self.responseProcessing(response)
        return self.data, response
        
    """__API for perspectives__"""
    def perspectiveList(self):
        response = requests.get("{}/v1.1/perspectives")
        self.responseProcessing(response)
        return self.data, response
        
    def perspectiveCommunities(self,perspectiveId):
        print( "{}/v1.1/perspectives/{}/communities".format(self.server,perspectiveId) )
        response = requests.get("{}/v1.1/perspectives/{}/communities".format(self.server,perspectiveId))
        self.responseProcessing(response)
        return self.data, response
    
    """__API for similarities__"""
    def similarityCommunities(self,communityId,otherCommunityId):
        response = requests.get("{}/v1.1/communities/{}/similarity/{}".format(self.server,communityId,otherCommunityId))
        self.responseProcessing(response)
        return self.data, response
        
    def dissimilarityCommunities(self,communityId,otherCommunityId):
        response = requests.get("{}/v1.1/communities/{}/dissimilarity/{}".format(self.server,communityId,otherCommunityId))
        self.responseProcessing(response)
        return self.data, response
        
    
    """__API for jobs__"""
    def jobDescription(self, jobId):
        response = requests.get("{}/v1.1/jobs/{}".format(self.server,jobId))
        self.responseProcessing(response)
        return self.data, response
       