from context import dao
# First one is for local, second one for remote.
from dao.dao_api import DAO_api

import time

def wait(seconds):
    time.sleep(seconds)

def main():
    
    # Perform GET \communities
    daoAPI = DAO_api()
    #daoAPI = DAO_api_remote()
    response = daoAPI.communityList()
    
    # We get returned json object
    jsonObject = response[0]
    
    # If the CM has to update (for example, after performing "post.py" since there are new users")
    # It returns a job url to track the update status (class: dict) ( e.g., ({'path': '/jobs/5058'}, <Response [202]>) ) 
    if (isinstance(jsonObject, dict) and 'path' in jsonObject):
        jobId = jsonObject['path'].replace("/jobs/","")
        jobStatus = ''
        
        print(response)
        
        # When the CM stops updating, the job will change to status (COMPLETED) and include the requested data.
        while jobStatus != 'COMPLETED':
            wait(60)
            
            jobResponse = daoAPI.jobDescription(jobId)
            jobStatus = jobResponse[0]['job']['job-state']
                
        # Retrieve requested data from the job json object
        requestedData = jobResponse[0]['job']['data']
        
        
    # If it doesn't need to update, it directly returns the desired result (in this case a list of communities)
    else:
        requestedData = jsonObject
    
    # Check 
    print("GET \communities")
    print(requestedData)
    
    
main()