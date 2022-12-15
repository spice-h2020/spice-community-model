#--------------------------------------------------------------------------------------------------------------------------
#    Converts "array of user data" to "dict: {keys: userid, value: user data}"
#--------------------------------------------------------------------------------------------------------------------------

import json

def main():

    root = 'data/HECHT/'
    filename = 'linked data hub.json'
    #filename = 'user model data.json'

    #--------------------------------------------------------------------------------------------------------------------------
    #    Read data
    #--------------------------------------------------------------------------------------------------------------------------
    
    route = root + 'original/' + filename
    with open(route, 'r', encoding='utf8') as f:
        data = json.load(f) 
        
    postDict = {}
    for user in data:
        key = user['userid']
        if(key not in postDict):
            postDict[key] = []
        
        requiredKeys = ['id', 'origin', 'source_id']
        for requiredKey in requiredKeys:
            user[requiredKey] = user['userid']
            
        
        postDict[key].append(user)
        
    #--------------------------------------------------------------------------------------------------------------------------
    #    Save it in user dictionary format
    #--------------------------------------------------------------------------------------------------------------------------
    
    route = root + filename
    with open(route, "w") as outfile:
        json.dump(postDict, outfile, indent=4)



main()