/* Function definitions */

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


/*
(function() {
  var multimediaButton = $('button.multimedia');
  var media_next = 1;
  multimediaButton.on('click', function() {
    multimediaButton.toggleClass('is-loading');
    $.get($SCRIPT_ROOT + '/_ajax_more?html5=true&next=' + media_next, function(data) {
      multimediaButton.parent().before(data);
      media_next += 1;
    });
    multimediaButton.toggleClass('is-loading');
  });
  var otherButton = $('button.other');
  var other_next = 1;
  otherButton.on('click', function() {
    otherButton.toggleClass('is-loading');
    $.get($SCRIPT_ROOT + '/_ajax_more?html5=&next=' + other_next, function(data) {
      otherButton.parent().before(data);
      other_next += 1;
    });
    otherButton.toggleClass('is-loading');
  });
})();
var d = document.getElementById('submit');
function loadButton() {
  d.classList.add('is-loading');
}
*/
