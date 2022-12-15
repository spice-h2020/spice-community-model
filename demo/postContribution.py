from context import dao
# First one is for local, second one for remote.
from dao.dao_api import DAO_api

import requests

import json

#--------------------------------------------------------------------------------------------------------------------------
#    Used to post contribution data (dict of interaction_attributes)
#--------------------------------------------------------------------------------------------------------------------------

def main():
    
    #--------------------------------------------------------------------------------------------------------------------------
    #    Change server
    #--------------------------------------------------------------------------------------------------------------------------
    
    server = "http://localhost:8080"
    
    #--------------------------------------------------------------------------------------------------------------------------
    #    Change data file
    #--------------------------------------------------------------------------------------------------------------------------

    museum = 'GAM'
    filename = 'ugcContributions.json'
    
    #--------------------------------------------------------------------------------------------------------------------------
    #    Read data
    #--------------------------------------------------------------------------------------------------------------------------
    
    fileRoute = 'data/' + museum + '/' + filename
    with open(fileRoute, 'r', encoding='utf8') as f:
        data = json.load(f) 

    #--------------------------------------------------------------------------------------------------------------------------
    #    Perform POST requests (interactions)
    #--------------------------------------------------------------------------------------------------------------------------
    
    postDict = data

    postDictKeys = ["English translation", "plutchik_emotions"]
    postDictKeys = postDict.keys()
    for ctype in postDictKeys:
        contribsDict = postDict[ctype]
        for key, value in contribsDict.items():
            response=requests.post(f'{server}/v1.1/users/{key}/update-generated-content', json = value)
            
            print("key: " + str(key))
            print("value: " + str(value))
            print(response)
            print("\n\n")


main()