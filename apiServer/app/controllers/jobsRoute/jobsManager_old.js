/**
 * Jobs queue manager.
 * Contains a list with jobs, and basic CRUD operations. Used to add, remove and read for specific job
 */

const Flags = require('../../service/FlagsService.js');

var jobsList = []

/**
 * Returns a boolean and a jobPath. A path for an existing or a new job.
 * [Boolean, jobPath] 
 * Boolean = existence of the same job
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
                    var path = "/v1.1/jobs/" + jobId
                    var data = {
                        "path": path
                    }
                    resolve([false, data]);
                }
                else {
                    var path = "/v1.1/jobs/" + existingJob["jobId"]
                    var data = {
                        "path": path
                    }
                    resolve([true, data]);
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
                    if (elem["request"] == requestTypeName && elem["param"] == param && JSON.stringify(elem["flags_id"]) == JSON.stringify(flags)) {
                        job = elem;
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
            
            data.forEach(element => {
                
            });
            var job = {
                jobId: jobId,
                request: request,
                param: param,
                "start-time": new Date(),
                autoremove: false,
                flags_id: data
            }
            jobsList.push(job);

            removeJobWithTimeout(jobId, 60 * 30); // 30 min = 60 * 30
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
    getJob(jobId).autoremove = true;
    setTimeout(() => {
        // console.log(`<JobsQueue> auto-removing job => ${jobId}`);
        try {
            removeJob(jobId)
        } catch (error) {
            console.log(error)
        }
    }, seconds * 1000, jobId, jobsList);
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



exports.createJob = createJob;
// exports.findExistingJob = findExistingJob;
exports.getJob = getJob;
exports.getJobs = getJobs
exports.addJob = addJob;
exports.removeJob = removeJob;
exports.removeJobWithTimeout = removeJobWithTimeout;
exports.generateId = generateId;



// Refactoring for future

/*

var map = {};

map[Date.now()] = ['a', 'b'];
console.log(map);

setTimeout(function() {
  map[Date.now()] = ['c', 'd'];
  console.log(map);
}, 5000);

setInterval(function() {
  var times = Object.keys(map);
  
  times.forEach(function(time) {
    if(Date.now() > (+time + 14000)) {
      delete map[time];
    }
  });
  
  console.log(map);
}, 1000);

*/