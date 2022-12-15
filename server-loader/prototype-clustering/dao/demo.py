from context import dao
from dao_class import DAO
import os

from context import dao
from dao.dao_class import DAO
from dao.dao_db_users import DAO_db_users
from dao.dao_db_communities import DAO_db_community
from dao.dao_db_similarities import DAO_db_similarity
from dao.dao_csv import DAO_csv
from dao.dao_json import DAO_json
from dao.dao_api import DAO_api
from dao.dao_linkedDataHub import DAO_linkedDataHub

import json

import requests
from requests.auth import HTTPBasicAuth

from bson.json_util import dumps, loads


# Daos
# from dao.dao_db_interactionData import DAO_db_interactionDatas



def main():

    # route1 = r"../communityModel/data/new-annotated-stories.json"
    # # route2 = r"test/data/parser_output.json"
    # route2 = r"../communityModel/perspectives/GAM similar user emotions in similar artworks (iconclass) annotated-stories.json"
    routeDump = r"../dao/test/data/dump.json"
    dump = DAO_json(routeDump).getData()
    # perspective = DAO_json(route2).getData()

    # api = DAO_api()

    # a = requests.post("http://localhost:8080/v1.1/dataInput", json = annotatedStories)
    # print(a)
    # print(a.text)

    b = requests.post("http://localhost:8080/databaseController/load", json = dump)
    print(b)
    print(b.text)

main()