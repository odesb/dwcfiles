/* Functions used in details file view */

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


