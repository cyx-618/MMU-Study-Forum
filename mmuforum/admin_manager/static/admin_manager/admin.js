//admin-base
var lastScrollTop = 0;
var banner = document.getElementById('main-banner');

window.addEventListener('scroll', function () {
    let scrollTop = window.pageYOffset || document.documentElement.scrollTop;

    if (scrollTop > lastScrollTop && scrollTop > 100) {
        banner.classList.add('banner-hidden');
    } else {
        banner.classList.remove('banner-hidden');
    }
    lastScrollTop = scrollTop;
});

