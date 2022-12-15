const DataInput = require('../service/DataInput.js');
var jobManager = require('./jobsRoute/jobsManager.js');


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
    res.status(200).send(getExampleSeed());
    // DataInput.getSeed()
    //     .then(function (response) {
    //         var seed = response
    //         res.status(200).send(seed);
    //     })
    //     .catch(function (response) {
    //         res.status(400).send("seed error");
    //     });
};

function getExampleSeed() {
    let seed = require('../src/seedFile.json');
    // console.log(seed);
    return seed;
}