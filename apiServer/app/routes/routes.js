// Adds rest actions defined in openapi.yaml and jobs managet to the router
module.exports = app => {
    const yaml = require('js-yaml');
    const fs = require('fs');

    const customControllers = {
        Communities: require("../controllers/communities.js"),
        Similarity: require("../controllers/similarity.js"),
        Users: require("../controllers/users.js"),
        Perspectives: require("../controllers/perspectives.js"),
        DataInput: require("../controllers/dataInput.js")
    };

    function initRouters(router) {
        try {
            const doc = yaml.load(fs.readFileSync(app.get("apiSpec"), 'utf8'));
            router.path = doc.servers[0].url;
            let routes = [];
            for (let path in doc.paths) {
                let newPath = transformPath(path);
                const restActions = ['get', 'post', 'put', 'delete'];
                for (const action of restActions) {
                    if (doc.paths[path][action]) {
                        if (doc.paths[path][action]['operationId'] != "none") {
                            let service = doc.paths[path][action]['x-swagger-router-controller'];
                            let method = doc.paths[path][action]['operationId'];
                            router[action](newPath, customControllers[service][method]);
                        }
                    }
                }
            }
        } catch (e) {
            console.log(e);
        }
    }

    function transformPath(path) {
        const regex = /{([^}]+)}/g;
        let parameters = path.match(regex);
        let result = path;
        if (parameters) {

            for (let i = 0; i < parameters.length; ++i) {
                let word = parameters[i].slice(1, -1);
                let words = word.split('-');
                for (let j = 1; j < words.length; ++j) {
                    let temp = words[j];
                    words[j] = temp.charAt(0).toUpperCase() + temp.slice(1);
                }
                parameters[i] = ":" + words.join('');
            }
            result = path.replace(regex, () => parameters.shift());
        }
        return result;
    }

    const express = require("express");

    var router = express.Router();
    var visAPI = require("../controllers/communitiesVisualization.js")
    var jobsRouter = require("../controllers/jobsRoute/jobsRoute.js")
    var databaseContrl = require("../controllers/databaseController.js")

    // Adds jobs and api routes to the server
    app.use('/visualizationAPI', visAPI); // if we add /v1.1/ to this path, it will go through validation of the openapi.yml spec file
    app.use('/databaseController', databaseContrl); // if we add /v1.1/ to this path, it will go through validation of the openapi.yml spec file
    app.use('/v1.1/jobs', jobsRouter);
    initRouters(router);
    app.use('/', express.static('api'));
    app.use(router.path, router);

};