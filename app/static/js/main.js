document.addEventListener("DOMContentLoaded", () => {
    const carousel = document.querySelector("[data-hero-carousel]");

    if (!carousel) {
        return;
    }

    const track = carousel.querySelector("[data-hero-track]");
    const slides = Array.from(track.children);
    const dots = Array.from(carousel.querySelectorAll("[data-hero-dot]"));
    const previousButton = carousel.querySelector("[data-hero-prev]");
    const nextButton = carousel.querySelector("[data-hero-next]");
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
    const intervalMilliseconds = 3000;
    let currentIndex = 0;
    let physicalIndex = 1;
    let timerId = null;
    let isAnimating = false;

    if (slides.length < 2) {
        carousel.querySelector(".hero__controls")?.setAttribute("hidden", "");
        return;
    }

    const firstClone = slides[0].cloneNode(true);
    const lastClone = slides[slides.length - 1].cloneNode(true);
    firstClone.setAttribute("aria-hidden", "true");
    lastClone.setAttribute("aria-hidden", "true");
    firstClone.dataset.heroClone = "first";
    lastClone.dataset.heroClone = "last";
    track.append(firstClone);
    track.prepend(lastClone);

    const updateControls = () => {
        slides.forEach((slide, slideIndex) => {
            slide.setAttribute("aria-hidden", String(slideIndex !== currentIndex));
        });

        firstClone.setAttribute("aria-hidden", "true");
        lastClone.setAttribute("aria-hidden", "true");

        dots.forEach((dot, dotIndex) => {
            const isCurrent = dotIndex === currentIndex;
            dot.classList.toggle("is-active", isCurrent);
            dot.toggleAttribute("aria-current", isCurrent);
        });
    };

    const setTrackPosition = (index, animate = true) => {
        if (!animate || reduceMotion.matches) {
            track.style.transition = "none";
        }
        track.style.transform = `translateX(-${index * 100}%)`;

        if (!animate || reduceMotion.matches) {
            track.getBoundingClientRect();
            track.style.transition = "";
        }
    };

    const normalizeClonePosition = () => {
        if (physicalIndex === 0) {
            physicalIndex = slides.length;
            setTrackPosition(physicalIndex, false);
        } else if (physicalIndex === slides.length + 1) {
            physicalIndex = 1;
            setTrackPosition(physicalIndex, false);
        }
        isAnimating = false;
    };

    const moveBy = (direction) => {
        if (isAnimating) {
            return;
        }

        isAnimating = true;
        currentIndex =
            (currentIndex + direction + slides.length) % slides.length;
        physicalIndex += direction;
        updateControls();
        setTrackPosition(physicalIndex);

        if (reduceMotion.matches) {
            normalizeClonePosition();
        }
    };

    const showSlide = (index) => {
        if (isAnimating) {
            return;
        }

        const nextIndex = (index + slides.length) % slides.length;
        if (nextIndex === currentIndex) {
            return;
        }

        isAnimating = true;
        currentIndex = nextIndex;
        physicalIndex = currentIndex + 1;
        updateControls();
        setTrackPosition(physicalIndex);

        if (reduceMotion.matches) {
            normalizeClonePosition();
        }
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
            timerId = window.setInterval(() => moveBy(1), intervalMilliseconds);
        }
    };

    const selectSlide = (index) => {
        showSlide(index);
        startAutoplay();
    };

    previousButton.addEventListener("click", () => {
        moveBy(-1);
        startAutoplay();
    });
    nextButton.addEventListener("click", () => {
        moveBy(1);
        startAutoplay();
    });
    dots.forEach((dot, index) => {
        dot.addEventListener("click", () => selectSlide(index));
    });

    track.addEventListener("transitionend", (event) => {
        if (event.propertyName === "transform") {
            normalizeClonePosition();
        }
    });

    carousel.addEventListener("mouseenter", stopAutoplay);
    carousel.addEventListener("mouseleave", startAutoplay);
    carousel.addEventListener("focusin", stopAutoplay);
    carousel.addEventListener("focusout", (event) => {
        if (!carousel.contains(event.relatedTarget)) {
            startAutoplay();
        }
    });
    document.addEventListener("visibilitychange", startAutoplay);
    reduceMotion.addEventListener("change", () => {
        normalizeClonePosition();
        startAutoplay();
    });

    updateControls();
    setTrackPosition(physicalIndex, false);
    startAutoplay();
});
