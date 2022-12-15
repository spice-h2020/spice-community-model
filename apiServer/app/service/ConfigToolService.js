'use strict';
const db = require("../models");

const InteractionData = db.interactionData;
const FlagDAO = db.flag;


/**
 * Obsolete 
 */

// exports.getSeed = function () {
//     return new Promise(function (resolve, reject) {
//         try {

//             const http = require('http');
//             // Sample URL

//             const options = {
//                 // hostname: '172.20.0.4',
//                 host: '172.20.0.4',
//                 port: process.env.CM_DOCKER_PORT || 8090,
//                 path: "/seed",
//                 method: 'GET',
//                 headers: {
//                     'Content-Type': 'application/json',
//                     'Content-Length': 0,
//                 },
//             };

//             const request = http.request(options, (response) => {
//                 let data = '';
//                 response.on('data', (chunk) => {
//                     data = data + chunk.toString();
//                 });

//                 response.on('end', () => {
//                     const body = JSON.parse(data);
//                     console.log(body);
//                     resolve(body)
//                 });
//             })

//             request.on('error', (error) => {
//                 console.log('An error', error);
//                 reject(error)
//             });

//             request.end()
//         } catch (error) {
//             console.log(error)
//             reject(error)
//         }
//     });
// };