const postResponse = async (payload, url) => {
    const csrfToken = document
        .querySelector('meta[name="csrf-token"')
        .getAttribute("content");
    const res = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify(payload),
    });

    console.log(res);

    return res.json();
};

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
            submitCreateTask: document.getElementById("submit-create-task"),
            submitResetTaskForm: document.getElementById("reset-form-data"),
            submitTaskData: document.getElementById("submit-task-data"),
            toggleEditMode: [...document.querySelectorAll(".edit-project")],
            confirmEdits: [...document.querySelectorAll(".confirm-edit")],
            toggleDeleteMode: [...document.querySelectorAll(".delete-project")],
            confirmDelete: [
                ...document.querySelectorAll(".confirm-delete-task"),
            ],
            cancelDelete: [...document.querySelectorAll(".cancel-delete-task")],
            checkTask: [...document.querySelectorAll(".mark-task-complete")],
            uncheckTask: [
                ...document.querySelectorAll(".mark-task-incomplete"),
            ],
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
    };

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

    const processCreateTask = (e) => {
        e.preventDefault();
        const { submitTaskData } = _cache.buttons;
        submitTaskData.click();
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
    };

    const closeNearestSidebar = (e) => {
        const { target } = e;
        const container = target.closest(".sidebar");
        const isShown = container.classList.contains("shown");

        if (isShown) {
            container.classList.remove("shown");
            return;
        }

        container.classList.add("shown");
        return;
    };

    const toggleTaskEditMode = (e) => {
        const { target } = e;
        const card = target.closest(".task-card");
        const isEditing = card.classList.contains("editing");

        if (isEditing) {
            card.classList.remove("editing");
            return;
        }

        card.classList.add("editing");
        return;
    };

    const submitTaskEdits = async (e) => {
        const { target } = e;
        const card = target.closest(".task-card");
        const taskNameInput = card.querySelector(".edit-task-name");
        const taskDueDateInput = card.querySelector(".edit-task-due-date");
        const { taskId } = card.dataset;

        const taskName = taskNameInput.value;
        const taskDueDate = taskDueDateInput.value;

        const payload = {
            taskId,
            taskName,
            taskDueDate,
        };

        const url = "/api/tasks/edit";

        const { success, message } = await postResponse(payload, url);

        if (!success) {
            console.error(message);
        } else {
            console.log(message);
        }

        location.reload()
    };

    const toggleTaskDeletion = (e) => {
        const { target } = e;
        const card = target.closest(".task-card");
        const isDeleting = card.classList.contains("deleting");

        if (isDeleting) {
            card.classList.remove("deleting");
            return;
        }

        card.classList.add("deleting");
        return;
    };

    const submitDeleteTask = async (e) => {
        const { target } = e;
        const card = target.closest(".task-card");
        const { taskId } = card.dataset;

        const payload = {
            taskId,
        };

        const url = "/api/tasks/delete";

        const { success, message } = await postResponse(payload, url);

        if (!success) {
            console.error(message);
        } else {
            console.log(message);
        }

        location.reload()
    };

    const submitTaskStatus = async (e) => {
        const { target } = e;
        const card = target.closest(".task-card");
        const { taskId } = card.dataset;

        console.log(taskId);

        const payload = {
            taskId,
        };

        const url = "/api/tasks/status";

        const { success, message } = await postResponse(payload, url);

        if (!success) {
            console.error(message);
        } else {
            console.log(message);
        }

        location.reload();
    }

    const bindEvents = () => {
        const {
            openCreateTask,
            openIdentities,
            openSelectProject,
            closeSidebars,
            submitCreateTask,
            toggleEditMode,
            confirmEdits,
            toggleDeleteMode,
            confirmDelete,
            cancelDelete,
            checkTask,
            uncheckTask,
        } = _cache.buttons;

        const { identityCheckboxes, switchProjectCheckboxes } = _cache.inputs;

        openCreateTask.onclick = showCreateTask;
        openIdentities.onclick = showSelectIdentity;
        openSelectProject.onclick = showSelectProject;
        closeSidebars.forEach((el) => (el.onclick = closeNearestSidebar));
        identityCheckboxes.forEach(
            (el) => (el.onchange = processIdentitySwitch)
        );
        switchProjectCheckboxes.forEach(
            (el) => (el.onchange = processProjectSwitch)
        );
        submitCreateTask.onclick = processCreateTask;
        toggleEditMode.forEach((el) => (el.onclick = toggleTaskEditMode));
        confirmEdits.forEach((el) => (el.onclick = submitTaskEdits));
        toggleDeleteMode.forEach(el => el.onclick = toggleTaskDeletion);
        confirmDelete.forEach(el => el.onclick = submitDeleteTask);
        cancelDelete.forEach(el => el.onclick = toggleTaskDeletion);
        checkTask.forEach(el => el.onclick = submitTaskStatus);
        uncheckTask.forEach(el => el.onclick = submitTaskStatus);
    };

    return {
        bindEvents,
    };
};

domController().bindEvents();
