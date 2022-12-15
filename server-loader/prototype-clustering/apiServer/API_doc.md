# API Server (Loader) simple documentation


#### - GET:
  * http://localhost:8090/file/all                                      -> return all files -- type(List)
  * http://localhost:8090/file/{fileId}                                 -> return the first file with name equal to "fileId" -- type(json)
  * http://localhost:8090/perspectives/all                              -> return all perspectives -- type(List)
  * http://localhost:8090/perspectives/{perspectiveId}                  -> return the first perspectives with name equal to "perspectiveId" -- type(json)
  * http://localhost:8090/perspectives/{perspectiveId}/communities      -> Communities with the same "perspectiveId" -- type(List)
  * http://localhost:8090/index                                         -> return index with id of files -- type(list)

#### - POST:

Used only for redirection of POST requests from API Spice