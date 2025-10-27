const domController = () => {
    const _cache = {
        tokens: {
            csrfToken: document.getElementById("csrf-token"),
        },
        buttons: {
            openIdentities: document.getElementById("toggle-identities"),
            closeIdentities: document.getElementById("close-identities"),
            openFooter: document.getElementById("open-footer"),
            closeFooter: document.getElementById("close-footer"),
            openMobileMenu: document.getElementById("show-mobile-options"),
        },
        containers: {
            identities: document.getElementById("select-identity"),
            footer: document.querySelector("footer"),
            mobileMenu: document.getElementById("mobile-nav-group"),
        },
        cards: {
            identities: [...document.querySelectorAll(".select-identity")],
            currIdentity: document.getElementById("curr-identity"),
        },
    };

    const toggleIdentities = () => {
        const { buttons, containers } = _cache;
        if (containers.identities.classList.contains("show-all")) {
            buttons.openIdentities.classList.remove("rotate-up");
            containers.identities.classList.remove("show-all");
            return;
        }

        buttons.openIdentities.classList.add("rotate-up");
        containers.identities.classList.add("show-all");
    }

    const toggleMobileMenu = () => {
        _cache.containers.mobileMenu.classList.toggle("expanded");
    }

    const toggleFooter = () => {
        const { containers } = _cache;
        if (containers.footer.classList.contains('expanded')) {
            _cache.containers.footer.classList.remove("expanded");
            return;
        }

        containers.mobileMenu.classList.remove("expanded");
        containers.footer.classList.add("expanded");
    }

    const setCurrentIdentity = (newName, newImageSrc) => {
        const { currIdentity } = _cache.cards;
        const imageContainer = currIdentity.querySelector(".identity-img");
        const nameContainer = currIdentity.querySelector(".identity-name");
        imageContainer.src = newImageSrc;
        nameContainer.textContent = newName;
    }

    const getIdentity = async (e) => {
        e.preventDefault()
        let { target } = e;
        target = target.closest(".select-identity");
        let { dbId } = target.dataset;
        dbId = Number(dbId);

        try {
            const url = "/api/set-identity";
            const response = await fetch(url, {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': _cache.tokens.csrfToken.value,
                },
                body: JSON.stringify({ selectedID: dbId })
            })

            const result = await response.json();
            const { payload } = result;
            setCurrentIdentity(payload.identityName ,payload.identityImagePath);
            _cache.containers.identities.classList.remove("show-all")
        } catch (error) {
            console.log(error);
        }
    };

    const bindEvents = () => {
        const { buttons, cards } = _cache;
        buttons.openIdentities.onclick = toggleIdentities;
        buttons.closeIdentities.onclick = toggleIdentities;
        buttons.openFooter.onclick = buttons.closeFooter.onclick = toggleFooter;
        buttons.openMobileMenu.onclick = toggleMobileMenu;
        cards.identities.forEach(card => card.onclick = getIdentity);
    }

    return {
        bindEvents
    }
}

domController().bindEvents();