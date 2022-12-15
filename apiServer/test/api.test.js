const request = require('supertest');
const assert = require('assert');
let app = {};
beforeAll(()=>{
    return new Promise(function(resolve, reject) {
        const server = require("../app/server.js");
        if (!server) {
            console.error("Unable to load server");    
        }
        else {
            app = server.test((theApp)=> {
                app =theApp;
                resolve();
            }).catch(console.error);
        }
    });
});


describe ("Test communities endpoint", ()=>{
    test ("GET /communities", (done)=>{
        request(app)
            .get('/communities')
            .expect('Content-Type', /json/)
            .expect(200)
            .end(function(err, res) {
                if (err) done(err);
                else done();
            });
    });
    test ("GET /communities/{id}/users", (done)=>{
        request(app)
            .get('/communities/621e53cf0aa6aa7517c2afdd/users')
            .expect('Content-Type', /json/)
            .expect(200)
            .end(function(err, res) {
                if (err) done(err);
                else done();
            });
    });
    test ("GET /communities/BAD_id/users", (done)=>{
        request(app)
            .get('/communities/wrongId/users')
            .expect(400)
            .end(function(err, res) {
                if (err) done(err);
                else done();
            });
    });
    test ("GET /communities/{id}", (done)=>{
        request(app)
            .get('/communities/621e53cf0aa6aa7517c2afdd/users')
            .expect('Content-Type', /json/)
            .expect(200)
            .end(function(err, res) {
                if (err) done(err);
                else done();
            });
    });
    test ("GET /communities/BAD_id", (done)=>{
        request(app)
            .get('/communities/wrongId')
            .expect(400)
            .end(function(err, res) {
                if (err) done(err);
                else done();
            });
    });
});

describe ("Test users endpoint", ()=>{
    test ("GET /users/{userId}/communities", (done)=>{
        request(app)
            .get('/users/23/communities')
            .expect('Content-Type', /json/)
            .expect(200)
            .end(function(err, res) {
                if (err) done(err);
                else done();
            });
    });
    test ("GET /users/{BADUSERID}/communities", (done)=>{
        request(app)
            .get('/users/BADUSERID/communities')
            .expect(400)
            .end(function(err, res) {
                if (err) done(err);
                else done();
            });
    });
    test ("POST /users/update-generated-content", (done)=>{
        request(app)
            .post('/users/update-generated-content')
            .set('Content-Type', 'application/json')
            .send('["21","22"]')
            .expect(204)
            .end(function(err, res) {
                if (err) done(err);
                else done();
            });
    });

    test ("POST /users/update-generated-content NO_BODY", (done)=>{
        request(app)
            .post('/users/update-generated-content')
            .set('Content-Type', 'application/json')
            .expect(400)
            .end(function(err, res) {
                if (err) done(err);
                else done();
            });
    });
});

