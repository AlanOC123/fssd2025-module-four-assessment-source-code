const domController = () => {
    const _cache = {
        buttons: {
            submitMode: document.getElementById('submit-mode'),
            submitScheme: document.getElementById('submit-scheme'),
        },
        optionContainers: {
            mode: [...document.querySelectorAll('.theme-mode-option')],
            scheme: [...document.querySelectorAll('.theme-scheme-option')],
        }
    }

    const submitMode = () => {
        _cache.buttons.submitMode.click()
    }

    const submitScheme = () => {
        _cache.buttons.submitScheme.click()
    }

    const bindEvents = () => {
        const { mode, scheme } = _cache.optionContainers;
        mode.forEach(el => el.onclick = submitMode)
        scheme.forEach(el => el.onclick = submitScheme)
    }

    return {
        bindEvents
    }
}

domController().bindEvents();