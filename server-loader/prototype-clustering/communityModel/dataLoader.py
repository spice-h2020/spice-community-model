import os

class DataLoader():
    
#--------------------------------------------------------------------------------------------------------------------------
#   Data
#--------------------------------------------------------------------------------------------------------------------------
    
    def fileRoute(self,filename):
        abspath = os.path.dirname(__file__)
        relpath = filename
        route = os.path.normpath(os.path.join(abspath, relpath))
                
        return route
