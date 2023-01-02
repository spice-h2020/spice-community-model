# from cmSpice.apiServer import run


# local modules
import cmSpice.apiServer.init as initialization
import cmSpice.apiServer.server as apiServer



# For now, we are not using it
# removeData()
# importData()

# To prepare things
# clearDatabase()
# initializeDatabase()
# importDatabase()


# init db/cm
initialization.clearDatabase()
# run
apiServer.run()
