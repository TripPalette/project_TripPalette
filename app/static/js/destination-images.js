(() => {
    const endpoint = document.body.dataset.unsplashPhotoEndpoint;
    const elements = Array.from(document.querySelectorAll("[data-unsplash-photo]"));

    if (!endpoint || elements.length === 0) {
        return;
    }

    const pendingNames = [];
    const queuedNames = new Set();
    const loadedNames = new Set();
    const requestByName = new Map();
    const maxConcurrentRequests = 4;
    let activeRequests = 0;

    const matchingElements = (name) => Array.from(
        document.querySelectorAll("[data-unsplash-photo]")
    ).filter((element) => element.dataset.destinationName === name);

    const applyPhoto = (name, photo) => {
        matchingElements(name).forEach((container) => {
            const image = container.querySelector("[data-unsplash-image]");
            if (!image) {
                return;
            }

            const size = image.dataset.unsplashSize === "regular" ? "regular" : "small";
            image.src = photo.urls[size] || photo.urls.regular || photo.urls.small;
            image.alt = image.alt || photo.alt || `${name} 여행 풍경`;
            image.hidden = false;

            const placeholder = container.querySelector("[data-unsplash-placeholder]");
            if (placeholder) {
                placeholder.hidden = true;
            }

            const attribution = container.querySelector("[data-unsplash-attribution]");
            const photographer = container.querySelector("[data-unsplash-photographer]");
            const source = container.querySelector("[data-unsplash-source]");
            if (attribution && photographer && source) {
                photographer.textContent = photo.photographer;
                photographer.href = photo.photographer_url || photo.photo_url;
                source.href = photo.photo_url || photo.unsplash_url;
                attribution.hidden = false;
            }

            container.dataset.unsplashLoaded = "true";
        });
    };

    const loadPhoto = (name) => {
        if (!requestByName.has(name)) {
            const url = `${endpoint}?${new URLSearchParams({ name })}`;
            requestByName.set(
                name,
                fetch(url, { headers: { Accept: "application/json" } })
                    .then((response) => response.ok ? response.json() : null)
                    .catch(() => null)
            );
        }

        return requestByName.get(name).then((payload) => {
            if (payload?.available && payload.photo) {
                applyPhoto(name, payload.photo);
            }
        });
    };

    const runQueue = () => {
        while (activeRequests < maxConcurrentRequests && pendingNames.length > 0) {
            const name = pendingNames.shift();
            queuedNames.delete(name);
            if (loadedNames.has(name)) {
                continue;
            }

            loadedNames.add(name);
            activeRequests += 1;
            loadPhoto(name).finally(() => {
                activeRequests -= 1;
                runQueue();
            });
        }
    };

    const enqueue = (name) => {
        if (!name || queuedNames.has(name) || loadedNames.has(name)) {
            return;
        }
        queuedNames.add(name);
        pendingNames.push(name);
        runQueue();
    };

    if (!("IntersectionObserver" in window)) {
        elements.forEach((element) => enqueue(element.dataset.destinationName));
        return;
    }

    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (!entry.isIntersecting) {
                return;
            }
            observer.unobserve(entry.target);
            enqueue(entry.target.dataset.destinationName);
        });
    }, { rootMargin: "300px 0px" });

    elements.forEach((element) => observer.observe(element));
})();
