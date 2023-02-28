const SeedFileConfig = require("../config/seedFile.config.js");

module.exports.getSeed = function getSeed(req, res, next) {
    let seedFile = require('../src/' + SeedFileConfig.filename);
    // console.log(seedFile);
    res.status(200).send(seedFile);
};
