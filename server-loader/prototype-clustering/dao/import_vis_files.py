from context import dao
from dao_class import DAO


from dao.dao_db_communities import DAO_db_community
from dao.dao_json import DAO_json

def main():
    # Nombre/ruta del fichero
    daoJSON = DAO_json("test/data/agglomerativeClusteringGAM_light.json")
    daoCom = DAO_db_community("localhost", 27018, "spice", "spicepassword")

    # leemos el fichero
    data = daoJSON.getData()
    # print(data)

    # Insertamos el fichero en la BD
    daoCom.insertFileList("agglomerativeClusteringGAM_light", data)

main()