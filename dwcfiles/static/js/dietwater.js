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
(function() {
  var file = $('#actualfile');
  var filename = $('#title');
  file.change(function() {
    var clean=file.val().split('\\').pop();
    filename.val(clean);
  });
})();
(function() {
  var modal_close = $('.modal-close');
  var modal_background = $('.modal-background');
  var modal_open = $('.modal-open');
  modal_open.on('click', function() {
    $(this).siblings('.modal').toggleClass('is-active');
  });
  modal_background.on('click', function() {
    $(this).parents('.modal').toggleClass('is-active');
  });
  modal_close.on('click', function() {
    $(this).parents('.modal').toggleClass('is-active');
  });
})();

