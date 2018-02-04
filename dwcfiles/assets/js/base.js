/* Function defintions used in all views */

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

// Extract filename from file "loaded" in browser
function extractFilenameEvent() {
  var file = document.querySelector('#actualfile');
  file.addEventListener('change', function() {
    var filename = file.files[0].name;
    document.querySelector('#title').value = filename;
  });
}

