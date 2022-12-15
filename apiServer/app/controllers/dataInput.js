const DataInput = require('../service/DataInput.js');
var jobManager = require('./jobsRoute/jobsManager.js');
const seedFileConfig = require("../config/seedFile.config.js");

// redirect post request to api_loader
// module.exports.postInputData = function postInputData(req, res, next) {
//     try {
//         DataInput.PostDataInput(req.body)
//             .then(function (perspectiveId) {
//                 // var jobPath = jobManager.createJob(perspectiveId, "postPerspective")
//                 res.status(200).send(perspectiveId);
//             })
//             .catch(function (response) {
//                 res.status(400).send("postInputData error");
//                 res.send(response);
//             });
//     } catch (error) {
//         console.error("postInputData:" + error)
//         res.status(500)
//     }
// };

module.exports.getSeed = function getSeed(req, res, next) {
    let seedFile = require('../src/' + seedFileConfig.filename);
    // console.log(seedFile);
    res.status(200).send(seedFile);
};
