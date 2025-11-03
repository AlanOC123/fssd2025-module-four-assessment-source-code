const postResponse = async (payload, url) => {
    const csrfToken = document.querySelector('meta[name="csrf-token"').getAttribute('content')
    console.log(csrfToken)
    const res = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify(payload),
    });

    return res.json();
};

const domController = () => {
    const _cache = {
        buttons: {
            toggleIdentities: document.getElementById("show-identities"),
            submitThought: document.getElementById("submit-thought"),
            submitThoughtControl: document.getElementById(
                "submit-thought-control"
            ),
            submitIdentitySwitch: document.getElementById("switch-identity"),
            showThoughtCardControls: [
                ...document.querySelectorAll(".toggle-thought-controls"),
            ],
            deleteThoughtControls: [
                ...document.querySelectorAll(".delete-thought"),
            ],
            editThoughtControls: [
                ...document.querySelectorAll(".edit-thought"),
            ],
            submitEditControls: [...document.querySelectorAll(".confirm-edit")],
            openTimeline: document.getElementById("open-timeline"),
            closeTimeline: document.getElementById("close-timeline"),
        },
        inputs: {
            identityCheckboxes: [
                ...document.querySelectorAll(".select-identity-input"),
            ],
        },
        containers: {
            identitiesMenu: document.getElementById("identity-controls"),
            identityForm: document.getElementById("all-identities-wrapper"),
            thoughtList: document.getElementById("timeline-groupings"),
            thoughtWindow: document.getElementById("view-thoughts"),
            thoughtViewport: document.getElementById('thought-window'),
        },
        cards: {
            identityCards: [...document.querySelectorAll(".select-identity")],
        },
    };

    const noThoughts = () => _cache.containers.thoughtWindow.children.length === 0;

    const toggleTimelineView = () => {
        const { thoughtViewport } = _cache.containers;
        const hasTimeline = thoughtViewport.classList.contains("show-timeline");

        if (hasTimeline) {
            thoughtViewport.classList.remove("show-timeline");
            return
        }

        thoughtViewport.classList.add("show-timeline");
        return
    }

    const toggleIdentitiesMenu = () => {
        const { identitiesMenu } = _cache.containers;
        const isShown = identitiesMenu.classList.contains("shown");

        if (isShown) {
            identitiesMenu.classList.remove("shown");
            return;
        }

        identitiesMenu.classList.add("shown");
        return;
    };

    const processThought = () => {
        const { submitThought } = _cache.buttons;
        submitThought.click();
    };

    const processIdentitySwitch = (e) => {
        e.preventDefault();
        const { submitIdentitySwitch } = _cache.buttons;
        submitIdentitySwitch.click();
    };

    const scrollChatToBottom = () => {
        if (noThoughts()) return;

        const { thoughtList } = _cache.containers;
        if (!thoughtList) return;

        thoughtList.scrollTop = thoughtList.scrollHeight;
    };

    const showThoughtCardControlsMenu = (e) => {
        let { target } = e;

        const menu = target.closest(".controls");
        const isShown = menu.classList.contains("shown");

        if (isShown) {
            menu.classList.remove("shown");
            return;
        }

        menu.classList.add("shown");
    };

    const deleteThought = async (e) => {
        const { target } = e;

        const card = target.closest(".thought-card");
        const { thoughtId } = card.dataset;

        const payload = {
            thoughtId,
        };

        const url = "/api/thought/delete";

        try {
            const res = await postResponse(payload, url);
            const { success, message } = res;

            if (!success) {
                console.error(message)
                return
            }

            console.log(message);
            location.reload()
        } catch (err) {
            console.log(err);
        }
    };

    const toggleEditMode = (e) => {
        e.preventDefault()
        e.stopPropagation()

        const { target } = e;

        const card = target.closest(".thought-card");
        const isEditing = card.classList.contains("editing");

        const input = card.querySelector(".thought-text-input");

        console.log(card)

        if (isEditing) {
            card.classList.remove("editing");
            return
        }

        card.classList.add("editing");
        input.focus();
        return
    }

    const submitThoughtEdit = async (e) => {
        e.preventDefault();
        e.stopPropagation();

        const { target } = e;

        const card = target.closest(".thought-card");
        const isEditing = card.classList.contains("editing");

        const input = card.querySelector(".thought-text-input");
        const { thoughtId } = card.dataset;

        console.log(input.value);

        if (input.checkValidity()) {
            try {
                const payload = {
                    thoughtId,
                    content: input.value,
                };

                const url = '/api/thought/edit'
                const res = await postResponse(payload, url);

                const { message, success } = res;

                if (!success) {
                    console.error(`Error editing thought. Error: ${message}`)
                }

                console.log(message)
                location.reload()

            } catch (err) {
                console.error(err);
            }
        }

        if (isEditing) {
            card.classList.remove("editing");
            return;
        }
    }

    const bindEvents = () => {
        const {
            toggleIdentities,
            submitThoughtControl,
            showThoughtCardControls,
            deleteThoughtControls,
            editThoughtControls,
            submitEditControls,
            openTimeline,
            closeTimeline
        } = _cache.buttons;
        const { identityCheckboxes } = _cache.inputs;

        toggleIdentities.onclick = toggleIdentitiesMenu;
        submitThoughtControl.onclick = processThought;
        identityCheckboxes.forEach(
            (el) => (el.onchange = processIdentitySwitch)
        );
        document.addEventListener("DOMContentLoaded", scrollChatToBottom);
        showThoughtCardControls.forEach(
            (el) => (el.onclick = showThoughtCardControlsMenu)
        );

        deleteThoughtControls.forEach((el) => (el.onclick = deleteThought));
        editThoughtControls.forEach(el => el.onclick = toggleEditMode);
        submitEditControls.forEach(el => el.onclick = submitThoughtEdit);

        openTimeline.onclick = closeTimeline.onclick = toggleTimelineView;
    };

    return {
        bindEvents,
    };
};

domController().bindEvents();
