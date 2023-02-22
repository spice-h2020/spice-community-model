'use strict';

const Flags = require('../../service/FlagsService.js');
const jobsHandler = require("./jobsHandler.js");

var jobManager = require('./jobsManager.js');



var express = require('express');
const { response } = require("express");
const { communities } = require('../../models/index.js');
var router = express.Router();


var jobPrefix = "/v1.1/jobs/";

/**Response templates */
var jobStarted = {
    "job": {
        "path": "xxx",
        "jobId": "xx",
        "name": "CM Update",
        "job-state": "STARTED",
        "time-created": -1,
        "time-completed": -1,
        "time-to-autoremove-job": -1,
        "data": {}
    }
}
var jobCompleted = {
    "job": {
        "path": "",
        "jobId": "",
        "name": "CM Update",
        "job-state": "COMPLETED",
        "time-created": -1,
        "time-completed": -1,
        "time-to-autoremove-job": -1,
        "data": {}
    }
}


/**
 * Returns filled response template 
 * @param {Job id} jobId 
 * @returns Completed response
 */
function generateCompletedResponse(job, data) {
    jobManager.advanceState(job);

    var response = jobCompleted;
    var timeLeft = -1;
    if (job["job-state"] != jobManager.jobStates.ERROR) {
        var msLeft = job["time-completed"].getTime() + jobManager.timeoutAfterCompletion - (new Date().getTime());
        var dateLeft = new Date(msLeft);
        timeLeft = dateLeft.getMinutes() + ":" + dateLeft.getSeconds();
    }
    response["job"]["job-state"] = job["job-state"];
    response["job"]["path"] = jobPrefix + job.jobId;
    response["job"]["jobId"] = job.jobId;
    response["job"]["data"] = data;
    response["job"]["time-created"] = job["time-created"];
    response["job"]["time-completed"] = job["time-completed"];
    response["job"]["time-to-autoremove-job"] = timeLeft;
    return response
}

/**
 * Returns filled response template 
 * @param {string} jobId 
 * @returns Progress response
 */
function generateProgressResponse(job) {
    var data = {}
    var response = jobStarted;
    response["job"]["job-state"] = job["job-state"];
    response["job"]["path"] = jobPrefix + job.jobId;
    response["job"]["jobId"] = job.jobId;
    response["job"]["data"] = data;
    response["job"]["time-created"] = job["time-created"];
    response["job"]["time-completed"] = job["time-completed"];
    return response
}


/**
 * /jobs/:job_id GET request
 * Allows to monitor job status and get data if CM update is finished.
 * 
 */
router.get('/:job_id', function (req, res, next) {
    // console.log("List of current jobs: ");
    // console.log(JSON.stringify(jobManager.getJobs(), null, " "));

    var jobId = req.params.job_id;
    var job = jobManager.getJob(req.params.job_id);

    if (job == null) {
        res.status(404).send("JobsManager: Job not found");
    }
    else {
        var param = job.param;
        var request = job.request;

        // console.log("Monitoring Job: <" + jobId + ">, from request: <" + request + ">, with param: <" + param + ">");

        // var checkState;
        // if (request == "getPerspectives" || request == "getCommunities" || ...) {
        //     checkState = Flags.getFlags();
        // }
        // else {
        //     checkState = Flags.getFlagById(param);
        // }

        // Checks for specific flag
        // let filter = ["getPerspectives", "getCommunities", "getFilesIndex"]
        // if (filter.includes(request)) {
        if (param == 0) {
            Flags.getFlags()
                .then(function (data) {
                    if (data == null) {
                        data = {};
                        // Get data from mongodb if flag is positive
                        jobsHandler.getData(request, param)
                            .then(function (data) {
                                // if (!job.autoremove) {
                                //     jobManager.removeJobWithTimeout(jobId, 60 * 5); // 5 min = 60 * 5
                                // }
                                res.status(200).send(generateCompletedResponse(job, data));
                            })
                            .catch(function (error) {
                                res.status(404).send("JobsManager: getData exception: " + error);
                            });
                    }
                    else {
                        res.send(generateProgressResponse(job));
                    }
                })
                .catch(function (error) {
                    res.status(404).send("JobsManager: flag not found: " + error);
                });
        }
        else {
            Flags.getFlagById(param)
                .then(function (data) {
                    if (data == null) {
                        data = {};
                        // Get data from mongodb if flag is positive
                        jobsHandler.getData(request, param)
                            .then(function (data) {
                                // if (!job.autoremove) {
                                //     jobManager.removeJobWithTimeout(jobId, 60 * 5); // 5 min
                                // }
                                res.status(200).send(generateCompletedResponse(job, data));
                            })
                            .catch(function (error) {
                                res.status(404).send("JobsManager: getData error: " + error);
                            });
                    }
                    else {
                        res.send(generateProgressResponse(job));
                    }
                })
                .catch(function (error) {
                    res.status(404).send("JobsManager: flag not found: " + error);
                });
        }

    }
});

module.exports = router;