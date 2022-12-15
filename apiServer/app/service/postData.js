// postUpdateCM.js
// ========
/**
 * Sends a POST request to api_loader.py to update CM clustering 
 */

// const http = require('http');
const axios = require('axios');

const { resolve } = require('path');

module.exports = {
    post_data: function (body, path) {
        var data = JSON.stringify(body)

        let port = process.env.CM_DOCKER_PORT || 8090;
        let url = "http://172.20.1.4:" + port + path;



        return new Promise((resolve, reject) => {
            try {

                axios.post(url, data)
                    .then((response) => {
                        // console.log("data: "+ response.data);
                        // console.log("status: " + response.status);
                        // console.log("statusText: "+ response.statusText);
                        resolve(body);
                    })
                    .catch((error) => {
                        console.log("post_data.Promise.axios.post: " + error)
                        reject("post_data.Promise.axios.post: " + error);
                    });


            } catch (error) {
                console.log("post_data.Promise.axios:" + error)
                reject("post_data.Promise.axios:" + error);
            }
        })

        // var data = JSON.stringify(body)
        // const options = {
        //     // hostname: '172.20.1.4',
        //     host: '172.20.1.4',
        //     port: process.env.CM_DOCKER_PORT || 8090,
        //     path: path,
        //     method: 'POST',
        //     headers: {
        //         'Content-Type': 'application/json',
        //         'Content-Length': data.length,
        //     },
        // };

        // return new Promise((resolve, reject) => {
        //     const req = http.request(options, (res) => {
        //         res.on('data', (d) => {
        //             process.stdout.write(d);
        //         });

        //         res.on('end', () => {
        //             if (res.statusCode == 204) {
        //                 console.log(' post_data success')
        //                 resolve(body);
        //             }
        //             else {
        //                 console.log(' post_data failed')
        //                 resolve(body);
        //             }
        //         });
        //         res.on('error', () => {
        //             console.log('error');
        //             reject(Error('HTTP call failed'));
        //         });
        //     });

        //     req.write(data);
        //     req.end();
        // })
    }
};