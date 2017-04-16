const Utils = {
  JsonPost (submitUrl, json, callback){

    var self = this;

    var req = new XMLHttpRequest();
    var return_object = {'error': null, 'data': null}
    req.overrideMimeType("application/json");
    req.open("POST", submitUrl,  true);
    req.setRequestHeader("Content-Type", "application/json");

    req.onload = function (e) {
      if (req.readyState === 4) {
        if (req.status === 200) {
          return_object.data = req.responseText;
          callback(return_object);
        } else {
          console.error(req.statusText);
          return_object.error = req.statusText;
          callback(return_object);
        }
      }
    }

    req.onerror = function (e) {
      return_object.error = req.statusText;
      callback(return_object);
    }

    req.send(JSON.stringify(json));
  },

  JsonGet (getUrl, callback) {
    var self = this;

    var req = new XMLHttpRequest();
    var return_object = {'error': null, 'data': null}
    req.overrideMimeType("application/json");
    req.open("GET", getUrl,  true);
    req.setRequestHeader("Content-Type", "application/json");

    req.onload = function (e) {
      if (req.readyState === 4) {
        if (req.status === 200) {
          return_object.data = req.responseText;
          callback(return_object);
        } else {
          console.error(req.statusText);
          return_object.error = req.statusText;
          callback(return_object);
        }
      }
    }

    req.onerror = function (e) {
      return_object.error = req.statusText;
      callback(return_object);
    }

    req.send();
  }
}

export default Utils;