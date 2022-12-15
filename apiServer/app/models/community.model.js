module.exports = mongoose => {
  var schema = mongoose.Schema(
    {
      id: String,
      name: String,
      "explanations": [{
        _id: false,
        "explanation_type": String,
        "explanation_data": { type: mongoose.Mixed, default: {} },
        "visible": Boolean
      }],
      perspectiveId: String,
      users: [String]
    }, { minimize: false }
  );

  schema.method("toJSON", function () {
    const { __v, _id, ...object } = this.toObject();
    // object.id = _id.toString();
    return object;
  });
  
  const Communities = mongoose.model("Communities", schema);
  
  // Access mongobd and retrieve requested data
  return {
    all: function (onSuccess) {
      let items = [];
      Communities.find({}, { projection: { _id: 0 } }, function (error, data) {
        let i = 0;
        data.forEach(element => {
          items[i] = element.toJSON();
          i++;
        });
        onSuccess(items);
      });
    },
    getById: function (id, onSuccess, onError) {
      Communities.findOne({ id: id }, { projection: { _id: 0 } }, function (error, data) {
        if (error) {
          onError(error);
        } else {
          if (data) {
            onSuccess(data.toJSON());
          }
          else {
            onError(id);
          }
        }
      });
    },
    allWithUserId: function (userId, onSuccess, onError) {
      let items = [];
      Communities.find({ users: userId }, { projection: { _id: 0 } }, function (error, data) {
        if (data.length > 0) {
          let i = 0;
          data.forEach(element => {
            items[i] = element.toJSON();
            i++;
          });
          onSuccess(items);
        }
        else {
          onError(userId);
        }
      });
    }
  };
};
