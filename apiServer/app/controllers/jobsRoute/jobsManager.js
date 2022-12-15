/**
 * Jobs queue manager.
 * Contains a list with jobs, and basic CRUD operations. Used to add, remove and read for specific job
 */

const Flags = require('../../service/FlagsService.js');
var post = require('./postUpdateCM');

var jobsList = []

var jobPrefix = "/v1.1/jobs/";

jobTemplate = {
    "job": {
        "path": "xxx",                  // path to id
        "jobId": "xx",                  // id
        "name": "CM Update",            // request type
        "job-state": "STARTED",         // INQUEUE,     STARTED,    COMPLETED 
        "job-status": "INPROGRESS",     // INQUEUE,     INPROGRESS, SUCCESS/ERROR -- state=completed -> status=SUCCESS/ERROR
        "start-time": "",               // new Date
        "time-to-autoremove-job": "",   // timeleft
        "data": {}                      // data
    }
}


/*
    Main loop
*/
startJobManager = function () {
    // repeat 
    setInterval(function () {
        checkAndStartNewJob();
        autoremoveJobs();
    }, 2000);
};


advanceState = function (job) {
    if (job["job-state"] == "INQUEUE") {
        job["job-state"] = "STARTED";
        job["job-status"] = "INPROGRESS";
    }
    else if (job["job-state"] == "STARTED") {
        job["job-state"] = "COMPLETED";
        job["job-status"] = "SUCCESS";
    }
    // else{
    //     throw 'Incorrect use of "advanceState()" function';
    // }
}

checkAndStartNewJob = function () {
    return new Promise(function (resolve, reject) {
        Flags.getFlags()
            .then(function (flags) {
                if (flags != null) {
                    // check if CM is updating
                    var updatesNow = false;
                    flags.forEach(flag => {
                        if (!flag["needToprocess"])
                            updatesNow = true;
                    });
                    
                    // find first job that need an update
                    var jobToUpdate = jobsList.find(job => (job["job-state"] == "INQUEUE" && job["job-status"] == "INQUEUE"));
                    console.log(jobToUpdate);
                    
                    if (!updatesNow && jobToUpdate != undefined) {
                        post.update_CM(jobToUpdate["param"]);
                        advanceState(jobToUpdate);
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


autoremoveJobs = function () {
    // if actualtime > timecreation+livetime then remove job
};


/**
 * Returns a path for an existing or a new job.
 * jobPath 
 */
createJob = function (param, requestTypeName) {
    return new Promise(function (resolve, reject) {
        findExistingJob(param, requestTypeName)
            .then(function (existingJob) {
                console.log(existingJob)
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
 */
findExistingJob = function (param, requestTypeName) {
    return new Promise(function (resolve, reject) {
        Flags.getFlags()
            .then(function (flags) {
                var job = null;
                console.log(flags)
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
 */
getJob = function (jobId) {
    return jobsList.find(element => element.jobId == jobId);
};

/**
 * Returns jobs
 */
getJobs = function () {
    return jobsList;
};

/**
 * Adds new job to the job list
 */
addJob = function (jobId, request, param) {
    Flags.getFlags()
        .then(function (data) {

            // data.forEach(element => {

            // });

            var job = {
                path: "",
                jobId: jobId,
                name: "CM Update",
                "job-state": "INQUEUE",
                "job-status": "INQUEUE",
                "start-time": new Date(),
                "time-to-autoremove-job": "",
                request: request,
                param: param,
                autoremove: false,
                flags_id: data
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

removeJobWithTimeout = removeTimeout = function (jobId, seconds) {
    // if (!getJob(jobId).autoremove) {
    // getJob(jobId).autoremove = true;
    // setTimeout(() => {
    //     // console.log(`<JobsQueue> auto-removing job => ${jobId}`);
    //     try {
    //         removeJob(jobId)
    //     } catch (error) {
    //         console.log(error)
    //     }
    // }, seconds * 1000, jobId, jobsList);
    // }

}


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


exports.advanceState = advanceState;
exports.startJobManager = startJobManager;
exports.createJob = createJob;
// exports.findExistingJob = findExistingJob;
exports.getJob = getJob;
exports.getJobs = getJobs
exports.addJob = addJob;
exports.removeJob = removeJob;
exports.removeJobWithTimeout = removeJobWithTimeout;
exports.generateId = generateId;


