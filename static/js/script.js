$(document).ready(function () {
  $('.sidenav').sidenav();
  $('select').formSelect();
  $('.carousel').carousel({
    padding: 200
  });
  autoplay();

  //This fucntion was taken from https://stackoverflow.com/questions/36581504/materialize-carousel-slider-autoplay 
  function autoplay() {
    $('.carousel').carousel('next');
    setTimeout(autoplay, 4000);
  }
});