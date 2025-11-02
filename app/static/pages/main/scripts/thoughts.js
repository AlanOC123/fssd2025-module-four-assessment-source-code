const domController = () => {
    const _cache = {
        buttons: {
            toggleIdentities: document.getElementById("show-identities"),
            submitThought: document.getElementById("submit-thought"),
            submitThoughtControl: document.getElementById(
                "submit-thought-control"
            ),
            submitIdentitySwitch: document.getElementById("switch-identity"),
        },
        inputs: {
            identityCheckboxes: [
                ...document.querySelectorAll(".select-identity-input"),
            ],
        },
        containers: {
            identitiesMenu: document.getElementById("identity-controls"),
            identityForm: document.getElementById("all-identities-wrapper"),
            thoughtList: document.getElementById('thought-list')
        },
        cards: {
            identityCards: [...document.querySelectorAll(".select-identity")],
        },
    };

    const toggleIdentitiesMenu = () => {
        const { identitiesMenu } = _cache.containers;
        const isShown = identitiesMenu.classList.contains("shown");

        if (isShown) {
            identitiesMenu.classList.remove("shown");
            return
        }

        identitiesMenu.classList.add("shown");
        return
    }

    const processThought = () => {
        const { submitThought } = _cache.buttons;
        const { identityForm } = _cache.containers;
        submitThought.click();
    }

    const processIdentitySwitch = (e) => {
        e.preventDefault();
        const { submitIdentitySwitch } = _cache.buttons;
        submitIdentitySwitch.click();
    }

    const scrollChatToBottom = () => {
        const { thoughtList } = _cache.containers;

        thoughtList.scrollTop = thoughtList.scrollHeight
    }

    const bindEvents = () => {
        const { toggleIdentities, submitThoughtControl } = _cache.buttons;
        const { identityCheckboxes } = _cache.inputs;

        toggleIdentities.onclick = toggleIdentitiesMenu;
        submitThoughtControl.onclick = processThought;
        identityCheckboxes.forEach(el => el.onchange = processIdentitySwitch);
        document.addEventListener('DOMContentLoaded', scrollChatToBottom);
    }

    return {
        bindEvents
    }
}

domController().bindEvents()