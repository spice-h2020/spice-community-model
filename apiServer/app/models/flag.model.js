module.exports = mongoose => {
  var schema = mongoose.Schema(
    {
      perspectiveId: String,
      userid: String,
      needToprocess: Boolean
    }
  );

  schema.method("toJSON", function () {
    const { __v, _id, ...object } = this.toObject();
    // object.id = _id.toString();
    return object;
  });

  const Flags = mongoose.model("Flags", schema);

  // Access mongobd and retrieve requested flag
  return {
    insertFlag: function (data, onSuccess, onError) {
      // console.log(json);
      Flags.create(data, function (err, res) {
        if (err) {
          console.log("insertFlag: error");
          onError("insertFlag:" + user);
        }
        else {
          onSuccess(res._id.toString());
        }
      });
    },
    checkFlag: function (onSuccess, onError) {
      Flags.find({}, function (error, data) {
        // var res = JSON.stringify(data)
        if (error) {
          onError("checkFlag:" + error);
        } else {
          if (Object.keys(data).length > 0) {
            // console.log(data.toJSON())
            onSuccess(data);
          }
          else {
            onSuccess(null);
          }
        }
      });
    },
    checkFlagById: function (id, onSuccess, onError) {
      // console.log("id " + id)
      Flags.findOne({ "perspectiveId": id }, { projection: { _id: 0 } }, function (error, data) {
        if (error) {
          console.log("errorHere")
          onError("checkFlagById:" + error);
        } else {
          if (data) {
            console.log(data.toJSON())
            onSuccess(data.toJSON());
          }
          else {
            onSuccess(null);
          }
        }
      });
    }
  };
};

