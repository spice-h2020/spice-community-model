# API server

API is a web application that allows finding communities between different data.
This API allows inserting data for the configuration of the Community Model and retrieving generated data, or data neccesary for other tools like the Config Tool App.

## Quick start

Refer to [root readme](../readme.md)

## Developing

Refer to [root readme](../readme.md)

### Structure

- app: Includes src files and seed files
    - api: HTML files and OpenApi specifications
    - config: Setup variables for API
    - controllers: Controllers that manages incoming HTTP request
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
