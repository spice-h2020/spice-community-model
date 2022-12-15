import os
import pymongo
from bson.json_util import dumps, loads
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ForkingMixIn
from bson.objectid import ObjectId

import logging

from context import dao
from dao.dao_db import DAO_db
from dao.dao_db_users import DAO_db_users
from dao.dao_db_communities import DAO_db_community
from dao.dao_db_similarities import DAO_db_similarity
from dao.dao_db_perspectives import DAO_db_perspectives
from dao.dao_db_flags import DAO_db_flags
from dao.dao_db_distanceMatrixes import DAO_db_distanceMatrixes
import json

from dao.dao_json import DAO_json
import time

from communityModel.communityModel import CommunityModel
from communityModel.communitiesSimilarityModel import CommunitiesSimilarityModel

from communityModel.dataLoader import DataLoader


server_loader_port = int(os.environ['CM_DOCKER_PORT'])
server_loader_ip = "0.0.0.0"

db_host = os.environ['DB_HOST']
db_user = os.environ['DB_USER']
db_password = os.environ['DB_PASSWORD']
db_name = os.environ['DB_NAME']
db_port = os.environ['DB_PORT']

class Handler(BaseHTTPRequestHandler):

    # TODO:
    # - incorrect path or filename
    # - create thread for each connection/request
    # - refactor code

    def do_GET(self):
        """
        _get handler_
        API doc:
        - GET:
        http://localhost:8090/file/all                                      -> return all files -- List
        http://localhost:8090/file/{fileId}                                 -> return the first file with name equal to "fileId" -- JSON
        http://localhost:8090/perspectives/all                              -> ... -- List
        http://localhost:8090/perspectives/{perspectiveId}                  -> ... -- JSON
        http://localhost:8090/perspectives/{perspectiveId}/communities      -> Communities with the same "perspectiveId" -- List
        http://localhost:8090/index                                         -> return json files index (returns only files id) -- list
        - POST:
        Used only for redirection of POST requests from API Spice and access DB from here
        """
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n",
                     str(self.path), str(self.headers))
        try:
            request = self.path.split("/")
            print("Request GET: ", request)
            first_arg = request[1]
            if first_arg == "file":
                self.__getFile(request[2])
            elif first_arg == "perspectives":
                self.__getPerspertives(request)
            elif first_arg == "index":
                self.__getIndex()
            elif first_arg == "dump":
                self.__getDump()
            else:
                print("-Error-")
                self.__set_response(404)
                self.wfile.write(
                    "-Error-\nThis GET request is not defined.\nGET request for {}".format(self.path).encode('utf-8'))
        except Exception as e:
            print("-Error-")
            print(e)
            if str(e) != "pymongo.errors.ServerSelectionTimeoutError":
                self.__set_response(500)
                self.wfile.write("-Error-\nGET request for {}".format(self.path).encode('utf-8'))
                # raise
            else:
                self.__set_response(500)
                self.wfile.write(
                    "-MongoDB connection timeout error-\nGET request for {}".format(self.path).encode('utf-8'))

    def do_POST(self):
        """
        _post handler_

        """
        content_length = int(
            self.headers['Content-Length'])  # <--- Gets the size of data
        # <--- Gets the data itself
        post_data = self.rfile.read(content_length)
        post_data = post_data.decode('utf-8')
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                     str(self.path), str(self.headers), post_data)
        ok = False
        request = self.path.split("/")
        print("Request POST: ", request)
        first_arg = request[1]
        if first_arg == "perspective":
            ok = True
            perspectiveId = loads(post_data)
            print(perspectiveId)
            print("\n\n")

            # retrive perspective from db
            daoPerspective = DAO_db_perspectives()
            #perspective = daoPerspective.getPerspective(
                #ObjectId(perspectiveId))
                
            perspective = daoPerspective.getPerspective(perspectiveId)
            print("perspective: ", perspective)

            # ok = daoPerspective.insertPerspective(perspective)
            
            # newFlag = {
            #     "perspectiveId": perspective["id"],
            #     "userId": ""
            # }
            # daoFlags = DAO_db_flags()
            # daoFlags.updateFlag(newFlag)

        elif first_arg == "updateUsers":
            # add or update user
            users = loads(post_data)
            daoUsers = DAO_db_users()
            ok = daoUsers.insertUser_API(users)
            
            # Activate flags associated to user/perspective pair (perspective makes use of one of the user's attributes (pname))
            daoPerspectives = DAO_db_perspectives()
            daoFlags = DAO_db_flags()
            
            perspectives = daoPerspectives.getPerspectives()
            
            for user in users:
                for perspective in perspectives:
                    for similarityFunction in perspective['similarity_functions'] + perspective['interaction_similarity_functions']:
                        """
                        print("checking similarity function")
                        print("att_name: " + str(similarityFunction['sim_function']['on_attribute']['att_name']))
                        print("pname: " + str(user['pname']))
                        """
                        attributeLabel = user["category"] + "." + user["pname"]
                        if (similarityFunction['sim_function']['on_attribute']['att_name'] == attributeLabel):
                            flag = {'perspectiveId': perspective['id'], 'userid': user['userid'], 'needToprocess': True}
                            # flag = {'perspectiveId': perspective['id'], 'userid': 'flagAllUsers', 'flag': True}
                            daoFlags.updateFlag(flag)

        elif first_arg == "update_CM":
            #data = loads(post_data.decode('utf-8'))
            data = "1000"
            print("update_CM")
            ok = "updateCM"

        elif first_arg == "load":
            data = loads(post_data)
            DAO_db().loadDB(data)
            ok = True
            
        if ok == "updateCM":
            self.__set_response(204)
            self.wfile.write("POST request for {}".format(
                self.path).encode('utf-8'))
            self.__updateCM(post_data)
        elif ok:
            self.__set_response(204)
            self.wfile.write("POST request for {}".format(
                self.path).encode('utf-8'))
        else:
            self.__set_response(500)
            self.wfile.write("POST request for {}".format(
                self.path).encode('utf-8'))

    def __updateCM(self, post_data):
        # Check if there is an update flag
        daoPerspectives = DAO_db_perspectives()
        daoFlags = DAO_db_flags()

        flags = daoFlags.getFlags()
        
        # Sort all flags by perspectiveId
        perspectiveFlagsDict = {}
        for flag in flags:
            if flag["perspectiveId"] not in perspectiveFlagsDict:
                perspectiveFlagsDict[flag["perspectiveId"]] = []
            perspectiveFlagsDict[flag["perspectiveId"]].append(flag['userid'])
            # needToprocess to false
            flag["needToprocess"] = False
            daoFlags.replaceFlag(flag)

            
        # Update each perspective communities
        for perspectiveId in perspectiveFlagsDict:

            perspective = daoPerspectives.getPerspective(perspectiveId)
            
            # Call to the community model
            communityModel = CommunityModel(perspective,perspectiveFlagsDict[perspectiveId])
            communityModel.start()
            
            # Compute the similarity between the new communities generated with self.perspective and all the other communities
            data = communityModel.getData()
            communitiesSimilarityModel = CommunitiesSimilarityModel(perspectiveId,data)
        
        # Delete updated flags (cannot delete the whole collection because new flags may have been added while CM was updating)
        for flag in flags:
            # Remove flag
            daoFlags.deleteFlag(flag)
        
    def __set_response(self, code, dataType='text/html'):
        self.send_response(code)
        self.send_header('Content-type', dataType)
        self.end_headers()

    def __getIndex(self):
        dao = DAO_db_community()
        data = dao.getFileIndex()
        print(data)
        self.__set_response(200, 'application/json')
        self.wfile.write(dumps(data).encode(encoding='utf_8'))
    
    def __getDump(self):
        dump = DAO_db().dumpDB()
        # print(data)
        self.__set_response(200, 'application/json')
        self.wfile.write(dumps(dump).encode(encoding='utf_8'))

    def __getPerspertives(self, request):
        dao = DAO_db_perspectives()
        perspectiveId = request[2]
        if perspectiveId == "all":
            data = dao.getPerspectives()
            self.__set_response(200, 'application/json')
            self.wfile.write(dumps(data).encode(encoding='utf_8'))
        else:
            if len(request) == 4 and request[3] == "communities":
                # perspectives/{perspectiveId}/communities
                result = []
                coms = DAO_db_community(
                    db_host, db_port, db_user, db_password, db_name).getCommunities()
                for com in coms:
                    if com["perspectiveId"] == perspectiveId:
                        result.append(com)
                self.__set_response(200, 'application/json')
                self.wfile.write(dumps(result).encode(encoding='utf_8'))
            else:
                data = dao.getPerspective(perspectiveId)
                print(data)
                if data:
                    self.__set_response(200, 'application/json')
                    self.wfile.write(dumps(data).encode(encoding='utf_8'))
                else:
                    self.__set_response(404)
                    self.wfile.write("File not found\nGET request for {}".format(self.path).encode('utf-8'))

    def __getFile(self, fileId):
        dao = DAO_db_community(db_host, db_port, db_user, db_password, db_name)
        if fileId == "all":
            data = dao.getFileLists()
            self.__set_response(200, 'application/json')
            self.wfile.write(dumps(data).encode(encoding='utf_8'))
        else:
            data = dao.getFileList(fileId)
            if data:
                self.__set_response(200, 'application/json')
                self.wfile.write(dumps(data).encode(encoding='utf_8'))
            else:
                self.__set_response(404)
                self.wfile.write("File not found\nGET request for {}".format(self.path).encode('utf-8'))


