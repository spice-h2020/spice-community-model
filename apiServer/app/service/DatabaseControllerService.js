'use strict';
const http = require('http');

var postData = require('./postData.js');


exports.getDump = function () {
    return new Promise(function (resolve, reject) {
        try {
            const options = {
                host: 'cm',
                port: process.env.CM_DOCKER_PORT || 8090,
                path: '/dump',
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Content-Length': 0,
                },
            };

            const request = http.request(options, (response) => {
                let data = '';
                response.on('data', (chunk) => {
                    data = data + chunk.toString();
                });

                response.on('end', () => {
                    const body = JSON.parse(data);
                    // console.log(body);
                    resolve(body)
                });
            })

            request.on('error', (error) => {
                console.log('An error', error);
                reject(error)
            });

            request.end()
        } catch (error) {
            console.log("databaseControllerService.dump error:" + error)
            reject(error)
        }
    })
}


/**
 * Redirect post request to CM model to load data into mongoDB
 */
exports.postLoad = function (body) {
    return postData.post_data(body, "/load");

}