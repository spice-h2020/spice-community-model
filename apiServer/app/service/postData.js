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
        let url = "http://cm:" + port + path;

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
    }
};