from context import dao
from dao.dao_class import DAO
from dao.dao_db_users import DAO_db_users
from dao.dao_db_communities import DAO_db_community
from dao.dao_db_similarities import DAO_db_similarity
from dao.dao_db_perspectives import DAO_db_perspectives
from dao.dao_csv import DAO_csv
from dao.dao_json import DAO_json
from dao.dao_api import DAO_api
from dao.dao_linkedDataHub import DAO_linkedDataHub
# from dao.deleteAndLoadDefaultData import deleteAndLoad
import json

import requests
from requests.auth import HTTPBasicAuth

from bson.json_util import dumps, loads

"""
TODO
Anadir datos de prueba, por fin finalizar el repositorio y dejarselo a marco
"""


def main():
    # ## Delete old data and load default values
    # deleteAndLoad()

    # -------------------------------------------------------------
    # ## Pruebas para el POST y el GET. Descomentar el get necesario
    # ## 8090 => local api server
    # ## 8080 => spice api
    # -------------------------------------------------------------

    # # response = requests.post("http://localhost:8090/", json=data_set)
    # response = requests.get("http://localhost:8090/file/file0")
    # response = requests.get("http://localhost:8090/file/all") # 102
    # response = requests.get("http://localhost:8090/thisRequestShouldReturn404Error")
    # response = requests.get("http://localhost:8090/perspectives/100")
    response = requests.get("http://localhost:8090/file/agglomerativeClusteringGAM_light")
    # response = requests.get("http://localhost:8090/perspectives/101/communities")
    # response = requests.get("http://localhost:8080/v1.1/perspectives/101/communities")
    # response = requests.get("http://localhost:8080/v1.1/communities")
    print(response)
    print(response.text)
    print(response.status_code)
    print(response.headers)

    print("________________________________")
    # response = requests.get("http://localhost/102")
    # print(response)
    # print(response.text)
    # print(response.status_code)
    # print(response.headers)

main()
