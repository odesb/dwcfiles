/* Function definitions */

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

// Add AJAX to load buttons on home page
function addEventButtonLess() {
  var load_less = document.querySelector('#load-less');

  load_less.addEventListener('click', function() {
    var invisible_columns = document.querySelectorAll('.columns > .column.is-2.is-gone');
    if (invisible_columns.length === 0) {
      return;
    } else {
      var visible_columns = document.querySelectorAll('.columns > .column.is-2:not(.is-gone)');
      invisible_columns[invisible_columns.length - 1].classList.toggle('is-gone');
      visible_columns[visible_columns.length - 1].classList.toggle('is-gone');
    }
  });
}

function addEventButtonMore() {
  var load_more = document.querySelector('#load-more');
  var increment = 3;

  load_more.addEventListener('click', function() {
    ajaxRequest('/_ajax_more?html5=true&next=' + increment, false, function(data) {
      if (data.length === 0) {
        return;
      } else {
        increment += 3;
        var visible_columns = document.querySelectorAll('.columns > .column.is-2:not(.is-gone)');
        visible_columns[0].classList.toggle('is-gone');
        visible_columns[visible_columns.length - 1].insertAdjacentHTML('afterend', data);
      }
    });
  });
}

// Show/hide the file uploader
function toggleUploader() {
  var togglers = document.querySelectorAll('.toggle-uploader');
  var uploader = document.querySelector('#uploader');
  var overlay = document.querySelector('#uploader-overlay');

  function toggleDisplay() {
    uploader.classList.toggle('is-gone');
    overlay.classList.toggle('is-gone');
  }

  Array.from(togglers).forEach(function(el) {
    el.addEventListener('click', toggleDisplay);
  });
  // If user clicks on overlay, close uploader
  overlay.addEventListener('click', toggleDisplay);
}

// User uploaded file modal events (open and close)
function modalEvents() {
  var modal = document.querySelector('.modal');
  var modal_open = document.querySelector('.modal-open');
  var modal_background = document.querySelector('.modal-background');
  var modal_close = document.querySelector('.modal-close');

  function toggleModalClass() {
    modal.classList.toggle('is-active');
  }

  // Open event
  modal_open.addEventListener('click', toggleModalClass);
  // Close events
  modal_background.addEventListener('click', toggleModalClass);
  modal_close.addEventListener('click', toggleModalClass);
}

// Extract filename from file "loaded" in browser
function extractFilenameEvent() {
  var file = document.querySelector('#actualfile');
  file.addEventListener('change', function() {
    var filename = file.files[0].name;
    document.querySelector('#title').value = filename;
  });
}

