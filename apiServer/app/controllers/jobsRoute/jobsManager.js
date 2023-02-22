/**
 * Jobs queue manager.
 * Contains a list with jobs, and basic CRUD operations. Used to add, remove and read for specific job
 */

const Flags = require('../../service/FlagsService.js');
var redirect = require('../../service/redirectRequest.js');

var jobsList = []

var jobPrefix = "/v1.1/jobs/";

// time: minutes*60*1000=ms
export var timeoutAfterCompletion = 30 * 60 * 1000;

// job states
export const jobStates = {
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
export function startJobManager() {
    // repeat 
    setInterval(function () {
        checkAndStartNewJob();
        autoremoveJobs();
    }, 2000);
};

/**
 * Advance state of the job
 * @param {object} job job
 * {job-state} -> {job-state}
 * INQUEUE,    -> STARTED,
 * STARTED,    -> COMPLETED 
 */
function advanceState(job) {
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
/**
 * Set job to error state and remove the flag with error from mongoDB
 * @param {JSON} flag flag that contains the error
 * @param {String} errorMsg error message
 */
function setJobToErrorState(flag, errorMsg) {
    // create copy of the flag and preprocess the flag before comparing 
    var flagWithError = JSON.parse(JSON.stringify(flag["_id"]));

    // find the failed job and set the state to ERROR. remove flag that contains the error 
    jobsList.forEach(elem => {
        elem["flags_id"].forEach(elemFlag => {
            if ((JSON.stringify(elemFlag) == JSON.stringify(flagWithError))) {
                elem["job-state"] = jobStates.ERROR;
                elem["request"] = "error";
                elem["param"] = errorMsg;
                elem["time-completed"] = new Date();
                Flags.removeFlag(flag["_id"]);
            }
        })
    });
}

/**
 * Check flags and if CM is not updating then find the first job in the queue. Update CM with that job and advance the state of the job.
 */
function checkAndStartNewJob() {
    return new Promise(function (resolve, reject) {
        var cmState = "idle";

        // Check flags
        Flags.getFlags("withErrors")
            .then(function (flags) {
                if (flags == null) {
                    flags = []
                }

                // Iterate flags, check if CM is updating and if there are flags with errors
                flags.forEach(flag => {
                    //check for jobs with errors
                    if (flag["error"] != "N/D") {
                        // cmState = "error";
                        var errorMsg = flag["error"];
                        setJobToErrorState(flag, errorMsg)
                    }

                    if (!flag["needToProcess"] && flag["error"] == "N/D")
                        cmState = "updating";

                });

                // check for finished jobs. checking for flags from certain jobs in mongodb  
                jobsList.forEach(job => {
                    if (job["job-state"] == jobStates.STARTED) {
                        var finished = true;
                        for (let jobflag of job["flags_id"]) {
                            for (let flag of flags) {
                                if (JSON.stringify(jobflag) == JSON.stringify(flag["_id"])) {
                                    finished = false;
                                }
                                if (!finished)
                                    break;
                            }
                            if (!finished)
                                break;
                        }
                        if (finished) {
                            advanceState(job);
                        }
                    }
                });
                // console.log(jobsList)

                // Find first job that need an update
                var jobToUpdate = jobsList.find(job => (job["job-state"] == jobStates.INQUEUE));

                // If cm is not updating and there are jobs to update, then update cm and advance that job state from queue to started
                if (cmState == "idle" && jobToUpdate != undefined) {
                    redirect.postData(jobToUpdate["param"], "/update_CM")
                    advanceState(jobToUpdate);
                }

                console.log("CM State: " + cmState);

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
function autoremoveJobs() {
    // for in jobs
    // if actualtime > timeCompleted+livetime => then remove job
    var actualTime = new Date().getTime();
    jobsList.forEach(job => {
        if (job["job-state"] == jobStates.COMPLETED || job["job-state"] == jobStates.ERROR) {
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
export function createJob(param, requestTypeName) {
    return new Promise(function (resolve, reject) {
        findExistingJob(param, requestTypeName)
            .then(function (existingJob) {
                if (existingJob == null) {
                    var jobId = generateId()
                    console.log("<JobsQueue> created new job")
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
function findExistingJob(param, requestTypeName) {
    return new Promise(function (resolve, reject) {
        Flags.getFlags()
            .then(function (flags) {
                var job = null;
                // remove needToProcess field to compare even if the job has started

                let flags_id = flags.map(a => a._id);

                jobsList.forEach(elem => {
                    if (elem["request"] == requestTypeName && elem["param"] == param) {
                        if (JSON.stringify(elem["flags_id"]) == JSON.stringify(flags_id)) {
                            job = elem;
                        }
                    }
                });
                resolve(job);
            })
            .catch(function (error) {
                console.log("<JobsQueue> ERROR findExistingJob.Flags.getFlags: " + error);
                reject(error);
            });
    });
}

/**
 * Returns requested job by id
 * @param {integer} jobId job Id
 * @returns job object
 */
export function getJob(jobId) {
    return jobsList.find(element => element.jobId == jobId);
};

/**
 * Returns jobs
 * @returns List with all jobs
 */
export function getJobs() {
    return jobsList;
};

/**
 * Adds new job to the job list
 * @param {integer} jobId job Id
 * @param {string} request request type
 * @param {string} param param
 */
function addJob(jobId, request, param) {
    Flags.getFlags()
        .then(function (flags) {

            var flags_id = flags.map(a => a._id);

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
                flags_id: flags_id
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
function removeJob(jobId) {
    var job = jobsList.find(element => element.jobId == jobId);
    if (job != undefined) { //if still not removed removed by timeout
        console.log(`<JobsQueue> removing job => ${jobId}`);
        const index = jobsList.indexOf(job);
        if (index > -1) { // only splice array when item is found
            jobsList.splice(index, 1); // 2nd parameter means remove one item only
        }
    }
};


/**
 * Generates non-repeating random 4-digit job id
 * @returns id
 */
function generateId(jobId) {
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





