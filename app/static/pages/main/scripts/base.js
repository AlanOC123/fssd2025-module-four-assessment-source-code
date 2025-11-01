const domController = () => {
    const _cache = {
        buttons: {
            openIndex: document.getElementById("open-nav"),
            closeIndex: document.getElementById("close-nav"),
            footerControl: document.getElementById("toggle-footer"),
        },
        containers: {
            index: document.getElementById("index"),
            footer: document.getElementById("main-footer"),
        },
    };

    const toggleIndex = () => {
        const { index } = _cache.containers;
        const isShown = index.classList.contains("shown");

        if (isShown) {
            index.classList.remove("shown");
            return;
        }
        index.classList.add("shown");
    };

    const toggleFooter = () => {
        console.log(1)
        const { footer } = _cache.containers;

        footer.classList.toggle("shown")
    }

    const bindEvents = () => {
        const { openIndex, closeIndex, footerControl } = _cache.buttons;

        openIndex.onclick = closeIndex.onclick = toggleIndex;
        footerControl.onclick = toggleFooter;
    };

    return {
        bindEvents,
    };
};

domController().bindEvents();
