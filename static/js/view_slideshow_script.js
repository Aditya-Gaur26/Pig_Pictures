function toggleEnlarge(box) {
    var enlargedContainer = document.querySelector('.container');
    var enlargedButtons = document.getElementById('enlargedButtons');
    box.classList.toggle('enlarged');
    enlargedContainer.classList.toggle('enlarged');
    enlargedButtons.style.display = box.classList.contains('enlarged') ? 'flex' : 'none';
}

function pauseSlideshow() {
    // Add logic for pausing the slideshow
    console.log('Slideshow paused');
}

function playSlideshow() {
    // Add logic for playing the slideshow
    console.log('Slideshow played');
}