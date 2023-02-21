/**
 * Jobs queue manager.
 * Contains a list with jobs, and basic CRUD operations. Used to add, remove and read for specific job
 */

const Flags = require('../../service/FlagsService.js');
var redirect = require('../../service/redirectRequest.js');

var jobsList = []

var jobPrefix = "/v1.1/jobs/";

// time: minutes*60*1000=ms
var timeoutAfterCompletion = 30 * 60 * 1000;

// job states
const jobStates = {
    INQUEUE: "INQUEUE",
    STARTED: "STARTED",
    COMPLETED: "COMPLETED",
    ERROR: "ERROR"
}

// path: "",
// jobId: jobId,
// name: "CM Update",
// "job-state": jobStates.INQUEUE,
// "time-created": new Date(),
// "time-completed": new Date(),
// "time-to-autoremove-job": "",
// request: request,
// param: param,
// autoremove: false,
// flags_id: data


/**
 * Main loop. Executes every 2 seconds
 */
startJobManager = function () {
    // repeat 
    setInterval(function () {
        checkAndStartNewJob();
        autoremoveJobs();
    }, 2000);
};

/**
 * Advance state of the job
 * {job-state} -> {job-state}
 * INQUEUE,    -> STARTED,
 * STARTED,    -> COMPLETED 
 */
advanceState = function (job) {
    if (job["job-state"] == jobStates.INQUEUE) {
        job["job-state"] = jobStates.STARTED;
    }
    else if (job["job-state"] == jobStates.STARTED) {
        job["job-state"] = jobStates.COMPLETED;
        job["time-completed"] = new Date();
    }
    // else {
    //     throw 'Incorrect use of "advanceState()" function';
    // }
}

setAllJobsToErrorState = function (errorMsg) {
    jobsList.forEach(elem => {
        elem["job-state"] = jobStates.ERROR;
        elem["request"] = "error";
        elem["param"] = errorMsg;
    });
}

/**
 * Check flags and if CM is not updating then find the first job in the queue. Update CM with that job and advance the state of the job.
 */
checkAndStartNewJob = function () {
    return new Promise(function (resolve, reject) {
        // Check flags
        Flags.getFlags()
            .then(function (flags) {
                if (flags != null) {
                    // Check if CM is updating
                    var cmState = "idle";
                    var errorMsg = "";
                    flags.forEach(flag => {
                        /*
                        if (!flag["needToProcess"])
                            cmState = "updating";
                        if (flag["error"] != "N/D") {
                            cmState = "error";
                            errorMsg = flag["error"];
                        }
                        */
                        if (!flag["needToProcess"] && flag['error'] == "N/D")
                            cmState = "updating";
                    });
                    if (cmState == "error") {
                        // If any job has an error state, then set all jobs to error state (jobManager stops)
                        setAllJobsToErrorState(errorMsg)
                    }
                    else {
                        // Find first job that need an update
                        var jobToUpdate = jobsList.find(job => (job["job-state"] == jobStates.INQUEUE));
                        // 
                        if (cmState == "idle" && jobToUpdate != undefined) {
                            // update CM
                            redirect.postData(jobToUpdate["param"], "/update_CM")
                            // advance job state from queue to started
                            advanceState(jobToUpdate);
                        }
                    }
                }
                resolve();
            })
            .catch(function (error) {
                console.log("<JobsQueue> ERROR checkAndStartNewJobs: " + error);
                reject(error);
            });
    });
};

/**
 * 
 */
autoremoveJobs = function () {
    // for in jobs
    // if actualtime > timeCompleted+livetime => then remove job
    var actualTime = new Date().getTime();
    jobsList.forEach(job => {
        if (job["job-state"] == jobStates.COMPLETED) {
            var timeRemove = job["time-completed"].getTime() + timeoutAfterCompletion;
            if (actualTime > timeRemove) {
                removeJob(job["jobId"]);
            }
        }
    });
};


/**
 * Returns a path for an existing or a new job.
 * @param {string or integer} param param (if no params then set it to integer zero '0')
 * @param {string} requestTypeName request type (getCommunities, getPerspectiveById, etc)
 * @returns jobPath
 */