class ForkingHTTPServer(ForkingMixIn, HTTPServer):
    def finish_request(self, request, client_address):
        request.settimeout(30)
        HTTPServer.finish_request(self, request, client_address)

def run(server_class=HTTPServer, handler_class=Handler):
    logging.basicConfig(level=logging.INFO)
    server_address = (server_loader_ip, server_loader_port)
    httpd = ForkingHTTPServer(server_address, handler_class)
    logging.info('Starting server-loader...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping server-loader...\n')

def removeData():
    daoP = DAO_db_perspectives()
    daoP.drop()
    daoC = DAO_db_community()
    daoC.drop()
    daoC.dropFullList()
    daoS = DAO_db_similarity()
    daoS.drop()

def importData():



    json5 = DAO_json("app/prototype-clustering/api_server/data/5.json").getData()
    json6 = DAO_json("app/prototype-clustering/api_server/data/6.json").getData()

    daoC = DAO_db_community()
    daoC.insertFileList("5", json5)
    daoC.insertFileList("6", json6)
    
    # jsonAll = DAO_json("app/prototype-clustering/api_server/data/Allperspectives.json").getData()
    # daoP = DAO_db_perspectives()
    # daoP.insertPerspective(jsonAll)
    
def clearDatabase():
    print("1")
    daoF = DAO_db_flags()
    print("1a")
    #flags = daoF.getFlags()
    #print(flags)
    daoF.drop()
    
    print("2")
    daoC = DAO_db_community()
    daoC.drop()
    daoC.dropFullList()
    
    print("3")
    daoU = DAO_db_users()
    daoU.drop()
    
    print("4")
    daoDistanceMatrixes = DAO_db_distanceMatrixes()
    daoDistanceMatrixes.drop()
    
    print("5")
    daoSimilarities = DAO_db_similarity()
    daoSimilarities.drop()
    
    daoPerspectives = DAO_db_perspectives()
    daoPerspectives.drop()
    

