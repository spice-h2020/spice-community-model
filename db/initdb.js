let spiceUser = _getEnv('MONGODB_USER');
let spicePwd = _getEnv('MONGODB_PASSWORD');
let dbName = _getEnv('MONGO_INITDB_DATABASE');
db = new Mongo().getDB(dbName);
print("Connected to " + db.getName());

db.createUser({
  user: spiceUser,
  pwd: spicePwd,
  roles: [
    {
      role: 'readWrite',
      db: db.getName()
    }
  ]
});

db.createCollection('users', { capped: false });
db.users.deleteMany({});

db.createCollection('perspectives', { capped: false });
db.perspectives.deleteMany({});

db.perspectives.insertMany([
{
  "id": "1000-agglomerative",
  "name": "HEHCT Perspective (agglomerative)",
  "algorithm": {
    "name": "agglomerative",
    "params": [
    ]
  },
  "similarity_functions": [
    {
      "sim_function": {
        "name": "TableSimilarityDAO",
        "params": [
        ],
        "on_attribute": {
          "att_name": "beliefR",
          "att_type": "String"
        },
        "weight": 0.5
      }
    },
    {
      "sim_function": {
        "name": "TableSimilarityDAO",
        "params": [
        ],
        "on_attribute": {
          "att_name": "beliefJ",
          "att_type": "String"
        },
        "weight": 0.3
      }
    },
    {
      "sim_function": {
        "name": "TableSimilarityDAO",
        "params": [
        ],
        "on_attribute": {
          "att_name": "beliefE",
          "att_type": "String"
        },
        "weight": 0.2
      }
    }
  ],
  "user_attributes": [
    {
        "att_name": "DemographicsReligous",
        "att_type": "String"
    },
    {
        "att_name": "DemographicsPolitics",
        "att_type": "String"
    }
  ],
  "interaction_similarity_functions": []
}
]);

db.createCollection('communitiesVisualization', { capped: false });
db.communitiesVisualization.deleteMany({});

db.createCollection('communities', { capped: false });
db.communities.deleteMany({});

db.createCollection('similarities', { capped: false });
db.similarities.deleteMany({});

db.createCollection('flags', { capped: false });
db.flags.deleteMany({});
// db.flags.insertOne({ "flag" : true});


db.createCollection('distanceMatrixes', { capped: false });
db.distanceMatrixes.deleteMany({});



