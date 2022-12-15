import os
import pymongo
from bson.json_util import dumps, loads
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ForkingMixIn
from bson.objectid import ObjectId

import logging

from context import dao
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
from communityModel.dataLoader import DataLoader


# distance(medoid(A), medoid(B)) {[}community A} + distance(medoid(A), medoid(B)) /2 {community B}



def computeDissimilarity(daoU, daoDistanceMatrixes):
    