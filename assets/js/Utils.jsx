const Utils = {
  JsonReq (submitUrl, json, method, callback){

    var self = this;

    var return_object = {'error': null, 'data': null}
    
    var req = new XMLHttpRequest();
    req.overrideMimeType("application/json");
    req.open(method, submitUrl,  true);
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

    req.send(json ? JSON.stringify(json) : null);
  }
}

export default Utils;