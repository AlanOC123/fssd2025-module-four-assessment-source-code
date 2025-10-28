const domController = () => {
    const _cache = {
        buttons: {
            showAccountControls: document.getElementById(
                "show-account-controls"
            ),
            showChangePassword: document.getElementById("open-update-password"),
            closeChangePassword: document.getElementById(
                "close-update-password"
            ),
            showAccountDeletion: document.getElementById(
                "open-account-deletion"
            ),
            closeAccountDeletion: document.getElementById(
                "close-account-deletion"
            ),
        },
        containers: {
            accountSettingsNav: document.getElementById("account-settings-nav"),
            hiddenFormContainers: [
                ...document.querySelectorAll(".hidden-form-container"),
            ],
            updatePassword: document.getElementById("update-password"),
            deleteAccount: document.getElementById("delete-account"),
        },
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

    const hideFormContainers = () => {
        const { hiddenFormContainers } = _cache.containers;

        hiddenFormContainers.forEach(el => el.classList.remove('shown'))
    }

    const openUpdatePassword = () => {
        const { updatePassword } = _cache.containers

        hideFormContainers()
        toggleAccountControls()
        updatePassword.classList.add('shown');
    }

    const closeUpdatePassword = () => {
        hideFormContainers()
    }

    const openDeleteAccount = () => {
        const { deleteAccount } = _cache.containers

        hideFormContainers()
        toggleAccountControls()
        deleteAccount.classList.add('shown');
    }

    const closeDeleteAccount = () => {
        hideFormContainers()
    }

    const bindEvents = () => {
        const { buttons } = _cache;
        buttons.showAccountControls.onclick = toggleAccountControls;
        buttons.showChangePassword.onclick = openUpdatePassword;
        buttons.closeChangePassword.onclick = closeUpdatePassword;
        buttons.showAccountDeletion.onclick = openDeleteAccount;
        buttons.closeAccountDeletion.onclick = closeDeleteAccount;
    };

    return {
        bindEvents
    }
}

domController().bindEvents()