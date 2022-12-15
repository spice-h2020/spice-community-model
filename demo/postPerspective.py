import json
import requests
import config as cf

def main():

    #--------------------------------------------------------------------------------------------------------------------------
    #    Select Configuration dictionary for a case study
    #--------------------------------------------------------------------------------------------------------------------------
    
    configData = cf.DMH_CONFIG
    
    #--------------------------------------------------------------------------------------------------------------------------

   
    server = configData["server"]
    museum = configData["museum"]

    # Change Sample Perspective
    filename = 'samplePerspective.json'

    #--------------------------------------------------------------------------------------------------------------------------
    #    Insert perspective
    #--------------------------------------------------------------------------------------------------------------------------

    route = "data/" + museum + "/" + filename
    file = open(route)
    perspective = json.load(file)
    
    response = requests.post("{}/v1.1/perspective".format(server), json=perspective)
    print(response)
    print(response.text)
    

main()
