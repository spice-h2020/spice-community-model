'use strict';
const db = require("../models");

const FlagDAO = db.flag;

/**
* Flags
* Access to specific flag to check it
*
* returns flag document
**/
exports.getFlags = function () {
    return new Promise(function (resolve, reject) {
        FlagDAO.checkFlag(
            data => {
                resolve(data)
            },
            error => {
                console.log("flagService error: " + error);
                reject(error)
            })
    });
};

exports.getFlagsById = function (perspectiveId) {
    return new Promise(function (resolve, reject) {
        FlagDAO.checkFlagById(perspectiveId,
            data => {
                resolve(data)
            },
            error => {
                console.log("flagService error: " + error);
                reject(error)
            })
    });
};

