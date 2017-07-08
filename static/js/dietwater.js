$(function() {
	var multimediaButton = $('button.multimedia');
	var media_next = 1;
	multimediaButton.on('click', function() {
		multimediaButton.toggleClass('is-loading');
		$.get($SCRIPT_ROOT + '/_ajax_multimedia?next=' + media_next, function(data) {
			multimediaButton.parent().before(data);
			media_next += 1;
		});
		multimediaButton.toggleClass('is-loading');
	});
	var otherButton = $('button.other');
	var other_next = 1;
	otherButton.on('click', function() {
		otherButton.toggleClass('is-loading');
		$.get($SCRIPT_ROOT + '/_ajax_other?next=' + other_next, function(data) {
			otherButton.parent().before(data);
			other_next += 1;
		});
		otherButton.toggleClass('is-loading');
	});
});
var d = document.getElementById('submit');
function loadButton() {
	d.classList.add('is-loading');
}
