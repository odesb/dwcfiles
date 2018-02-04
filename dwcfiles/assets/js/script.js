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
function ajaxButtonsEvents() {
  var all_columns = document.getElementsByClassName('column is-2');
  var load_less = document.querySelector('#load-less');
  var load_more = document.querySelector('#load-more');
  var ajaxFinished = false;
  var increment = 3;

  function colWithClass(position, cls, not) {
    var col;
    for (var i = 0; i < all_columns.length; i++) {
      if (all_columns[i].classList.contains(cls) && !all_columns[i].classList.contains(not)) {
        if (position === 'first') {
          return all_columns[i];
        } else if (position === 'last') {
          col = all_columns[i];
        }
      }
    }
    return col;
  }

  load_more.addEventListener('click', function() {
    // If there is no cached files, do a AJAX request
    var first_right_invis = colWithClass('first', 'is-gone', 'left');
    if (first_right_invis === undefined && !ajaxFinished) {
      ajaxRequest('/_ajax_more?html5=true&next=' + increment, false, function(data) {
        if (data.length !== 0) {
          increment += 3;
          var first_visible = colWithClass('first', 'is-2', 'is-gone');
          first_visible.classList.toggle('is-gone');
          first_visible.classList.add('left');
          all_columns[all_columns.length - 1].insertAdjacentHTML('afterend', data);
        }
        else {
          ajaxFinished = true;
        }
      });
    } else if (first_right_invis !== undefined) {
      first_right_invis.classList.toggle('is-gone');
      var first_visible = colWithClass('first', 'is-2', 'is-gone');
      first_visible.classList.toggle('is-gone');
      first_visible.classList.add('left');
    }
  });

  load_less.addEventListener('click', function() {
    var last_left_invis = colWithClass('last', 'left');
    if (last_left_invis !== undefined) {
      last_left_invis.classList.toggle('is-gone');
      last_left_invis.classList.remove('left');
      var last_visible = colWithClass('last', 'is-2', 'is-gone');
      last_visible.classList.toggle('is-gone');
    }
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

