# API server

API is a web application that allows finding communities between different data.
This API allows inserting data for the configuration of the Community Model and retrieving generated data, or data neccesary for other tools like the Config Tool App.

## Quick start

Refer to [root readme](../readme.md)

## Developing

Refer to [root readme](../readme.md)

### API entry points

- Configuration Tool: OneProvides functionality for Configuration Tool
    - Get `/seed` Retrieve seed file used by Configuration Tool
- Perspectives: Four entry points related to perspectives
    - Get `/perspectives` Perspectives within the CM. If the CM update is necessary returns a job.
    - Get `/perspectives/{perspectiveId}` Information about a concrete perspective. If the CM update is necessary returns a job.
    - Get `/perspectives/{perspectiveId}/communities` Communities that have the same perspective. If the CM update is necessary returns a job.
    - Post `/perspective` Injects new perspectives in the CM. Checks if perspectives with the same id already exist. Creates the need to update the CM.
- Communities: Three entry points to query information about communities
    - Get `/communities` The communities within the CM. If the CM update is necessary returns a job.
    - Get `/communities/{communityId}` The informat ion about a concrete community. If the CM update is necessary returns a job.
    - Get `/communities/{communityId}/users` The users that belong to a community. If the CM update is necessary returns a job.
- Users: Two entry points related to users
    - Get `/users/{userId}/communities` One for querying about the communities that a user belongs to. 
    - Post `/users/{userId}/update-generated-content` One for injecting user contributions in the CM. Creates the need to update the CM.
- Similarities: Four entry points to provide services about similarity and dissimilarity between communities
    - Get `/communities/{communityId}/similarity` Provides the k-most similar communities to a given one.
    - Get `/communities/{communityId}/similarity/{otherCommunityId}` Provides the dissimilar communities to a given one.
    - Get `/communities/{communityId}/similarity` Provides the similarity between two given communities.
    - Get `/communities/{communityId}/similarity/{otherCommunityId}` Provides the dissimilarity between two given communities.
- Jobs Monitor: One entry point for jobs monitor
    - Get `/jobs/{jobId}` It is used to monitor the current status of a certain job.

#### Hidden API entry points
Used by others applications or by developers.
- VISIR entry points
    - Get `/visualizationAPI/index` Returns an array[name, id] with all stored Vis files. If the CM update is necessary returns a job.
    - Get `/visualizationAPI/file/{perspectiveId}` Returns the Vis file. If the CM update is necessary returns a job.
- Database controller entry points
    - Get `/databaseController/dump` Returns dumped data from CM-API database.
    - Post `/databaseController/load` Allows uploading data to CM-API database.


### Structure

- app: Includes src files and seed files
    - api: HTML files and OpenApi specifications
    - config: Setup variables for API
    - controllers: Controllers that manages incoming HTTP requests
        - jobsRoute: Job manager that is responsible for managing requests that need an update of the Community Model.
    - models: MongoDB model files responsible for retrieving data from MongoDB
    - routes: Configures the API route
    - service: Services that manage the process of creating the response data
    - src: Seed files
    - server.js: Main file that executes the API
- test: Includes test files (WIP)

## Tests

(WIP)

## License

The content of this repository is distributed under [Apache 2.0 License](LICENSE).
