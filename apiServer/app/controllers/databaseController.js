'use strict';
const DatabaseContrl = require('../service/DatabaseControllerService');

var express = require('express');
var router = express.Router();


/**
    http://localhost:8080/databaseController/dump
   */

router.get('/dump', function (req, res, next) {
    DatabaseContrl.getDump()
        .then(function (response) {
            res.status(200).send(response);
        })
        .catch(function (response) {
            res.status(400).send(response);
        });
});

/**
router.post('/load', function (req, res, next) {
    DatabaseContrl.postLoad(req.body)
        .then(function (response) {
            res.status(200).send(response);
        })
        .catch(function (response) {
            res.status(400).send(response);
        });
});
**/


module.exports = router;