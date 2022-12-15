const server = require("./app/server.js");
if (server) {
    server.run().catch(console.error);
}
else {
    console.error("Unable to load server");
}