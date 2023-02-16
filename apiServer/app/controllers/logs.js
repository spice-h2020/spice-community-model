const idParam_nLogs = 'nLogs';
const idParam_startDate = 'startDate';
const idParam_endDate = 'endDate';
const Logs = require('../service/LogsService.js');


module.exports.getNLatestLogs = function getPerspectives(req, res, next) {
    const nLogs = parseInt(req.params[idParam_nLogs]);

    if (isNaN(nLogs)) {
        res.status(400).send("Parameter is NaN");
    }
    else if (nLogs <= 0) {
        res.status(400).send("Parameter is <=0");
    }
    else {
        Logs.getNLatestLogs(nLogs)
            .then(function (response) {
                res.send(response);
            })
            .catch(function (error) {
                res.status(400).send(error);
            });
    }
};


module.exports.getLogsBetweenTwoDates = function getPerspectives(req, res, next) {
    const startDate = req.query[idParam_startDate];
    const endDate = req.query[idParam_endDate];

    if (isNaN(Date.parse(startDate)) || isNaN(Date.parse(endDate))) {
        res.status(400).send("Parameters are NaN");
    }
    else if (new Date(startDate) >= new Date(endDate)) {
        res.status(400).send("startDate is >= than endDate");
    }
    else {
        Logs.getLogsBetweenTwoDates(new Date(startDate), new Date(endDate))
            .then(function (response) {
                res.send(response);
            })
            .catch(function (error) {
                res.status(400).send(error);
            });
    }
};