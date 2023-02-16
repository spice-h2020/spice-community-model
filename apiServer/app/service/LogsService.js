'use strict';
const db = require("../models");

const LogsDAO = db.logs;

/**
* Logs
* Access to CM logs
*
* returns logs documents
**/
exports.getNLatestLogs = function (n) {
    return new Promise(function (resolve, reject) {
        LogsDAO.nLatestLogs(n,
            data => {
                resolve(data)
            },
            error => {
                console.log("LogsService error: " + error);
                reject(error)
            })
    });
};

exports.getLogsBetweenTwoDates = function (startDate, endDate) {
    return new Promise(function (resolve, reject) {
        LogsDAO.logsBetweenTwoDates(startDate, endDate,
            data => {
                resolve(data)
            },
            error => {
                console.log("LogsService error: " + error);
                reject(error)
            })
    });
};

