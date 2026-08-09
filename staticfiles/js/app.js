(() => {
    "use strict";

    const body = document.body;
    const header = document.querySelector("[data-header]");
    const menuToggle = document.querySelector("[data-menu-toggle]");
    const mainNav = document.querySelector("[data-main-nav]");
    const searchOverlay = document.querySelector("[data-search-overlay]");
    const searchOpen = document.querySelector("[data-search-open]");
    const searchClose = document.querySelector("[data-search-close]");
    const toastStack = document.querySelector("[data-toast-stack]");

    window.addEventListener("scroll", () => {
        header?.classList.toggle("scrolled", window.scrollY > 12);
    }, { passive: true });

    menuToggle?.addEventListener("click", () => {
        const isOpen = mainNav.classList.toggle("open");
        menuToggle.setAttribute("aria-expanded", String(isOpen));
        body.classList.toggle("menu-open", isOpen);
    });

    mainNav?.querySelectorAll("a").forEach((link) => {
        link.addEventListener("click", () => {
            mainNav.classList.remove("open");
            menuToggle?.setAttribute("aria-expanded", "false");
            body.classList.remove("menu-open");
        });
    });

    function openSearch() {
        if (!searchOverlay) return;
        searchOverlay.hidden = false;
        body.classList.add("search-open");
        window.setTimeout(() => searchOverlay.querySelector("input")?.focus(), 50);
    }

    function closeSearch() {
        if (!searchOverlay) return;
        searchOverlay.hidden = true;
        body.classList.remove("search-open");
        searchOpen?.focus();
    }

    searchOpen?.addEventListener("click", openSearch);
    searchClose?.addEventListener("click", closeSearch);
    searchOverlay?.addEventListener("click", (event) => {
        if (event.target === searchOverlay) closeSearch();
    });
    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && searchOverlay && !searchOverlay.hidden) closeSearch();
    });

    function dismissToast(toast) {
        toast.style.opacity = "0";
        toast.style.transform = "translateY(-8px)";
        window.setTimeout(() => toast.remove(), 220);
    }

    function bindToast(toast) {
        toast.querySelector("[data-toast-close]")?.addEventListener("click", () => dismissToast(toast));
        window.setTimeout(() => {
            if (toast.isConnected) dismissToast(toast);
        }, 4500);
    }

    document.querySelectorAll("[data-toast]").forEach(bindToast);

    function showToast(message, type = "success") {
        if (!toastStack) return;
        const toast = document.createElement("div");
        toast.className = `toast toast-${type}`;
        toast.dataset.toast = "";
        const text = document.createElement("span");
        text.textContent = message;
        const button = document.createElement("button");
        button.type = "button";
        button.setAttribute("aria-label", "Dismiss notification");
        button.dataset.toastClose = "";
        button.textContent = "×";
        toast.append(text, button);
        toastStack.append(toast);
        bindToast(toast);
    }

    document.querySelectorAll("[data-quantity]").forEach((control) => {
        const input = control.querySelector("input");
        const minus = control.querySelector("[data-quantity-minus]");
        const plus = control.querySelector("[data-quantity-plus]");
        if (!input) return;

        function setQuantity(value) {
            const min = Number(input.min || 1);
            const max = Number(input.max || 9999);
            input.value = String(Math.max(min, Math.min(max, value)));
        }

        minus?.addEventListener("click", () => setQuantity(Number(input.value || 1) - 1));
        plus?.addEventListener("click", () => setQuantity(Number(input.value || 1) + 1));
        input.addEventListener("change", () => setQuantity(Number(input.value || 1)));
    });

    document.querySelectorAll(".ajax-cart-form").forEach((form) => {
        form.addEventListener("submit", async (event) => {
            event.preventDefault();
            const button = form.querySelector("button[type='submit']");
            const previousText = button?.innerHTML;
            if (button) {
                button.disabled = true;
                button.classList.add("loading");
            }
            try {
                const response = await fetch(form.action, {
                    method: "POST",
                    body: new FormData(form),
                    headers: { "X-Requested-With": "XMLHttpRequest" },
                    credentials: "same-origin",
                });
                const data = await response.json();
                if (!response.ok || !data.ok) throw new Error(data.message || "Unable to update your cart.");
                document.querySelectorAll("[data-cart-count]").forEach((node) => {
                    node.textContent = data.cart_count;
                    node.parentElement?.setAttribute("aria-label", `Cart with ${data.cart_count} items`);
                });
                showToast(data.message, "success");
            } catch (error) {
                showToast(error.message || "Something went wrong. Please try again.", "error");
            } finally {
                if (button) {
                    button.disabled = false;
                    button.classList.remove("loading");
                    button.innerHTML = previousText;
                }
            }
        });
    });

    const mainImage = document.querySelector("[data-main-image]");
    document.querySelectorAll("[data-gallery-image]").forEach((button) => {
        button.addEventListener("click", () => {
            if (mainImage) mainImage.src = button.dataset.galleryImage;
            document.querySelectorAll("[data-gallery-image]").forEach((thumb) => thumb.classList.remove("active"));
            button.classList.add("active");
        });
    });

    document.querySelectorAll("[data-image-fallback]").forEach((image) => {
        image.addEventListener("error", () => {
            if (!image.src.endsWith("/static/images/placeholder.svg")) {
                image.src = "/static/images/placeholder.svg";
            }
        }, { once: true });
    });

    document.querySelector("[data-filter-toggle]")?.addEventListener("click", () => {
        document.querySelector("[data-filter-panel]")?.classList.toggle("open");
    });

    document.querySelectorAll("[data-password-toggle]").forEach((button) => {
        button.addEventListener("click", () => {
            const input = button.parentElement?.querySelector("input");
            if (!input) return;
            const show = input.type === "password";
            input.type = show ? "text" : "password";
            button.textContent = show ? "Hide" : "Show";
            button.setAttribute("aria-label", show ? "Hide password" : "Show password");
        });
    });

    document.querySelectorAll("[data-confirm]").forEach((form) => {
        form.addEventListener("submit", (event) => {
            if (!window.confirm(form.dataset.confirm)) event.preventDefault();
        });
    });

    document.querySelector("[data-newsletter-form]")?.addEventListener("submit", (event) => {
        event.preventDefault();
        event.currentTarget.reset();
        showToast("You’re on the Luxe Letter list.", "success");
    });

    document.querySelectorAll("[data-copy]").forEach((button) => {
        button.addEventListener("click", async () => {
            try {
                await navigator.clipboard.writeText(button.dataset.copy);
                const original = button.textContent;
                button.textContent = "Copied";
                window.setTimeout(() => { button.textContent = original; }, 1500);
            } catch {
                showToast("Copy failed. Select the order number manually.", "error");
            }
        });
    });
})();