def initializeDatabase():
    daoPerspectives = DAO_db_perspectives()
    daoPerspectives.drop()
    
    route = DataLoader().fileRoute("perspectives/HECHT/hecht agglomerative.json")
    #route = DataLoader().fileRoute("perspectives/GAM/GAM similar user emotions in similar artworks (iconclass) annotated-stories.json")
    file = open(route)
    perspectives = json.load(file)
    print(perspectives)
    file.close()
    

    
    daoPerspectives.insertPerspective(perspectives)


def importDatabase():
    route = DataLoader().fileRoute("databases/database.json")
    file = open(route)
    database = json.load(file)
    
    for key in database:
        for data in database[key]:
            data.pop("_id", "")

    # daos
    daoFlags = DAO_db_flags()
    daoSimilarities = DAO_db_similarity()
    daoCommunities = DAO_db_community()
    daoUsers = DAO_db_users()
    daoPerspectives = DAO_db_perspectives()
    daoMatrixes = DAO_db_distanceMatrixes()
    
    #daoFlags.insertFlag(database['flags'])
    #daoSimilarities.insertSimilarity(database['similarities'])
    for data in database['communitiesVisualization']:
        daoCommunities.insertFileList("", data)
    daoUsers.insertUser(database['users'])  
    daoPerspectives.insertPerspective(database['perspectives']) 
    daoMatrixes.insertDistanceMatrix(database['distanceMatrixes'])       
        
    
    
if __name__ == '__main__':
    from sys import argv
    
    # For now, we are not using it
    #removeData()
    #importData()
    
    
    # To prepare things
    clearDatabase()
    #initializeDatabase()
    
    #importDatabase()

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
