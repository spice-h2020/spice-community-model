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

import json

import requests
from requests.auth import HTTPBasicAuth

from bson.json_util import dumps, loads

"""
Script used to load some default data
"""

def main():
    deleteAndLoad()


def deleteAndLoad():

    users = [
        {
            "id": "1",
            "userid": "23",
            "origin": "a",
            "source_id": "b",
            "source": "c description",
            "pname": "DemographicGender",
            "pvalue": "F (for Female value)",
            "context": "application P:DemographicsPrep",
            "datapoints": 0
        },
        {
            "id": "2",
            "userid": "28",
            "origin": "a",
            "source_id": "b",
            "source": "Content description",
            "pname": "Age",
            "pvalue": "28",
            "context": "application P:DemographicsPrep",
            "datapoints": 0
        },
        {
            "id": "3",
            "userid": "44",
            "origin": "90e6d701748f08514b01",
            "source_id": "90e6d701748f08514b01",
            "source": "Content description",
            "pname": "DemographicGender",
            "pvalue": "M (for Female value)",
            "context": "application P:DemographicsPrep",
            "datapoints": 0
        },
        {
            "id": "4",
            "userid": "56",
            "origin": "90e6d701748f08514b01",
            "source_id": "90e6d701748f08514b01",
            "source": "Content description",
            "pname": "Age",
            "pvalue": "56",
            "context": "application P:DemographicsPrep",
            "datapoints": 0
        }]

    perspectives = [{
        "id": "100",
        "name": "Perspective_100",
        "algorithm": {
            "name": "String",
            "params": [
                "param_a", "param_b"
            ]
        },
        "similarity_functions": [{
            "sim_function": {
                "name": "String",
                "params": [
                    "param_a", "param_b"
                ],
                "on_attribute": {
                    "att_name": "String",
                    "att_type": "String"
                },
                "weight": 100
            }
        }]
    }, {
        "id": "101",
        "name": "Perspective_101",
        "algorithm": {
            "name": "String",
            "params": [
                "param_a", "param_b"
            ]
        },
        "similarity_functions": [{
            "sim_function": {
                "name": "String",
                "params": [
                    "param_a", "param_b"
                ],
                "on_attribute": {
                    "att_name": "String",
                    "att_type": "String"
                },
                "weight": 101
            }
        }]
    }]

    communities = [{
        "id": "621e53cf0aa6aa7517c2afdd",
        "community-type": "explicit",
        "name": "elderly",
        "perspectiveId": "101",
        "explanation": "People above 65",
        "users": [
            "23",
            "28"
        ],
    }, {
        "id": "721e53cf0aa6aa7517c2afdd",
        "community-type": "implicit",
        "explanation": "lorem ipsum",
        "perspectiveId": "101",
        "name": "impl_1",
        "users": [
            "44",
            "23"
        ]
    }, {
        "id": "821e53cf0aa6aa7517c2afdd",
        "community-type": "explicit",
        "name": "teenager",
        "perspectiveId": "100",
        "explanation": "People whose age is between 12 and 17",
        "users": [
            "44",
            "56"
        ],
    }]

    similarities = [{
        "target-community-id": "621e53cf0aa6aa7517c2afdd",
        "other-community-id": "721e53cf0aa6aa7517c2afdd",
        "similarity-function": "cosine",
        "value": 0.893,
    }, {
        "target-community-id": "721e53cf0aa6aa7517c2afdd",
        "other-community-id": "821e53cf0aa6aa7517c2afdd",
        "similarity-function": "cosine",
        "value": 0.563,
    }, {
        "target-community-id": "621e53cf0aa6aa7517c2afdd",
        "other-community-id": "821e53cf0aa6aa7517c2afdd",
        "similarity-function": "cosine",
        "value": 0.915,
    }, {
        "target-community-id": "721e53cf0aa6aa7517c2afdd",
        "other-community-id": "621e53cf0aa6aa7517c2afdd",
        "similarity-function": "cosine",
        "value": 0.893,
    }, {
        "target-community-id": "821e53cf0aa6aa7517c2afdd",
        "other-community-id": "621e53cf0aa6aa7517c2afdd",
        "similarity-function": "cosine",
        "value": 0.915,
    }, {
        "target-community-id": "821e53cf0aa6aa7517c2afdd",
        "other-community-id": "721e53cf0aa6aa7517c2afdd",
        "similarity-function": "cosine",
        "value": 0.563,
    }]

    print("Starting.")
    daoP = DAO_db_perspectives("localhost", 27018, "spice", "spicepassword")
    daoP.drop()
    daoP.insertPerspective(perspectives)

    daoC = DAO_db_community("localhost", 27018, "spice", "spicepassword")
    daoC.drop()
    daoC.dropFullList()
    daoC.insertCommunity(communities)

    daoS = DAO_db_similarity("localhost", 27018, "spice", "spicepassword")
    daoS.drop()
    daoS.insertSimilarity(similarities)
    print("Finished.")


main()