describe ("Test similarity endpoint", ()=>{
    test ("GET /communities/{communityId}/similarity", (done)=>{
        request(app)
            .get('/communities/821e53cf0aa6aa7517c2afdd/similarity')
            .query({ k: '2' })
            .expect('Content-Type', /json/)
            .expect(200)
            .end(function(err, res) {
                if (err) done(err);
                else done();
            });
    });
    test ("GET /communities/{communityId}/similarity NO QUERY PARAMETER", (done)=>{
        request(app)
            .get('/communities/821e53cf0aa6aa7517c2afdd/similarity')
            .expect(400)
            .end(function(err, res) {
                if (err) done(err);
                else done();
            });
    });
    test ("GET /communities/{BADCOMMUNITYID}/similarity", (done)=>{
        request(app)
            .get('/communities/badId/similarity')
            .query({ k: '2' })
            .expect(400)
            .end(function(err, res) {
                if (err) done(err);
                else done();
            });
    });
    test ("GET /communities/{communityId}/similarity/{otherCommunityId}", (done)=>{
        request(app)
            .get('/communities/821e53cf0aa6aa7517c2afdd/similarity/821e53cf0aa6aa7517c2afdd')
            .expect('Content-Type', /json/)
            .expect(200)
            .end(function(err, res) {
                if (err) done(err);
                else done();
            });
    });

    test ("GET /communities/BADCOMMUNITYID/similarity/{otherCommunityId}", (done)=>{
        request(app)
            .get('/communities/badid/similarity/821e53cf0aa6aa7517c2afdd')
            .expect(400)
            .end(function(err, res) {
                if (err) return done(err);
                return done();
            });
    });

    test ("GET /communities/{communityId}/similarity/BADCOMMUNITYID", (done)=>{
        request(app)
            .get('/communities/821e53cf0aa6aa7517c2afdd/similarity/badId')
            .expect(400)
            .end(function(err, res) {
                if (err) done(err);
                else done();
            });
    });

    test ("GET /communities/SAME-ID/similarity/SAME-ID", (done)=>{
        request(app)
            .get('/communities/821e53cf0aa6aa7517c2afdd/similarity/821e53cf0aa6aa7517c2afdd')
            .expect(200)
            .expect('Content-Type', /json/)
            .then(res => {
                // sim(x,x) = 1
                expect(res.body.value).toBe(1.0);
                done();
            })
            .catch(function(err, res) {
                if (err) done(err);
            });
    });
});

describe ("Test dissimilarity endpoint", ()=>{
    test ("GET /communities/{communityId}/dissimilarity", (done)=>{
        request(app)
            .get('/communities/821e53cf0aa6aa7517c2afdd/dissimilarity')
            .query({ k: '2' })
            .expect('Content-Type', /json/)
            .expect(200)
            .end(function(err, res) {
                if (err) done(err);
                else done();
            });
    });
    test ("GET /communities/{communityId}/dissimilarity NO QUERY PARAMETER", (done)=>{
        request(app)
            .get('/communities/821e53cf0aa6aa7517c2afdd/dissimilarity')
            .expect(400)
            .end(function(err, res) {
                if (err) done(err);
                else done();
            });
    });
    test ("GET /communities/{BADCOMMUNITYID}/dissimilarity", (done)=>{
        request(app)
            .get('/communities/badId/dissimilarity')
            .query({ k: '2' })
            .expect(400)
            .end(function(err, res) {
                if (err) done(err);
                else done();
            });
    });
    test ("GET /communities/{communityId}/dissimilarity/{otherCommunityId}", (done)=>{
        request(app)
            .get('/communities/821e53cf0aa6aa7517c2afdd/dissimilarity/821e53cf0aa6aa7517c2afdd')
            .expect('Content-Type', /json/)
            .expect(200)
            .end(function(err, res) {
                if (err) done(err);
                else done();
            });
    });

    test ("GET /communities/BADCOMMUNITYID/dissimilarity/{otherCommunityId}", (done)=>{
        request(app)
            .get('/communities/badid/dissimilarity/821e53cf0aa6aa7517c2afdd')
            .expect(400)
            .end(function(err, res) {
                if (err) return done(err);
                return done();
            });
    });

    test ("GET /communities/{communityId}/dissimilarity/BADCOMMUNITYID", (done)=>{
        request(app)
            .get('/communities/821e53cf0aa6aa7517c2afdd/dissimilarity/badId')
            .expect(400)
            .end(function(err, res) {
                if (err) done(err);
                else done();
            });
    });

    test ("GET /communities/SAME-ID/dissimilarity/SAME-ID", (done)=>{
        request(app)
            .get('/communities/821e53cf0aa6aa7517c2afdd/dissimilarity/821e53cf0aa6aa7517c2afdd')
            .expect(200)
            .expect('Content-Type', /json/)
            .then(res => {
                // dissim(x,x) = 0
                expect(res.body.value).toBe(0);
                done();
            })
            .catch(function(err, res) {
                if (err) done(err);
            });
    });
});
