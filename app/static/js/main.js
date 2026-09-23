document.addEventListener('DOMContentLoaded', () => {
    const carousel = document.querySelector('[data-hero-carousel]');

    if (!carousel) {
        return;
    }

    const track = carousel.querySelector('[data-hero-track]');
    const slides = Array.from(track.children);
    const dots = Array.from(carousel.querySelectorAll('[data-hero-dot]'));
    const previousButton = carousel.querySelector('[data-hero-prev]');
    const nextButton = carousel.querySelector('[data-hero-next]');
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
    const intervalMilliseconds = 5000;
    let currentIndex = 0;
    let timerId = null;

    if (slides.length < 2) {
        carousel.querySelector('.hero__controls')?.setAttribute('hidden', '');
        return;
    }

    const showSlide = (index) => {
        currentIndex = (index + slides.length) % slides.length;
        track.style.transform = `translateX(-${currentIndex * 100}%)`;

        slides.forEach((slide, slideIndex) => {
            slide.setAttribute('aria-hidden', String(slideIndex !== currentIndex));
        });

        dots.forEach((dot, dotIndex) => {
            const isCurrent = dotIndex === currentIndex;
            dot.classList.toggle('is-active', isCurrent);
            dot.toggleAttribute('aria-current', isCurrent);
        });
    };

    const stopAutoplay = () => {
        if (timerId !== null) {
            window.clearInterval(timerId);
            timerId = null;
        }
    };

    const startAutoplay = () => {
        stopAutoplay();

        if (!reduceMotion.matches && !document.hidden) {
            timerId = window.setInterval(() => showSlide(currentIndex + 1), intervalMilliseconds);
        }
    };

    const selectSlide = (index) => {
        showSlide(index);
        startAutoplay();
    };

    previousButton.addEventListener('click', () => selectSlide(currentIndex - 1));
    nextButton.addEventListener('click', () => selectSlide(currentIndex + 1));
    dots.forEach((dot, index) => {
        dot.addEventListener('click', () => selectSlide(index));
    });

    carousel.addEventListener('mouseenter', stopAutoplay);
    carousel.addEventListener('mouseleave', startAutoplay);
    carousel.addEventListener('focusin', stopAutoplay);
    carousel.addEventListener('focusout', (event) => {
        if (!carousel.contains(event.relatedTarget)) {
            startAutoplay();
        }
    });
    document.addEventListener('visibilitychange', startAutoplay);
    reduceMotion.addEventListener('change', startAutoplay);

    showSlide(0);
    startAutoplay();
});
