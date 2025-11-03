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
            showCreateProject: document.getElementById("create-project-btn"),
            cancelCreateProject: document.getElementById("cancel-creation-btn"),
            showSelectIdentity: document.getElementById("select-identity-btn"),
            cancelSelectIdentity: document.getElementById(
                "cancel-select-identity-btn"
            ),
            submitIdentitySwitch: document.getElementById("switch-identity"),
            createProjectControl: document.getElementById(
                "submit-create-project"
            ),
            createProjectSubmission:
                document.getElementById("submit-new-project"),
            resetProjectControls: document.getElementById("reset-form"),
            resetProjectSubmission: document.getElementById("reset-form-data"),
            enableEditMode: [...document.querySelectorAll(".edit-project")],
            confirmEdits: [...document.querySelectorAll(".confirm-edit")],
            showDeleteProject: [
                ...document.querySelectorAll(".delete-project"),
            ],
            confirmDeleteProject: [
                ...document.querySelectorAll(".confirm-delete-project"),
            ],
            hideDeleteProject: [
                ...document.querySelectorAll(".cancel-delete-project"),
            ],
        },
        containers: {
            createProject: document.getElementById("create-project"),
            selectIdentity: document.getElementById("select-identity"),
        },
        cards: {
            projectCards: [...document.querySelectorAll(".project-card")],
        },
        inputs: {
            identityCheckboxes: [
                ...document.querySelectorAll(".select-identity-input"),
            ],
        },
    };

    const toggleCreateProject = () => {
        const { createProject } = _cache.containers;
        const isShown = createProject.classList.contains("shown");

        console.log(1);

        if (isShown) {
            createProject.classList.remove("shown");
            return;
        }

        createProject.classList.add("shown");
        return;
    };

    const toggleSelectIdentity = () => {
        const { selectIdentity } = _cache.containers;
        console.log(selectIdentity);
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

    const processCreateProjectSubmission = () => {
        const { createProjectSubmission } = _cache.buttons;
        createProjectSubmission.click();
    };

    const processCreateProjectFormReset = () => {
        const { resetProjectSubmission } = _cache.buttons;
        resetProjectSubmission.click();
    };

    const toggleEditMode = (e) => {
        const { target } = e;
        const card = target.closest(".project-card");
        const isEditing = card.classList.contains("editing");

        if (isEditing) {
            card.classList.remove("editing");
            return;
        }

        card.classList.add("editing");
    };

    const submitProjectEdits = async (e) => {
        const { target } = e;
        const card = target.closest(".project-card");

        const projectNameInput = card.querySelector(".edit-project-name");
        const projectDescriptionInput = card.querySelector(
            ".edit-project-description"
        );
        const projectStartDateInput = card.querySelector(
            ".edit-project-start-date"
        );
        const projectEndDateInput = card.querySelector(
            ".edit-project-end-date"
        );
        const { projectId } = card.dataset;

        const payload = {
            projectId,
        };

        if (projectNameInput) payload["projectName"] = projectNameInput.value;
        if (projectDescriptionInput)
            payload["projectDescription"] = projectDescriptionInput.value;
        if (projectStartDateInput)
            payload["projectStartDate"] = projectStartDateInput.value;
        if (projectEndDateInput)
            payload["projectEndDate"] = projectEndDateInput.value;

        const url = "/api/project/edit";

        const res = await postResponse(payload, url);

        const { message, success } = res;

        if (!success) {
            console.error(message);
        } else {
            console.log(message);
        }

        location.reload();
    };

    const submitDeleteProject = async (e) => {
        const { target } = e;
        const card = target.closest(".project-card");

        const { projectId } = card.dataset;

        const payload = {
            projectId,
        };

        const url = "/api/project/delete";

        const res = await postResponse(payload, url);

        const { message, success } = res;

        if (!success) {
            console.error(message);
        } else {
            console.log(message);
        }

        location.reload();
    };

    const toggleDeleteMode = (e) => {
        const { target } = e;
        const card = target.closest(".project-card");
        const isDeleting = card.classList.contains("deleting");

        if (isDeleting) {
            card.classList.remove("deleting");
            return;
        }

        card.classList.add("deleting");
    };

    const bindEvents = () => {
        const {
            showCreateProject,
            cancelCreateProject,
            showSelectIdentity,
            cancelSelectIdentity,
            createProjectControl,
            resetProjectControls,
            enableEditMode,
            confirmEdits,
            showDeleteProject,
            confirmDeleteProject,
            hideDeleteProject
        } = _cache.buttons;

        const { identityCheckboxes } = _cache.inputs;

        showCreateProject.onclick = cancelCreateProject.onclick =
            toggleCreateProject;
        showSelectIdentity.onclick = cancelSelectIdentity.onclick =
            toggleSelectIdentity;
        identityCheckboxes.forEach(
            (el) => (el.onchange = processIdentitySwitch)
        );
        createProjectControl.onclick = processCreateProjectSubmission;
        resetProjectControls.onclick = processCreateProjectFormReset;
        enableEditMode.forEach((el) => (el.onclick = toggleEditMode));
        confirmEdits.forEach((el) => (el.onclick = submitProjectEdits));
        showDeleteProject.forEach(el => el.onclick = toggleDeleteMode);
        hideDeleteProject.forEach(el => el.onclick = toggleDeleteMode);
        confirmDeleteProject.forEach(el => el.onclick = submitDeleteProject)
    };

    return {
        bindEvents,
    };
};

domController().bindEvents();
