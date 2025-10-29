const domController = () => {
    const _cache = {
        buttons: {
            toggleUpdateEmail: document.getElementById("toggle-update-email"),
            toggleUpdatePassword: document.getElementById("toggle-update-password"),
            toggleDeleteAccount: document.getElementById("toggle-delete-account"),
        },
        containers: {
            formWrappers: [
                ...document.querySelectorAll(".form-wrapper"),
            ],
            updateEmail: document.getElementById("update-email"),
            updatePassword: document.getElementById("update-password"),
            deleteAccount: document.getElementById("delete-account"),
        },
    };

    const hideFormContainers = () => {
        const { formWrappers } = _cache.containers;

        formWrappers.forEach(el => el.classList.remove('expanded'))
    }

    const openFormContainer = (form) => {
        form.classList.add('expanded')
    }

    const toggleUpdateEmail = () => {
        const { updateEmail } = _cache.containers
        const isOpen = updateEmail.classList.contains('expanded');

        hideFormContainers();

        if (isOpen) return;

        openFormContainer(updateEmail)
    }

    const toggleUpdatePassword = () => {
        const { updatePassword } = _cache.containers;
        const isOpen = updatePassword.classList.contains("expanded");

        hideFormContainers();

        if (isOpen) return;

        openFormContainer(updatePassword);
    }

    const toggleDeleteAccount = () => {
        const { deleteAccount } = _cache.containers;
        const isOpen = deleteAccount.classList.contains("expanded");

        hideFormContainers();

        if (isOpen) return;

        openFormContainer(deleteAccount);
    }

    const bindEvents = () => {
        const { buttons } = _cache;
        buttons.toggleUpdateEmail.onclick = toggleUpdateEmail;
        buttons.toggleUpdatePassword.onclick = toggleUpdatePassword;
        buttons.toggleDeleteAccount.onclick = toggleDeleteAccount;
    };

    return {
        bindEvents
    }
}

domController().bindEvents()