import csv

from context import dao
from dao.dao_class import DAO
from dao.dao_db_users import DAO_db_users
from dao.dao_db_communities import DAO_db_community
from dao.dao_db_similarities import DAO_db_similarity
from dao.dao_csv import DAO_csv
from dao.dao_json import DAO_json
from dao.dao_api import DAO_api
from dao.dao_linkedDataHub import DAO_linkedDataHub

import pandas as pd


# {
# "id": "11541",
# "userid": "d290f1ee-6c54-4b01-90e6-d701748f0851",
# "origin": "90e6d701748f08514b01",
# "source_id": "90e6d701748f08514b01",
# "source": "Content description",
# "pname": "DemographicGender",
# "pvalue": "F (for Female value)",
# "context": "application P:DemographicsPrep",
# "datapoints": 0
# }

def main():
    route = "test/data/AllData15122021.xlsx"
    df = pd.read_excel(route)
    # print(df)
    daoU = DAO_db_users("localhost", 27018, "spice", "spicepassword")
    daoU.drop()
    # daoC = DAO_db_community("localhost", 27018, "spice", "spicepassword")
    # daoC.drop()
    # daoS = DAO_db_similarity("localhost", 27018, "spice", "spicepassword")
    # daoS.drop()
    for ind in df.index:
        # print(df[' '][ind], df['beleifR'][ind], df['DemographicPolitics'][ind], df['DemographicReligous'][ind])
        user = {}
        user["userid"] = df[' '][ind]
        user["origin"] = ""
        user["source_id"] = ""
        user["beliefR"] = df['beleifR'][ind]  # beleifR
        user["politics"] = df['DemographicPolitics'][ind]  # DemographicPolitics
        user["religion"] = df['DemographicReligous'][ind]  # DemographicReligous
        daoU.insertUser(user)


main()
