/* Function definitions */

// Show/hide the file uploader
function toggleUploader() {
  var togglers = document.getElementsByClassName('toggle-uploader');
  var uploader = document.querySelector('#uploader');
  Array.from(togglers).forEach(function(el) {
    el.addEventListener('click', function() {
      uploader.classList.toggle('is-gone');
    });
  });
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

