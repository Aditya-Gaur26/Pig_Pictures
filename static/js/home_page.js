document.addEventListener("DOMContentLoaded", function () {
    const sections = document.querySelectorAll('.reveal');

    const options = {
        root: null,
        rootMargin: '0px',
        threshold: 0.3
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, options);

    sections.forEach(section => {
        observer.observe(section);
    });

    const portfolioImages = document.querySelectorAll('.portfolio img');

    portfolioImages.forEach(function (img) {
        img.addEventListener("click", function () {
            // document.body.classList.add("blurred");
            this.classList.add("enlarged");

            // Reset the blur after a short delay (you can adjust the delay)
            setTimeout(function () {
                document.body.classList.remove("blurred");
            }, 1000);
        });
    });
});
document.addEventListener("DOMContentLoaded", function () {
const sections = document.querySelectorAll('.reveal');

const options = {
root: null,
rootMargin: '0px',
threshold: 0.3
};

const observer = new IntersectionObserver((entries, observer) => {
entries.forEach(entry => {
    if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
    }
});
}, options);

sections.forEach(section => {
observer.observe(section);
});

const portfolioImages = document.querySelectorAll('.portfolio img');

portfolioImages.forEach(function (img) {
img.addEventListener("click", function () {
    // Toggle the enlarged class on the clicked image
    this.classList.toggle("enlarged");

    // Reset the blur after a short delay (you can adjust the delay)
    setTimeout(function () {
        document.body.classList.remove("blurred");
    }, 1000);
});
});
 });