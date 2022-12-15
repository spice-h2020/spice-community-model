'use strict';
const mongoose = require("mongoose");
const http = require('http');

var postData = require('./postData.js');
const db = require("../models");
const DatabaseModelDAO = db.DatabaseModelDAO;


exports.getDump = function () {
    return new Promise(function (resolve, reject) {
        try {
            const options = {
                host: '172.20.1.4',
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



exports.postLoad = function (body) {
    // return new Promise(function (resolve, reject) {
    //     try {
           return postData.post_data(body, "/load");
            // const db = mongoose.connection.db;
            // // Get all collections
            // new Promise(function (resolve, reject) {
            //     var collections = db.listCollections().toArray();
            //     collections
            //         .map((collection) => collection.name)
            //         .forEach(async (collectionName) => {
            //             db.dropCollection(collectionName);
            //         });
            //     resolve(collections)
            // })
            //     .then((collections) => {
            //         // Create an array of collection names and drop each collection
            //         console.log(1)
            //         var schema = mongoose.Schema({ any: {} });
            //         console.log(2)
            //         new Promise(function (resolve, reject) {
            //             for (const coll in body) {
            //                 // console.log(body[coll]);
            //                 console.log(coll)
            //                 console.log(3)
            //                 try {
            //                     const model = mongoose.model("communitiesVisualization", schema, "communitiesVisualization");
            //                 } catch (error) {
            //                     console.log("aaaaaaaaaaaa:" + error)
            //                 }
            //                 console.log(4)
            //                 // for (const e in body[coll]) {
            //                 //     // console.log("  " + body[coll][e]);
            //                 //     model.create(body[coll][e], function (err, res) {
            //                 //         if (err) {
            //                 //             console.log("insert: error: " + body[coll][e]);
            //                 //             // onError(user);
            //                 //         }
            //                 //         else {
            //                 //             // onSuccess(res._id.toString());
            //                 //         }
            //                 //     });
            //                 // }
            //             }
            //             resolve();
            //         })
            //             .then((collections) => {

            //             });
            //         resolve()
            //     });
            // resolve()
    //     } catch (error) {
    //         console.log("databaseControllerService.dump error:" + error)
    //         reject(error)
    //     }
    // })
}