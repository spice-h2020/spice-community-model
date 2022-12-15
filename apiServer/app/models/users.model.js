

module.exports = mongoose => {
  var schema = mongoose.Schema(
    {
      "id": String,
      "userid": String,
      "origin": String,
      "source_id": String,
      "source": String,
      "pname": String,
      "pvalue": String,
      "context": String,
      "datapoints": Number
    }, {
    versionKey: false // Para que no se anyada el campo "__v"
  });

  schema.method("toJSON", function () {
    const { __v, _id, ...object } = this.toObject();
    object.id = _id.toString();
    return object;
  });

  const Users = mongoose.model("Users", schema);

  return {
    all: function (onSuccess) {
      let items = [];
      Users.find({}, { projection: { _id: 0 } }, function (error, data) {
        let i = 0;
        data.forEach(element => {
          items[i] = element.toJSON();
          i++;
        });
        onSuccess(items);
      });
    },
    update: function (user, onSuccess, onError) {
      
    }
  };
};


/// Add user directly into mongoDB:
//
// const Users = mongoose.model("Users", schema);
//
// users.forEach(function (user) {
//     // console.log(typeof user);
//     var json = JSON.parse(JSON.stringify(user));
//     // console.log(json);
//     Users.updateOne({ userid: json["userid"], pname: json["pname"] }, user, { upsert: true }, function (err, res) {
//         if (err) {
//             console.log("updateOne: error");
//             onError(user);
//         }
//     });
// });
// onSuccess("");