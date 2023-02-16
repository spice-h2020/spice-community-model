const idParam_nLogs = 'nLogs';
const idParam_date1 = 'date1';
const idParam_date2 = 'date2';
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
    const date1 = req.params[idParam_date1];
    const date2 = req.params[idParam_date2];

    Logs.getLogsBetweenTwoDates(date1, date2)
        .then(function (response) {
            res.send(response);
        })
        .catch(function (error) {
            res.status(400).send(error);
        });
};