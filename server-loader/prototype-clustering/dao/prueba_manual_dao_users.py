
import os
from context import dao
from dao.dao_class import DAO
from dao.dao_db_users import DAO_db_users
from dao.dao_db_communities import DAO_db_community
from dao.dao_db_similarities import DAO_db_similarity
from dao.dao_csv import DAO_csv
from dao.dao_json import DAO_json
from dao.dao_api import DAO_api
from dao.dao_db_flags import DAO_db_flags
from dao.dao_linkedDataHub import DAO_linkedDataHub
import json

import requests
from requests.auth import HTTPBasicAuth

from bson.json_util import dumps, loads



def main():
    
    dao = DAO_db_users()
    
    #dao = DAO_db_users("localhost", 27018, "spice", "spicepassword")
    # dao = DAO_db_community("localhost", 27018, "spice", "XXX")

    dao.drop()
    user1 = {
        "id": "hola",
        "userid": "001",
        "origin": "aaa",
        "source_id": "bbb",
        "age": "22",
        "gender": "F",
        "hobby": "bwm"
    }
    user2 = {
        "id": "hola",
        "userid": "001",
        "origin": "aaa",
        "source_id": "bbb",
        "age": "19",
        "gender": "M",
        "religion": "AA"
    }
    correctResponse = {
        "id": "hola",
        'userid': '001',
        'origin': 'aaa',
        'source_id': 'bbb',
        'hobby': 'bwm',
        'gender': 'M',
        'age': '19',
        'religion': 'AA'
        # ,'_id': "xxx"
    }
    dao.insertUser(user1)
    # print(dao.getUsers())
    # print(dao.getUser("001"))
    # dao.updateUser(dao.getUser("001"))
    #
    # # print(dao.getUser("001"))
    # print(dao.getUsers())
    
    """
    daoF = DAO_db_flags()
    daoF.insertFlag(False)
    data = daoF.getFlag()
    print(data)
    daoF.invertFlag()
    data = daoF.getFlag()
    print(data)
    """


main()
