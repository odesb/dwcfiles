/* Useful function definitions to use anywhere */

// This function can be used to make AJAX requests
function ajaxRequest(url, json, callback) {
  var request = new XMLHttpRequest();
  request.open('GET', url, true);

  request.onload = function() {
    if (this.status >= 200 && this.status < 400) {
      // Success
      if (json) {
        var data = JSON.parse(this.response);
      } else {
        var data = this.response;
      }
      callback(data);
    } else {
      // Error
    }
  };

  request.onerror = function() {
    // Error
  };

  request.send();
}
