const domController = () => {
    const _cache = {
        buttons: {
            showAccountControls: document.getElementById(
                "show-account-controls"
            ),
        },
        containers: {
            accountSettingsNav: document.getElementById("account-settings-nav"),
        }
    };

    const toggleAccountControls = () => {
        const container = _cache.containers.accountSettingsNav;
        const isShown = container.classList.contains("shown")

        if (isShown) {
            container.classList.remove("shown");
            return
        }

        container.classList.add("shown")
    }

    const bindEvents = () => {
        const { buttons } = _cache;
        buttons.showAccountControls.onclick = toggleAccountControls;
    };
}

domController().bindEvents()