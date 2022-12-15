const Similarity = require('../service/SimilarityService.js');

const idParam = 'communityId';
const otherIdParam = 'otherCommunityId';

module.exports.computeDissimilarity = function computeDissimilarity (req, res, next) {
  const communityId = req.params[idParam];
  const otherCommunityId = req.params[otherIdParam];
  Similarity.computeDissimilarity(communityId, otherCommunityId)
    .then(function (response) {
      res.send(response);
    })
    .catch(function (response) {
      res.status(400).send("Invalid communityIds (target or other)");
    });
};

module.exports.computeKmostDissimilar = function computeKmostDissimilar (req, res, next) {
  const communityId = req.params[idParam];
  const k = req.query['k'];
  Similarity.computeKmostDissimilar(communityId, k)
    .then(function (response) {
      res.send(response);
    })
    .catch(function (response) {
      res.status(400).send("Invalid communityId or query parameters");
    });
};

module.exports.computeKmostSimilar = function computeKmostSimilar (req, res, next) {
  const communityId = req.params[idParam];
  const k = req.query['k'];
  Similarity.computeKmostSimilar(communityId, k)
    .then(function (response) {
      res.send(response);
    })
    .catch(function (response) {
      res.status(400).send("Invalid communityId or query parameters");
    });
};

module.exports.computeSimilarity = function computeSimilarity (req, res, next) {
  const communityId = req.params[idParam];
  const otherCommunityId = req.params[otherIdParam];
  Similarity.computeSimilarity(communityId, otherCommunityId)
    .then(function (response) {
      res.send(response);
    })
    .catch(function (response) {
      res.status(400).send("Invalid communityIds (target or other)");
    });
};
