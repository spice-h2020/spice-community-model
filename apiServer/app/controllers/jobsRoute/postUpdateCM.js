// postUpdateCM.js
// ========
/**
 * Sends a POST request to api_loader.py to update CM clustering 
 */



const http = require('http');

function oldPost(data = "empty") {

  const options = {
    host: '172.20.1.4',
    port: process.env.CM_DOCKER_PORT || 8090,
    path: '/update_CM',
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Content-Length': data.length,
    },
  };
  const req = http.request(options, res => {

    res.on('data', d => {
      // console.log(req.status)
      if (req.status != 102) {
        process.stdout.write(d);
        // console.log(`BODY: ${d}`);
      }
    });

    res.on('end', () => {
      // console.log("_end_");
    })

    var myStatus = req.status;
    if (myStatus >= 400) {
      req.on('error', (err) => {
        console.error(err);
      })
    }
    else if (myStatus == 102) {
      // console.log("Received 102 Processing Status Code. Waiting...");
    }
    else if (myStatus == 200) {
      // console.log("Received 200. OK.");
    }
  });

  req.write(data);
  req.end();

  req.on('error', (err) => {
    console.error("error");
    console.error(err);
  })
}


module.exports = {
  update_CM: function (data) {
    if (data == 0) data = "0";
    console.log("postData: " + data);
    oldPost(data);
  }
};