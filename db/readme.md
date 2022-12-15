# Community model Database

Community model uses a non-sql database implemented using MongoDB. 

## Quick start

## Developing

### Structure

`initdb.js` creates the initial structure of collections in MongoDB. The collections are the following:

- users: Stores information about users (both demographic and contribution data)
- perspectives: Stores perspective configuration files
- communities: Stores the communities created by the community model.
- communitiesVisualization: Stores community information for the visualization tool VISIR.
- similarities: Stores information about similarity among communities.
- flags: Intermediate information to know which collections must be updated.
- distanceMatrixes: Stores distance values among users in a perspective. 

## Tests

## License

The content of this repository is distributed under [Apache 2.0 License](LICENSE).
