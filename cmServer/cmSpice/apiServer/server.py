# python modules
import os
import pymongo
from bson.json_util import dumps, loads
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ForkingMixIn
from bson.objectid import ObjectId
import json
import time
import logging

# local modules
from cmSpice.dao.dao_db import DAO_db
from cmSpice.dao.dao_db_users import DAO_db_users
from cmSpice.dao.dao_db_communities import DAO_db_community
from cmSpice.dao.dao_db_similarities import DAO_db_similarity
from cmSpice.dao.dao_db_perspectives import DAO_db_perspectives
from cmSpice.dao.dao_db_flags import DAO_db_flags
from cmSpice.dao.dao_db_distanceMatrixes import DAO_db_distanceMatrixes

from cmSpice.dao.dao_json import DAO_json

from cmSpice.communityModel.communityModel import CommunityModel
from cmSpice.communityModel.communitiesSimilarityModel import CommunitiesSimilarityModel
from cmSpice.communityModel.dataLoader import DataLoader

from cmSpice.apiServer import getHandler
from cmSpice.apiServer import postHandler

server_loader_port = int(os.environ['CM_DOCKER_PORT'])
server_loader_ip = "0.0.0.0"

db_host = os.environ['DB_HOST']
db_user = os.environ['DB_USER']
db_password = os.environ['DB_PASSWORD']
db_name = os.environ['DB_NAME']
db_port = os.environ['DB_PORT']


class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        getHandler.get(self)

    def do_POST(self):
        postHandler.post(self)


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
