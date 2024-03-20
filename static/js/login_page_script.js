document.addEventListener('DOMContentLoaded', function() {
    const signupLink = document.querySelector('.additional-links a[href="#signup"]');
    const homepageLink = document.querySelector('.additional-links a[href="#homepage"]');
    signupLink.addEventListener('click', function() {
        signupLink.classList.add('clicked');
        homepageLink.classList.remove('clicked');
    });

    homepageLink.addEventListener('click', function() {
        homepageLink.classList.add('clicked');
        signupLink.classList.remove('clicked');
    });

    const passwordInput = document.getElementById('password');
    const showPasswordBtn = document.getElementById('showPasswordBtn');
    showPasswordBtn.innerHTML = '<i class="fas fa-eye-slash"></i>';
    showPasswordBtn.addEventListener('click', function() {
        togglePasswordVisibility();
    });

    function togglePasswordVisibility() {
        const type = passwordInput.type === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);
        showPasswordBtn.innerHTML = type === 'password' ? '<i class="fas fa-eye-slash"></i>' :'<i class="fas fa-eye"></i>' ;
    }
});