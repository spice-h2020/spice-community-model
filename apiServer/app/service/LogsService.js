'use strict';
const db = require("../models");

const logsDAO = db.logs;

/**
* Logs
* Access to CM logs
*
* returns logs documents
**/
exports.getNLatestLogs = function (n) {
    return new Promise(function (resolve, reject) {
        logsDAO.nLatestLogs(n,
            data => {
                resolve(data)
            },
            error => {
                console.log("LogsService error: " + error);
                reject(error)
            })
    });
};

exports.getLogsBetweenTwoDates = function (date1, date2) {
    return new Promise(function (resolve, reject) {
        logsDAO.logsBetweenTwoDates(date1, date2,
            data => {
                resolve(data)
            },
            error => {
                console.log("LogsService error: " + error);
                reject(error)
            })
    });
};

