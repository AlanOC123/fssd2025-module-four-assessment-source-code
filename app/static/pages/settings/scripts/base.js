const domController = () => {
    const _cache = {
        buttons: {
            openIndex: document.getElementById('open-nav'),
            closeIndex: document.getElementById('close-nav'),
        },
        containers: {
            settingsNav: document.getElementById('settings-index')
        }
    }

    const toggleSettingsNav = () => {
        const { settingsNav } = _cache.containers;
        console.log(settingsNav)
        const isShown = settingsNav.classList.contains('shown');

        if (isShown) {
            settingsNav.classList.remove("shown");
            return
        }
        settingsNav.classList.add('shown');
    }

    const bindEvents = () => {
        const { openIndex, closeIndex } = _cache.buttons;

        openIndex.onclick = closeIndex.onclick = toggleSettingsNav;
    }

    return {
        bindEvents
    }
}

domController().bindEvents()