createJob = function (param, requestTypeName) {
    return new Promise(function (resolve, reject) {
        findExistingJob(param, requestTypeName)
            .then(function (existingJob) {
                if (existingJob == null) {
                    var jobId = generateId()
                    console.log("<JobsQueue> generateId: " + jobId)
                    console.log("<JobsQueue> param: " + param)
                    addJob(jobId, requestTypeName, param);
                    var path = jobPrefix + jobId
                    var data = {
                        "path": path
                    }
                    resolve(data);
                }
                else {
                    var path = jobPrefix + existingJob["jobId"]
                    var data = {
                        "path": path
                    }
                    resolve(data);
                }
            })
            .catch(function (error) {
                console.log("<JobsQueue> ERROR createJob.findExistingJob.promise: " + error);
                reject(error);
            });
    });
}

/**
 * Checks if a job with same parameters and request type already exist
 * Compares request, param and flags_id (without "needToProcess" field)
 * @param {string} param param
 * @param {string} requestTypeName request type
 * @returns promise that resolves with existing job or null if does not exist
 */
findExistingJob = function (param, requestTypeName) {
    return new Promise(function (resolve, reject) {
        Flags.getFlags()
            .then(function (flags) {
                var job = null;
                // remove needToProcess field to compare even if the job has started
                flags.forEach(function (v) { delete v.needToProcess });
                jobsList.forEach(elem => {
                    if (elem["request"] == requestTypeName && elem["param"] == param) {
                        if (JSON.stringify(elem["flags_id"]) == JSON.stringify(flags)) {
                            job = elem;
                        }
                    }
                });
                resolve(job);
            })
            .catch(function (error) {
                console.log("<JobsQueue> ERROR addJob.Flags.getFlags: " + error);
                reject(error);
            });
    });
}

/**
 * Returns requested job by id
 * @param {integer} jobId job Id
 * @returns job object
 */
getJob = function (jobId) {
    return jobsList.find(element => element.jobId == jobId);
};

/**
 * Returns jobs
 * @returns List with all jobs
 */
getJobs = function () {
    return jobsList;
};

/**
 * Adds new job to the job list
 * @param {integer} jobId job Id
 * @param {string} request request type
 * @param {string} param param
 */
addJob = function (jobId, request, param) {
    Flags.getFlags()
        .then(function (flags) {
            // remove needToProcess field, so later we can compare jobs (and if the job started it will have this field modified so new job will be creted for the same task)
            flags.forEach(function (v) { delete v.needToProcess });
            var job = {
                path: "",
                jobId: jobId,
                name: "CM Update",
                "job-state": jobStates.INQUEUE,
                "time-created": new Date(),
                "time-completed": -1,
                "time-to-autoremove-job": -1,
                request: request,
                param: param,
                autoremove: false,
                flags_id: flags
            }
            jobsList.push(job);
        })
        .catch(function (error) {
            console.log("<JobsQueue> ERROR addJob.Flags.getFlags: " + error)
        });
};

/**
 * Removes job by id
 */
removeJob = function (jobId) {
    var job = jobsList.find(element => element.jobId == jobId);
    if (job != undefined) { //if still not removed removed by timeout
        console.log(`<JobsQueue> removing job => ${jobId}`);
        const index = jobsList.indexOf(job);
        if (index > -1) { // only splice array when item is found
            jobsList.splice(index, 1); // 2nd parameter means remove one item only
        }
    }
};

// removeJobWithTimeout = removeTimeout = function (jobId, seconds) {
//     // if (!getJob(jobId).autoremove) {
//     // getJob(jobId).autoremove = true;
//     // setTimeout(() => {
//     //     // console.log(`<JobsQueue> auto-removing job => ${jobId}`);
//     //     try {
//     //         removeJob(jobId)
//     //     } catch (error) {
//     //         console.log(error)
//     //     }
//     // }, seconds * 1000, jobId, jobsList);
//     // }

// }


/**
 * Generates non-repeating random 4-digit job id
 * @returns id
 */
generateId = function (jobId) {
    var id = 0;
    var ok = false;
    while (!ok) {
        id = Math.floor(
            Math.random() * (9999 - 1000) + 1000
        );
        if (jobsList.find(element => element.jobId == jobId) == null)
            ok = true;
    }
    return id;
};

exports.jobStates = jobStates;
exports.timeoutAfterCompletion = timeoutAfterCompletion;
exports.advanceState = advanceState;
exports.startJobManager = startJobManager;
exports.createJob = createJob;
// exports.findExistingJob = findExistingJob;
exports.getJob = getJob;
exports.getJobs = getJobs
exports.addJob = addJob;
exports.removeJob = removeJob;
exports.generateId = generateId;


