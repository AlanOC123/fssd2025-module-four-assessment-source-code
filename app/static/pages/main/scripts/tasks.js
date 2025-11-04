const domController = () => {
    const _cache = {
        buttons: {
            openCreateTask: document.getElementById("show-create-task"),
            openIdentities: document.getElementById("show-select-identity"),
            openSelectProject: document.getElementById("show-select-project"),
            closeSidebars: [...document.querySelectorAll(".close-sidebar")],
            submitIdentitySwitch: document.getElementById("switch-identity"),
            submitProjectSwitch: document.getElementById(
                "switch-project-submit"
            ),
            submitCreateTask: document.getElementById("submit-new-task"),
            submitResetTaskForm: document.getElementById("reset-form-data"),
        },
        cards: {},
        inputs: {
            identityCheckboxes: [
                ...document.querySelectorAll(".select-identity-input"),
            ],
            switchProjectCheckboxes: [
                ...document.querySelectorAll(".project-choice-input"),
            ],
        },
        containers: {
            createTask: document.getElementById("create-task"),
            selectIdentity: document.getElementById("select-identity"),
            selectProject: document.getElementById("select-project"),
        },
    };

    const showCreateTask = () => {
        const { createTask, selectProject } = _cache.containers;
        const { activeProject } = createTask.dataset;

        let container = createTask;
        const hasActiveProject = activeProject === "true";

        if (!hasActiveProject) {
            container = selectProject;
        }

        const isShown = container.classList.contains("shown");

        if (isShown) {
            container.classList.remove("shown");
            return;
        }

        container.classList.add("shown");
        return;
    }

    const showSelectIdentity = () => {
        const { selectIdentity } = _cache.containers;
        const isShown = selectIdentity.classList.contains("shown");

        if (isShown) {
            selectIdentity.classList.remove("shown");
            return;
        }

        selectIdentity.classList.add("shown");
        return;
    };

    const processIdentitySwitch = (e) => {
        e.preventDefault();
        const { submitIdentitySwitch } = _cache.buttons;
        submitIdentitySwitch.click();
    };

    const processProjectSwitch = (e) => {
        e.preventDefault();
        const { submitProjectSwitch } = _cache.buttons;
        submitProjectSwitch.click();
    };

    const showSelectProject = () => {
        const { selectProject } = _cache.containers;
        const isShown = selectProject.classList.contains("shown");

        if (isShown) {
            selectProject.classList.remove("shown");
            return;
        }

        selectProject.classList.add("shown");
        return;
    }

    const closeNearestSidebar = (e) => {
        const { target } = e;
        const container = target.closest(".sidebar");
        const isShown = container.classList.contains("shown");

        if (isShown) {
            container.classList.remove("shown")
            return;
        }

        container.classList.add("shown")
        return;
    }

    const bindEvents = () => {
        const { 
            openCreateTask,
            openIdentities,
            openSelectProject,
            closeSidebars
        } = _cache.buttons;

        const {
            identityCheckboxes,
            switchProjectCheckboxes
        } = _cache.inputs;

        openCreateTask.onclick = showCreateTask;
        openIdentities.onclick = showSelectIdentity;
        openSelectProject.onclick = showSelectProject;
        closeSidebars.forEach(el => el.onclick = closeNearestSidebar);
        identityCheckboxes.forEach(el => el.onchange = processIdentitySwitch);
        switchProjectCheckboxes.forEach(el => el.onchange = processProjectSwitch);
    }

    return {
        bindEvents
    }
}

domController().bindEvents()